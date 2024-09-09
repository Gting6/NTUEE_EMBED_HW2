import socket
from _thread import *
import sys
import time
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

status0["game"] = 0
status1["game"] = 0

status0["time"] = 0
status1["time"] = 0

constTime = 39


gameTime = constTime

players = [status0, status1]


def decideGame(player):
    if player == 1:
        opp = 0
    else:
        opp = 1
    if players[player]["game"] == 0 and players[opp]["game"] == 0:
        return 0
    if players[player]["game"] == 1 and players[opp]["game"] == 0:
        return 1
    if players[player]["game"] == 0 and players[opp]["game"] == 1:
        print("should not happen")
        return 1
    if players[player]["game"] == 1 and players[opp]["game"] == 1:
        players[player]["game"] = 2
        players[opp]["game"] = 2
        return 2
    if players[player]["game"] == 2 and players[opp]["game"] == 2:
        if gameTime == 0:
            if players[0]["score0"] > players[1]["score0"]:
                players[player]["game"] = 3
                players[opp]["game"] = 4
                return 3  # 3 = 0 win, 4 = 1 win
            elif players[0]["score0"] < players[1]["score0"]:
                players[player]["game"] = 4
                players[opp]["game"] = 3
                return 4  # 3 = 0 win, 4 = 1 win
            else:
                players[player]["game"] = 5
                players[opp]["game"] = 5
                return 5  # 3 = 0 win, 4 = 1 win
        # TODO: implement crashed case here
        return 2
    if players[player]["game"] == 3:
        return 3
    if players[player]["game"] == 4:
        return 4
    if players[player]["game"] == 5:
        return 5
    return 0


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
            oldGame = players[player]["game"]
            players[player] = data
            if players[player]["game"] == 6:  # crash signal by client
                players[player]["game"] = 4
                if player == 0:
                    players[1]["game"] = 3
                else:
                    players[0]["game"] = 3
            else:
                players[player]["game"] = oldGame

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
                    elif key == "game":
                        pack["game"] = decideGame(player)
                    elif key == "time":
                        pack["time"] = gameTime
                    else:
                        if reply[key] == 8:  # we don't show shadow on enemy to avoid some bug
                            pack[(key[0]+600, key[1])] = 0
                        else:
                            pack[(key[0]+600, key[1])] = reply[key]
                # print("Received: ", data)
                # print("Sending : ", reply)
            reply["time"] = gameTime
            conn.sendall(pickle.dumps(pack))
        except:
            print((player+1) % 2)
            break
    print("Lost connection")
    conn.close()


def countDown():
    global gameTime
    while gameTime:
        time.sleep(1)
        if players[0]["game"] + players[1]["game"] != 4:
            gameTime = constTime
        gameTime -= 1
        print(gameTime, players[0]["game"], players[1]["game"])

    tmp0 = decideGame(0)
    print("OVER!", players[0]["game"], players[1]["game"])

    while players[0]["game"] > 0 or players[1]["game"] > 0:
        time.sleep(1)
        gameTime = 0
        print(gameTime, players[0]["game"], players[1]["game"])

    gameTime = constTime

    countDown()


currentPlayer = 0
# continuously looking for connection
start_new_thread(countDown, ())
while True:
    conn, addr = s.accept()  # accept any incoming connection, addr is ip address
    print("Connected to", addr)

    start_new_thread(threaded_client, (conn, currentPlayer))
    players[currentPlayer]["game"] = 1
    currentPlayer += 1

# client send pos to server, server send back another client's position
