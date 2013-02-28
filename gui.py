#!/usr/bin/python3
# -*-coding:Utf-8 -*
import curses
from curses import ascii

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

class Window:
    def __init__(self, x, y, width, height):
        self._win = curses.newwin(0, 0)
        self.resize(x, y, width, height)

    def _refresh(self):
        ''' refresh the window. all things drawn will be printed. '''
        self._win.refresh()

    def _erase(self):
        ''' clear the window. the next refresh, the window will be empty. '''
        self._win.erase()

    def resize(self, x, y, width, height):
        ''' resize the window, and redraw it. '''
        self._win.resize(height, width)
        self._win.mvwin(y, x)
        self.redraw()

    def redraw(self):
        ''' redraw the window. '''
        self._refresh()

    def key_event(self, key):
        ''' manage a keyboard event. '''
        pass

class UserInput(Window):
    PROMPT = '[%s] # '

    def __init__(self, client, x, y, width, height):
        self.client = client
        self._input = str()
        self._cursor = 0
        Window.__init__(self, x, y, width, height)

    def get_prompt(self):
        return UserInput.PROMPT % self.client.username

    def redraw(self):
        self._erase()
        self._win.addstr(self.get_prompt())
        self._win.addstr(self._input)
        self.redraw_cursor()
        self._refresh()

    def redraw_cursor(self):
        self._win.move(0, len(self.get_prompt()) + self._cursor)
        self._refresh()

    def key_event(self, key):
        if key >= 0 and key <= 255 and not ascii.iscntrl(key):
            self._win.insstr(chr(key))
            self._input = self._input[:self._cursor] + chr(key) + self._input[self._cursor:]
            self._cursor += 1
            self.redraw_cursor()
        elif key == curses.KEY_LEFT and self._cursor > 0:
            self._cursor -= 1
            self.redraw_cursor()
        elif key == curses.KEY_RIGHT and self._cursor < len(self._input):
            self._cursor += 1
            self.redraw_cursor()
        elif key == curses.KEY_BACKSPACE and self._cursor > 0:
            self._input = self._input[:self._cursor-1] + self._input[self._cursor:]
            self._cursor -= 1
            self.redraw()
        elif ascii.SOH == key:
            self._cursor = 0
            self.redraw_cursor()
        elif ascii.ENQ == key:
            self._cursor = len(self._input)
            self.redraw_cursor()
        elif ascii.NAK == key:
            self._input = str()
            self._cursor = 0
            self.redraw()
            
class Chat(Window):
    def __init__(self, messages, redraw_cursor, x, y, width, height):
        self._messages = messages
        self.redraw_cursor = redraw_cursor
        self._scroll = 0
        self._lines = []
        Window.__init__(self, x, y, width, height)

    def redraw(self):
        y, x = self._win.getmaxyx()
        self._erase()

        for i, line in enumerate(self._lines[self._scroll:][:y]):
            self._win.addstr(y-1-i, 0, line)

        self._refresh()
        self.redraw_cursor()
        
    def key_event(self, key):
        if key in (curses.KEY_UP, curses.KEY_DOWN):
            if key == curses.KEY_UP:
                self._scroll += 1
            if key == curses.KEY_DOWN and self._scroll >= 1:
                self._scroll -= 1
            self.redraw()
        
@wrapper
def run(screen, client):
    screen.refresh()
    y, x = screen.getmaxyx()
    user_input = UserInput(client, 0, y-1, x, 1)
    chat = Chat([], user_input.redraw_cursor, 0, 0, x, y-1)

    # Only for test
    chat._lines = ['Maxima: ça va ça va', 'Truc: oui et toi ?', 'Maxima: salut ça va ?']
    chat.redraw()
    user_input.redraw()

    while True:
        key = screen.getch()
        chat.key_event(key)
        user_input.key_event(key)
        if key == curses.KEY_RESIZE:
            y, x = screen.getmaxyx()
            screen.refresh()
            chat.resize(0, 0, x, y-1)
            user_input.resize(0, y-1, x, 1)
