#!/usr/bin/python3
# -*-coding:Utf-8 -*
import curses
from curses import ascii
from time import sleep
import locale

def wrapper(fun):
    def wrapped(*args, **kwargs):
        screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        screen.keypad(1)
        screen.nodelay(1)
        new_args = (screen,) + args

        try:
            fun(*new_args, **kwargs)
        except KeyboardInterrupt:
            pass
        finally:
            curses.nocbreak()
            screen.keypad(0)
            screen.nodelay(0)
            curses.echo()
            curses.endwin()
    return wrapped

def getch_convert(getch, c):
    ''' getch_convert tries to convert a key to a character.
    it returns None if the key is not a character.

    getch_convert needs screen.getch() because getch returns only the first byte. '''
    def get_next_byte():
        c = getch()
        if 128 <= c and c <= 191:
            return c
        else:
            raise UnicodeError

    if locale.getpreferredencoding() == 'UTF-8':
        # thanks to Iñigo Serna <inigoserna@gmail.com> for this part
        byte_list = []
        try:
            if 32 <= c and c <= 126:
                byte_list.append(c)
            if 194 <= c and c <= 223:
                byte_list.append(c)
                byte_list.append(get_next_byte())
            elif 224 <= c and c <= 239:
                byte_list.append(c)
                byte_list.append(get_next_byte())
                byte_list.append(get_next_byte())
            elif 240 <= c and c <= 244:
                byte_list.append(c)
                byte_list.append(get_next_byte())
                byte_list.append(get_next_byte())
                byte_list.append(get_next_byte())

            if byte_list:
                buffer = ''.join([chr(byte) for byte in byte_list])
                return bytes(buffer, 'latin1').decode('UTF-8')
            else:
                return None
        except UnicodeDecodeError or UnicodeError:
            return None
    else: # ASCII
        if c >= 32 and c <= 126:
            return chr(c)
        else:
            return None

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

    def __init__(self, client, getch_convert, x, y, width, height):
        self.client = client
        self.getch_convert = getch_convert
        self._input = str()
        self._cursor = 0
        Window.__init__(self, x, y, width, height)

    def get_prompt(self):
        return UserInput.PROMPT % self.client.username

    def resize(self, x, y, width, height):
        if len(self.get_prompt()) + len(self._input) + 2 > width: # window too small for current input
            input_size = width - len(self.get_prompt()) - 1
            self._input = self._input[:input_size]
            if self._cursor > input_size:
                self._cursor = input_size

        Window.resize(self, x, y, width, height)

    def redraw(self):
        self._erase()
        self._win.addstr(self.get_prompt())
        self._win.addstr(self._input)
        self.redraw_cursor()
        self._refresh()

    def redraw_cursor(self):
        self._win.move(0, len(self.get_prompt()) + self._cursor)
        self._refresh()

    def get_input(self):
        return self._input

    def key_event(self, key):
        if key in (curses.KEY_LEFT, ascii.STX) and self._cursor > 0: # <- or Ctrl+B
            self._cursor -= 1
            self.redraw_cursor()
        elif key in (curses.KEY_RIGHT, ascii.ACK) and self._cursor < len(self._input): # -> or Ctrl+F
            self._cursor += 1
            self.redraw_cursor()
        elif key in (curses.KEY_BACKSPACE, ascii.BS) and self._cursor > 0: # Backspace or Ctrl+H
            self._input = self._input[:self._cursor-1] + self._input[self._cursor:]
            self._cursor -= 1
            self.redraw()
        elif key in (curses.KEY_DC, ascii.EOT) and self._cursor < len(self._input): # Suppr or Ctrl+D
            self._input = self._input[:self._cursor] + self._input[self._cursor+1:]
            self._win.delch()
            self._refresh()
        elif key == ascii.SOH: # Ctrl+A
            self._cursor = 0
            self.redraw_cursor()
        elif key == ascii.ENQ: # Ctrl+E
            self._cursor = len(self._input)
            self.redraw_cursor()
        elif key == ascii.NAK: # Ctrl+U
            self._input = str()
            self._cursor = 0
            self.redraw()
        elif key == ascii.VT: # Ctrl+K
            self._input = self._input[:self._cursor]
            self.redraw()
        elif key in (curses.KEY_ENTER, ascii.NL): # Enter
            self.client.send(self._input)
            self._input = str()
            self._cursor = 0
            self.redraw()
        elif key is not curses.ERR and len(self.get_prompt()) + len(self._input) + 1 < self._win.getmaxyx()[1]: # window not too small
            s = self.getch_convert(key)

            if s:
                self._win.insstr(s)
                self._input = self._input[:self._cursor] + s + self._input[self._cursor:]
                self._cursor += 1
                self.redraw_cursor()
            
class Chat(Window):
    def __init__(self, messages, redraw_cursor, x, y, width, height):
        self._messages = messages
        self.redraw_cursor = redraw_cursor
        self._scroll = 0
        self._lines = []
        Window.__init__(self, x, y, width, height)

    def redraw(self):
        height, width = self._win.getmaxyx()
        self._erase()

        for i, line in enumerate(self._lines[self._scroll:][:height]):
            if len(line) >= width:
                self._win.addstr(height-1-i, 0, line[:width-4] + '...')
            else:
                self._win.addstr(height-1-i, 0, line)

        self._refresh()
        self.redraw_cursor()

    def handle_messages(self):
        redraw = not self._messages.empty()

        while not self._messages.empty():
            line = self._messages.get()
            self._lines.insert(0, line)
            if self._scroll > 0:
                self._scroll += 1
        
        if redraw:
            self.redraw()

    def key_event(self, key):
        if key in (curses.KEY_UP, curses.KEY_DOWN, ascii.DLE, ascii.SO):
            if key in (curses.KEY_UP, ascii.DLE): # Up or Ctrl+P
                self._scroll += 1
            if key in (curses.KEY_DOWN, ascii.SO) and self._scroll >= 1: # Down or Ctrl+N
                self._scroll -= 1
            self.redraw()
        
@wrapper
def run(screen, client):
    screen.refresh()
    height, width = screen.getmaxyx()
    user_input = UserInput(client, lambda c : getch_convert(screen.getch, c),
            0, height-1, width, 1)
    chat = Chat(client.messages, user_input.redraw_cursor,
            0, 0, width, height-1)

    while True:
        key = screen.getch()
        user_input.key_event(key)
        chat.handle_messages()
        chat.key_event(key)

        if key == curses.KEY_RESIZE:
            height, width = screen.getmaxyx()
            screen.refresh()
            user_input.resize(0, height-1, width, 1)
            chat.resize(0, 0, width, height-1)
        elif key == ascii.EOT and user_input.get_input() == '': # Ctrl+D and empty input
            break 
        elif not client.is_alive(): # disconnected
            break
        sleep(0.025)
