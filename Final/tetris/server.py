import socket
from _thread import *
from player import Player
import sys
import pickle

server = "192.168.0.104"  # my local ipv4 address, which will be server address
port = 5555  # typically safe

# Use IPV4, sock_stream = get input string?
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))  # bind socket to server and port

except socket.error as e:
    str(e)
    print(e)

s.listen(2)
print("Waiting for connection, Server started")

players = [Player(0, 0, 50, 50, (255, 0, 0)),
           Player(100, 100, 50, 50, (0, 0, 255))]


def threaded_client(conn, player):
    conn.send(pickle.dumps(players[player]))
    reply = ""
    while True:
        try:
            # receive 2048 bits, larger will take longer time
            data = pickle.loads(conn.recv(2048))
            players[player] = data  # update information

            if not data:
                print("Disconnected")  # not get anything
                break
            else:
                if player == 1:
                    reply = players[0]
                else:
                    reply = players[1]
                print("Received: ", data)
                print("Sending : ", reply)
            conn.sendall(pickle.dumps(reply))
        except:
            print((player+1) % 2)
            break
    print("Lost connection")
    conn.close()


currentPlayer = 0
# continuously looking for connection
while True:
    conn, addr = s.accept()  # accept any incoming connection, addr is ip address
    print("Connected to", addr)

    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1

# client send pos to server, server send back another client's position
