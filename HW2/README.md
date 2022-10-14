# Socket Programming and Data Visualization 
## Experiment Instruction
1. Import `mbed-os-example-sockets` program in MBED Studio
2. Replace `mbed_app.json`, `main.cpp` in the project
3. Use `ipconfig` to check your host's ip address, replace `config['hostname']['value']` in `mbed_app.json` with your ip
4. Run `python HW2.py --num 10` to listen 10 data (one can specify `num` to receive)
5. Build and run in MBED Studio

## Prerequisite
1. `pip install matplotlib`
2. Add Library `BSP_B-L475E-IOT01` in MBED Stuio
3. Use Board `B-L475E-IOT01A2`

## Result
The program will visualize `num` point and plot it as following:
![result](https://user-images.githubusercontent.com/46078333/195804641-ed0a7b71-33fd-4c1d-93d3-81d7f08f8719.png)
