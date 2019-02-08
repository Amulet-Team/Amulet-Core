from __future__ import annotations

from typing import Union, List
from typing import Any, Dict
import json
from collections import UserDict, UserList
from glob import iglob
from os.path import join, basename
from functools import partial

from nbt import nbt


class NBTStruct:
    """
    Base class implemented by all NBT structure classes
    """

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
        """
        The template ``NBTStructure`` that will be applied to each item in a ``NBTListEntry`` object

        :return: The template ``NBTStructure``
        """
        return self._schema

    @property
    def default_value(self) -> Any:
        """
        The default value for the NBT structure

        :return: The value that will be inserted if the given NBT structure is required, ``None`` if not required
        """
        return self._default_value

    def create_entry_from_template(self, initial_value=None) -> NBTListEntry:
        """
        See :meth:`api.nbt_template.NBTStruct.create_entry_from_template`
        """
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
        """
        The expected structure for a ``NBTCompoundEntry`` that will be applied to each key/value pair item in a
        ``NBTCompoundEntry`` object

        :return: The structure of `NBTStructure` objects mapped to their corresponding keys
        """
        return self._structure

    @property
    def default_value(self) -> Any:
        """
        The default value for the NBT structure

        :return: The value that will be inserted if the given NBT structure is required, ``None`` if not required
        """
        return self._default_value

    def create_entry_from_template(self, initial_value=None) -> NBTCompoundEntry:
        """
        See :meth:`api.nbt_template.NBTStruct.create_entry_from_template`
        """
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

    def __repr__(self):
        return f'NBTEntry("{self.tag_type}", {repr(self.value)})'

    def apply_template(self, template_tag: NBTStructure) -> NBTEntry:
        """
        Applies the supplied ``NBTStructure`` to the current object

        :param template_tag: The ``NBTStructure`` to apply to the current ``NBTEntry`` object
        :return: A new ``NBTEntry`` object with the template applied to it
        """
        if template_tag.tag_type == "any":
            return NBTEntry(self.tag_type, self.value)

        if self.tag_type == template_tag.tag_type:
            return NBTEntry(self.tag_type, self.value)

        return template_tag.create_entry_from_template(self.value)


class NBTListEntry(UserList):
    """
    Container to represent a NBT List entry
    """

    tag_type = "list"

    @property
    def value(self):
        """
        :return: The internal list of the `NBTListEntry` object
        """
        return self.data

    def apply_template(self, template_tag: NBTListStructure) -> NBTListEntry:
        """
        Applies the supplied ``NBTListStructure`` to each item in the current object

        :param template_tag: The ``NBTListStructure`` to apply to the current ``NBTListEntry`` object
        :return: A new ``NBTListEntry`` object with the template applied to it
        """
        if template_tag.schema.tag_type == "any":
            return NBTListEntry(self.data)

        new_tag = NBTListEntry([None for i in range(len(self))])
        for i in range(len(self)):
            new_tag[i] = self[i].apply_template(template_tag.schema)

        return new_tag


class NBTCompoundEntry(UserDict):
    """
    Container to represent a NBT Compound entry
    """

    tag_type = "compound"

    @property
    def value(self):
        """
        :return: The internal dictionary of the ``NBTCompoundEntry`` object
        """
        return self.data

    def apply_template(self, template_tag: NBTCompoundStructure) -> NBTCompoundEntry:
        """
        Applies the supplied ``NBTCompoundStructure`` to each key/value pair in the current object

        :param template_tag: The ``NBTCompoundStructure`` to apply to the current ``NBTCompoundEntry`` object
        :return: A new ``NBTCompoundEntry`` object with the template applied to it
        """
        if (
            isinstance(template_tag.structure, NBTStructure)
            and template_tag.structure.tag_type == "any"
        ):
            return NBTCompoundEntry(self.data)

        new_tag = NBTCompoundEntry(self.data)
        for tag_name in template_tag.structure.keys():
            child_template_tag = template_tag.structure[tag_name]
            nbt_tag = self.get(tag_name)

            if nbt_tag:
                if child_template_tag.tag_type == "any":
                    continue

                new_tag[tag_name] = nbt_tag.apply_template(child_template_tag)
            elif child_template_tag.default_value is not None:
                new_tag[tag_name] = child_template_tag.create_entry_from_template()

        return new_tag


class TemplateLoader:
    """
    Handles the loading of NBT template json files
    """

    suffix = "_nbt.json"

    def __init__(self, template_dir: str):
        self._template_dir = template_dir
        self._templates = {}

        self.reload()

    @property
    def template_dir(self) -> str:
        """
        :return: The path to the directory that the current ``TemplateLoader`` will search template files for
        """
        return self._template_dir

    @property
    def templates(self) -> Dict[str, str]:
        """
        Returns the mapping of the normalized Entity names to the full path of the corresponding template file

        :return: The dictionary mapping for normalized Entity names and the path of their template files
        """
        return self._templates

    def reload(self) -> None:
        """
        Re-searches :attr:`api.nbt_template.TemplateLoader.template_dir` and re-adds all existing templates along with
        any new template files
        """
        template_iter = iglob(
            join(self._template_dir, "**", f"*{self.suffix}"), recursive=True
        )

        self._templates = {basename(p)[: -len(self.suffix)]: p for p in template_iter}

    @staticmethod
    def _remove_comments(json_object: dict) -> dict:
        comments = []
        for key in json_object.keys():
            if key.startswith("__comment"):
                comments.append(key)
        for comment in comments:
            del json_object[comment]

        return json_object

    def _tag_hook(self, json_object: dict) -> Union[dict, NBTStruct]:
        json_object = self._remove_comments(json_object)
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
            raise FileNotFoundError(
                join(self.template_dir, "*", f"{template_name}_nbt.json")
            )

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


_tag_to_entry_map = {
    nbt.TAG_BYTE: partial(NBTEntry, "byte"),
    nbt.TAG_SHORT: partial(NBTEntry, "short"),
    nbt.TAG_INT: partial(NBTEntry, "int"),
    nbt.TAG_LONG: partial(NBTEntry, "long"),
    nbt.TAG_FLOAT: partial(NBTEntry, "float"),
    nbt.TAG_DOUBLE: partial(NBTEntry, "double"),
    nbt.TAG_BYTE_ARRAY: partial(NBTEntry, "byte_array"),
    nbt.TAG_STRING: partial(NBTEntry, "string"),
    nbt.TAG_INT_ARRAY: partial(NBTEntry, "int_array"),
    nbt.TAG_LONG_ARRAY: partial(NBTEntry, "long_array"),
}

_entry_to_tag_map = {
    "byte": nbt.TAG_Byte,
    "short": nbt.TAG_Short,
    "int": nbt.TAG_Int,
    "long": nbt.TAG_Long,
    "float": nbt.TAG_Float,
    "double": nbt.TAG_Double,
    "byte_array": nbt.TAG_Byte_Array,
    "string": nbt.TAG_String,
    "int_array": nbt.TAG_Int_Array,
    "long_array": nbt.TAG_Long_Array,
}


def create_entry_from_nbt(tag_root: nbt.TAG) -> NBTCompoundEntry:
    entry = None
    tag_id = tag_root.id
    if tag_id in _tag_to_entry_map:
        entry = _tag_to_entry_map[tag_id](tag_root.value)
    elif tag_id == nbt.TAG_COMPOUND:
        tag_root: nbt.TAG_Compound
        entry = NBTCompoundEntry()
        for name, tag in tag_root.iteritems():
            entry[name] = create_entry_from_nbt(tag)
    elif tag_id == nbt.TAG_LIST:
        tag_root: nbt.TAG_List
        entry = NBTListEntry()
        for tag in tag_root:
            entry.append(tag.value)

        # Not sure if needed, but our current NBT library doesn't properly
        # populate it's internal list used by it's __iter__ if you construct
        # the object with the 'value' keyword argument, this is a workaround
        # - Podshot 2019.2.8
        if len(entry) == 0:
            for tag in tag_root.value:
                entry.append(create_entry_from_nbt(tag))
    return entry


def create_nbt_from_entry(
    entry: Union[NBTEntry, NBTListEntry, NBTCompoundEntry]
) -> nbt.TAG:
    tag = None
    entry_type = entry.tag_type
    if entry_type in _entry_to_tag_map:
        tag = _entry_to_tag_map[entry_type](value=entry.value)
    elif isinstance(entry, NBTCompoundEntry):
        tag = nbt.TAG_Compound()
        for name, child_entry in entry.items():
            tag[name] = create_nbt_from_entry(child_entry)
    elif isinstance(entry, NBTListEntry):
        tag = nbt.TAG_List()
        for child_entry in entry:
            tag.append(create_nbt_from_entry(child_entry))
    return tag


if __name__ == "__main__":
    print(create_entry_from_nbt(nbt.TAG_Byte(value=4)))

    compound = nbt.TAG_Compound()
    compound["test1"] = nbt.TAG_Int(value=-100)
    compound["test2"] = nbt.TAG_String(value="hello!")

    test1 = create_entry_from_nbt(compound)
    print(test1)
    print(create_nbt_from_entry(test1))
    print("=" * 16)

    test2 = create_entry_from_nbt(
        nbt.TAG_List(
            value=[
                nbt.TAG_String(value="test1"),
                nbt.TAG_String(value="test2"),
                nbt.TAG_String(value="test3"),
            ]
        )
    )
    print(test2)
    print(create_nbt_from_entry(test2))
