import sys
import version
from command_line import command_line

COMMAND_MODE = "--command-line" in sys.argv or "-c" in sys.argv

print("=" * 54)
print(f"| Unified-Minecraft-Editor version: {version.VERSION_STRING:<16} |")
print("=" * 54)

if __name__ == "__main__":
    if COMMAND_MODE:
        cmd = command_line.init()
        sys.exit(cmd.run())
    else:
        raise NotImplementedError()
