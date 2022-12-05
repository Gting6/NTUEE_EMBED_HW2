#include "mbed.h"
#include <vector>
#include <string>
#include <iostream>

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

std::vector<std::string> direction = {"left", "none", "right"};
std::string d;

int main()
{
    button1.fall(button1_released); 
    button1.rise(button1_pressed); // Change led

    button2.fall(&button2_released); 
    button2.rise(&button2_pressed); // Chtange led

    while (1){
        if (led1.read()) {
            std::cout << direction[0] << std::endl;
        } else if (led2.read()) {
            std::cout << direction[2] << std::endl;
        } else {
            std::cout << direction[1] << std::endl;
        }
        
        // printf("%s \n", d);…
        ThisThread:ThisThread::sleep_for(10);
    };
}