# Mbed-DSP programming
## Experiment instruction
1. New empty Mbed OS program
2. Replace `main.cpp` with github `main.cpp`
3. Replace `targets.json` with github `targets.json` for printing float point 
4. Add the file `arm_fir_data.c` to the project for example test
5. Add library `mbed-dsp` and `BSP_B-L475E-IOT01` to the project
mbed-dsp: https://os.mbed.com/teams/mbed-official/code/mbed-dsp/
BSP_B-L475E-IOT01: https://os.mbed.com/teams/ST/code/BSP_B-L475E-IOT01/
6. Replace `mbed-dsp/cmsis_dsp/TransformFunctions/arm_bitreversal2.S` with github `arm_bitreversal2.S`
7. Using matlab or python to plot the results

## Results
![](https://i.imgur.com/RVqBlF9.png)
![](https://i.imgur.com/7GWbd1n.png)