from json import JSONDecodeError
from typing import TextIO

from _typeshed import Incomplete

JSONValue: Incomplete
JSONDict = dict[str, JSONValue]
JSONList = list[JSONValue]

class CommentJSONDecodeError(JSONDecodeError): ...

def from_file(path: str) -> JSONValue: ...
def load(obj: TextIO) -> JSONValue: ...
def loads(s: str) -> JSONValue: ...
