from typing import Any, Union, Generator, Callable, Tuple

Dimension = str
Coordinates = Tuple[int, int]
DimensionCoordinates = Tuple[Dimension, int, int]

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
