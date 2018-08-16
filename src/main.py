import sys
from command_line import command_line, curses_line

if "--command-line" in sys.argv:
    if '--curses' in sys.argv:
        cmd = curses_line.init()
    else:
        cmd = command_line.init()
    sys.exit(cmd.run())
else:
    raise NotImplementedError()
