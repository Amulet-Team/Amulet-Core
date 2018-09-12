import sys
import version
from command_line import command_line, enhanced_prompt, reduced_prompt, CommandHandler

COMMAND_MODE = "--command-line" in sys.argv or "-c" in sys.argv
PROMPT_MODE = "--prompt" in sys.argv or "-p" in sys.argv

print("=" * 54)
print(f"| Amulet-Map-Editor version: {version.VERSION_STRING:<23} |")
print("=" * 54)

if __name__ == "__main__":
    if COMMAND_MODE or PROMPT_MODE:
        io_wrapper = None
        if COMMAND_MODE:
            io_wrapper = reduced_prompt.ReducedPromptIO()
        elif PROMPT_MODE:
            io_wrapper = enhanced_prompt.EnhancedPromptIO()

        #cmd = command_line.init(io_wrapper)
        cmd = CommandHandler(io_wrapper)
        sys.exit(cmd.run())
        #cmd = command_line.init()
        #sys.exit(cmd.run())
    #elif PROMPT_MODE:
    #    cmd = prompt_line.init()
    #    sys.exit(cmd.run())
    else:
        raise NotImplementedError()
