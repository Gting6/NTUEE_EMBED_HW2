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



// void get_up_down(int16_t pDataXYZ, float pGyroDataXYZ, float &angle){
//     if (pGyroDataXYZ > 4000){
//         angle += pGyroDataXYZ;
//     }
//     else if (pGyroDataXYZ < -4000){
//         angle += pGyroDataXYZ;
//     }
//     else{
//         angle = 0;
//     }
//     //printf("%.2f\n", angle);
//     if (angle > 800000 && pDataXYZ > 1250){
//         printf("up\n\n\n");
//         sending('u');
//         ThisThread::sleep_for(300);
//         angle = 0;
//     }
//     else if (angle < -800000 && pDataXYZ < 850){
//         printf("down\n\n\n");
//         sending('d');
//         ThisThread::sleep_for(300);
//         angle = 0;
//     }
// }

// void side_rotate(float pGyroDataXYZ, float &angle){
//     if (pGyroDataXYZ > 4000){
//         angle += pGyroDataXYZ;
//     }
//     else if (pGyroDataXYZ < -4000){
//         angle = 0;
//     }
//     else{
//         angle = 0;
//     }
//     //printf("%.2f\n", angle);
//     if (angle > 3000000){
//         printf("rotate\n\n\n");
//         sending('o');
//         ThisThread::sleep_for(200);
        
//         angle = 0;
//     }
// }

char direction[3] = {'l', 'n', 'r'};


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

    void sending(char tmp)
    {
        // int response = 0;
        // char acc_json[MAX_MESSAGE_RECEIVED_LENGTH];
        // printf("send! %c\n", tmp);
        // int len = sprintf(acc_json, "%c", tmp);
        // response = _socket.send(acc_json, len);
        // ThisThread::sleep_for(10ms);
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
            sending('u');
            ThisThread::sleep_for(300);
            angle = 0;
        }
        else if (angle < -800000 && pDataXYZ < 850){
            printf("down\n\n\n");
            sending('d');
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
            sending('o');
            ThisThread::sleep_for(200);
            
            angle = 0;
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
        int response = 0;

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

        while (1)
        {
            BSP_ACCELERO_AccGetXYZ(pDataXYZ);
            BSP_GYRO_GetXYZ(pGyroDataXYZ);

            get_up_down(pDataXYZ[2], pGyroDataXYZ[0], up_down_angle);
            side_rotate(pGyroDataXYZ[1], side_angle);

            if (led1.read()) {
               printf("%c\n", direction[0]);
                sending('l');
                ThisThread::sleep_for(200);
                
            } else if (led2.read()) {
                printf("%c\n", direction[2]);
                sending('r');
                ThisThread::sleep_for(200);

            } 
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
        // if (0 > response)
        // {
        //     printf("Error sending: %d\n", response);
        // }
        // else
        // {
        //     printf("sent %d bytes\r\n", response);
        // }
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
