#include "mbed.h"
#include "stm32l475e_iot01_accelero.h"

#include <iostream>
#include <vector>

using namespace std;

#define TEST_LENGTH_SAMPLES 1024
#define BLOCK_SIZE 32

Thread t1;

typedef struct {
  vector<int16_t> buffer;
  int printIndex;
  time_t start;
} SensorData;

void printBuffer(SensorData *sensorData) {
  int blockSize = BLOCK_SIZE;
  int bufferSize;

  while (((time(NULL) - sensorData->start)) < 10) {
    bufferSize = sensorData->buffer.size();
    if (bufferSize - sensorData->printIndex >= blockSize) {
      for (int i = sensorData->printIndex;
           i < sensorData->printIndex + blockSize; i++) {
        // cout << sensorData->buffer[i] << "\n";
        printf("%d,", sensorData->buffer[i]);
      }
      printf("\n");
      sensorData->printIndex += 32;
    }
  }
}

int main() {
  BSP_ACCELERO_Init();
  set_time(1256729737);
  int16_t pDataXYZ[3] = {0};

  SensorData sensorData;
  sensorData.printIndex = 0;
  sensorData.start = time(NULL);
  ; // get current time

  t1.start(callback(printBuffer, &sensorData));

  while (1) {
    BSP_ACCELERO_AccGetXYZ(pDataXYZ);
    sensorData.buffer.push_back(pDataXYZ[2]);
    ThisThread::sleep_for(10);
  }

  t1.join();
}
