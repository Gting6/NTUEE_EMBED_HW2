import pygame
from network import Network
from player import Player
from threading import Thread
import queue
import socket
q = queue.Queue()


def redrawWindow(win, player, player2):
    win.fill((255, 255, 255))
    player.draw(win)
    player2.draw(win)
    pygame.display.update()


def client():
    print("thread 1 start")
    width = 500
    height = 500
    win = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Client")

    clientNumber = 0  # increment once connected to server
    run = True
    n = Network()
    p = n.getP()
    clock = pygame.time.Clock()

    while run:
        clock.tick(60)  # frame per second
        p2 = n.send(p)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
        p.move()
        # if not q.empty():
        # p.move(q.get())
        redrawWindow(win, p, p2)


def signal():
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
                if data == "d" or data == "u":
                    q.put(data)


# def main():
# client()
# signal_thread = Thread(target=signal)

client_thread = Thread(target=client)

client_thread.start()
# signal_thread.start()

client_thread.join()
# signal_thread.join()

# main()
