#include "mbed.h"
#include "stm32l475e_iot01_accelero.h"
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

#define BUFFER_SIZE 320
#define DSP_WINDOW 160
#define DSP_BLOCK 16
#if defined(ARM_MATH_MVEF) && !defined(ARM_MATH_AUTOVECTORIZE)
#define NUM_TAPS_ARRAY_SIZE              32
#else
#define NUM_TAPS_ARRAY_SIZE              32
#endif
#define NUM_TAPS              16

static float32_t testOutput[DSP_WINDOW];
#if defined(ARM_MATH_MVEF) && !defined(ARM_MATH_AUTOVECTORIZE)
static float32_t firStateF32[2 * DSP_BLOCK + NUM_TAPS - 1];
#else
static float32_t firStateF32[DSP_BLOCK + NUM_TAPS - 1];
#endif 
#if defined(ARM_MATH_MVEF) && !defined(ARM_MATH_AUTOVECTORIZE)
const float32_t firCoeffs32[NUM_TAPS_ARRAY_SIZE] = {
  -0.0018225230f, -0.0015879294f, +0.0000000000f, +0.0036977508f, +0.0080754303f, +0.0085302217f, -0.0000000000f, -0.0173976984f,
  -0.0341458607f, -0.0333591565f, +0.0000000000f, +0.0676308395f, +0.1522061835f, +0.2229246956f, +0.2504960933f, +0.2229246956f,
  +0.1522061835f, +0.0676308395f, +0.0000000000f, -0.0333591565f, -0.0341458607f, -0.0173976984f, -0.0000000000f, +0.0085302217f,
  +0.0080754303f, +0.0036977508f, +0.0000000000f, -0.0015879294f, -0.0018225230f, 0.0f,0.0f,0.0f
};
#else
const float32_t firCoeffs32[NUM_TAPS_ARRAY_SIZE] = {
  -0.0018225230f, -0.0015879294f, +0.0000000000f, +0.0036977508f, +0.0080754303f, +0.0085302217f, -0.0000000000f, -0.0173976984f,
  -0.0341458607f, -0.0333591565f, +0.0000000000f, +0.0676308395f, +0.1522061835f, +0.2229246956f, +0.2504960933f, +0.2229246956f,
  +0.1522061835f, +0.0676308395f, +0.0000000000f, -0.0333591565f, -0.0341458607f, -0.0173976984f, -0.0000000000f, +0.0085302217f,
  +0.0080754303f, +0.0036977508f, +0.0000000000f, -0.0015879294f, -0.0018225230f
};
#endif
uint32_t blockSize = DSP_BLOCK;
uint32_t numBlocks = DSP_WINDOW/DSP_BLOCK;

typedef struct {
  vector<int16_t> buffer;
  int printIndex;
  time_t start;
} SensorData;

class FSM{
public:
    string state = "WAIT";
    map<string, map<int, string>> fsm = {
        {"WAIT", {{0, "WAIT"}, {1, "S1"}, {-1, "S4"}}},
        {"S1", {{0, "S1"}, {1, "S1"}, {-1, "S2"}}},
        {"S2", {{0, "S2"}, {1, "S3"}, {-1, "S2"}}},
        {"S3", {{0, "WAIT"}, {1, "S3"}, {-1, "ERROR"}}},
        {"S4", {{0, "S4"}, {1, "S5"}, {-1, "S4"}}},
        {"S5", {{0, "S5"}, {1, "S5"}, {-1, "S6"}}},
        {"S6", {{0, "WAIT"}, {1, "ERROR"}, {-1, "S6"}}}
    };
    vector<char> actions;


    string _change_state(int16_t input){
        state = fsm[state][input];
        if (state == "ERROR"){
            state = "WAIT";
            return "ERROR";
        }
        return state;
    }
};

void clip(int16_t &input){
    if (input > 750 && input < 1400) input = 0;
    else if (input >= 1400) input = 1;
    else input = -1;
}

// single simple with fsm
void get_up_down(int16_t input, FSM &fsm){
    int16_t data = input;
    clip(data);

    // using fsm
    string state = fsm.state;
    if (state == "S3"){
        if (fsm._change_state(data) == "WAIT") printf("%c\n", 'u');
    }
    else if (state  == "S6"){
        if (fsm._change_state(data) == "WAIT") printf("%c\n", 'd');
    }
    else fsm._change_state(data);
}

void fir(float32_t *input){
    uint32_t i;
    arm_fir_instance_f32 S;
    arm_status status;
    float32_t  *inputF32, *outputF32;
    inputF32 =  &input[0];
    outputF32 = &testOutput[0];
    arm_fir_init_f32(&S, NUM_TAPS, (float32_t *)&firCoeffs32[0], &firStateF32[0], blockSize);
    for(i=0; i < numBlocks; i++)
    {
        arm_fir_f32(&S, inputF32 + (i * blockSize), outputF32 + (i * blockSize), blockSize);
    }
}


int main() {
    
    BSP_ACCELERO_Init();
    int16_t pDataXYZ[3] = {0};
    FSM fsm;
    vector<int16_t> input;

    while (1) {
        BSP_ACCELERO_AccGetXYZ(pDataXYZ);
        get_up_down(pDataXYZ[2], fsm);
        
/*
        // print y and clip_y
        input.push_back(pDataXYZ[2]);
        if (input.size() > 1000){
            for (int i = 0; i < input.size(); i++){
                printf("%d, ", input[i]);
            }

            printf("\n\n");

            for (int i = 0; i < input.size(); i++){
                clip(input[i]);
                printf("%d, ", input[i]);
            }
            break;
        }
        
*/
        ThisThread::sleep_for(10);
    }
    return 0;
}
