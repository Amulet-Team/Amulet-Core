import json
import os

import re  # For command-line


class Prototype1:

    def __init__(self, definitions_to_build):
        self.blocks = {}
        self._definitions = {}

        fp = open(os.path.join("internal", "minecraft.json"))
        self.defs_internal = json.load(fp)
        fp.close()

        self._definitions["internal"] = {"minecraft": self.defs_internal["minecraft"]}

        if not os.path.exists("{}.json".format(definitions_to_build)):
            raise FileNotFoundError()

        fp = open("{}.json".format(definitions_to_build), "r")
        defs = json.load(fp)
        fp.close()
        self._definitions[definitions_to_build] = {"minecraft": {}}
        for resource_location in defs:
            for base_block in defs[resource_location]:
                if base_block not in defs[resource_location]:
                    self._definitions[definitions_to_build]["minecraft"][
                        base_block
                    ] = {}

                if (
                    "map_to" in defs[resource_location][base_block]
                    and "id" in defs[resource_location][base_block]
                ):
                    map_to = defs[resource_location][base_block]["map_to"]
                    block_idenifier = defs[resource_location][base_block]["id"]
                    self.blocks[map_to[map_to.index(":") + 1:]] = block_idenifier
                else:
                    for blockstate in defs[resource_location][base_block]:
                        block_id = defs[resource_location][base_block][blockstate].get(
                            "id", [-1, -1]
                        )
                        map_to = defs[resource_location][base_block][blockstate].get(
                            "map_to", "internal:minecraft:unknown"
                        )
                        self.blocks[map_to[map_to.index(":") + 1:]] = block_id


if __name__ == "__main__":
    ver = input("Version definitions to build: ")
    proto = Prototype1(ver)
    matcher = re.compile(r"^(.)+:(.)+$")
    while True:
        user_input = input(">> ").lower()
        if user_input == "quit" or user_input == "q":
            break

        elif user_input.startswith("block"):
            print(
                "Result: {}".format(
                    proto.blocks.get(
                        user_input.replace("block ", ""), "minecraft:unknown"
                    )
                )
            )
        elif user_input.startswith("reverse"):
            user_input = user_input.replace("reverse ", "")
            result = None
            if matcher.match(user_input):
                for key, value in proto.blocks.items():
                    if user_input == value:
                        result = key
                        break

            else:
                numerical_ids = map(int, user_input.replace(" ", "")[1:-1].split(","))
                numerical_ids = [i for i in numerical_ids]
                result = None
                for key, value in proto.blocks.items():
                    if value == numerical_ids:
                        result = key
                        break

            if result:
                print("Result: {}".format(result))
            else:
                print("Block not found")
        elif user_input.startswith("load"):
            user_input = user_input.replace("load ", "")
            proto = Prototype1(user_input)
            print("Successfully loaded '{}' definitions".format(user_input))
        elif user_input == "list":
            print(proto.blocks)
        else:
            print("==== Help ====")
            print(
                "block: Looks up a block from it's internal mapping name (internal -> version)"
            )
            print(
                "reverse: Looks up a block from it's internal mapping value (version -> internal)"
            )
            print("list: Lists all blocks in the current mapping")
