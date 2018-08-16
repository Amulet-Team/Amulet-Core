from typing import List

from api.box import SubBox, SelectionBox

from command_line import command, subcommand, ComplexCommand, parse_coordinates


@command("box")
class BoxCommand(ComplexCommand):

    def __init__(self, *args, **kwargs):
        super(BoxCommand, self).__init__(*args, **kwargs)
        self.handler.shared_data["boxes"] = {}

    @subcommand("create")
    def create(self, args: List[str]):
        if len(args) < 4:
            print("Usage: box.create \"name\" <x1,y1,z1> <x2,y2,z2> ....")

        box_name = args[1]

        if len(args[2:]) % 2 != 0:
            self.error("You must have an even amount of coordinate pairs")
            return

        if len(args[2:]) == 2:
            p1 = parse_coordinates(args[2])
            p2 = parse_coordinates(args[3])

            selection_box = SelectionBox((SubBox(p1,p2),))
        else:
            selection_box = SelectionBox()
            for start in range(0, len(args[2:]), 2):
                p1 = parse_coordinates(args[2 + start])
                p2 = parse_coordinates(args[3 + start])
                selection_box.add_box(SubBox(p1,p2))

        self.handler.shared_data["boxes"][box_name] = selection_box

    @subcommand("list")
    def list(self, args: List[str]):
        print("==== Selection Boxes ====")
        for name in self.handler.shared_data.get("boxes", {}):
            print(f"{name}")

    @subcommand("info")
    def info(self, args: List[str]):
        if len(args) < 2:
            print("Usage: box.info \"<box name>\"")
            return

        name = args[1]
        box = self.handler.shared_data.get("boxes", {}).get(name)

        if box:
            print(f"==== {name} Info ====")
            print(f"Included sub-boxes: {' '.join(str(b) for b in box._boxes)}")

    @subcommand("delete")
    def delete(self, args: List[str]):
        if len(args) < 2:
            print("Usage: box.delete \"<box name>\"")
            return

        name = args[1]
        if name in self.handler.shared_data.get("boxes", {}):
            del self.handler.shared_data["boxes"][name]
        else:
            self.error(f"Box \"{name}\" doesn't exist")




    @classmethod
    def help(cls, command_name: str = None):
        if command_name == "create":
            print("Creates a selection box from a list of coordinate pairs. Each coordinate")
            print("pair corresponds to the minimum and maximum points of a sub-box\n")
            print("Usage: box.create \"name\" <x1,y1,z1> <x2,y2,z2> ....")
        else:
            print("create - Creates a new selection box")

    @classmethod
    def short_help(cls) -> str:
        return "Various commands for creating selection boxes"

