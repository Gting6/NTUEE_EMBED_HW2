# Tetris Battle 2.0
We use STM32 as joysticks, RPI to run the program, and Screen or LED Board to display a Tetris Battle Game!

## Prequisite
- `pygame`

## Demo
1. Please check the video below: https://youtu.be/rcX75-qD13I
2. A slide for introduction: `Demo Slide.pdf`
3. A report for technical detail: `Final Report.pdf`

Some Screenshots:
<img width="582" alt="image" src="https://user-images.githubusercontent.com/46078333/209315081-62248a95-53dc-40ea-bdbf-e48494b2353b.png">
<img width="960" alt="image" src="https://user-images.githubusercontent.com/46078333/209315214-d7f6a900-9213-46e2-9178-d7bd46498e94.png">
<img width="342" alt="image" src="https://user-images.githubusercontent.com/46078333/209315025-5fa43155-7685-4262-8037-99ac9c633d8b.png">


## To Reproduce
### rpi
- `make; ./rpi_to_panel`
- `python s3.py`: open tetris server
- `python t3.py`: use LED to play
### stm32
- import `mbed-os-example-sockets` in mbed studio. Replace `main.cpp` with repo's `main.cpp`. Setting ssid and password in `mbed_app.json`. Clean build and run on stm32.

If one want to play on PC, use `t.py` for tetris client
* Rember to update your IP at `n / n3.py`, `s / s3.py`
