#!/usr/bin/env python3
import socket
import numpy as np
import json
import matplotlib.pyplot as plt
import argparse

HOST = '170.20.10.1'
PORT = 65431         # Port to listen on

counter = 0
plt_array = {}
source = ["Gyro", "Acce"]
ax = ["x", "y", "z"]


parser = argparse.ArgumentParser()
parser.add_argument('--num', default=5,
                    help='number of point to received, at most 20')

args = parser.parse_args()
n = int(args.num)

if n >= 20:
    n = 20

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print("listen!")
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while counter < n:  # draw ten result sent by the sensot
            print("processing data", counter)
            counter += 1
            data = conn.recv(1024).decode('utf-8')

            json_data = json.loads(data)

            if not plt_array:
                plt_array = json_data

            for ss in source:
                for aa in ax:
                    if not isinstance(plt_array[ss][aa], list):
                        plt_array[ss][aa] = [
                            plt_array[ss][aa], json_data[ss][aa]]
                    else:
                        plt_array[ss][aa].append(json_data[ss][aa])

fig = plt.figure(figsize=plt.figaspect(0.5))
ax = fig.add_subplot(1, 2, 1, projection='3d')
ax.plot(plt_array["Gyro"]["x"], plt_array["Gyro"]["y"],
        plt_array["Gyro"]["z"], label="Gyro", color="blue")
ax.legend()
ax = fig.add_subplot(1, 2, 2, projection='3d')
ax.plot(plt_array["Acce"]["x"], plt_array["Acce"]["y"],
        plt_array["Acce"]["z"], label="Acce", color="red")
ax.legend()
plt.show()
