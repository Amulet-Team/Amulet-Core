from typing import Dict, Any, Union, Generator, Callable, TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from amulet.api.world import World

Dimension = int

OperationYieldType = Union[int, float, Tuple[Union[int, float], str]]
OperationReturnType = Union[
    Generator[
        OperationYieldType,
        None,
        Any
    ],
    Any
]
OperationType = Callable[
    ["World", Dimension, Any],
    OperationReturnType
]