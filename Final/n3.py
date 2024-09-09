import socket
import pickle

# To connect to the server


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "192.168.0.100"
        self.port = 5555
        self.addr = (self.server, self.port)
        self.p = self.connect()  # id is sent by client player

    def getP(self):
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
            return
        except Exception as e:
            print(e)

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            tmp = []
            ct = 1
            while True:
                ct += 1
                if ct == 4:  # the initial status is exactly 4 package
                    break
                packet = self.client.recv(2048)
                tmp.append(packet)
            return pickle.loads(b"".join(tmp))  # load byte data
            # return pickle.loads(self.client.recv(2048))
        except Exception as e:
            print("Sending Error", e)
