#include "mbed.h"
#include "stm32l475e_iot01_accelero.h"
#include "stm32l475e_iot01_gyro.h"
#include "arm_math.h"
#include "math_helper.h"
#include <cstdint>
#include <stdio.h>

#include <cstdint>
#include <cstdio>
#include <iostream>
#include <vector>
#include <map>
#include <string>

using namespace std;

#define LD1_ON     {led1 = 1;}
#define LD1_OFF    {led1 = 0;}
#define LD1_TOG    {led1 = !led1;}

#define LD2_ON     {led2 = 1;}
#define LD2_OFF    {led2 = 0;}
#define LD2_TOG    {led2 = !led2;}


DigitalOut led1(LED1);
DigitalOut led2(LED2);

InterruptIn button1(D2);
InterruptIn button2(D4);



void button1_pressed()
{
    LD1_ON;
}

void button1_released()
{
    LD1_OFF;
}

void button2_pressed()
{
    LD2_ON;
}

void button2_released()
{
    LD2_OFF;
}

void get_up_down(int16_t pDataXYZ, float pGyroDataXYZ, float &angle){
    if (pGyroDataXYZ > 4000){
        angle += pGyroDataXYZ;
    }
    else if (pGyroDataXYZ < -4000){
        angle += pGyroDataXYZ;
    }
    else{
        angle = 0;
    }
    //printf("%.2f\n", angle);
    if (angle > 800000 && pDataXYZ > 1250){
        printf("up\n\n\n");
        ThisThread::sleep_for(300);
        
        angle = 0;
    }
    else if (angle < -800000 && pDataXYZ < 850){
        printf("down\n\n\n");
        ThisThread::sleep_for(300);
        
        angle = 0;
    }
}

void side_rotate(float pGyroDataXYZ, float &angle){
    if (pGyroDataXYZ > 4000){
        angle += pGyroDataXYZ;
    }
    else if (pGyroDataXYZ < -4000){
        angle = 0;
    }
    else{
        angle = 0;
    }
    //printf("%.2f\n", angle);
    if (angle > 3000000){
        printf("rotate\n\n\n");
        ThisThread::sleep_for(200);
        
        angle = 0;
    }
}

char direction[3] = {'l', 'n', 'r'};

int main() {
    
    vector<int16_t> input;


    button1.fall(button1_released); 
    button1.rise(button1_pressed); // Change led

    button2.fall(&button2_released); 
    button2.rise(&button2_pressed); // Chtange led

    BSP_ACCELERO_Init();
    BSP_GYRO_Init();
    int16_t pDataXYZ[3] = {0};
    float pGyroDataXYZ[3] = {0};
    float side_angle = 0;
    float up_down_angle = 0;

    

    while (1) {

        BSP_ACCELERO_AccGetXYZ(pDataXYZ);
        BSP_GYRO_GetXYZ(pGyroDataXYZ);
        get_up_down(pDataXYZ[2], pGyroDataXYZ[0], up_down_angle);
        side_rotate(pGyroDataXYZ[1], side_angle);

        if (led1.read()) {
            printf("%c\n", direction[0]);
            ThisThread::sleep_for(200);
            
        } else if (led2.read()) {
            printf("%c\n", direction[2]);
            ThisThread::sleep_for(200);

        } 
        /*
        else {
            std::cout << direction[1] << std::endl;
        }
        */
        
/*
        // print y and clip_y
        input.push_back(pDataXYZ[2]);
        if (input.size() > 1000){
            for (int i = 0; i < input.size(); i++){
                printf("%d, ", input[i]);
            }
            printf("\n\n");
            break;
        }
        
*/
        ThisThread::sleep_for(10);
    }
    return 0;
}
