from __future__ import annotations

from importlib import import_module
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
                else:
                    options.append(arg)

            operation = self._get_operation(op_name, *options)
            try:
                world.run_operation(operation)
            except Exception as e:
                print(e)

    def help(self):
        pass

    def short_help(self) -> str:
        return ""

    @staticmethod
    def _get_operation(operation_name, *args):
        operation_module = import_module(f"operations.{operation_name}")
        operation_class_name = "".join(x.title() for x in operation_name.split("_"))
        operation_class = getattr(operation_module, operation_class_name)
        operation_instance = operation_class(*args)

        return operation_instance
