#include "led-matrix.h"
#include "graphics.h"
#include "threaded-canvas-manipulator.h"

#include <fstream>
#include <iostream>
#include <string>
#include <signal.h>
#include <unistd.h>
#include <pthread.h>
#include <fcntl.h>
#include <errno.h>
#include <cstring>
#include <vector>
#include <unordered_map>

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/select.h>

using rgb_matrix::Canvas;
using rgb_matrix::FrameCanvas;
using rgb_matrix::RGBMatrix;
using namespace std;

#define RECTANGLE_X_OFFSET 5
#define RECTANGLE_Y_OFFSET 22
#define SQUARE_X_OFFSET 5
#define SQUARE_Y_OFFSET 12

typedef struct Stats {
	int player0_main[10][20];
	int player0_shift[4][4];
	int player0_next[4][4];
	int player0_pts;
	int player0_cbs;
	int player1_main[10][20];
	int player1_shift[4][4];
	int player1_next[4][4];
	int player1_pts;
	int player1_cbs;
} Stats;

Stats stats = {
	{0},
	{0},
	{0},
	0,
	0,
	{0},
	{0},
	{0},
	0,
	0,
};
pthread_mutex_t stats_lock = PTHREAD_MUTEX_INITIALIZER;

rgb_matrix::Color bg(100, 255, 200);	// white background
rgb_matrix::Color text(255, 0, 255);	// white background

rgb_matrix::Color EMPTY(0, 0, 0);	// void black
rgb_matrix::Color I(23, 238, 222);	// light blue
rgb_matrix::Color J(3, 174, 65);	// deep blue
rgb_matrix::Color L(255, 28, 151);	// orange
rgb_matrix::Color O(255, 0, 213);	// yellow
rgb_matrix::Color S(114, 59, 203);	// green
rgb_matrix::Color T(118, 175, 55);	// purple
rgb_matrix::Color Z(255, 19, 50);	// red

unordered_map<int, rgb_matrix::Color> id2color = {
	{0, EMPTY},
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

void thread_read_fifo(const char* fifo_path) {
	Stats packet;
	int fifo_fd;
	
	cerr << "thread start" << endl;

	do {
		fifo_fd = open(fifo_path, O_RDONLY);
		cerr << fifo_fd << endl;
	} while (!interrupt_received && fifo_fd == -1);
	
	if (interrupt_received) {
		cerr << "thread end " << endl;
		int err = unlink(fifo_path);
		return;
	}

	if (fifo_fd == -1) {
		cerr << "open error" << endl;
		exit(1);
	}

	int ready;

	fd_set readset;
	timeval timeout;
	FD_ZERO(&readset);
	FD_SET(fifo_fd, &readset);
	timeout.tv_sec = 1;
	timeout.tv_usec = 0;

	while (!interrupt_received) {
		cerr << "thread loop" << endl;
		ready = select(fifo_fd+1, &readset, NULL, NULL, &timeout);
		if (ready == 1) {
			cerr << "ready" << endl;
			read(fifo_fd, &packet, sizeof(Stats));
			/* TODO: write to stats */
			int ret = pthread_mutex_trylock(&stats_lock);
			if (ret == 0) {
				stats = packet;
				pthread_mutex_unlock(&stats_lock);
			}
		} else if (ready == -1) {
			cerr << "select error" << endl;
			exit(1);
		}
		
	}

	close(fifo_fd);
	unlink(fifo_path);
	cerr << "thread end" << endl;

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
	int next_shift_x_offset = 12;
	int letter_spacing = 0;

	// p1
	draw_rectangle_outline(offscreen_canvas, RECTANGLE_X_OFFSET, RECTANGLE_Y_OFFSET);
	draw_square_outline(offscreen_canvas, SQUARE_X_OFFSET, SQUARE_Y_OFFSET);
	draw_square_outline(offscreen_canvas, SQUARE_X_OFFSET+next_shift_x_offset, SQUARE_Y_OFFSET);
	/*int length = */rgb_matrix::DrawText(offscreen_canvas, font,
								  0, 0 + font.baseline(),
								  text, nullptr,
								  "SCORE", letter_spacing);
	rgb_matrix::DrawText(offscreen_canvas, font,
								  0, 6 + font.baseline(),
								  text, nullptr,
								  "COMBO", letter_spacing);


	// p2
	draw_rectangle_outline(offscreen_canvas, RECTANGLE_X_OFFSET+p2_x_offset, RECTANGLE_Y_OFFSET);
	draw_square_outline(offscreen_canvas, SQUARE_X_OFFSET+p2_x_offset, SQUARE_Y_OFFSET);
	draw_square_outline(offscreen_canvas, SQUARE_X_OFFSET+next_shift_x_offset+p2_x_offset, SQUARE_Y_OFFSET);
	rgb_matrix::DrawText(offscreen_canvas, font,
								  0+p2_x_offset, 0 + font.baseline(),
								  text, nullptr,
								  "SCORE", letter_spacing);
	rgb_matrix::DrawText(offscreen_canvas, font,
								  0+p2_x_offset, 6 + font.baseline(),
								  text, nullptr,
								  "COMBO", letter_spacing);
}

void draw_pixel(FrameCanvas* offscreen_canvas, int x, int y, rgb_matrix::Color& color) {
	for (int i=x; i<x+2; i++) {
		for (int j=y; j<y+2; j++) {
			offscreen_canvas->SetPixel(i, j, color.r, color.g, color.b);
		}
	}
}

void draw_rectangle_content(FrameCanvas* offscreen_canvas) {
	int p2_x_offset = 32;
	rgb_matrix::Color color;

	for (int i=0; i<10; i++) {
		for (int j=0; j<20; j++) {
			color = id2color[stats.player0_main[i][j]];
			draw_pixel(
				offscreen_canvas, 
				RECTANGLE_X_OFFSET+1+2*i, 
				RECTANGLE_Y_OFFSET+1+2*j,
				color
			);

			color = id2color[stats.player1_main[i][j]];
			draw_pixel(
				offscreen_canvas, 
				RECTANGLE_X_OFFSET+p2_x_offset+1+2*i, 
				RECTANGLE_Y_OFFSET+1+2*j,
				color
			);
		}
	}
}

void draw_square_content(FrameCanvas* offscreen_canvas) {
	int p2_x_offset = 32;
	int next_shift_x_offset = 12;
	rgb_matrix::Color color;

	for (int i=0; i<4; i++) {
		for (int j=0; j<4; j++) {
			color = id2color[stats.player0_next[i][j]];
			draw_pixel(
				offscreen_canvas, 
				SQUARE_X_OFFSET+1+2*i, 
				SQUARE_Y_OFFSET+1+2*j,
				color
			);

			color = id2color[stats.player0_shift[i][j]];
			draw_pixel(
				offscreen_canvas, 
				SQUARE_X_OFFSET+next_shift_x_offset+1+2*i, 
				SQUARE_Y_OFFSET+1+2*j,
				color
			);

			color = id2color[stats.player1_next[i][j]];
			draw_pixel(
				offscreen_canvas, 
				SQUARE_X_OFFSET+p2_x_offset+1+2*i, 
				SQUARE_Y_OFFSET+1+2*j,
				color
			);

			color = id2color[stats.player1_shift[i][j]];
			draw_pixel(
				offscreen_canvas, 
				SQUARE_X_OFFSET+next_shift_x_offset+p2_x_offset+1+2*i, 
				SQUARE_Y_OFFSET+1+2*j,
				color
			);
		}
	}
}

void draw_text(FrameCanvas* offscreen_canvas, rgb_matrix::Font& font) {
/* TODO */
	int letter_spacing = 0;
	rgb_matrix::DrawText(offscreen_canvas, font,
								  20, 0 + font.baseline(),
								  text, nullptr,
								  "200", letter_spacing);
}

/* TODO */
void draw_stats(FrameCanvas* offscreen_canvas, rgb_matrix::Font& font) {
	int ret = pthread_mutex_trylock(&stats_lock);
	if (ret == 0) {
		draw_rectangle_content(offscreen_canvas);
		draw_square_content(offscreen_canvas);
		draw_text(offscreen_canvas, font);

		pthread_mutex_unlock(&stats_lock);
	}
}

class BackgroundThread : public rgb_matrix::ThreadedCanvasManipulator {
	public:
		BackgroundThread(RGBMatrix *matrix) : rgb_matrix::ThreadedCanvasManipulator(matrix), matrix_(matrix) {
			offscreen_canvas = matrix->CreateFrameCanvas();
			if (!font.LoadFont("../fonts/tom-thumb.bdf")) {
				cerr << "Couldn't load font\n";
			}
		}
		virtual void Run() {
			// unsigned char c;
			// while (running()) {
			// 	// Calculate the next frame.
			// 	c++;
			// 	for (int x = 0; x < canvas()->width(); ++x) {
			// 		for (int y = 0; y < canvas()->height(); ++y) {
			// 			canvas()->SetPixel(x, y, c, c, c);
			// 		}
			// 	}
			// 	usleep(15 * 1000);
			// }

			draw_background(offscreen_canvas, font);
			offscreen_canvas = matrix_->SwapOnVSync(offscreen_canvas);
			draw_background(offscreen_canvas, font);


			while (running() && !interrupt_received) {
				offscreen_canvas->SetPixel(10, 10, 0, 0, 0);
				draw_stats(offscreen_canvas, font);
				// Swap the offscreen_canvas with canvas on vsync, avoids flickering
				offscreen_canvas = matrix_->SwapOnVSync(offscreen_canvas);
				usleep(100000);	// sleep 0.1 s

				offscreen_canvas->SetPixel(10, 10, 255, 0, 0);
				draw_stats(offscreen_canvas, font);
				offscreen_canvas = matrix_->SwapOnVSync(offscreen_canvas);
				usleep(100000);
			}
		}
	private:
		RGBMatrix *const matrix_;
		FrameCanvas *offscreen_canvas;
		rgb_matrix::Font font;
};


int main(int argc, char **argv) {
	signal(SIGTERM, InterruptHandler);
	signal(SIGINT, InterruptHandler);

	int err;
	memset(&stats, 0, sizeof(Stats));

	// create FIFO
	const char* fifo_path = "./panel.fifo";
	if (exists(fifo_path) == false) {
		err = mkfifo(fifo_path, 0666);
		if (err == -1) {
			cerr << "ERROR: mkfifo error\n";
			exit(1);
		}
	}

	// pthread_t tid;
	// err = pthread_create(&tid, NULL, thread_read_fifo, const_cast<char *> (fifo_path));

	// set panel defaults config
	RGBMatrix::Options panel_config;
	panel_config.hardware_mapping = "regular";
	panel_config.rows = 64;
	panel_config.cols = 64;
	panel_config.chain_length = 1;
	panel_config.parallel = 1;
	panel_config.pwm_bits = 11; //set from 1 ~ 11
	panel_config.show_refresh_rate = false;
	panel_config.limit_refresh_rate_hz = 80;

	//set privileges
	rgb_matrix::RuntimeOptions runtime_defaults;
	runtime_defaults.drop_privileges = 1;    // 1

	// rgb_matrix::Font font;
	// if (!font.LoadFont("../fonts/tom-thumb.bdf"))
	// {
	// 	fprintf(stderr, "Couldn't load font\n");
	// 	return 1;
	// }

	// rgb_matrix::Color test = id2color[1];
	// cout << "r g b" << unsigned(test.r) << unsigned(test.g) << unsigned(test.b) << endl;

	RGBMatrix *matrix = RGBMatrix::CreateFromOptions(panel_config, runtime_defaults);
	//check if matrix is built
	if (matrix == NULL) {
		PrintMatrixFlags(stderr, panel_config, runtime_defaults);
		return 1;
	}
	matrix->Fill(0, 0, 0);

	BackgroundThread *background_matrix = new BackgroundThread(matrix);
	background_matrix->Start();

	Stats packet;
	int fifo_fd;

	while (!interrupt_received) {
		cerr << "thread start" << endl;

		do {
			fifo_fd = open(fifo_path, O_RDONLY | O_NONBLOCK);
			cerr << fifo_fd << endl;
		} while (!interrupt_received && fifo_fd == -1);
		
		if (interrupt_received) {
			cerr << "thread end " << endl;
			break;
		}

		if (fifo_fd == -1) {
			cerr << "open error" << endl;
			exit(1);
		}

		// int ready;

		// fd_set readset;
		// timeval timeout;
		// FD_ZERO(&readset);
		// FD_SET(fifo_fd, &readset);
		// timeout.tv_sec = 1;
		// timeout.tv_usec = 0;

		while (!interrupt_received) {
			cerr << "thread loop" << endl;
			// ready = select(fifo_fd+1, &readset, NULL, NULL, &timeout);
			// if (ready == 1) {
			// 	cerr << "ready" << endl;
			// 	read(fifo_fd, &packet, sizeof(Stats));
			// 	/* TODO: write to stats */
			// 	int ret = pthread_mutex_trylock(&stats_lock);
			// 	if (ret == 0) {
			// 		stats = packet;
			// 		pthread_mutex_unlock(&stats_lock);
			// 	}
			// } else if (ready == -1) {
			// 	cerr << "select error" << endl;
			// 	exit(1);
			// }
			int n = read(fifo_fd, &packet, sizeof(Stats));
			if (n == sizeof(Stats)) {
				int ret = pthread_mutex_trylock(&stats_lock);
				if (ret == 0) {
					stats = packet;
					pthread_mutex_unlock(&stats_lock);
				}
			}
			
		}

		close(fifo_fd);
		unlink(fifo_path);
		cerr << "thread end" << endl;
	}


	background_matrix->Stop();
	delete background_matrix;
	delete matrix;


	// Create a new canvas to be used with led_matrix_swap_on_vsync
	// FrameCanvas *offscreen_canvas = matrix->CreateFrameCanvas();
	// draw_background(offscreen_canvas, font);
	// offscreen_canvas = matrix->SwapOnVSync(offscreen_canvas);
	// draw_background(offscreen_canvas, font);

	// while (!interrupt_received) {
	// 	offscreen_canvas->SetPixel(10, 10, 0, 0, 0);
	// 	// draw_stats(offscreen_canvas);
	// 	// Swap the offscreen_canvas with canvas on vsync, avoids flickering
	// 	offscreen_canvas = matrix->SwapOnVSync(offscreen_canvas);
	// 	usleep(100000);	// sleep 0.1 s

	// 	offscreen_canvas->SetPixel(10, 10, 255, 0, 0);
	// 	// draw_stats(offscreen_canvas);
	// 	offscreen_canvas = matrix->SwapOnVSync(offscreen_canvas);
	// 	usleep(100000);
	// }

	// pthread_join(tid, NULL);
	//delete matrix in the end
	// matrix->Clear();
	// delete matrix;
}