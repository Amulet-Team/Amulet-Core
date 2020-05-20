from typing import Any, Union, Generator, Callable, Tuple
from .world_types import Dimension

# Operation types
OperationYieldType = Union[int, float, Tuple[Union[int, float], str]]
OperationReturnType = Union[Generator[OperationYieldType, None, Any], Any]
OperationType = Callable[["World", Dimension, Any], OperationReturnType]
