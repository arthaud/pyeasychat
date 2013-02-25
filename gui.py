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

class Window(object):
    def __init__(self, screen):
        self.screen = screen
        self.win = curses.newwin(0, 0)
        self.reset_size()

    def refresh(self):
        self.win.refresh()

    def reset_size(self):
        pass

class UserInput(Window):
    def __init__(self, screen, client):
        self.client = client
        self.input = u''
        Window.__init__(self, screen)

    def reset_size(self):
        y, x = self.screen.getmaxyx()
        self.win.resize(1, x)
        self.win.mvwin(y-1, 0)

        self.win.erase()
        self.win.addstr('[%s] # %s' % (self.client.username, self.input))
            
class Chat(Window):
    def reset_size(self):
        y, x = self.screen.getmaxyx()
        self.win.resize(y-1, x)
        self.win.mvwin(0, 0)

        self.win.erase()
        self.win.addstr('Connecté a localhost')

@wrapper
def run(client, screen):
    user_input = UserInput(screen, client)
    chat = Chat(screen)

    screen.refresh()
    chat.refresh()
    user_input.refresh()
    while True:
        c = screen.getch()
        if c == ord('q'):
            break
        else:
            user_input.win.addstr(chr(c))
            user_input.refresh()
