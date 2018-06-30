import sys
from command_line import command_line

if "--command-line" in sys.argv:
    cmd = command_line.init()
    sys.exit(cmd._run())
else:
    raise NotImplementedError()
