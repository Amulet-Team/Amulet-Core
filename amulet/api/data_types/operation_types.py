from typing import (
    Any,
    Union,
    Generator,
    Callable,
    Tuple,
    TYPE_CHECKING,
    Optional,
    TypeAlias,
)

if TYPE_CHECKING:
    from amulet.api.level import BaseLevel
    from .world_types import Dimension

# Operation types

#: The data type that an operation is able to yield.
OperationYieldType: TypeAlias = Union[int, float, Tuple[Union[int, float], str]]

#: The data type that an operation is able to return.
OperationReturnType: TypeAlias = Optional[
    Union[Generator[OperationYieldType, None, Any], Any]
]

#: The data type for an operation callable object.
OperationType: TypeAlias = Callable[
    ["BaseLevel", "Dimension", Any], OperationReturnType
]
