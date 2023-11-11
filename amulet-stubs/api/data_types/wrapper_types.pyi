import numpy
from .world_types import BlockCoordinates as BlockCoordinates
from _typeshed import Incomplete
from amulet.api.chunk import Chunk as Chunk
from amulet.block import Block as Block
from amulet.block_entity import BlockEntity as BlockEntity
from amulet.entity import Entity as Entity
from typing import Tuple, Union

BlockNDArray = numpy.ndarray
AnyNDArray = numpy.ndarray
PlatformType = str
VersionNumberInt = int
VersionNumberTuple = Tuple[int, ...]
VersionNumberAny = Union[VersionNumberInt, VersionNumberTuple]
VersionIdentifierType = Tuple[PlatformType, VersionNumberAny]
VersionIdentifierInt = Tuple[PlatformType, VersionNumberInt]
VersionIdentifierTuple = Tuple[PlatformType, VersionNumberTuple]
GetChunkCallback: Incomplete
BedrockInterfaceBlockType: Incomplete
GetBlockCallback: Incomplete
TranslateBlockCallbackReturn: Incomplete
TranslateEntityCallbackReturn: Incomplete
TranslateBlockCallback: Incomplete
TranslateEntityCallback: Incomplete
