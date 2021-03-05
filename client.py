import threading
import socket
import time
import re
import json
from random import randint
class Client():

    def __init__(self, username, server, port):
        self.socket= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server, port))
        self.username = username
        self.election = randint(1, 1000)
        join_payload = {
            'type': 'join',
            'data': {
                'election': self.election,
            },
        }
        self.send(join_payload)
        self.listening= True

    def listener(self):
        while self.listening:
            data= ""
            try:
                data= self.socket.recv(1024).decode('UTF-8')
            except socket.error:
                print("Unable to receive data")
            self.handle_msg(data)
            time.sleep(0.1)

    def listen(self, handler):
        self.handler = handler
        self.listen_thread = threading.Thread(target=self.listener)
        self.listen_thread.daemon = True
        self.listen_thread.start()

    def send(self, message):
        try:
            data = {
                'username': self.username,
                'message':message
            }   
            print(message)
            self.socket.sendall(json.dumps(data).encode("UTF-8"))
        except socket.error:
            print("unable to send message")

    def tidy_up(self):
        self.listening = False
        self.socket.close()

    def handle_msg(self, data):
        if data=="QUIT":
            self.tidy_up()
        elif data=="":
            self.tidy_up()
        else:
            self.handler(data)


def handle(msg):
    print(msg)
    
if __name__ == "__main__":
    username= input("username: ")
    server= input("server: ")
    port= int(input("port: "))
    client= Client(username, server, port)
    client.listen(handle)
    message= ""
    while message!="QUIT":
        message= input()
        client.send(message)