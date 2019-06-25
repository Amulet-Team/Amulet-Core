import curses

from io import StringIO

class CursesProgram:

    def __init__(self):

        self._commands = {}
        self._complex_commands = {}
        #self._modes = ModeStack()

        self._retry_modules = []
        self._modules = []
        #self._load_commands_and_modes()
        self._entry_history = []
        self._history_index = 0
        self._line_number = 0
        self._column_number = 0
        self._current_io = []

        self.data = {}

    def run(self):

        curses.wrapper(self._run)

    def _run(self, screen):
        curses.beep()
        #curses.echo()
        while True:
            screen.addstr(self._line_number, 0, "> ")
            self._column_number += 1
            # Store the key value in the variable `c`
            c = screen.getkey()
            screen.clear()
            screen.move(self._line_number, self._column_number)
            if c in ('KEY_BACKSPACE', '\b', '\x7f'):
                if len(self._current_io) > 0:
                    self._current_io.pop()
                    self._column_number -= 1
            else:
                self._current_io.append(str(c))
                self._column_number += 1
            screen.addstr(self._line_number, self._column_number, ''.join(self._current_io))

            screen.addstr(10,10, str(self._column_number))
            screen.addstr(11,10, str(curses.KEY_BACKSPACE))
            screen.addstr(12, 10, str(curses.KEY_DC))
            # Clear the terminal
            #screen.clear()
            #if c == ord('a'):
            #    screen.addstr("\nYou pressed the 'a' key.")
            #elif c == curses.KEY_UP:
            #    screen.addstr("You pressed the up arrow.")
            #elif c == 27:
            #    break
            #else:
                #screen.addstr(0,0,str(c))
            #    screen.addstr(1,0,"This program doesn't know that key.....")




def init():
    return CursesProgram()

if __name__ == "__main__":
    obj = init()
    obj.run()