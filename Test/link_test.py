'''import socket
import threading

class connectListener(threading.Thread):

    def __init__(self,request,addr):
        super().__init__()
        self.request = request
        self.addr = addr
        print(f'Start {self.addr}')

    def run(self):
        while(True):
            msg = self.request.recv(1024)
            if(msg ==b'quit' or msg == b''):
                self.request.close()
                print(f"{self.addr} Quit")
                break
            print(msg.decode())

class TCPListener(threading.Thread):
    def __init__(self):
        super().__init__()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('0.0.0.0',8777))
        self.server.listen(5)

    def run(self):
        while(True):
            s, addr = self.server.accept()
            c = connectListener(s,addr)
            c.start()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

Listener = TCPListener()
Listener.start()

client1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client1.connect(('127.0.0.1',8777))
print('1 Connect Success')
client1.send(b'quit')'''


import socketserver
import socket
import threading

class TCPhHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print(f"Connect to {self.client_address}")
        self.request.send(b'TTTTTTT')
        self.finish()

class server(threading.Thread):
    def __init__(self):
        super().__init__()
        self.server = socketserver.ThreadingTCPServer(('0.0.0.0',8777),TCPhHandler)

    def run(self):
        self.server.serve_forever()

t = server()
t.start()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1',8777))
s = client.recv(1024).decode()
print(s)
client.close()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1',8777))
s = client.recv(1024).decode()
print(s)
client.close()

