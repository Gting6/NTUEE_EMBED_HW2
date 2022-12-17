#include "led-matrix.h"
#include "graphics.h"

#include <fstream>
#include <iostream>
#include <string>
#include <signal.h>
#include <unistd.h>
#include <pthread.h>
#include <vector>
#include <unordered_map>

#include <sys/types.h>
#include <sys/stat.h>

using rgb_matrix::Canvas;
using rgb_matrix::FrameCanvas;
using rgb_matrix::RGBMatrix;
using namespace std;

typedef struct thread_prop {
	const char* fifo_path;
	int buf[1024];
} thread_prop;

// typedef struct RGBColor {
// 	int r;
// 	int g;
// 	int b;
// } RGBColor;

// RGBColor I = {23, 222, 238};	// light blue
// RGBColor J = {3, 65, 174};		// deep blue
// RGBColor L = {255, 151, 28};	// orange
// RGBColor O = {255, 213, 0};		// yellow
// RGBColor S = {114, 203, 59};	// green
// RGBColor T = {118, 55, 175};	// purple
// RGBColor Z = {255, 50, 19};		// red

rgb_matrix::Color bg(0, 0, 100);	// white background

rgb_matrix::Color I(23, 238, 222);	// light blue
rgb_matrix::Color J(3, 174, 65);	// deep blue
rgb_matrix::Color L(255, 28, 151);	// orange
rgb_matrix::Color O(255, 0, 213);	// yellow
rgb_matrix::Color S(114, 59, 203);	// green
rgb_matrix::Color T(118, 175, 55);	// purple
rgb_matrix::Color Z(255, 19, 50);	// red

unordered_map<int, rgb_matrix::Color> id2color = {
	{1, I}, 
	{2, J}, 
	{3, L}, 
	{4, O},
	{5, S},
	{6, T},
	{7, Z}
};

// Make sure we can exit gracefully when Ctrl-C is pressed.
volatile bool interrupt_received = false;
static void InterruptHandler(int signo)
{
	interrupt_received = true;
}

inline bool exists(const char* name) {
    return (access(name, F_OK) != -1);
}

void* thread_read_fifo(void* args) {
	/* TODO */
	thread_prop* t_prop = (thread_prop*)args;

	// int fifo_fd = open(fifo_path, O_RDONLY);
	// read(fifo_fd, t_prop->buf, 1024);
	// close(fifo_fd);
	// unlink(fifo_path);
	cout << t_prop->fifo_path << endl;

	pthread_exit(NULL);
}


void draw_rectangle_outline(FrameCanvas* offscreen_canvas, int x, int y) {
	for (int i=x; i<x+22; i++) {
		offscreen_canvas->SetPixel(i, y, bg.r, bg.g, bg.b);
		offscreen_canvas->SetPixel(i, y+41, bg.r, bg.g, bg.b);
	}
	for (int i=y+1; i<y+41; i++) {
		offscreen_canvas->SetPixel(x, i, bg.r, bg.g, bg.b);
		offscreen_canvas->SetPixel(x+21, i, bg.r, bg.g, bg.b);		
	}
}

void draw_square_outline(FrameCanvas* offscreen_canvas, int x, int y) {
	for (int i=x; i<x+10; i++) {
		offscreen_canvas->SetPixel(i, y, bg.r, bg.g, bg.b);
		offscreen_canvas->SetPixel(i, y+9, bg.r, bg.g, bg.b);
	}
	for (int i=y+1; i<y+10; i++) {
		offscreen_canvas->SetPixel(x, i, bg.r, bg.g, bg.b);
		offscreen_canvas->SetPixel(x+9, i, bg.r, bg.g, bg.b);		
	}
}

void draw_background(FrameCanvas* offscreen_canvas, rgb_matrix::Font& font) {
	int p2_x_offset = 32;
	int letter_spacing = 0;

	// p1
	draw_rectangle_outline(offscreen_canvas, 5, 20);
	draw_square_outline(offscreen_canvas, 5, 9);
	draw_square_outline(offscreen_canvas, 5+12, 9);
	int length = rgb_matrix::DrawText(offscreen_canvas, font,
                                  0, 0 + font.baseline(),
                                  bg, nullptr,
                                  "SCORE", letter_spacing);

	// p2
	draw_rectangle_outline(offscreen_canvas, 5+p2_x_offset, 20);
	draw_square_outline(offscreen_canvas, 5+p2_x_offset, 9);
	draw_square_outline(offscreen_canvas, 5+12+p2_x_offset, 9);
	length = rgb_matrix::DrawText(offscreen_canvas, font,
                                  0+p2_x_offset, 0 + font.baseline(),
                                  bg, nullptr,
                                  "SCORE", letter_spacing);
}

/* TODO */
// void draw_screen() {
// 	/* TODO */
// }

int main(int argc, char **argv) {
	signal(SIGTERM, InterruptHandler);
	signal(SIGINT, InterruptHandler);

	int err;

	// create FIFO
	const char* fifo_path = "./panel.fifo";
	if (exists(fifo_path) == false) {
		err = mkfifo(fifo_path, 0666);
		if (err == -1) {
			cerr << "ERROR: mkfifo error\n";
			exit(1);
		}
	}

	pthread_t tid;
	thread_prop* t_prop = (thread_prop*) malloc(sizeof(thread_prop));
	t_prop->fifo_path = fifo_path;
	err = pthread_create(&tid, NULL, thread_read_fifo, t_prop);

	// set panel defaults config
	RGBMatrix::Options panel_config;
	panel_config.hardware_mapping = "regular";
	panel_config.rows = 64;
	panel_config.cols = 64;
	panel_config.chain_length = 1;
	panel_config.parallel = 1;
	panel_config.pwm_bits = 11; //set from 1 ~ 11
	panel_config.show_refresh_rate = true;
	panel_config.limit_refresh_rate_hz = 80;

	//set privileges
	rgb_matrix::RuntimeOptions runtime_defaults;
	runtime_defaults.drop_privileges = 1;    // 1

	rgb_matrix::Font font;
	if (!font.LoadFont("../fonts/tom-thumb.bdf"))
	{
		fprintf(stderr, "Couldn't load font\n");
		return 1;
	}

	RGBMatrix *matrix = RGBMatrix::CreateFromOptions(panel_config, runtime_defaults);
	//check if matrix is built
	if (matrix == NULL) {
		PrintMatrixFlags(stderr, panel_config, runtime_defaults);
		return 1;
	}

	// Create a new canvas to be used with led_matrix_swap_on_vsync
	FrameCanvas *offscreen_canvas = matrix->CreateFrameCanvas();

	// matrix->Fill(0, 0, 0);
	while (!interrupt_received) {
		offscreen_canvas->Fill(0, 0, 0);
		draw_background(offscreen_canvas, font);
		// length = holds how many pixels our text takes up
		// length = rgb_matrix::DrawText(offscreen_canvas, font,
		// 								x, y + font.baseline(),
		// 								color, nullptr,
		// 								line.c_str(), letter_spacing);

		// if (speed > 0 && --x + length < 0) {
		// 	x = x_orig;
		// 	if (loops > 0) --loops;
		// }

		/*TODO: draw game screen*/ 

		// Swap the offscreen_canvas with canvas on vsync, avoids flickering
		offscreen_canvas = matrix->SwapOnVSync(offscreen_canvas);
		// usleep(1000000);
		sleep(3);

		draw_background(offscreen_canvas, font);
		offscreen_canvas->SetPixel(10, 10, 255, 0, 0);
		offscreen_canvas = matrix->SwapOnVSync(offscreen_canvas);
		// usleep(1000000);
		sleep(3);
	}

	pthread_join(tid, NULL);
	//delete matrix in the end
	matrix->Clear();
	delete matrix;
}