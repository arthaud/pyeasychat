#!/usr/bin/python3
# -*-coding:Utf-8 -*
from threading import Thread
import socket
import select
import queue

class ServerThread(Thread):
    def __init__(self, host, port):
        Thread.__init__(self)
        self.daemon = True
        self._clients = []

        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.setblocking(False)
        self._server.bind((host, port))
        self._server.listen(5)

    def _send(self, data):
        if self._server:
            for client in self._clients:
                client.send(bytes(data + '\n', 'UTF-8'))

    def run(self):
        while self._server:
            readable, writable, exceptional = select.select(
                self._clients + [self._server], # input
                [], # output
                [self._server]) # error

            for s in readable:
                if s is self._server: # incoming connection
                    client, address = self._server.accept()
                    client.setblocking(False)
                    self._clients.append(client)
                else: # client
                    data = s.recv(1024)
                    if data: # message
                        self._send(data.strip().decode('UTF-8'))
                    else: # disconnection
                        self._clients.remove(s)
                        s.close()

            if exceptional:
                for client in self._clients:
                    client.close()
                self._clients = []
                self._server.close()
                self._server = None

class ClientThread(Thread):
    CONNECTION_MESSAGE = 'server: %s has joined the chat.'
    DISCONNECTION_MESSAGE = 'server: %s has left the chat.'
    
    def __init__(self, host, port, username):
        Thread.__init__(self)
        self.daemon = True
        self.messages = queue.Queue()
        self.username = username

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((host, port))

    def _send(self, data):
        if self._socket:
            self._socket.send(bytes(data + '\n', 'UTF-8'))

    def send(self, data):
        self._send('%s: %s' % (self.username, data))

    def send_connection_message(self):
        self._send(ClientThread.CONNECTION_MESSAGE % self.username)

    def send_disconnection_message(self):
        self._send(ClientThread.DISCONNECTION_MESSAGE % self.username)

    def run(self):
        self.send_connection_message()

        while self._socket:
            data = self._socket.recv(1024)
            if data:
                self.messages.put(data.strip().decode('UTF-8'))
            else:
                self._socket.close()
                self._socket = None
