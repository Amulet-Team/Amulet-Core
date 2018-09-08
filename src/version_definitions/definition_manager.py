import json
import os

import re
from typing import Union

from api.paths import DEFINITIONS_DIR


class DefinitionManager:
    """
    Handles loading block definitions and mapping them to our internal definitions
    """

    @staticmethod
    def properties_to_string(props: dict) -> str:
        """
        Converts a dictionary of blockstate properties to a string

        :param props: The dictionary of blockstate properties
        :return: The string version of the supplied blockstate properties
        """
        result = []
        for key, value in props.items():
            result.append("{}={}".format(key, value))
        return ",".join(result)

    @staticmethod
    def string_to_properties(string: str) -> dict:
        """
        Converts a string into a dictionary of blockstate properties

        :param string: The string of blockstate properties
        :return: The resulting dictionary of blockstate properties
        """
        result = {}
        split = string.split(",")
        for pair in split:
            key, value = pair.split("=")
            if not value.isdigit() and not value.isalpha():
                value = float(value)
            elif not value.isalpha():
                value = int(value)
            result[key] = value
        return result

    def __init__(self, definitions_to_build: str):
        self.blocks = {}
        self._definitions = {}

        self.matcher = re.compile(r"^(.)+:(.)+$")

        fp = open(os.path.join(DEFINITIONS_DIR, "internal", "blocks.json"))
        self.defs_internal = json.load(fp)
        fp.close()

        self._definitions["internal"] = {"minecraft": self.defs_internal["minecraft"]}

        if not os.path.exists(
            "{}.json".format(
                os.path.join(DEFINITIONS_DIR, definitions_to_build, "blocks")
            )
        ):
            raise FileNotFoundError()

        fp = open(
            "{}.json".format(
                os.path.join(DEFINITIONS_DIR, definitions_to_build, "blocks")
            ),
            "r",
        )
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
                    self.blocks[map_to[map_to.index(":") + 1 :]] = block_idenifier
                else:
                    for blockstate in defs[resource_location][base_block]:
                        block_id = defs[resource_location][base_block][blockstate].get(
                            "id", [-1, -1]
                        )
                        map_to = defs[resource_location][base_block][blockstate].get(
                            "map_to", "internal:minecraft:unknown"
                        )
                        self.blocks[map_to[map_to.index(":") + 1 :]] = block_id

    def get_internal_block(
        self, resource_location="minecraft", basename="air", properties=None
    ) -> dict:
        """
        Returns the versioned definition for the supplied internal block.
        Internal definitions are loosely based off of the flattened blockstates of Java Edition 1.13

        :param resource_location: The resource location to look in
        :param basename: The basename of the block
        :param properties: The properties of the blockstate
        :return: A dictionary representing the versioned definition of the internal block
        """
        if properties:
            properties = self.properties_to_string(properties)

        if resource_location in self._definitions["internal"]:
            if basename in self._definitions["internal"][resource_location]:
                if (
                    properties
                    and properties
                    in self._definitions["internal"][resource_location][basename]
                ):
                    return self._definitions["internal"][resource_location][basename][
                        properties
                    ]

                elif properties:
                    raise KeyError(
                        "No blockstate definition found for '{}:{}[{}]'".format(
                            resource_location, basename, properties
                        )
                    )

                else:
                    return self._definitions["internal"][resource_location][basename]

        raise KeyError(
            "No blockstate definition found for '{}:{}'".format(
                resource_location, basename
            )
        )

    def get_block_from_definition(
        self, block: Union[str, list, tuple], default=None
    ) -> str:
        """
        Returns the internal name of the supplied versioned block

        :param block: The versioned block
        :param default: The default value to return if missing
        :return: The internal name that is mapped to the versioned block
        """
        if isinstance(block, str) and self.matcher.match(block):
            for key, value in self.blocks.items():
                if block == value:
                    return key

            return default

        elif isinstance(block, (list, tuple)):
            for key, value in self.blocks.items():
                if value[0] == block[0] and value[1] == block[1]:
                    return key

            return default

        else:
            raise KeyError()


if __name__ == "__main__":
    ver = input("Version definitions to build: ")
    proto = DefinitionManager(ver)
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
                print(user_input.replace(" ", "")[1:-1])
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
            proto = DefinitionManager(user_input)
            print("Successfully loaded '{}' definitions".format(user_input))
        elif user_input == "list":
            print(proto.blocks)
        else:
            print("==== Help ====")
            print(
                "block <internal name>: Looks up a block from it's internal mapping name (internal -> version)"
            )
            print(
                "reverse <versioned name>: Looks up a block from it's internal mapping value (version -> internal)"
            )
            print("list: Lists all blocks in the current mapping")
            print(
                "load <version>: Loads the specified version of block definitions.rst"
            )
