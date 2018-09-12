import sys

from command_line import enhanced_prompt, reduced_prompt, CommandHandler
from version import VERSION_STRING


COMMAND_MODE = "--command-line" in sys.argv or "-c" in sys.argv
REDUCED_MODE = "--reduced" in sys.argv or "-r" in sys.argv


if __name__ == "__main__":
    if COMMAND_MODE:
        print("=" * 54)
        print(f"| Amulet-Map-Editor version: {VERSION_STRING:<23} |")
        print("=" * 54)

        io_wrapper = None
        if REDUCED_MODE:
            io_wrapper = reduced_prompt.ReducedPromptIO()
        else:
            io_wrapper = enhanced_prompt.EnhancedPromptIO()

        cmd = CommandHandler(io_wrapper)
        sys.exit(cmd.run())
    else:
        raise NotImplementedError(
            "There is only a command line version for now. "
            "To start it, you should use the argument '--command-line'"
        )
