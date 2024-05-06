import json
from typing import Any
from uuid import uuid4

from amulet_nbt import StringTag, CompoundTag, ListTag
from ._text import RawTextComponent, ExtendedBedrockSectionParser
from .._state import SrcData, StateData, DstData


BedrockFrontText = str(uuid4())
BedrockBackText = str(uuid4())


def _to_universal(
    src: CompoundTag,
    src_key: str,
    dst: DstData,
    universal_native_key: str,
    universal_key: str,
) -> None:
    text = src.get_string(src_key)
    if not isinstance(text, StringTag):
        return

    dst.nbt.append(
        (
            "",
            CompoundTag,
            (("utags", CompoundTag),),
            universal_native_key,
            text,
        )
    )

    if text:
        for line_num, component in enumerate(
            RawTextComponent.from_section_text(
                text.py_str, ExtendedBedrockSectionParser, True
            )
        ):
            dst.nbt.append(
                (
                    "",
                    CompoundTag,
                    (
                        ("utags", CompoundTag),
                        (universal_key, CompoundTag),
                        ("messages", ListTag),
                    ),
                    line_num,
                    StringTag(json.dumps(component.to_java_raw_text())),
                )
            )


def _from_universal(
    utags: CompoundTag,
    universal_native_key: str,
    universal_key: str,
    dst: DstData,
    native_key: str,
) -> None:
    native_text = utags.get_string(universal_native_key)
    text: StringTag
    if isinstance(native_text, StringTag):
        text = native_text
    else:
        messages = utags.get_compound(universal_key, CompoundTag()).get_list(
            "messages", ListTag()
        )

        lines: list[Any] = [""]
        if messages.element_class is StringTag:
            for line_num in range(4):
                if line_num >= len(messages):
                    lines.append("")
                else:
                    try:
                        lines.append(json.loads(messages.get_string(line_num).py_str))
                    except:
                        lines.append("")
        else:
            lines.extend([""] * 4)

        text = StringTag(
            RawTextComponent.from_java_raw_text(lines).to_section_text(
                ExtendedBedrockSectionParser
            )
        )

    dst.nbt.append(
        (
            "",
            CompoundTag,
            (),
            native_key,
            text,
        )
    )


def to_universal(src: SrcData, state: StateData, dst: DstData) -> None:
    nbt = src.nbt
    if nbt is None:
        return

    tag = nbt.tag
    if not isinstance(tag, CompoundTag):
        return

    _to_universal(tag, "Text", dst, BedrockFrontText, "front_text")


def from_universal(src: SrcData, state: StateData, dst: DstData) -> None:
    nbt = src.nbt
    if nbt is not None:
        tag = nbt.tag
        if isinstance(tag, CompoundTag):
            utags = tag.get_compound("utags")
            if isinstance(utags, CompoundTag):
                _from_universal(utags, BedrockFrontText, "front_text", dst, "Text")
                return

    dst.nbt.append(("", CompoundTag, (), "Text", StringTag()))


def to_universal_120(src: SrcData, state: StateData, dst: DstData) -> None:
    nbt = src.nbt
    if nbt is None:
        return

    tag = nbt.tag
    if not isinstance(tag, CompoundTag):
        return

    _to_universal(tag, "FrontText", dst, BedrockFrontText, "front_text")
    _to_universal(tag, "BackText", dst, BedrockBackText, "back_text")


def from_universal_120(src: SrcData, state: StateData, dst: DstData) -> None:
    nbt = src.nbt
    if nbt is not None:
        tag = nbt.tag
        if isinstance(tag, CompoundTag):
            utags = tag.get_compound("utags")
            if isinstance(utags, CompoundTag):
                _from_universal(utags, BedrockFrontText, "front_text", dst, "FrontText")
                _from_universal(utags, BedrockBackText, "back_text", dst, "BackText")
                return

    dst.nbt.append(("", CompoundTag, (), "FrontText", StringTag()))
    dst.nbt.append(("", CompoundTag, (), "BackText", StringTag()))
