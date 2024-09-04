from __future__ import annotations
from amulet.utils.call_spec._call_spec import AbstractArg
from amulet.utils.call_spec._call_spec import AbstractHashableArg
from amulet.utils.call_spec._call_spec import BoolArg
from amulet.utils.call_spec._call_spec import BytesArg
from amulet.utils.call_spec._call_spec import CallSpec
from amulet.utils.call_spec._call_spec import CallableArg
from amulet.utils.call_spec._call_spec import ConstantArg
from amulet.utils.call_spec._call_spec import DictArg
from amulet.utils.call_spec._call_spec import DirectoryPathArg
from amulet.utils.call_spec._call_spec import FilePathArg
from amulet.utils.call_spec._call_spec import FloatArg
from amulet.utils.call_spec._call_spec import HashableCallableArg
from amulet.utils.call_spec._call_spec import HashableTupleArg
from amulet.utils.call_spec._call_spec import HashableUnionArg
from amulet.utils.call_spec._call_spec import IntArg
from amulet.utils.call_spec._call_spec import PositionalArgs
from amulet.utils.call_spec._call_spec import SequenceArg
from amulet.utils.call_spec._call_spec import StringArg
from amulet.utils.call_spec._call_spec import TupleArg
from amulet.utils.call_spec._call_spec import UnionArg
from amulet.utils.call_spec._call_spec import callable_spec
from amulet.utils.call_spec._call_spec import method_spec
from . import _call_spec

__all__ = [
    "AbstractArg",
    "AbstractHashableArg",
    "BoolArg",
    "BytesArg",
    "CallSpec",
    "CallableArg",
    "ConstantArg",
    "DictArg",
    "DirectoryPathArg",
    "FilePathArg",
    "FloatArg",
    "HashableCallableArg",
    "HashableTupleArg",
    "HashableUnionArg",
    "IntArg",
    "PositionalArgs",
    "SequenceArg",
    "StringArg",
    "TupleArg",
    "UnionArg",
    "callable_spec",
    "method_spec",
]
