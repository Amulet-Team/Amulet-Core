from uuid import uuid4
import json
from typing import Callable

from amulet_nbt import CompoundTag, StringTag

from .._state import SrcData, StateData, DstData
from ._text import (
    RawTextComponent,
    BedrockSectionParser,
    ExtendedBedrockSectionParser,
    JavaSectionParser,
)


JavaSectionText = str(uuid4())
JavaRawText = str(uuid4())
BedrockSectionText = str(uuid4())
BedrockExtendedSectionText = str(uuid4())


def get_custom_name(src: SrcData, dst: DstData, key: str) -> None:
    nbt = src.nbt
    if nbt is None:
        return

    tag = nbt.tag
    if not isinstance(tag, CompoundTag):
        return

    custom_name = tag.get("CustomName")
    if not isinstance(custom_name, StringTag):
        return

    # Store the raw value so we can non-destructively recover it
    dst.nbt.append(("", CompoundTag, (("utags", CompoundTag),), key, custom_name))


def java_section_to_universal(src: SrcData, state: StateData, dst: DstData) -> None:
    get_custom_name(src, dst, JavaSectionText)


def java_raw_to_universal(src: SrcData, state: StateData, dst: DstData) -> None:
    get_custom_name(src, dst, JavaRawText)


def bedrock_to_universal(src: SrcData, state: StateData, dst: DstData) -> None:
    get_custom_name(src, dst, BedrockSectionText)


def bedrock_extended_to_universal(src: SrcData, state: StateData, dst: DstData) -> None:
    get_custom_name(src, dst, BedrockExtendedSectionText)


def set_custom_name(
    src: SrcData,
    dst: DstData,
    target: str,
    component_to_raw: Callable[[RawTextComponent], StringTag],
) -> None:
    nbt = src.nbt
    if nbt is None:
        return

    tag = nbt.tag
    if not isinstance(tag, CompoundTag):
        return

    utags = tag.get("utags")
    if not isinstance(utags, CompoundTag):
        return

    if isinstance((native_custom_name := utags.get(target)), StringTag):
        custom_name = native_custom_name
    elif isinstance(
        (java_section_custom_name := utags.get(JavaSectionText)), StringTag
    ):
        component = RawTextComponent.from_section_text(
            java_section_custom_name.py_str, JavaSectionParser
        )
        custom_name = component_to_raw(component)
    elif isinstance((java_raw_custom_name := utags.get(JavaRawText)), StringTag):
        try:
            component = RawTextComponent.from_java_raw_text(
                json.loads(java_raw_custom_name.py_str)
            )
        except:
            custom_name = StringTag()
        else:
            custom_name = component_to_raw(component)

    elif isinstance((bedrock_custom_name := utags.get(BedrockSectionText)), StringTag):
        component = RawTextComponent.from_section_text(
            bedrock_custom_name.py_str, BedrockSectionParser
        )
        custom_name = component_to_raw(component)
    elif isinstance(
        (bedrock_extended_custom_name := utags.get(BedrockExtendedSectionText)),
        StringTag,
    ):
        component = RawTextComponent.from_section_text(
            bedrock_extended_custom_name.py_str, ExtendedBedrockSectionParser
        )
        custom_name = component_to_raw(component)
    else:
        custom_name = StringTag()

    dst.nbt.append(
        (
            "",
            CompoundTag,
            (),
            "CustomName",
            custom_name,
        )
    )


def java_section_from_universal(src: SrcData, state: StateData, dst: DstData) -> None:
    def component_to_raw(component: RawTextComponent) -> StringTag:
        return StringTag(component.to_section_text(JavaSectionParser))

    set_custom_name(src, dst, JavaSectionText, component_to_raw)


def java_raw_from_universal(src: SrcData, state: StateData, dst: DstData) -> None:
    def component_to_raw(component: RawTextComponent) -> StringTag:
        return StringTag(json.dumps(component.to_java_raw_text()))

    set_custom_name(src, dst, JavaSectionText, component_to_raw)


def bedrock_from_universal(src: SrcData, state: StateData, dst: DstData) -> None:
    def component_to_raw(component: RawTextComponent) -> StringTag:
        return StringTag(component.to_section_text(BedrockSectionParser))

    set_custom_name(src, dst, BedrockSectionText, component_to_raw)


def bedrock_extended_from_universal(
    src: SrcData, state: StateData, dst: DstData
) -> None:
    def component_to_raw(component: RawTextComponent) -> StringTag:
        return StringTag(component.to_section_text(ExtendedBedrockSectionParser))

    set_custom_name(src, dst, BedrockExtendedSectionText, component_to_raw)
