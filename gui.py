#!/usr/bin/python3
# -*-coding:Utf-8 -*
import curses

def wrapper(fun):
    def wrapped(*args, **kwargs):
        screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        screen.keypad(1)
        kwargs['screen'] = screen

        try:
            fun(*args, **kwargs)
        finally:
            curses.nocbreak()
            screen.keypad(0)
            curses.echo()
            curses.endwin()
    return wrapped

@wrapper
def run(client, screen):
    y, x = screen.getmaxyx()

    # User Input
    user_input = curses.newwin(1, x, y-1, 0)
    user_input.addstr('[%s] # ' % client.username)

    # Chat
    chat = curses.newwin(y-1, x, 0, 0)
    chat.addstr('Connecté a %s\n' % client.socket.getpeername())

    screen.refresh()
    chat.refresh()
    user_input.refresh()
    while True:
        c = screen.getch()
        if c == ord('q'):
            break
        else:
            user_input.addstr(chr(c))
            user_input.refresh()
