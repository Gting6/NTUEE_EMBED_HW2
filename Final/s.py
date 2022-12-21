import socket
from _thread import *
import sys
import pickle

server = "192.168.0.100"  # my local ipv4 address, which will be server address
# print("Server at", server)
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


status0 = {}
status1 = {}

for i in range(200, 400, 20):
    for j in range(160, 600, 20):
        status0[(i, j)] = 0
        status1[(i, j)] = 0


players = [status0, status1]


def threaded_client(conn, player):
    # print("Send:", players[player])
    # conn.send(pickle.dumps(players[player]))
    reply = ""
    while True:
        try:
            # receive 2048 bits, larger will take longer time
            tmp = []
            ct = 1
            while True:
                ct += 1
                if ct == 4:  # the receive status is exactly 3 package
                    break
                packet = conn.recv(2048)
                tmp.append(packet)
            data = pickle.loads(b"".join(tmp))  # load byte data

            # data = pickle.loads(conn.recv(2048))
            players[player] = data  # update information

            if not data:
                print("Disconnected")  # not get anything
                break
            else:
                if player == 1:
                    reply = players[0]
                else:
                    reply = players[1]
                pack = {}
                for key in reply:
                    if key == "combo0":
                        pack["combo1"] = reply[key]
                    elif key == "score0":
                        pack["score1"] = reply[key]
                    elif key == "shift0":
                        pack["shift1"] = reply[key]
                    elif key == "next0":
                        pack["next1"] = reply[key]
                    else:
                        if reply[key] == 8:  # we don't show shadow on enemy to avoid some bug
                            pack[(key[0]+600, key[1])] = 0
                        else:
                            pack[(key[0]+600, key[1])] = reply[key]
                # print("Received: ", data)
                # print("Sending : ", reply)
            conn.sendall(pickle.dumps(pack))
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
