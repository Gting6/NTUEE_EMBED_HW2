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

#include "wifi_helper.h"
#include "mbed-trace/mbed_trace.h"

#include "stm32l475e_iot01_gyro.h"

#if MBED_CONF_APP_USE_TLS_SOCKET
#include "root_ca_cert.h"

#ifndef DEVICE_TRNG
#error "mbed-os-example-tls-socket requires a device which supports TRNG"
#endif
#endif // MBED_CONF_APP_USE_TLS_SOCKET

using namespace std;

#define BUFFER_SIZE 320
#define DSP_WINDOW 160
#define DSP_BLOCK 16
#if defined(ARM_MATH_MVEF) && !defined(ARM_MATH_AUTOVECTORIZE)
#define NUM_TAPS_ARRAY_SIZE 32
#else
#define NUM_TAPS_ARRAY_SIZE 32
#endif
#define NUM_TAPS 16

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
    +0.0080754303f, +0.0036977508f, +0.0000000000f, -0.0015879294f, -0.0018225230f, 0.0f, 0.0f, 0.0f};
#else
const float32_t firCoeffs32[NUM_TAPS_ARRAY_SIZE] = {
    -0.0018225230f, -0.0015879294f, +0.0000000000f, +0.0036977508f, +0.0080754303f, +0.0085302217f, -0.0000000000f, -0.0173976984f,
    -0.0341458607f, -0.0333591565f, +0.0000000000f, +0.0676308395f, +0.1522061835f, +0.2229246956f, +0.2504960933f, +0.2229246956f,
    +0.1522061835f, +0.0676308395f, +0.0000000000f, -0.0333591565f, -0.0341458607f, -0.0173976984f, -0.0000000000f, +0.0085302217f,
    +0.0080754303f, +0.0036977508f, +0.0000000000f, -0.0015879294f, -0.0018225230f};
#endif
uint32_t blockSize = DSP_BLOCK;
uint32_t numBlocks = DSP_WINDOW / DSP_BLOCK;

typedef struct
{
    vector<int16_t> buffer;
    int printIndex;
    time_t start;
} SensorData;

class FSM
{
public:
    string state = "WAIT";
    map<string, map<int, string>> fsm = {
        {"WAIT", {{0, "WAIT"}, {1, "S1"}, {-1, "S4"}}},
        {"S1", {{0, "S1"}, {1, "S1"}, {-1, "S2"}}},
        {"S2", {{0, "S2"}, {1, "S3"}, {-1, "S2"}}},
        {"S3", {{0, "WAIT"}, {1, "S3"}, {-1, "ERROR"}}},
        {"S4", {{0, "S4"}, {1, "S5"}, {-1, "S4"}}},
        {"S5", {{0, "S5"}, {1, "S5"}, {-1, "S6"}}},
        {"S6", {{0, "WAIT"}, {1, "ERROR"}, {-1, "S6"}}}};
    vector<char> actions;

    string _change_state(int16_t input)
    {
        state = fsm[state][input];
        if (state == "ERROR")
        {
            state = "WAIT";
            return "ERROR";
        }
        return state;
    }
};

void clip(int16_t &input)
{
    if (input > 750 && input < 1400)
        input = 0;
    else if (input >= 1400)
        input = 1;
    else
        input = -1;
}

// single simple with fsm
char get_up_down(int16_t input, FSM &fsm)
{
    int16_t data = input;
    clip(data);

    // using fsm
    string state = fsm.state;
    // if (state == "S3")
    // {
    //     if (fsm._change_state(data) == "WAIT")
    //     {
    //         return 'u';
    //     }
    //     // printf("%c\n", 'u');
    // }
    // else if (state == "S6")
    // {
    //     if (fsm._change_state(data) == "WAIT")
    //     {
    //         return 'd';
    //         // int len = sprintf(acc_json, "%c", "d");
    //         // response = _socket.send(acc_json, len);
    //     }
    //     // printf("%c\n", 'd');
    // }
    if (state == "S1")
    {
        if (fsm._change_state(data) == "S2")
        {
            return 'u';
        }
    }
    else if (state == "S4")
    {
        if (fsm._change_state(data) == "S5")
        {
            return 'd';
        }
    }
    else
        fsm._change_state(data);
    return ' ';
}

void fir(float32_t *input)
{
    uint32_t i;
    arm_fir_instance_f32 S;
    arm_status status;
    float32_t *inputF32, *outputF32;
    inputF32 = &input[0];
    outputF32 = &testOutput[0];
    arm_fir_init_f32(&S, NUM_TAPS, (float32_t *)&firCoeffs32[0], &firStateF32[0], blockSize);
    for (i = 0; i < numBlocks; i++)
    {
        arm_fir_f32(&S, inputF32 + (i * blockSize), outputF32 + (i * blockSize), blockSize);
    }
}

class SocketDemo
{
    static constexpr size_t MAX_NUMBER_OF_ACCESS_POINTS = 10;
    static constexpr size_t MAX_MESSAGE_RECEIVED_LENGTH = 250;

#if MBED_CONF_APP_USE_TLS_SOCKET
    static constexpr size_t REMOTE_PORT = 443; // tls port
#else
    static constexpr size_t REMOTE_PORT = 65431; // standard HTTP port 80
#endif // MBED_CONF_APP_USE_TLS_SOCKET

public:
    SocketDemo() : _net(NetworkInterface::get_default_instance())
    {
    }

    ~SocketDemo()
    {
        if (_net)
        {
            _net->disconnect();
        }
    }

    void run()
    {
        if (!_net)
        {
            printf("Error! No network interface found.\r\n");
            return;
        }

        printf("Connecting to the network...\r\n");

        nsapi_size_or_error_t result = _net->connect();
        if (result != 0)
        {
            printf("Error! _net->connect() returned: %d\r\n", result);
            return;
        }

        print_network_info();

        /* opening the socket only allocates resources */
        result = _socket.open(_net);
        if (result != 0)
        {
            printf("Error! _socket.open() returned: %d\r\n", result);
            return;
        }

#if MBED_CONF_APP_USE_TLS_SOCKET
        result = _socket.set_root_ca_cert(root_ca_cert);
        if (result != NSAPI_ERROR_OK)
        {
            printf("Error: _socket.set_root_ca_cert() returned %d\n", result);
            return;
        }
        _socket.set_hostname(MBED_CONF_APP_HOSTNAME);
#endif // MBED_CONF_APP_USE_TLS_SOCKET

        /* now we have to find where to connect */

        SocketAddress address;

        if (!resolve_hostname(address))
        {
            return;
        }

        address.set_port(REMOTE_PORT);

        /* we are connected to the network but since we're using a connection oriented
         * protocol we still need to open a connection on the socket */

        printf("Opening connection to remote port %d\r\n", REMOTE_PORT);

        result = _socket.connect(address);
        if (result != 0)
        {
            printf("Error! _socket.connect() returned: %d\r\n", result);
            return;
        }

        /* exchange an HTTP request and response */
        int16_t pDataXYZ[3] = {0};
        FSM fsm;
        vector<int16_t> input;
        int response;
        char acc_json[MAX_MESSAGE_RECEIVED_LENGTH];

        BSP_ACCELERO_Init();
        while (1)
        {
            BSP_ACCELERO_AccGetXYZ(pDataXYZ);
            char tmp = get_up_down(pDataXYZ[2], fsm);
            if (tmp != ' ')
            {
                int len = sprintf(acc_json, "%c", tmp);
                response = _socket.send(acc_json, len);
            }
            ThisThread::sleep_for(10ms);
        }

        // int sample_num = 0;
        // int16_t pDataXYZ[3] = {0};
        // float pGyroDataXYZ[3] = {0};
        // BSP_GYRO_Init();
        // BSP_ACCELERO_Init();
        // int SCALE_MULTIPLIER = 1;
        // char acc_json[MAX_MESSAGE_RECEIVED_LENGTH];
        // int response;

        // while (sample_num < 20)
        // {
        //     ++sample_num;
        //     BSP_GYRO_GetXYZ(pGyroDataXYZ);
        //     BSP_ACCELERO_AccGetXYZ(pDataXYZ);
        //     ThisThread::sleep_for(1s);
        //     float x = pDataXYZ[0] * SCALE_MULTIPLIER, y = pDataXYZ[1] * SCALE_MULTIPLIER, z = pDataXYZ[2] * SCALE_MULTIPLIER;
        //     // printf("(x,y,z,s) = %d, %d, %d, %d\r\n", pDataXYZ[0],pDataXYZ[1],pDataXYZ[2],sample_num);
        //     int len = sprintf(acc_json, "{\"Gyro\":{\"x\":%f,\"y\":%f,\"z\":%f},\
        //                                   \"Acce\":{\"x\":%f,\"y\":%f,\"z\":%f},\
        //                                   \"s\":%d}",
        //                       (float)((int)(pGyroDataXYZ[0] * 10000)) / 10000,
        //                       (float)((int)(pGyroDataXYZ[1] * 10000)) / 10000,
        //                       (float)((int)(pGyroDataXYZ[2] * 10000)) / 10000,
        //                       (float)((int)(pDataXYZ[0] * 10000)) / 10000,
        //                       (float)((int)(pDataXYZ[1] * 10000)) / 10000,
        //                       (float)((int)(pDataXYZ[2] * 10000)) / 10000,
        //                       sample_num);
        //     response = _socket.send(acc_json, len);
        if (0 > response)
        {
            printf("Error seding: %d\n", response);
        }
        else
        {
            printf("sent %d bytes\r\n", response);
        }
        // len -= response;
        ThisThread::sleep_for(1s);
    }

    // printf("Demo concluded successfully \r\n");
    // _socket.close();

private:
    bool
    resolve_hostname(SocketAddress &address)
    {
        const char hostname[] = MBED_CONF_APP_HOSTNAME;

        /* get the host address */
        printf("\nResolve hostname %s\r\n", hostname);
        nsapi_size_or_error_t result = _net->gethostbyname(hostname, &address);
        if (result != 0)
        {
            printf("Error! gethostbyname(%s) returned: %d\r\n", hostname, result);
            return false;
        }

        printf("%s address is %s\r\n", hostname, (address.get_ip_address() ? address.get_ip_address() : "None"));

        return true;
    }

    bool send_http_request()
    {
        /* loop until whole request sent */
        const char buffer[] = "GET / HTTP/1.1\r\n"
                              "Host: 172.20.10.1\r\n"
                              "Connection: close\r\n"
                              "\r\n";

        nsapi_size_t bytes_to_send = strlen(buffer);
        nsapi_size_or_error_t bytes_sent = 0;

        printf("\r\nSending message: \r\n%s", buffer);

        while (bytes_to_send)
        {
            bytes_sent = _socket.send(buffer + bytes_sent, bytes_to_send);
            if (bytes_sent < 0)
            {
                printf("Error! _socket.send() returned: %d\r\n", bytes_sent);
                return false;
            }
            else
            {
                printf("sent %d bytes\r\n", bytes_sent);
            }

            bytes_to_send -= bytes_sent;
        }

        printf("Complete message sent\r\n");

        return true;
    }

    bool receive_http_response()
    {
        char buffer[MAX_MESSAGE_RECEIVED_LENGTH];
        int remaining_bytes = MAX_MESSAGE_RECEIVED_LENGTH;
        int received_bytes = 0;

        /* loop until there is nothing received or we've ran out of buffer space */
        nsapi_size_or_error_t result = remaining_bytes;
        while (result > 0 && remaining_bytes > 0)
        {
            result = _socket.recv(buffer + received_bytes, remaining_bytes);
            if (result < 0)
            {
                printf("Error! _socket.recv() returned: %d\r\n", result);
                return false;
            }

            received_bytes += result;
            remaining_bytes -= result;
        }

        /* the message is likely larger but we only want the HTTP response code */

        printf("received %d bytes:\r\n%.*s\r\n\r\n", received_bytes, strstr(buffer, "\n") - buffer, buffer);

        return true;
    }

    void wifi_scan()
    {
        WiFiInterface *wifi = _net->wifiInterface();

        WiFiAccessPoint ap[MAX_NUMBER_OF_ACCESS_POINTS];

        /* scan call returns number of access points found */
        int result = wifi->scan(ap, MAX_NUMBER_OF_ACCESS_POINTS);

        if (result <= 0)
        {
            printf("WiFiInterface::scan() failed with return value: %d\r\n", result);
            return;
        }

        printf("%d networks available:\r\n", result);

        for (int i = 0; i < result; i++)
        {
            printf("Network: %s secured: %s BSSID: %hhX:%hhX:%hhX:%hhx:%hhx:%hhx RSSI: %hhd Ch: %hhd\r\n",
                   ap[i].get_ssid(), get_security_string(ap[i].get_security()),
                   ap[i].get_bssid()[0], ap[i].get_bssid()[1], ap[i].get_bssid()[2],
                   ap[i].get_bssid()[3], ap[i].get_bssid()[4], ap[i].get_bssid()[5],
                   ap[i].get_rssi(), ap[i].get_channel());
        }
        printf("\r\n");
    }

    void print_network_info()
    {
        /* print the network info */
        SocketAddress a;
        _net->get_ip_address(&a);
        printf("IP address: %s\r\n", a.get_ip_address() ? a.get_ip_address() : "None");
        _net->get_netmask(&a);
        printf("Netmask: %s\r\n", a.get_ip_address() ? a.get_ip_address() : "None");
        _net->get_gateway(&a);
        printf("Gateway: %s\r\n", a.get_ip_address() ? a.get_ip_address() : "None");
    }

private:
    NetworkInterface *_net;

#if MBED_CONF_APP_USE_TLS_SOCKET
    TLSSocket _socket;
#else
    TCPSocket _socket;
#endif // MBED_CONF_APP_USE_TLS_SOCKET
};

int main()
{

    SocketDemo *example = new SocketDemo();
    // MBED_ASSERT(example);
    example->run();

    return 0;
}

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
