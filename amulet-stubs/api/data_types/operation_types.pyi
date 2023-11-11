from .world_types import Dimension as Dimension
from _typeshed import Incomplete
from amulet.api.level import BaseLevel as BaseLevel
from typing import Any, Generator, Optional, Tuple, Union

OperationYieldType = Union[int, float, Tuple[Union[int, float], str]]
OperationReturnType = Optional[Union[Generator[OperationYieldType, None, Any], Any]]
OperationType: Incomplete
