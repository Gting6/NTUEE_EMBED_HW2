#!/usr/bin/env python3
import socket
import numpy as np

HOST = '192.168.0.104'
PORT = 65431         # Port to listen on
counter = 0
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("listen!")
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:  # draw ten result sent by the sensot
            print("processing data", counter)
            counter += 1
            data = conn.recv(1024).decode('utf-8')
            print(data)
