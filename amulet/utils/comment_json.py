from json import JSONDecodeError, loads as json_loads
from typing import TextIO, Union

"""
Some of the Bedrock json files contain comments which is not valid JSON and the standard json parser
will throw errors. This will first try and use the vanilla json parser and fall back to the slower version if that fails.
"""


JSONValue = Union[str, int, float, bool, None, "JSONDict", "JSONList"]
JSONDict = dict[str, JSONValue]
JSONList = list[JSONValue]


class CommentJSONDecodeError(JSONDecodeError):
    pass


def from_file(path: str) -> JSONValue:
    with open(path) as f:
        return load(f)


def load(obj: TextIO) -> JSONValue:
    return loads(obj.read())


def loads(s: str) -> JSONValue:
    try:
        return json_loads(s)  # type: ignore
    except JSONDecodeError:
        return _loads(s)


def _loads(text: str) -> JSONValue:
    # given a valid MinecraftJSON string will return the values as python objects
    # in this context MinecraftJSON is standard JSON but with comment blocks and
    # line comments that would normally be illegal in standard JSON
    _number = set("0123456789-")
    _float = set("0123456789-.")
    _whitespace = set(" \t\r\n")

    def strip_whitespace(index: int) -> int:
        # skips whitespace characters (<space>, <tab>, <charrage return> and <newline>)
        # as well as block comments and line comments
        while text[index] in _whitespace:
            index += 1
        if text[index] == "/":
            if text[index + 1] == "/":
                index += 2
                while text[index] != "\n":
                    index += 1
                index = strip_whitespace(index)
            elif text[index + 1] == "*":
                index += 2
                while text[index : index + 2] != "*/":
                    index += 1
                    if index + 1 >= len(text):
                        raise JSONDecodeError(
                            "expected */ but reached the end of file", text, index
                        )
                index += 2
                index = strip_whitespace(index)
            else:
                raise JSONDecodeError(f"unexpected / at index {index}", text, index)
        return index

    def parse_json_recursive(index: int = 0) -> tuple[JSONValue, int]:
        index = strip_whitespace(index)
        if text[index] == "{":
            index += 1
            # dictionary
            json_obj = {}
            repeat = True
            while repeat:
                index = strip_whitespace(index)
                # }"
                if text[index] == '"':
                    index += 1
                    key = ""
                    while text[index] != '"':
                        key += text[index]
                        index += 1
                    index += 1

                    index = strip_whitespace(index)

                    if text[index] == ":":
                        index += 1
                    else:
                        raise JSONDecodeError(
                            f"expected : got {text[index]} at index {index}",
                            text,
                            index,
                        )

                    index = strip_whitespace(index)

                    json_obj[key], index = parse_json_recursive(index)

                    index = strip_whitespace(index)

                    if text[index] == ",":
                        index += 1
                    else:
                        repeat = False
                else:
                    repeat = False

            if index >= len(text):
                raise JSONDecodeError("expected } but reached end of file", text, index)
            elif text[index] == "}":
                index += 1
            else:
                raise JSONDecodeError(
                    f"expected }} got {text[index]} at index {index}", text, index
                )
            return json_obj, index

        elif text[index] == "[":
            index += 1
            # list
            json_array = []
            index = strip_whitespace(index)
            repeat = text[index] != "]"
            while repeat:
                val, index = parse_json_recursive(index)
                json_array.append(val)

                index = strip_whitespace(index)

                if text[index] == ",":
                    index += 1
                else:
                    repeat = False
                index = strip_whitespace(index)

            if index >= len(text):
                raise JSONDecodeError("expected ] but reached end of file", text, index)
            elif text[index] == "]":
                index += 1
            else:
                raise JSONDecodeError(
                    f"expected ] got {text[index]} at index {index}", text, index
                )
            return json_array, index

        elif text[index] == '"':
            index += 1
            # string
            json_obj_list = []
            while text[index] != '"':
                json_obj_list.append(text[index])
                index += 1
            index += 1
            return "".join(json_obj_list), index

        elif text[index] in _number:
            # number
            json_obj_list = []
            while text[index] in _float:
                json_obj_list += text[index]
                index += 1
            if "." in json_obj_list:
                return float("".join(json_obj_list)), index
            else:
                return int("".join(json_obj_list)), index

        elif text[index] == "n" and text[index : index + 4] == "null":
            index += 4
            return None, index

        elif text[index] == "t" and text[index : index + 4] == "true":
            index += 4
            return True, index

        elif text[index] == "f" and text[index : index + 5] == "false":
            index += 5
            return False, index
        else:
            raise JSONDecodeError(
                f'unexpected key {text[index]} at {index}. Expected {{, [, ", num, null, true or false',
                text,
                index,
            )

    # call recursive function and pass back python object
    return parse_json_recursive()[0]
