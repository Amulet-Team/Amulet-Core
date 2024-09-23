from __future__ import annotations
from typing import overload, Literal, TypeVar
from dataclasses import dataclass, field
from copy import deepcopy
from enum import Enum

# section_string is a raw string containing section (§) codes
# raw text is a stringified json object


@dataclass(frozen=True)
class Colour:
    r: int
    g: int
    b: int

    def __post_init__(self) -> None:
        assert 0 <= self.r <= 255
        assert 0 <= self.g <= 255
        assert 0 <= self.b <= 255


class Formatting(Enum):
    Reset = "reset"
    Bold = "bold"
    Italic = "italic"
    Underlined = "underlined"
    Strikethrough = "strikethrough"
    Obfuscated = "obfuscated"


class JavaNameHexColourFactory:
    Colour2Name = {
        Colour(0x00, 0x00, 0x00): "black",
        Colour(0x00, 0x00, 0xAA): "dark_blue",
        Colour(0x00, 0xAA, 0x00): "dark_green",
        Colour(0x00, 0xAA, 0xAA): "dark_aqua",
        Colour(0xAA, 0x00, 0x00): "dark_red",
        Colour(0xAA, 0x00, 0xAA): "dark_purple",
        Colour(0xFF, 0xAA, 0x00): "gold",
        Colour(0xAA, 0xAA, 0xAA): "gray",
        Colour(0x55, 0x55, 0x55): "dark_gray",
        Colour(0x55, 0x55, 0xFF): "blue",
        Colour(0x55, 0xFF, 0x55): "green",
        Colour(0x55, 0xFF, 0xFF): "aqua",
        Colour(0xFF, 0x55, 0x55): "red",
        Colour(0xFF, 0x55, 0xFF): "light_purple",
        Colour(0xFF, 0xFF, 0x55): "yellow",
        Colour(0xFF, 0xFF, 0xFF): "white",
    }
    Name2Colour = {name: colour for colour, name in Colour2Name.items()}

    @classmethod
    def read(cls, raw_colour: str) -> Colour:
        if raw_colour in cls.Name2Colour:
            return cls.Name2Colour[raw_colour]
        elif raw_colour.startswith("#"):
            num = int(raw_colour[1:], 16)
            r = (num >> 16) & 0xFF
            g = (num >> 8) & 0xFF
            b = num & 0xFF
            return Colour(r, g, b)
        raise ValueError(raw_colour)

    @classmethod
    def write(cls, colour: Colour) -> str:
        if colour in cls.Colour2Name:
            return cls.Colour2Name[colour]
        else:
            return f"#{colour.r % 256:02X}{colour.g % 256:02X}{colour.b % 256:02X}"


class AbstractSectionParser:
    """A class to serialise and deserialise section codes"""

    Code2Colour: dict[str, Colour] = {}
    Colour2Code: dict[Colour, str] = {}
    Format2Code: dict[Formatting, str]
    Code2Format: dict[str, Formatting]

    @classmethod
    def read(cls, section_code: str) -> Colour | Formatting | None:
        return cls.Code2Colour.get(section_code) or cls.Code2Format.get(section_code)

    @classmethod
    def write(cls, value: Colour | Formatting) -> str | None:
        if isinstance(value, Colour):
            if value not in cls.Colour2Code:
                # Find the closest colour to this colour
                # This is a dumb city block search
                value = min(
                    cls.Colour2Code,
                    key=lambda col: abs(value.r - col.r)
                    + abs(value.g - col.g)
                    + abs(value.b - col.b),
                )
            return cls.Colour2Code[value]
        elif isinstance(value, Formatting) and value in cls.Format2Code:
            return cls.Format2Code[value]
        return None


class JavaSectionParser(AbstractSectionParser):
    Colour2Code = {
        Colour(0x00, 0x00, 0x00): "0",
        Colour(0x00, 0x00, 0xAA): "1",
        Colour(0x00, 0xAA, 0x00): "2",
        Colour(0x00, 0xAA, 0xAA): "3",
        Colour(0xAA, 0x00, 0x00): "4",
        Colour(0xAA, 0x00, 0xAA): "5",
        Colour(0xFF, 0xAA, 0x00): "6",
        Colour(0xAA, 0xAA, 0xAA): "7",
        Colour(0x55, 0x55, 0x55): "8",
        Colour(0x55, 0x55, 0xFF): "9",
        Colour(0x55, 0xFF, 0x55): "a",
        Colour(0x55, 0xFF, 0xFF): "b",
        Colour(0xFF, 0x55, 0x55): "c",
        Colour(0xFF, 0x55, 0xFF): "d",
        Colour(0xFF, 0xFF, 0x55): "e",
        Colour(0xFF, 0xFF, 0xFF): "f",
    }
    Code2Colour = {name: colour for colour, name in Colour2Code.items()}
    Format2Code = {
        Formatting.Reset: "r",
        Formatting.Bold: "l",
        Formatting.Strikethrough: "m",
        Formatting.Underlined: "n",
        Formatting.Italic: "o",
        Formatting.Obfuscated: "k",
    }
    Code2Format = {c: f for f, c in Format2Code.items()}


class BedrockSectionParser(AbstractSectionParser):
    Colour2Code = {
        Colour(0x00, 0x00, 0x00): "0",
        Colour(0x00, 0x00, 0xAA): "1",
        Colour(0x00, 0xAA, 0x00): "2",
        Colour(0x00, 0xAA, 0xAA): "3",
        Colour(0xAA, 0x00, 0x00): "4",
        Colour(0xAA, 0x00, 0xAA): "5",
        Colour(0xFF, 0xAA, 0x00): "6",
        Colour(0xAA, 0xAA, 0xAA): "7",
        Colour(0x55, 0x55, 0x55): "8",
        Colour(0x55, 0x55, 0xFF): "9",
        Colour(0x55, 0xFF, 0x55): "a",
        Colour(0x55, 0xFF, 0xFF): "b",
        Colour(0xFF, 0x55, 0x55): "c",
        Colour(0xFF, 0x55, 0xFF): "d",
        Colour(0xFF, 0xFF, 0x55): "e",
        Colour(0xFF, 0xFF, 0xFF): "f",
    }
    Code2Colour = {name: colour for colour, name in Colour2Code.items()}
    Format2Code = {
        Formatting.Reset: "r",
        Formatting.Bold: "l",
        Formatting.Italic: "o",
        Formatting.Obfuscated: "k",
    }
    Code2Format = {c: f for f, c in Format2Code.items()}


class ExtendedBedrockSectionParser(AbstractSectionParser):
    Colour2Code = {
        Colour(0x00, 0x00, 0x00): "0",
        Colour(0x00, 0x00, 0xAA): "1",
        Colour(0x00, 0xAA, 0x00): "2",
        Colour(0x00, 0xAA, 0xAA): "3",
        Colour(0xAA, 0x00, 0x00): "4",
        Colour(0xAA, 0x00, 0xAA): "5",
        Colour(0xFF, 0xAA, 0x00): "6",
        Colour(0xAA, 0xAA, 0xAA): "7",
        Colour(0x55, 0x55, 0x55): "8",
        Colour(0x55, 0x55, 0xFF): "9",
        Colour(0x55, 0xFF, 0x55): "a",
        Colour(0x55, 0xFF, 0xFF): "b",
        Colour(0xFF, 0x55, 0x55): "c",
        Colour(0xFF, 0x55, 0xFF): "d",
        Colour(0xFF, 0xFF, 0x55): "e",
        Colour(0xFF, 0xFF, 0xFF): "f",
        Colour(0xDD, 0xD6, 0x05): "g",
        Colour(0xE3, 0xD4, 0xD1): "h",
        Colour(0xCE, 0xCA, 0xCA): "i",
        Colour(0x44, 0x3A, 0x3B): "j",
        Colour(0x97, 0x16, 0x07): "m",
        Colour(0xB4, 0x68, 0x4D): "n",
        Colour(0xDE, 0xB1, 0x2D): "p",
        Colour(0x47, 0xA0, 0x36): "q",
        Colour(0x2C, 0xBA, 0xA8): "s",
        Colour(0x21, 0x49, 0x7B): "t",
        Colour(0x9A, 0x5C, 0xC6): "u",
    }
    Code2Colour = {name: colour for colour, name in Colour2Code.items()}
    Format2Code = {
        Formatting.Reset: "r",
        Formatting.Bold: "l",
        Formatting.Italic: "o",
        Formatting.Obfuscated: "k",
    }
    Code2Format = {c: f for f, c in Format2Code.items()}


@dataclass
class RawTextFormatting:
    colour: Colour | None = None
    bold: bool | None = None
    italic: bool | None = None
    underlined: bool | None = None
    strikethrough: bool | None = None
    obfuscated: bool | None = None


T = TypeVar("T")


@dataclass
class RawTextComponent:
    """
    This class supports the core subset of the full raw text specification.
    This is not an attempt to support the full specification.
    """

    text: str = ""
    formatting: RawTextFormatting = field(default_factory=RawTextFormatting)
    children: list[RawTextComponent] = field(default_factory=list)

    @classmethod
    def from_java_raw_text(
        cls, obj: str | bool | float | list | dict
    ) -> RawTextComponent:
        """
        Parse a raw JSON text object and unpack it into this class.
        Note that the input is not a raw JSON string but the result from json.loads
        """
        if isinstance(obj, str):
            return cls.from_java_raw_text({"text": obj})
        elif isinstance(obj, bool):
            return cls.from_java_raw_text("true" if obj else "false")
        elif isinstance(obj, float):
            return cls.from_java_raw_text(str(obj))
        elif isinstance(obj, list):
            if obj:
                self = cls.from_java_raw_text(obj[0])
                for el in obj[1:]:
                    self.children.append(cls.from_java_raw_text(el))
                return self
            else:
                return cls.from_java_raw_text("")
        elif isinstance(obj, dict):
            text = obj.pop("text", "")
            if isinstance(text, bool):
                text = "true" if text else "false"
            else:
                text = str(text)

            extra: list = obj.pop("extra", None)
            children: list[RawTextComponent] = (
                [cls.from_java_raw_text(child) for child in extra]
                if isinstance(extra, list)
                else []
            )

            def get_bool(key: str) -> bool | None:
                val = obj.get(key)
                if isinstance(val, bool):
                    return val
                return None

            bold = get_bool("bold")
            italic = get_bool("italic")
            underlined = get_bool("underlined")
            strikethrough = get_bool("strikethrough")
            obfuscated = get_bool("obfuscated")

            colour_text = obj.get("color")
            if isinstance(colour_text, str):
                colour = JavaNameHexColourFactory.read(colour_text)
            else:
                colour = None

            return cls(
                text,
                RawTextFormatting(
                    colour,
                    bold,
                    italic,
                    underlined,
                    strikethrough,
                    obfuscated,
                ),
                children,
            )
        else:
            raise TypeError

    def to_java_raw_text(self) -> str | dict:
        component: dict[str, list | str | bool] = {"text": self.text}
        if self.children:
            component["extra"] = [child.to_java_raw_text() for child in self.children]
        if self.formatting.colour is not None:
            component["color"] = JavaNameHexColourFactory.write(self.formatting.colour)
        if self.formatting.bold is not None:
            component["bold"] = self.formatting.bold
        if self.formatting.italic is not None:
            component["italic"] = self.formatting.italic
        if self.formatting.underlined is not None:
            component["underlined"] = self.formatting.underlined
        if self.formatting.strikethrough is not None:
            component["strikethrough"] = self.formatting.strikethrough
        if self.formatting.obfuscated is not None:
            component["obfuscated"] = self.formatting.obfuscated
        if component.keys() == {"text"}:
            return self.text
        else:
            return component

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

    @classmethod
    def from_section_text(
        cls,
        section_text: str,
        section_parser: type[AbstractSectionParser],
        split_newline: bool = False,
    ) -> RawTextComponent | list[RawTextComponent]:
        """Parse a section string and convert it to raw JSON text format."""
        # Completed lines
        lines: list[RawTextComponent] = []
        # Components that make up this line
        components: list[RawTextComponent] = []

        # The formatting found so far in the line
        formatting = RawTextFormatting()

        # The character index in the string
        index = 0
        max_index = len(section_text)

        # The index of the next section character and newline.
        # If not found, these equal the length of the string
        next_section_index = section_text.find("§", index) % (max_index + 1)
        next_newline_index = (
            section_text.find("\n", index) % (max_index + 1)
            if split_newline
            else max_index
        )

        def append_section(text: str) -> None:
            if text:
                components.append(cls(text, deepcopy(formatting)))

        def append_line() -> None:
            # Push all components to a new line
            lines.append(cls(children=components.copy()))
            components.clear()

        while True:
            if next_section_index < next_newline_index:
                # section char first

                if next_section_index > index:
                    append_section(section_text[index:next_section_index])

                index = next_section_index + 1
                section_code = section_text[index : index + 1]
                value = section_parser.read(section_code)
                if isinstance(value, Formatting):
                    if value is Formatting.Obfuscated:  # obfuscated
                        formatting.obfuscated = True
                        index += 1
                    elif value is Formatting.Bold:  # bold
                        formatting.bold = True
                        index += 1
                    elif value is Formatting.Strikethrough:  # strikethrough
                        formatting.strikethrough = True
                        index += 1
                    elif value is Formatting.Underlined:  # underlined
                        formatting.underlined = True
                        index += 1
                    elif value is Formatting.Italic:  # italic
                        formatting.italic = True
                        index += 1
                    elif value is Formatting.Reset:  # reset
                        formatting.obfuscated = False
                        formatting.bold = False
                        formatting.strikethrough = False
                        formatting.underlined = False
                        formatting.italic = False
                        formatting.colour = None
                        index += 1
                elif isinstance(value, Colour):
                    formatting.colour = value
                    index += 1

                next_section_index = section_text.find("§", index) % (max_index + 1)

            elif next_newline_index == max_index:
                # No more in the string
                append_section(section_text[index:])
                append_line()
                break

            elif split_newline:
                # newline first

                append_section(section_text[index:next_newline_index])
                append_line()

                index = next_newline_index + 1
                next_newline_index = section_text.find("\n", index) % (max_index + 1)
            else:
                raise RuntimeError

        def compact(src: RawTextComponent) -> RawTextComponent:
            if len(src.children) == 1:
                # Don't need the parent node
                return src.children[0]
            return src

        if split_newline:
            return list(map(compact, lines))
        else:
            return compact(lines[0])

    def to_section_text(self, section_parser: type[AbstractSectionParser]) -> str:
        """
        Convert the raw text object to a section text string
        :param section_parser: The colour palette to use.
        :return: The section text.
        """

        text: list[str] = []

        current_formatting = RawTextFormatting()

        reset_code = section_parser.write(Formatting.Reset)
        bold_code = section_parser.write(Formatting.Bold)
        italic_code = section_parser.write(Formatting.Italic)
        underlined_code = section_parser.write(Formatting.Underlined)
        strikethrough_code = section_parser.write(Formatting.Strikethrough)
        obfuscated_code = section_parser.write(Formatting.Obfuscated)

        def merge_formatting(
            a: RawTextFormatting, b: RawTextFormatting
        ) -> RawTextFormatting:
            # Merge b into a
            return RawTextFormatting(
                a.colour if b.colour is None else b.colour,
                a.bold if b.bold is None else b.bold,
                a.italic if b.italic is None else b.italic,
                a.underlined if b.underlined is None else b.underlined,
                a.strikethrough if b.strikethrough is None else b.strikethrough,
                a.obfuscated if b.obfuscated is None else b.obfuscated,
            )

        def to_section_text(
            section: RawTextComponent, parent_formatting: RawTextFormatting
        ) -> None:
            desired_formatting = merge_formatting(parent_formatting, section.formatting)

            if section.text:
                if (
                    (
                        current_formatting.colour is not None
                        and desired_formatting.colour is None
                    )
                    or (current_formatting.bold and not desired_formatting.bold)
                    or (current_formatting.italic and not desired_formatting.italic)
                    or (
                        current_formatting.underlined
                        and not desired_formatting.underlined
                    )
                    or (
                        current_formatting.strikethrough
                        and not desired_formatting.strikethrough
                    )
                    or (
                        current_formatting.obfuscated
                        and not desired_formatting.obfuscated
                    )
                ):
                    # A property has been unset. Reset the formatting and apply everything again
                    if reset_code is not None:
                        text.append(f"§{reset_code}")
                    current_formatting.colour = None
                    current_formatting.bold = False
                    current_formatting.italic = False
                    current_formatting.underlined = False
                    current_formatting.strikethrough = False
                    current_formatting.obfuscated = False

                # If the formatting has been set and the original formatting is not set
                if desired_formatting.bold and not current_formatting.bold:
                    if bold_code is not None:
                        text.append(f"§{bold_code}")
                    current_formatting.bold = True
                if desired_formatting.italic and not current_formatting.italic:
                    if italic_code is not None:
                        text.append(f"§{italic_code}")
                    current_formatting.italic = True
                if desired_formatting.underlined and not current_formatting.underlined:
                    if underlined_code is not None:
                        text.append(f"§{underlined_code}")
                    current_formatting.underlined = True
                if (
                    desired_formatting.strikethrough
                    and not current_formatting.strikethrough
                ):
                    if strikethrough_code is not None:
                        text.append(f"§{strikethrough_code}")
                    current_formatting.strikethrough = True
                if desired_formatting.obfuscated and not current_formatting.obfuscated:
                    if obfuscated_code is not None:
                        text.append(f"§{obfuscated_code}")
                    current_formatting.obfuscated = True
                if (
                    desired_formatting.colour is not None
                    and desired_formatting.colour != current_formatting.colour
                ):
                    code = section_parser.write(desired_formatting.colour)
                    assert code is not None
                    text.append("§" + code)
                    current_formatting.colour = desired_formatting.colour

                text.append(section.text)

            for child in section.children:
                to_section_text(child, desired_formatting)

        to_section_text(self, RawTextFormatting())
        return "".join(text)
