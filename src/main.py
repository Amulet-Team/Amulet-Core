import sys
import version
from command_line import command_line, prompt_line

COMMAND_MODE = "--command-line" in sys.argv or "-c" in sys.argv
PROMPT_MODE = "--prompt" in sys.argv or "-p" in sys.argv

print("=" * 54)
print(f"| Amulet-Map-Editor version: {version.VERSION_STRING:<16} |")
print("=" * 54)

if __name__ == "__main__":
    if COMMAND_MODE:
        cmd = command_line.init()
        sys.exit(cmd.run())
    elif PROMPT_MODE:
        cmd = prompt_line.init()
        sys.exit(cmd.run())
    else:
        raise NotImplementedError()
