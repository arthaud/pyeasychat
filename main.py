#!/usr/bin/python3
# -*-coding:Utf-8 -*
import gui

class Client(object):
    pass

def run():
    c = Client()
    c.username = 'Maxima'
    c.socket = Client()
    c.socket.getpeername = lambda: 'localhost'
    gui.run(c)

if __name__ == '__main__':
    run()
