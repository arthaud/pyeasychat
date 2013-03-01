#!/usr/bin/python3
# -*-coding:Utf-8 -*
import gui
import queue

class Client(object):
    pass

def run():
    c = Client()
    c.messages = queue.Queue()
    c.send = lambda x: c.messages.put(x)
    c.username = 'Maxima'
    c.socket = Client()

    c.socket.getpeername = lambda: 'localhost'
    gui.run(c)

if __name__ == '__main__':
    run()
