from __future__ import annotations

from typing import Union, List
from typing import Any, Dict
import json
from collections import UserDict, UserList
from glob import iglob
from itertools import chain
from os.path import join, basename
import copy


class NBTStruct:
    """
    Base class implemented by all NBT structure classes
    """

    def apply_to(self, other_tag: Union[NBTEntry, NBTListEntry, NBTCompoundEntry]):
        """
        Applies the current NBT structure to the the supplied NBT entry

        :param other_tag: The NBT entry to apply the template to
        :return: A NBT entry object with the template applied to it
        """
        raise NotImplementedError()

    def create_entry_from_template(
        self, initial_value: Any = None
    ) -> Union[NBTEntry, NBTListEntry, NBTCompoundEntry]:
        """
        Creates a NBT entry from the NBT structure data

        :param initial_value: The value to populate the entry with
        :return: The corresponding NBT entry for the specified NBT structure object
        """
        raise NotImplementedError()


class NBTStructure(NBTStruct):
    """
    Generic structure for NBT templates
    """

    __slots__ = ("_tag_type", "_default_value")

    def __init__(self, tag_type: str, default_value: Any = None):
        self._tag_type = tag_type
        self._default_value = default_value

    @property
    def tag_type(self) -> str:
        """
        The tag type of the NBT structure

        :return: The tag type
        """
        return self._tag_type

    @property
    def default_value(self) -> Any:
        """
        The default value for the NBT structure

        :return: The value that will be inserted if the given NBT structure is required, ``None`` if not required
        """
        return self._default_value

    def apply_to(self, other_tag: NBTEntry) -> NBTEntry:
        """
        See :meth:`api.nbt_template.NBTStruct.apply_to`
        """
        if other_tag.tag_type == "any":
            return other_tag

        if self.tag_type == other_tag.tag_type:
            return other_tag
        else:
            return self.create_entry_from_template(other_tag.value)

    def create_entry_from_template(self, initial_value=None) -> NBTEntry:
        """
        See :meth:`api.nbt_template.NBTStruct.create_entry_from_template`
        """
        if initial_value is None:
            return NBTEntry(self.tag_type, self.default_value)
        return NBTEntry(self.tag_type, initial_value)


class NBTListStructure(NBTStruct):
    """
    NBT structure for List tags
    """

    __slots__ = ("_schema", "_default_value")

    def __init__(self, schema: NBTStructure = None, default_value: Any = None):
        self._schema = schema
        self._default_value = default_value

    @property
    def tag_type(self):
        return "list"

    @property
    def schema(self) -> NBTStructure:
        return self._schema

    @property
    def default_value(self) -> Any:
        return self._default_value

    def apply_to(self, other_tag: NBTListEntry) -> NBTListEntry:
        if self.schema.tag_type == "any":
            return other_tag

        for i in range(len(other_tag)):
            other_tag[i] = self.schema.apply_to(other_tag[i])

        return other_tag

    def create_entry_from_template(self, initial_value=None) -> NBTListEntry:
        if initial_value is None:
            return NBTListEntry(self.default_value)
        return NBTListEntry(initial_value)


class NBTCompoundStructure(NBTStruct):
    """
    NBT structure for Compound tags
    """

    __slots__ = ("_structure", "_default_value")

    def __init__(
        self,
        structure: Union[NBTStructure, Dict[str, NBTStructure]] = None,
        default_value: Any = None,
    ):
        self._structure = structure
        self._default_value = default_value

    @property
    def tag_type(self):
        return "compound"

    @property
    def structure(self) -> Union[NBTStructure, Dict[str, NBTStructure]]:
        return self._structure

    @property
    def default_value(self) -> Any:
        return self._default_value

    def apply_to(self, other_tag: NBTCompoundEntry) -> NBTCompoundEntry:
        if (
            isinstance(self.structure, NBTStructure)
            and self.structure.tag_type == "any"
        ):
            return other_tag

        for tag_name in self.structure.keys():
            template_tag = self.structure[tag_name]
            nbt_tag = other_tag.get(tag_name)

            if nbt_tag:
                if template_tag.tag_type == "any":
                    continue

                other_tag[tag_name] = template_tag.apply_to(nbt_tag)
            elif template_tag.default_value is not None:
                other_tag[tag_name] = template_tag.create_entry_from_template()

        return other_tag

    def create_entry_from_template(self, initial_value=None) -> NBTCompoundEntry:
        if initial_value is None:
            return NBTCompoundEntry(self.default_value)
        return NBTCompoundEntry(initial_value)


class NBTEntry:
    """
    Generic container used to represent a NBT entry that can have a template applied to it
    """

    __slots__ = ("tag_type", "value")

    def __init__(self, tag_type: str, value: Any):
        self.tag_type = tag_type
        self.value = value

    def __eq__(self, other: NBTEntry) -> bool:
        return self.tag_type == other.tag_type and self.value == other.value

    def __ne__(self, other: NBTEntry) -> bool:
        return not self == other


class NBTListEntry(UserList):
    """
    Container to represent a NBT List entry
    """

    tag_type = "list"

    @property
    def value(self):
        return self.data


class NBTCompoundEntry(UserDict):
    """
    Container to represent a NBT Compound entry
    """

    tag_type = "compound"

    @property
    def value(self):
        return self.data


class TemplateLoader:
    """
    Handles the loading of NBT template json files
    """

    suffix = "_nbt.json"

    def __init__(self, template_dir: str):
        self._template_dir = template_dir

        template_iter = iglob(
            join(self._template_dir, "**", f"*{self.suffix}"), recursive=True
        )

        self._templates = {basename(p)[: -len(self.suffix)]: p for p in template_iter}

    @property
    def template_dir(self) -> str:
        return self._template_dir

    @property
    def templates(self) -> Dict[str, str]:
        return self._templates

    def _tag_hook(self, json_object: dict) -> Union[dict, NBTStruct]:
        if "tag_type" not in json_object:
            return json_object

        tag_type: str = json_object["tag_type"]

        if tag_type.startswith("<") and tag_type.endswith(">"):
            return self.load_template(tag_type[1:-1])

        if tag_type == "compound":
            structure = json_object["structure"]
            if isinstance(structure, dict):
                return NBTCompoundStructure(
                    structure, default_value=json_object.get("default")
                )
            return NBTCompoundStructure(NBTStructure("any"))

        if tag_type == "list":
            return NBTListStructure(
                json_object["schema"], default_value=json_object.get("default")
            )

        return NBTStructure(tag_type, default_value=json_object.get("default"))

    def load_template(self, template_name: str) -> NBTCompoundStructure:
        """
        Loads the specified named NBT template file

        :param template_name: The (normalized) name of the template file (IE: "creeper" for "creeper.json")
        :return: The NBT template structure from the specified template file
        """
        if template_name not in self._templates:
            raise FileNotFoundError()

        template_path = self._templates[template_name]

        fp = open(template_path)
        result = json.load(fp, object_hook=self._tag_hook)
        fp.close()

        get_func = result.get if isinstance(result, dict) else result.structure.get
        update_func = (
            result.update if isinstance(result, dict) else result.structure.update
        )

        if "extends" in get_func("<metadata>", {}):
            parents: List[str] = result["<metadata>"]["extends"]
            if isinstance(parents, str):
                parents = [parents]

            for parent in parents:
                update_func(self.load_template(parent).structure)
            del result["<metadata>"]

        return NBTCompoundStructure(result)


if __name__ == "__main__":
    struct1 = NBTStructure("string")
    entry1 = NBTEntry("int", "test")

    print(struct1.apply_to(entry1))

    struct2 = NBTCompoundStructure(
        {
            "id": NBTStructure(
                "string", default_value=NBTEntry("string", "minecraft:unknown_item")
            ),
            "Count": NBTStructure("byte", default_value=NBTEntry("byte", 1)),
            "Slot": NBTStructure("byte", default_value=NBTEntry("byte", 0)),
            "tag": NBTCompoundStructure(
                {"Damage": NBTStructure("int"), "Unbreakable": NBTStructure("byte")}
            ),
        }
    )
    entry2 = NBTCompoundEntry()
    print(struct2.apply_to(entry2))

    print("=" * 16)

    tl = TemplateLoader(
        "C:\\Users\\gotharbg\\Documents\\Python Projects\\Amulet-Map-Editor\\src\\version_definitions\\java_1_13"
    )
    item_template = tl.load_template("item")
    print(item_template)
    print(item_template.apply_to(entry2))
