from dataclasses import dataclass
from enum import Enum
from typing import Literal, TypeVar, overload

from _typeshed import Incomplete

@dataclass(frozen=True)
class Colour:
    r: int
    g: int
    b: int
    def __post_init__(self) -> None: ...
    def __init__(self, r, g, b) -> None: ...

class Formatting(Enum):
    Reset: str
    Bold: str
    Italic: str
    Underlined: str
    Strikethrough: str
    Obfuscated: str

class JavaNameHexColourFactory:
    Colour2Name: Incomplete
    Name2Colour: Incomplete
    @classmethod
    def read(cls, raw_colour: str) -> Colour: ...
    @classmethod
    def write(cls, colour: Colour) -> str: ...

class AbstractSectionParser:
    """A class to serialise and deserialise section codes"""

    Code2Colour: dict[str, Colour]
    Colour2Code: dict[Colour, str]
    Format2Code: dict[Formatting, str]
    Code2Format: dict[str, Formatting]
    @classmethod
    def read(cls, section_code: str) -> Colour | Formatting | None: ...
    @classmethod
    def write(cls, value: Colour | Formatting) -> str | None: ...

class JavaSectionParser(AbstractSectionParser):
    Colour2Code: Incomplete
    Code2Colour: Incomplete
    Format2Code: Incomplete
    Code2Format: Incomplete

class BedrockSectionParser(AbstractSectionParser):
    Colour2Code: Incomplete
    Code2Colour: Incomplete
    Format2Code: Incomplete
    Code2Format: Incomplete

class ExtendedBedrockSectionParser(AbstractSectionParser):
    Colour2Code: Incomplete
    Code2Colour: Incomplete
    Format2Code: Incomplete
    Code2Format: Incomplete

@dataclass
class RawTextFormatting:
    colour: Colour | None = ...
    bold: bool | None = ...
    italic: bool | None = ...
    underlined: bool | None = ...
    strikethrough: bool | None = ...
    obfuscated: bool | None = ...
    def __init__(
        self,
        colour=...,
        bold=...,
        italic=...,
        underlined=...,
        strikethrough=...,
        obfuscated=...,
    ) -> None: ...

T = TypeVar("T")

@dataclass
class RawTextComponent:
    """
    This class supports the core subset of the full raw text specification.
    This is not an attempt to support the full specification.
    """

    text: str = ...
    formatting: RawTextFormatting = ...
    children: list[RawTextComponent] = ...
    @classmethod
    def from_java_raw_text(
        cls, obj: str | bool | float | list | dict
    ) -> RawTextComponent:
        """
        Parse a raw JSON text object and unpack it into this class.
        Note that the input is not a raw JSON string but the result from json.loads
        """

    def to_java_raw_text(self) -> str | dict: ...
    @overload
    @classmethod
    def from_section_text(
        cls, section_text: str, section_parser: type[AbstractSectionParser]
    ) -> RawTextComponent: ...
    @overload
    @classmethod
    def from_section_text(
        cls,
        section_text: str,
        section_parser: type[AbstractSectionParser],
        split_newline: Literal[False],
    ) -> RawTextComponent: ...
    @overload
    @classmethod
    def from_section_text(
        cls,
        section_text: str,
        section_parser: type[AbstractSectionParser],
        split_newline: Literal[True],
    ) -> list[RawTextComponent]: ...
    def to_section_text(self, section_parser: type[AbstractSectionParser]) -> str:
        """
        Convert the raw text object to a section text string
        :param section_parser: The colour palette to use.
        :return: The section text.
        """

    def __init__(self, text=..., formatting=..., children=...) -> None: ...
