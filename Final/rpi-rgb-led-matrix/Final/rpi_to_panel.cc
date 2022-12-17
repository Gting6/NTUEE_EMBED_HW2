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
	char* fifo_path;
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

rgb_matrix::Color I(23, 222, 238);	// light blue
rgb_matrix::Color J(3, 65, 174);	// deep blue
rgb_matrix::Color L(255, 151, 28);	// orange
rgb_matrix::Color O(255, 213, 0);	// yellow
rgb_matrix::Color S(114, 203, 59);	// green
rgb_matrix::Color T(118, 55, 175);	// purple
rgb_matrix::Color Z(255, 50, 19);	// red

unordered_map<int, RGBColor> id2color = {
	{1, I}, 
	{2, J}, 
	{3, L}, 
	{4, O},
	{5, S},
	{6, T},
	{7, Z}
};

// set panel defaults config
RGBMatrix::Options panel_config;
panel_config.hardware_mapping = "regular";
panel_config.rows = 64;
panel_config.cols = 64;
panel_config.chain_length = 1;
panel_config.parallel = 1;
panel_config.pwm_bits = 11; //set from 1 ~ 11
panel_config.show_refresh_rate = true;
// panel_config.limit_refresh_rate_hz = 30;

//set privileges
rgb_matrix::RuntimeOptions runtime_defaults;
runtime_defaults.drop_privileges = 1;    // 1

// Make sure we can exit gracefully when Ctrl-C is pressed.
volatile bool interrupt_received = false;
static void InterruptHandler(int signo)
{
	interrupt_received = true;
}

void* thread_read_fifo(void* args) {
	/* TODO */
	thread_prop* t_prop = args;

	// int fifo_fd = open(fifo_path, O_RDONLY);
	// read(fifo_fd, t_prop->buf, 1024);
	// close(fifo_fd);
	// unlink(fifo_path);
	cout << t_prop->fifo_path << endl;

	pthread_exit(NULL);
}

/* TODO */
// void draw_screen() {
// 	/* TODO */
// }

int main(int argc, char **argv) {
	signal(SIGTERM, InterruptHandler);
	signal(SIGINT, InterruptHandler);

	// create FIFO
	const char* fifo_path = "./panel.fifo";
	int err = mkfifo(fifo_path, 0666);
	if (err == -1) {
		cerr << "ERROR: mkfifo error\n";
		exit(1);
	}

	pthread_t tid;
	thread_prop* t_prop;
	t_prop->fifo_path = fifo_path;
	int err = pthread_create(&tid, NULL, thread_read_fifo, t_prop);

	RGBMatrix *matrix = RGBMatrix::CreateFromOptions(panel_config, runtime_defaults);
	//check if matrix is built
	if (matrix == NULL) {
		PrintMatrixFlags(stderr, panel_config, runtime_defaults);
		return 1;
	}

	// Create a new canvas to be used with led_matrix_swap_on_vsync
	FrameCanvas *offscreen_canvas = canvas->CreateFrameCanvas();

	// matrix->Fill(0, 0, 0);
	while (!interrupt_received) {
		offscreen_canvas->Fill(0, 0, 0);
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
		offscreen_canvas = canvas->SwapOnVSync(offscreen_canvas);
		// usleep(1000000);
		sleep(3);

		offscreen_canvas->Fill(255, 0, 0);
		offscreen_canvas = canvas->SwapOnVSync(offscreen_canvas);
		// usleep(1000000);
		sleep(3);
	}

	pthread_join(tid, NULL);
	//delete matrix in the end
	matrix->Clear();
	delete matrix;
}