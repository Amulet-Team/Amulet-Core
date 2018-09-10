from typing import List

from numpy import unique

from api.selection import SubBox, SelectionBox

from command_line import (
    command,
    subcommand,
    ComplexCommand,
    parse_coordinates,
    WorldMode,
)


@command("box")
class BoxCommand(ComplexCommand):
    def __init__(self, *args, **kwargs):
        super(BoxCommand, self).__init__(*args, **kwargs)

        if "boxes" not in self.handler.shared_data:
            self.handler.shared_data["boxes"] = {}

    @subcommand("create")
    def create(self, args: List[str]):
        if len(args) < 4:
            print('Usage: box.create "name" <x1,y1,z1> <x2,y2,z2> ....')

        box_name = args[1]

        if len(args[2:]) % 2 != 0:
            self.error("You must have an even amount of coordinate pairs")
            return

        if len(args[2:]) == 2:
            p1 = parse_coordinates(args[2])
            p2 = parse_coordinates(args[3])

            selection_box = SelectionBox((SubBox(p1, p2),))
        else:
            selection_box = SelectionBox()
            for start in range(0, len(args[2:]), 2):
                p1 = parse_coordinates(args[2 + start])
                p2 = parse_coordinates(args[3 + start])
                selection_box.add_box(SubBox(p1, p2))

        self.handler.shared_data["boxes"][box_name] = selection_box

    @subcommand("list")
    def list(self, args: List[str]):
        print("==== Selection Boxes ====")
        for name in self.handler.shared_data.get("boxes", {}):
            print(f"{name}")

    @subcommand("info")
    def info(self, args: List[str]):
        if len(args) < 2:
            print('Usage: box.info "<box name>"')
            return

        name = args[1]
        box = self.handler.shared_data.get("boxes", {}).get(name)

        if box:
            print(f"==== {name} Info ====")
            print(f"Included sub-boxes: {' '.join(str(b) for b in box._boxes)}")

    @subcommand("delete")
    def delete(self, args: List[str]):
        if len(args) < 2:
            print('Usage: box.delete "<box name>"')
            return

        name = args[1]
        if name in self.handler.shared_data.get("boxes", {}):
            del self.handler.shared_data["boxes"][name]
        else:
            self.error(f'Box "{name}" doesn\'t exist')

    @subcommand("analyze")
    def analyze(self, args: List[str]):
        if len(args) < 2:
            print('Usage: box.analyze "<box name>"')
            return

        box_name = args[1]
        if box_name not in self.handler.shared_data.get("boxes", {}):
            self.error(f'Box "{box_name}" doesn\'t exist')
            return

        if not self.in_mode(WorldMode):
            self.error(f"Box analysis can't be done without a world loaded")
            return

        world = self.get_mode(WorldMode).world

        box: SelectionBox = self.handler.shared_data.get("boxes", {}).get(box_name)
        blocks = {}
        for subbox in box.subboxes():
            selection_generator = world.get_sub_chunks(*subbox.to_slice())
            for selection in selection_generator:
                uniques = unique(world.block_definitions[selection.blocks])
                for u in uniques:
                    if u in blocks:
                        blocks[u] += 1
                    else:
                        blocks[u] = 1

        if blocks:
            print("=== Analysis Results ===")
            for key, value in blocks.items():
                print(f"{key}: {value}")

    @classmethod
    def help(cls, command_name: str = None):
        if command_name == "create":
            print(
                "Creates a selection box from a list of coordinate pairs. Each coordinate"
            )
            print("pair corresponds to the minimum and maximum points of a sub-box\n")
            print('Usage: box.create "name" <x1,y1,z1> <x2,y2,z2> ....')
        elif command_name == "list":
            print("Lists all created selection boxes\n")
            print("Usage: box.list")
        elif command_name == "info":
            print("Displays various information about the specified selection box\n")
            print('Usage: box.info "<box name>"')
        elif command_name == "delete":
            print(
                "Deletes a selection box from memory, this is a permanent operation\n"
            )
            print('Usage: box.delete "<box name>"')
        elif command_name == "analyze":
            print("Analyzes the specified selection box and displays the amount of")
            print("each block present in the selection time\n")
            print('Usage: box.analyze "<box name>"')
        else:
            print("create - Creates a new selection box")
            print("list - Lists all stored selection boxes")
            print("info - Prints details about a selection box")
            print("delete - Deletes a selection box")
            print("analyze - Analyzes the blocks in a selection box")

    @classmethod
    def short_help(cls) -> str:
        return "Various commands for creating selection boxes"
