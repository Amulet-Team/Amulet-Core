import json
from typing import Any
from uuid import uuid4

from amulet_nbt import StringTag, CompoundTag
from ._text import RawTextComponent, ExtendedBedrockSectionParser
from .._state import SrcData, StateData, DstData


BedrockText = str(uuid4())


def to_universal(src: SrcData, state: StateData, dst: DstData) -> None:
    nbt = src.nbt
    if nbt is None:
        return

    tag = nbt.tag
    if not isinstance(tag, CompoundTag):
        return

    text = tag.get("Text")
    if not isinstance(text, StringTag):
        return

    dst.nbt.append(
        (
            "",
            CompoundTag,
            (("utags", CompoundTag),),
            BedrockText,
            text,
        )
    )

    if text:
        line_num = 1
        for component in RawTextComponent.from_section_text(
            text.py_str, ExtendedBedrockSectionParser, True
        ):
            dst.nbt.append(
                (
                    "",
                    CompoundTag,
                    (("utags", CompoundTag),),
                    f"Text{line_num + 1}",
                    StringTag(json.dumps(component.to_java_raw_text())),
                )
            )
            line_num += 1


def from_universal(src: SrcData, state: StateData, dst: DstData) -> None:
    nbt = src.nbt
    if nbt is not None:
        tag = nbt.tag
        if isinstance(tag, CompoundTag):
            utags = tag.get("utags")
            if isinstance(utags, CompoundTag):
                if isinstance((native_text := utags.get(BedrockText)), StringTag):
                    text = native_text
                else:
                    lines: list[Any] = [""]
                    line_num = 1
                    while True:
                        key = f"Text{line_num}"
                        val = utags.get(key)
                        if isinstance(val, StringTag):
                            try:
                                lines.append(json.loads(val.py_str))
                            except:
                                lines.append("")
                        elif line_num <= 4:
                            lines.append("")
                        else:
                            break
                        line_num += 1

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
                        "Text",
                        text,
                    )
                )
                return
    dst.nbt.append(("", CompoundTag, (), "Text", StringTag()))
