from typing import List

from command_line import command, SimpleCommand, parse_coordinates, WorldMode


@command("operation")
class OperationCommand(SimpleCommand):

    def run(self, args: List[str]):
        if len(args) == 1:
            print("Usage: operation \"<operation name>\" <operation options> ....")
            return

        world_mode: WorldMode = self.handler.get_mode(WorldMode)
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
                    depth = arg[1:].split(":")
                    current_dict = self.handler.shared_data
                    for key in depth[:-1]:
                        if key not in current_dict:
                            print(f"Couldn't find shared data object \"{arg}\"")
                            return
                        current_dict = current_dict[key]
                    options.append(current_dict[depth[-1]])

            world.run_operation(op_name, *options)


    def help(self):
        pass

    def short_help(self) -> str:
        return ""