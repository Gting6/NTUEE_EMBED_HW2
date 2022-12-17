#include "led-matrix.h"
#include "graphics.h"

#include <jsoncpp/json/value.h>
#include <jsoncpp/json/json.h>
#include <Magick++.h>
#include <magick/image.h>

#include <fstream>
#include <iostream>
#include <string>
#include <signal.h>
#include <unistd.h>
#include <vector>
#include <tuple>

using rgb_matrix::Canvas;
using rgb_matrix::FrameCanvas;
using rgb_matrix::RGBMatrix;
using ImageVector = std::vector<Magick::Image>;

// static bool FullSaturation(const Color &c) {
//   return (c.r == 0 || c.r == 255)
//     && (c.g == 0 || c.g == 255)
//     && (c.b == 0 || c.b == 255);
// }

// Make sure we can exit gracefully when Ctrl-C is pressed.
volatile bool interrupt_received = false;
static void InterruptHandler(int signo)
{
	interrupt_received = true;
}

static Magick::Image LoadImageAndScaleImage(std::string filename, int target_width, int target_height);
void ShowAnimatedImage(const ImageVector &images, RGBMatrix *matrix, int offset_x, int offset_y);
void CopyImageToCanvas(const Magick::Image &image, Canvas *canvas, int offset_x, int offset_y);

int main(int argc, char **argv)
{
	// load json file
	// std::ifstream text_file("/home/ubuntu/web_project/2021_Summer_LED_Rpi_Project/full_web/rpi-rgb-led-matrix/examples-api-use/data.json", std::ifstream::binary);
	std::ifstream text_file("/home/ubuntu/LEDWebEditor/full_web/backend/data.json", std::ifstream::binary);
	Json::Value LEDContent, Programs, HubConfig;
	text_file >> LEDContent;
	Programs = LEDContent["program_list"];
	HubConfig = LEDContent["hub_config"]["rpi_config"];

	// set defaults value
	RGBMatrix::Options my_defaults;
	my_defaults.hardware_mapping = HubConfig["hardware_mapping"].asCString();
	my_defaults.rows = HubConfig["rows"].asInt();
	my_defaults.cols = HubConfig["cols"].asInt();
	my_defaults.chain_length = HubConfig["chain_length"].asInt();
	my_defaults.parallel = HubConfig["parallel"].asInt();
	my_defaults.pwm_bits = HubConfig["pwm_bits"].asInt();
	my_defaults.show_refresh_rate = HubConfig["show_refresh_rate"].asBool();
	// std::tie(
	// 	my_defaults.hardware_mapping,
	// 	my_defaults.rows,
	// 	my_defaults.cols,
	// 	my_defaults.chain_length,
	// 	my_defaults.parallel,
	// 	my_defaults.pwm_bits,
	// 	my_defaults.show_refresh_rate
	// ) = std::make_tuple(
	// 	HubConfig["hardware_mapping"].asString(),
	// 	HubConfig["rows"].asInt(),
	// 	HubConfig["cols"].asInt(),
	// 	HubConfig["chain_length"].asInt(),
	// 	HubConfig["parallel"].asInt(),
	// 	HubConfig["pwm_bits"].asInt(),
	// 	HubConfig["show_refresh_rate"].asBool()
	// );
	// my_defaults.hardware_mapping = "regular";
	// my_defaults.rows = 64;
	// my_defaults.chain_length = 4;
	// my_defaults.cols = 64;
	// my_defaults.pwm_bits = 11; //set from 1 ~ 11
	// my_defaults.show_refresh_rate = true;

	//set privileges **********
	rgb_matrix::RuntimeOptions runtime_defaults;
	runtime_defaults.drop_privileges = HubConfig["drop_privileges"].asInt();

	signal(SIGTERM, InterruptHandler);
	signal(SIGINT, InterruptHandler);

	Magick::InitializeMagick(*argv); //initialize magick
	
	// std::cout << Programs << std::endl;
	//std::cout << "size " << Text["text_data"].size() << std::endl;
	int m = Programs.size();
	// std::cout<<"size: "<<m<<std::endl;
	//int n = Programs["object_list"].size();

	//load font file
	rgb_matrix::Font font;
	if (!font.LoadFont("/home/ubuntu/LEDWebEditor/rpi-rgb-led-matrix/fonts/Microsoft-JhengHei.bdf"))
	{
		fprintf(stderr, "Couldn't load font\n");
		return 1;
	}

	//RGBMatrix *matrix = RGBMatrix::CreateFromFlags(&argc, &argv, &my_defaults, &runtime_defaults);
	RGBMatrix *matrix = RGBMatrix::CreateFromOptions(my_defaults, runtime_defaults);
	//check if matrix is built
	if (matrix == NULL)
	{
		PrintMatrixFlags(stderr, my_defaults, runtime_defaults);
		return 1;
	}

	//Load Image
	//要改成img_name.jpg
	//const char *picname = "./image/test.jpg";
	//matrix->width() 要改成img的參數
	//ImageVector images = LoadImageAndScaleImage(picname, matrix->width(), matrix->height());

	//LED OPERATIONS CODE HERE
	//while (true) {
	//		matrix->Fill(128,128,128);	//r, g, b
	//}
	//matrix.Clear()
	//matrix.SetPixel()		//x, y, r, g, b

	//FrameCanvas *offscreen_canvas = canvas->CreateFrameCanvas();

	// int x = 0;
	// int y = 0;
	// rgb_matrix::Color color(255,0,0);
	// rgb_matrix::Color color2(0,255,0);
	// std::string line1 = "test_text1";
	// std::string line2 = "test_text2";
	int letter_spacing = 0;

	int ***rgb=new int**[m];
	ImageVector *image_set = new ImageVector[m];
	for (int i = 0; i < m; i++)
	{
		int n = Programs[i]["object_list"].size();
		rgb[i] = new int*[n];
		ImageVector images;
		int key = 0 ;
		for(int j=0; j<n; j++){

			if (Programs[i]["object_list"][j]["data_type"].asString() == "0")
			{
				rgb[i][j] = new int[3];
				std::string hex = Programs[i]["object_list"][j]["color"]["hex"].asString().substr(1, 6);
				int r, g, b;
				std::sscanf(hex.c_str(), "%02x%02x%02x", &r, &g, &b);
				//std::cout << r << " " << g << " " << b << std::endl;
				rgb[i][j][0] = r;
				rgb[i][j][1] = g;
				rgb[i][j][2] = b;
			}
			else if(Programs[i]["object_list"][j]["data_type"].asString() == "1"){
				std::string abs_path = "/home/ubuntu/web_project/2021_Summer_LED_Rpi_Project/full_web/rpi-rgb-led-matrix/examples-api-use/";
				std::string img_name = Programs[i]["object_list"][j]["img_name"].asString();
				img_name = abs_path + img_name;
				int width = stoi(Programs[i]["object_list"][j]["img_width"].asString());
				int height = stoi(Programs[i]["object_list"][j]["img_height"].asString());
				std::cout<<"w: "<<width<<" h: "<<height<<std::endl;
				Magick::Image img = LoadImageAndScaleImage(img_name, width, height);
				images.push_back(img);
				key = 1;
			}
		}
		if(key == 1){
			image_set[i] = images;
		}
	}

	matrix->Fill(0, 0, 0);
	while (true)
	{
		for(int j = 0; j<m ;j++){
			int n = Programs[j]["object_list"].size();
			for (int i = 0; i < n; i++)
			{
				// rgb_matrix::Color color(Text["text_content"][i]["color"][0].asInt(), Text["text_content"][i]["color"][1].asInt(), Text["text_content"][i]["color"][2].asInt());
				//if (Programs["object_list"][i]["data_type"].asString() == '0')
				if (Programs[j]["object_list"][i]["data_type"].asString() == "0")
				{
					rgb_matrix::Color color(rgb[j][i][0], rgb[j][i][1], rgb[j][i][2]);
					int x = std::stoi(Programs[j]["object_list"][i]["x"].asString());
					int y = std::stoi(Programs[j]["object_list"][i]["y"].asString());
					rgb_matrix::DrawText(matrix, font, x, y + font.baseline(), color, nullptr, Programs[j]["object_list"][i]["text"].asString().c_str(), letter_spacing);
				}
				else if(Programs[j]["object_list"][i]["data_type"].asString() == "1"){
					for(int k=0;k<image_set[j].size();k++){
						int offset_x = stoi(Programs[j]["object_list"][i]["x"].asString());
						int offset_y = stoi(Programs[j]["object_list"][i]["y"].asString());
						//std::cout<<"x: "<<offset_x<<" y: "<<offset_y<<std::endl;
						CopyImageToCanvas(image_set[j][k], matrix, offset_x, offset_y);
					}
				}
				//rgb_matrix::DrawText(matrix, font, x, y + font.baseline() + 5, color2, nullptr, line2.c_str(), letter_spacing);

				//show image
				// switch (images.size())
				// {
				// case 0: // failed to load image.
				// 	break;
				// case 1: // Simple example: one image to show
				// 	CopyImageToCanvas(images[0], matrix);
				// 	while (!interrupt_received)
				// 		sleep(1000); // Until Ctrl-C is pressed
				// 	break;
				// default: // More than one image: this is an animation.
				// 	ShowAnimatedImage(images, matrix);
				// 	break;
				// }
			}
			sleep(5);
			matrix->Fill(0, 0, 0);
		}

		if (interrupt_received)
			break;
	}

	//delete matrix in the end
	matrix->Clear();
	delete matrix;
}

static Magick::Image LoadImageAndScaleImage(std::string filename, int target_width, int target_height)
{
	ImageVector result;
	ImageVector frames;

	try
	{
		readImages(&frames, filename);
	}
	catch (std::exception &e)
	{
		if (e.what())
			fprintf(stderr, "%s\n", e.what());
		//return result;
	}

	if (frames.empty())
	{
		fprintf(stderr, "No image found.");
		//return result;
	}

	// Animated images have partial frames that need to be put together
	if (frames.size() > 1)
	{
		Magick::coalesceImages(&result, frames.begin(), frames.end());
	}
	else
	{
		result.push_back(frames[0]); // just a single still image.
	}

	for (Magick::Image &image : result)
	{
		frames[0].scale(Magick::Geometry(target_width, target_height));
	}

	return frames[0];
}

//offset_x, offset_y要改成img裏面的參數
void CopyImageToCanvas(const Magick::Image &image, Canvas *canvas, int offset_x, int offset_y)
{											//add offset_x & y to set position
	//const int offset_x = 10, offset_y = 10; // If you want to move the image.
	// Copy all the pixels to the canvas.
	for (size_t y = 0; y < image.rows(); ++y)
	{
		for (size_t x = 0; x < image.columns(); ++x)
		{
			const Magick::Color &c = image.pixelColor(x, y);
			if (c.alphaQuantum() < 256)
			{
				canvas->SetPixel(x + offset_x, y + offset_y,
								 ScaleQuantumToChar(c.redQuantum()),
								 ScaleQuantumToChar(c.greenQuantum()),
								 ScaleQuantumToChar(c.blueQuantum()));
			}
		}
	}
}

void ShowAnimatedImage(const ImageVector &images, RGBMatrix *matrix, int offset_x, int offset_y)
{
	FrameCanvas *offscreen_canvas = matrix->CreateFrameCanvas();
	while (!interrupt_received)
	{
		for (const auto &image : images)
		{
			if (interrupt_received)
				break;
			CopyImageToCanvas(image, offscreen_canvas, offset_x , offset_y);
			offscreen_canvas = matrix->SwapOnVSync(offscreen_canvas);
			usleep(image.animationDelay() * 10000); // 1/100s converted to usec
		}
	}
}