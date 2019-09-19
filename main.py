import sys
from argparse import ArgumentParser

from amulet.command_line import enhanced_prompt, reduced_prompt, CommandHandler
from amulet.version import VERSION_STRING

if __name__ == "__main__":
    parser = ArgumentParser(
        description="A new Minecraft world editor that aims to be flexible, "
        "extendable and support most editions of Minecraft"
    )
    parser.add_argument(
        "-c",
        "--command-line",
        action="store_true",
        help="use the commandline interface",
    )
    parser.add_argument(
        "-r",
        "--reduced",
        action="store_true",
        help="use a reduced prompt (commandline mode only)",
    )
    args = parser.parse_args()
    if args.reduced and not args.command_line:
        parser.error("Reduced mode requires commandline mode to be active")
    if args.command_line:
        print("=" * 54)
        print(f"| Amulet-Map-Editor version: {VERSION_STRING:<23} |")
        print("=" * 54)

        io_wrapper = None
        if args.reduced:
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
