import sys
from command_line import command_line

if __name__ == "__main__":
    if "--command-line" in sys.argv:
        cmd = command_line.init()
        sys.exit(cmd.run())
    else:
        raise NotImplementedError()
