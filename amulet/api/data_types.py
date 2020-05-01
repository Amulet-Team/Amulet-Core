from typing import Any, Union, Generator, Callable, Tuple, Optional, TYPE_CHECKING, List
# from nptyping import NDArray
import numpy

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk
    from amulet.api.block import Block
    from amulet.api.block_entity import BlockEntity
    from amulet.api.entity import Entity

# World types
Dimension = str
ChunkCoordinates = Tuple[int, int]
DimensionCoordinates = Tuple[Dimension, int, int]
BlockCoordinates = Tuple[int, int, int]
SubChunkNDArray = numpy.ndarray  # NDArray[(16, 16, 16), numpy.uint]


# Wrapper types
BlockNDArray = numpy.ndarray  # NDArray[(Any, ), 'Block']
AnyNDArray = numpy.ndarray  # NDArray[(Any, ), Any]
VersionNumberInt = int
VersionNumberTuple = Tuple[int, int, int]
VersionNumberAny = Union[VersionNumberInt, VersionNumberTuple]

GetChunkCallback = Callable[[int, int], Tuple['Chunk', BlockNDArray]]

GetBlockCallback = Callable[  # get a block at a different location
    [
        BlockCoordinates
    ],  # this takes the coordinates relative to the block in question
    Tuple[
        'Block', Optional['BlockEntity']
    ],  # and returns a new block and optionally a block entity
]
BlockType = 'Block'

TranslateBlockCallbackReturn = Tuple[
    Optional['Block'], Optional['BlockEntity'], List['Entity'], bool
]

TranslateEntityCallbackReturn = Tuple[
    Optional['Block'], Optional['BlockEntity'], List['Entity']
]

TranslateBlockCallback = Callable[
    [  # a callable
        BlockType,  # that takes either a Block
        Optional[
            GetBlockCallback
        ],  # this is used in cases where the block needs data beyond itself to fully define itself (eg doors)
    ],
    TranslateBlockCallbackReturn,  # ultimately return the converted objects(s)
]

TranslateEntityCallback = Callable[
    [  # a callable
        'Entity'  # that takes either an Entity
    ],
    TranslateEntityCallbackReturn,  # ultimately return the converted objects(s)
]


# Operation types
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
