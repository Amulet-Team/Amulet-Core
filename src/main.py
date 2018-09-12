import sys
import version
from command_line import enhanced_prompt, reduced_prompt, CommandHandler

COMMAND_MODE = "--command-line" in sys.argv or "-c" in sys.argv
REDUCED_MODE = "--reduced" in sys.argv or "-r" in sys.argv

print("=" * 54)
print(f"| Amulet-Map-Editor version: {version.VERSION_STRING:<23} |")
print("=" * 54)

if __name__ == "__main__":
    if COMMAND_MODE:
        io_wrapper = None
        if REDUCED_MODE:
            io_wrapper = reduced_prompt.ReducedPromptIO()
        else:
            io_wrapper = enhanced_prompt.EnhancedPromptIO()

        cmd = CommandHandler(io_wrapper)
        sys.exit(cmd.run())
    else:
        raise NotImplementedError()
