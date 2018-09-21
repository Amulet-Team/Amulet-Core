from __future__ import annotations

from typing import List

from command_line import command, SimpleCommand, parse_coordinates, WorldMode


@command("operation")
class OperationCommand(SimpleCommand):

    def run(self, args: List[str]):
        if len(args) == 1:
            print('Usage: operation "<operation name>" <operation options> ....')
            return

        world_mode: WorldMode = self.get_mode(WorldMode)
        if not world_mode:
            self.error("You must be in a world mode to use this command")
            return

        world = world_mode.world

        op_name = args[1]
        options = []

        if len(args) >= 2:
            for arg in args[2:]:
                if arg.startswith("<") and arg.endswith(">"):
                    options.append(parse_coordinates(arg))
                elif arg.startswith("$"):
                    entry = self.get_shared_data(arg)

                    if entry:
                        options.append(entry)
                    else:
                        print(f'Couldn\'t find shared data object "{arg}"')
                        return

            print(options)
            world.run_operation_from_operation_name(op_name, *options)

    def help(self):
        pass

    def short_help(self) -> str:
        return ""
