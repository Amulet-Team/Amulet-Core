from __future__ import annotations

import copy
import json
from collections import UserDict
from glob import iglob
from itertools import chain
from os.path import join, basename, dirname
from typing import Dict, Union, Optional

from pprint import pprint


class NBTStructure:
    __slots__ = ["_tag_type", "_value"]

    def __init__(self, tag_type, value=None):
        self._tag_type = tag_type
        self._value = value

    def __repr__(self):
        return f"NBTStructure({self._tag_type}, {self._value})"

    def __eq__(self, other: NBTStructure):
        return self._tag_type == other._tag_type and self._value == other._value

    @property
    def tag_type(self):
        return self._tag_type

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

    def non_default(self):
        return self._value is not None

    def same_tag_type(self, other: NBTStructure) -> bool:
        return self._tag_type == other._tag_type

    def apply_template(self, template: NBTStructure) -> Optional[NBTStructure]:
        if self.same_tag_type(template) or template._tag_type == "any":
            return self
        elif self._tag_type != template._tag_type:
            return NBTStructure(template._tag_type, self.value)
        elif template._value:
            return NBTStructure(template._tag_type, template.value)
        return None


class NBTRangeStructure(NBTStructure):
    __slots__ = ["_tag_type", "_value", "_range"]

    def __init__(self, tag_type, value, _range):
        super().__init__(tag_type, value)
        self._range = _range
        if self._value:
            self._value = self.apply_range(self._value)

    def __repr__(self):
        return f'NBTRangeStructure("{self._tag_type}", {self._value}, {self._range})'

    def __eq__(self, other: NBTRangeStructure):
        return super().__eq__(other) and self._range == other._range

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = self.apply_range(val)

    @property
    def tag_range(self):
        return self._range

    def apply_range(self, value):
        return max(self._range[0], min(value, self._range[1]))

    def apply_template(
        self, template: NBTRangeStructure
    ) -> Optional[NBTRangeStructure]:
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


class NBTListStructure(NBTStructure):
    __slots__ = ["_tag_type", "_items", "_schema"]

    def __init__(self, schema, initial_value=None):
        super().__init__("list", [])
        if initial_value:
            if isinstance(initial_value, (list, tuple)):
                self._value = initial_value
            else:
                self._value.append(initial_value)
        self._schema = schema

    def __repr__(self):
        return f"NBTListStructure({self._schema}, {self._value})"

    def __iter__(self):
        return iter(self._value)

    def __len__(self):
        return len(self._value)

    def __getitem__(self, item):
        return self._value[item]

    def __setitem__(self, index, value):
        self._value[index] = value

    def __eq__(self, other: NBTListStructure):
        return super().__eq__(other) and self._schema == other._schema

    def append(self, value):
        self._value.append(value)

    def non_default(self):
        return len(self._value) > 0

    def apply_template(self, template: NBTListStructure) -> Optional[NBTListStructure]:
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
    def __init__(self, structure: dict, value: dict = None):
        super().__init__()
        self._tag_type = "compound"
        self._structure = structure
        self.data = value if value else {}

    @property
    def value(self):
        return self.data

    def non_default(self):
        return self.any_non_default_tags()

    def any_non_default_tags(self):
        for key in self.keys():
            if self[key].non_default():
                return True
        return False

    def apply_template(
        self, template: NBTCompoundStructure
    ) -> Optional[NBTCompoundStructure]:
        if self.value is None:
            return None

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
    def __init__(self, template_dir: str, tag_handlers=None):
        self._template_dir = template_dir
        self._tag_handlers = tag_handlers if tag_handlers else {}

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
            return NBTStructure("any", None)

        if tag_type == "list":
            return NBTListStructure(json_object["schema"], json_object.get("default"))

        if "range" in json_object:
            return NBTRangeStructure(
                tag_type, json_object.get("default"), tuple(json_object["range"])
            )

        else:
            return NBTStructure(tag_type, json_object.get("default"))

    def load_template(self, template_name: str) -> NBTCompoundStructure:
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
            result.update(self.load_template(result["<metadata>"]["extends"]))
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
