from __future__ import annotations

import copy
import json
from collections import UserDict, UserList
from glob import iglob
from itertools import chain
from os.path import join, basename, dirname
from typing import Any, Dict, Tuple, List, Union, Optional


class NBTStructure:
    """
    Generic container for NBT tags
    """

    __slots__ = ["_tag_type", "_value"]

    def __init__(self, tag_type: str, value: Any = None):
        self._tag_type: str = tag_type
        self._value: Any = value

    def __repr__(self):
        return f"NBTStructure({self._tag_type}, {self._value})"

    def __eq__(self, other: NBTStructure):
        return self.tag_type == other.tag_type and self.value == other.value

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def tag_type(self) -> str:
        """
        Returns the represented tag_type of the specified NBTStructure object

        :return: The tag type of specified NBTStructure
        """
        return self._tag_type

    @property
    def value(self) -> Any:
        """
        Returns the value stored in the specified NBTStructure object

        :return: The value of the specified NBTStructure object
        """
        return self._value

    @value.setter
    def value(self, val: Any):
        self._value = val

    def same_tag_type(self, other: NBTStructure) -> bool:
        """
        Function to determine whether tag types match between to NBTStructures

        :param other: The other NBTStructure
        :return: True if the types match, False otherwise
        """
        return self._tag_type == other._tag_type

    def apply_template(self, template: NBTStructure) -> Optional[NBTStructure]:
        """
        Applies the specified template to the existing NBTStructure object

        :param template: The template tag to apply to the existing NBTStructure object
        :return: Either the object itself if nothing was modified, or a new NBTStructure if the object needed to be
            modified to conform to the template
        """
        if template._tag_type == "any":
            return self

        if self.same_tag_type(template):
            return self
        elif self._tag_type != template._tag_type:
            return NBTStructure(template._tag_type, self.value)
        elif template._value:
            return NBTStructure(template._tag_type, template.value)
        return None


class NBTRangeStructure(NBTStructure):
    """
    NBT container that applies a specified range to it's value upon modification and instantiation
    """

    __slots__ = ["_tag_type", "_value", "_range"]

    def __init__(
        self,
        tag_type: str,
        value: Union[int, float],
        _range: Tuple[Union[int, float], Union[int, float]],
    ):
        super().__init__(tag_type, value)
        self._range = _range
        if self._value:
            self._value = self.apply_range(self._value)

    def __repr__(self):
        return f'NBTRangeStructure("{self._tag_type}", {self._value}, {self._range})'

    def __eq__(self, other: NBTRangeStructure):
        return super().__eq__(other) and self.tag_range == other.tag_range

    @property
    def value(self) -> Union[int, float]:
        return self._value

    @value.setter
    def value(self, val: Union[int, float]):
        self._value = self.apply_range(val)

    @property
    def tag_range(self) -> Tuple[Union[int, float], Union[int, float]]:
        return self._range

    def apply_range(self, value: Union[int, float]) -> Union[int, float]:
        """
        Clamps the value to the range specified by the NBTRangeStructure

        :param value: The value to clamp
        :return: The clamped value
        """
        return max(self._range[0], min(value, self._range[1]))

    def apply_template(
        self, template: NBTRangeStructure
    ) -> Optional[NBTRangeStructure]:
        """
        Applies the specified template to the existing NBTRangeStructure object

        :param template: The template tag to apply to the existing NBTStructure object
        :return: Either the object itself if nothing was modified, or a new NBTRangeStructure if the object needed to be
            modified to conform to the template
        """
        if template._tag_type == "any":
            return self

        if (
            self.same_tag_type(template)
            and self._range[0] <= self._value <= self._range[1]
        ):
            return self
        elif self._tag_type != template._tag_type:
            return NBTRangeStructure(template._tag_type, self.value, template._range)
        elif template._value:
            return NBTRangeStructure(template._tag_type, self.value, template._range)
        return None


class NBTListStructure(UserList, NBTStructure):
    """
    NBT container for lists that can apply a template "schema" to each value
    """

    def __init__(
        self, initial_value=None, schema: List[NBTStructure] = NBTStructure("any")
    ):
        super().__init__()
        self._tag_type = "list"
        if initial_value:
            if isinstance(initial_value, (list, tuple)):
                self.data = initial_value
            else:
                self.data.append(initial_value)
        self._schema = schema

    def __repr__(self):
        return f"NBTListStructure({repr(self.value)}, {repr(self._schema)})"

    def __eq__(self, other: NBTListStructure):
        return super().__eq__(other) and self._schema == other._schema

    @property
    def value(self):
        return self.data

    @property
    def schema(self):
        return self._schema

    def apply_template(self, template: NBTListStructure) -> Optional[NBTListStructure]:
        """
        Applies the specified template to the existing NBTListStructure object

        .. warning::
            When calling this method, the existing objects value will be modified so each member of the internal list
            conforms to the list "schema" and this considered a irreversible mutation

        :param template: The template tag to apply to the existing NBTStructure object
        :return: Either the object itself if nothing was modified, or a new NBTListStructure if the template "schema"
            didn't match the current NBTListStructures "schema" in which the templates schema will be used
        """

        if template._tag_type == "any":
            return self

        if self.same_tag_type(template) and self._schema == template._schema:
            for i in range(len(self)):
                self[i] = self[i].apply_template(self._schema)
            return self
        elif self.value:
            return NBTListStructure(template._schema, self.value).apply_template(
                template
            )
        return None


class NBTCompoundStructure(UserDict, NBTStructure):
    """
    NBT container for dictionary objects
    """

    def __init__(self, structure: dict = None, value: dict = None):
        super().__init__()
        self._tag_type = "compound"
        self._structure = structure
        self.data = value if value else {}

    def __repr__(self):
        return f"NBTCompoundStructure({repr(self._structure)}, {repr(self.value)})"

    @property
    def value(self):
        return self.data

    @property
    def structure(self):
        return self._structure

    def apply_template(
        self, template: NBTCompoundStructure
    ) -> Optional[NBTCompoundStructure]:
        """
        Applies the specified template to the existing NBTCompoundStructure object

        .. warning::
            When calling this method, the internal dictionary keys and values might be modified to conform to the
            specified template and is considered a irreversible mutation

        :param template: The template tag to apply to the existing NBTCompoundStructure object
        :return: The NBTCompoundStructure object
        """
        if self.value is None:
            return None

        if template._tag_type == "any":
            return self

        for tag_name in template.keys():
            template_tag: NBTStructure = template[tag_name]
            nbt_tag: NBTStructure = self.value.get(tag_name)

            if nbt_tag:
                self[tag_name] = nbt_tag.apply_template(template_tag)
            elif template_tag.value:
                self[tag_name] = copy.deepcopy(template_tag)

            if tag_name in self and self[tag_name] is None:
                del self[tag_name]

        if len(self):
            return self
        return None


class TemplateLoader:
    """
    Handles the loading of NBT template json files
    """

    def __init__(self, template_dir: str):
        self._template_dir = template_dir

        iter_chain = chain(
            iglob(join(self._template_dir, "entities", "*.json")),
            iglob(join(self._template_dir, "blockentities", "*.json")),
            iglob(join(self._template_dir, "misc", "*.json")),
        )
        self._templates = {basename(p)[:-5]: p for p in iter_chain}
        self._entity_template = self.load_template("entity")
        self._item_template = self.load_template("item")

    @property
    def template_dir(self) -> str:
        return self._template_dir

    @property
    def templates(self) -> Dict[str, str]:
        return self._templates

    def _tag_hook(self, json_object: dict) -> Union[dict, NBTStructure]:
        if "tag_type" not in json_object:
            return json_object

        tag_type: str = json_object["tag_type"]

        if tag_type.startswith("<") and tag_type.endswith(">"):
            return self.load_template(tag_type[1:-1])

        if tag_type == "compound":
            structure = json_object["structure"]
            if isinstance(structure, dict):
                return NBTCompoundStructure(structure)
            return NBTStructure("any")

        if tag_type == "list":
            return NBTListStructure(
                schema=json_object["schema"], initial_value=json_object.get("default")
            )

        if "range" in json_object:
            return NBTRangeStructure(
                tag_type, json_object.get("default"), tuple(json_object["range"])
            )

        else:
            return NBTStructure(tag_type, json_object.get("default"))

    def load_template(self, template_name: str) -> NBTCompoundStructure:
        """
        Loads the specified named NBT template file

        :param template_name: The (normalized) name of the template file (IE: "creeper" for "creeper.json")
        :return: The NBT template structure from the specified template file
        """

        if template_name not in self._templates:
            raise FileNotFoundError()

        # Use deepcopy() since we don't want any modification to the original dicts
        if template_name == "entity" and hasattr(self, "_entity_template"):
            return copy.deepcopy(self._entity_template)

        elif template_name == "item" and hasattr(self, "_item_template"):
            return copy.deepcopy(self._item_template)

        template_path = self._templates[template_name]

        fp = open(template_path)
        result = json.load(fp, object_hook=self._tag_hook)
        fp.close()

        if "extends" in result.get("<metadata>", {}):
            result.update(self.load_template(result["<metadata>"]["extends"]).structure)
            del result["<metadata>"]

        return NBTCompoundStructure(result)


if __name__ == "__main__":
    ls1 = NBTListStructure(
        NBTStructure("string", None),
        [NBTStructure("string", "test1"), NBTStructure("int", 1)],
    )
    print(ls1.value)
    ls1.apply_template(NBTListStructure(NBTStructure("string", None), None))
    print(ls1.value)

    print("\n=====\n")

    comp1 = NBTCompoundStructure(
        {
            "id": NBTStructure("string", "minecraft:shovel"),
            "Count": NBTStructure("int", 4),
            "tag": NBTCompoundStructure(
                {
                    "Unbreakable": NBTStructure("byte", 1),
                    "Damage": NBTStructure("float", 10),
                    "CanDestroy": NBTListStructure(
                        NBTStructure("string", None),
                        [
                            NBTStructure("string", "minecraft:dirt"),
                            NBTStructure("int", 10),
                        ],
                    ),
                }
            ),
        }
    )
    template1 = NBTCompoundStructure(
        {
            "id": NBTStructure("string", "minecraft:unknown_item"),
            "Count": NBTStructure("byte", 4),
            "tag": NBTCompoundStructure(
                {
                    "Unbreakable": NBTStructure("byte", 1),
                    "Damage": NBTStructure("int", 10),
                    "CanDestroy": NBTListStructure(NBTStructure("string", None), []),
                }
            ),
        }
    )
    print(comp1.value)
    print(comp1.value)

    print("\n=====\n")
    tl = TemplateLoader(dirname(__file__))
    item_template = tl.load_template("item")
    print("Template:", item_template)

    item1 = NBTCompoundStructure({"Count": NBTStructure("int", 1000)})
    print("Item #1 (Original):  ", item1)
    item1.apply_template(item_template)
    print(f"Item #1 (Save-able): {item1}")

    # item2 = NBTCompoundStructure({"Count": NBTRangeStructure("byte", 1, (-128, 127)), "Slot": NBTStructure("byte", 2),
    #          "id": NBTStructure("string", "minecraft:dirt"), "custom_tag": NBTStructure("long", 100)})
    # print("Item #2 (Original):  ", item2)
    # item2.apply_template(item_template)
    # print("Item #2 (Save-able): ", item2)
    #
    # item3 = NBTCompoundStructure({
    #     "tag": NBTCompoundStructure({
    #         "Enchantments": NBTListStructure(NBTStructure("string", None), [
    #             NBTStructure("string", "minecraft:dirt"),
    #             NBTStructure("int", "minecraft:stone")
    #         ]
    #                                          )}
    #     )})
    # print("Item #3 (Original):  ", item3)
    # item3.apply_template(item_template)
    # print("Item #3 (Save-able): ", item3)
