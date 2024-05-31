from typing import Union, Callable, Tuple, Optional, TYPE_CHECKING, List, TypeAlias
import numpy

if TYPE_CHECKING:
    from .world_types import BlockCoordinates
    from amulet.api.chunk import Chunk
    from amulet.block import Block
    from amulet.block_entity import BlockEntity
    from amulet.entity import Entity

# Wrapper types
BlockNDArray: TypeAlias = numpy.ndarray  # NDArray[(Any, ), 'Block']
AnyNDArray: TypeAlias = numpy.ndarray  # NDArray[(Any, ), Any]

#: The data type for an integer version number.
VersionNumberInt: TypeAlias = int

#: The data type for the tuple version number.
VersionNumberTuple: TypeAlias = Tuple[int, ...]

#: The data type for either an integer or tuple version number.
VersionNumberAny: TypeAlias = Union[VersionNumberInt, VersionNumberTuple]

#: The data type for a version identifier containing platform and int or tuple version number
VersionIdentifierType: TypeAlias = Tuple[PlatformType, VersionNumberAny]
#: The data type for a version identifier containing platform and int version number
VersionIdentifierInt: TypeAlias = Tuple[PlatformType, VersionNumberInt]
#: The data type for a version identifier containing platform and tuple version number
VersionIdentifierTuple: TypeAlias = Tuple[PlatformType, VersionNumberTuple]

GetChunkCallback: TypeAlias = Callable[[int, int], "Chunk"]

BedrockInterfaceBlockType: TypeAlias = Tuple[
    Union[Tuple[None, Tuple[int, int]], Tuple[None, "Block"], Tuple[int, "Block"]], ...
]

GetBlockCallback: TypeAlias = Callable[  # get a block at a different location
    [
        "BlockCoordinates"
    ],  # this takes the coordinates relative to the block in question
    Tuple[
        "Block", Optional["BlockEntity"]
    ],  # and returns a new block and optionally a block entity
]

TranslateBlockCallbackReturn: TypeAlias = Tuple[
    Optional["Block"], Optional["BlockEntity"], List["Entity"], bool
]

TranslateEntityCallbackReturn: TypeAlias = Tuple[
    Optional["Block"], Optional["BlockEntity"], List["Entity"]
]

TranslateBlockCallback: TypeAlias = Callable[
    [  # a callable
        "Block",  # that takes either a Block
        Optional[
            GetBlockCallback
        ],  # this is used in cases where the block needs data beyond itself to fully define itself (eg doors)
        "BlockCoordinates",  # used in a select few cases where the translation needs to know where the block is
    ],
    TranslateBlockCallbackReturn,  # ultimately return the converted objects(s)
]

TranslateEntityCallback: TypeAlias = Callable[
    ["Entity"],  # a callable  # that takes either an Entity
    TranslateEntityCallbackReturn,  # ultimately return the converted objects(s)
]
