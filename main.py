#!/usr/bin/python3
# -*-coding:Utf-8 -*
import gui
import queue
import argparse
import getpass

class Client(object):
    pass

def run(host, port, listen, username):
    c = Client()
    c.messages = queue.Queue()
    c.messages.put('server: Connected to %s:%s' % (host, port))
    c.send = lambda x: c.messages.put(x)
    c.username = username
    c.socket = Client()

    gui.run(c)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Chat with other people. pyeasychat use TCP/IP, so everybody can communicate with it, with netcat, telnet..')
    parser.add_argument('host', default='127.0.0.1', nargs='?',
        help='The host to connect to or listen. default is 127.0.0.1')
    parser.add_argument('port', type=int,
        help='The port to connect to or listen.')
    parser.add_argument('-l', '--listen', action='store_const', const=True, default=False,
        help='Used to specify that pyeasychat should start a server.')
    parser.add_argument('-u', '--username', type=str, default=getpass.getuser())
    args = parser.parse_args()
    run(args.host, args.port, args.listen, args.username)
