#!/usr/bin/python3
# -*-coding:Utf-8 -*
import curses

def wrapper(fun):
    def wrapped(*args, **kwargs):
        screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        screen.keypad(1)
        new_args = (screen,) + args

        try:
            fun(*new_args, **kwargs)
        except KeyboardInterrupt:
            pass
        finally:
            curses.nocbreak()
            screen.keypad(0)
            curses.echo()
            curses.endwin()
    return wrapped

class Window(object):
    def __init__(self, screen):
        self.screen = screen
        self._win = curses.newwin(0, 0)
        self.reset_size()

    def refresh(self):
        self._win.refresh()

    def reset_size(self):
        pass

    def key_event(self, key):
        pass

class UserInput(Window):
    def __init__(self, screen, client):
        self.client = client
        self._input = u''
        Window.__init__(self, screen)

    def reset_size(self):
        y, x = self.screen.getmaxyx()
        self._win.resize(1, x)
        self._win.mvwin(y-1, 0)

        self._win.erase()
        self._win.addstr('[%s] # %s' % (self.client.username, self._input))

    def key_event(self, key):
        self._win.addstr(chr(key))
        self.refresh()
            
class Chat(Window):
    def __init__(self, screen, messages):
        self._messages = messages
        self._index = 0
        self._lines = []
        Window.__init__(self, screen)
        self._win.leaveok(True)

    def reset_size(self):
        y, x = self.screen.getmaxyx()
        self._win.resize(y-1, x)
        self._win.mvwin(0, 0)
        self.draw()

    def draw(self):
        y, x = self._win.getmaxyx()
        self._win.erase()

        for i, line in enumerate(self._lines[self._index:][:y]):
            self._win.addstr(y-1-i, 0, line)

    def key_event(self, key):
        if key in (curses.KEY_UP, curses.KEY_DOWN):
            if key == curses.KEY_UP:
                self._index += 1
            if key == curses.KEY_DOWN and self._index >= 1:
                self._index -= 1
            self.draw()
            self.refresh() 
        
@wrapper
def run(screen, client):
    user_input = UserInput(screen, client)
    chat = Chat(screen, None)
    chat._lines = ['Maxima: ça va ça va', 'Truc: oui et toi ?', 'Maxima: salut ça va ?']
    chat.draw()

    screen.refresh()
    chat.refresh()
    user_input.refresh()
    while True:
        key = screen.getch()
        chat.key_event(key)
        user_input.key_event(key)
        
