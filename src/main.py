import sys
from version import VERSION_STRING

COMMAND_MODE = "--command-line" in sys.argv or "-c" in sys.argv

if __name__ == "__main__":
    if COMMAND_MODE:
        print("=" * 54)
        print(f"| Amulet-Map-Editor version: {VERSION_STRING:<16} |")
        print("=" * 54)

        from command_line import CommandLineHandler

        sys.exit(CommandLineHandler().run())
    else:
        raise NotImplementedError(
            "There is only a command line version for now. "
            "To start it, you should use the argument '--command-line'"
        )
