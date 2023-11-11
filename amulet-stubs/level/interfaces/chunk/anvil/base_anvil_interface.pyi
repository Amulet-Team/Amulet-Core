import abc
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from amulet.api.chunk import Chunk as Chunk, StatusFormats as StatusFormats
from amulet.api.data_types import AnyNDArray as AnyNDArray, VersionIdentifierType as VersionIdentifierType
from amulet.api.wrapper import EntityCoordType as EntityCoordType, EntityIDType as EntityIDType, Interface as Interface, Translator as Translator
from amulet.block_entity import BlockEntity as BlockEntity
from amulet.entity import Entity as Entity
from amulet.level import loader as loader
from amulet_nbt import AbstractBaseTag, AnyNBT as AnyNBT, ListTag, NamedTag
from typing import Any, Callable, Dict, Iterable, List, Sequence, Tuple, Type, Union

ChunkDataType = Dict[str, NamedTag]
ChunkPathType = Tuple[str, Sequence[Tuple[Union[str, int], Type[AbstractBaseTag]]], Type[AbstractBaseTag]]

class BaseDecoderEncoder(ABC):
    __decoders: Incomplete
    __post_decoders: Incomplete
    __encoders: Incomplete
    __post_encoders: Incomplete
    def __init__(self) -> None: ...
    def _register_decoder(self, decoder: Callable):
        """Register a function that does the decoding"""
    def _register_post_decoder(self, post_decoder: Callable):
        """Register a function that runs after the decoding"""
    def _unregister_decoder(self, decoder: Callable):
        """Unregister a function that does the decoding"""
    def _unregister_post_decoder(self, post_decoder: Callable):
        """Unregister a function that runs after the decoding"""
    def _do_decode(self, *args, **kwargs) -> None: ...
    def _register_encoder(self, encoder: Callable):
        """Register a function that does the encoding"""
    def _register_post_encoder(self, post_encoder: Callable):
        """Register a function that runs after the encoding"""
    def _unregister_encoder(self, encoder: Callable):
        """Unregister a function that does the encoding"""
    def _unregister_post_encoder(self, post_encoder: Callable):
        """Unregister a function that runs after the encoding"""
    def _do_encode(self, *args, **kwargs) -> None: ...

class BaseAnvilInterface(Interface, BaseDecoderEncoder, metaclass=abc.ABCMeta):
    DecoderType = Callable[[Chunk, ChunkDataType, int, int], None]
    EncoderType = Callable[[Chunk, ChunkDataType, int, int], None]
    _register_decoder: Callable[[DecoderType], None]
    _register_post_decoder: Callable[[DecoderType], None]
    _unregister_decoder: Callable[[DecoderType], None]
    _unregister_post_decoder: Callable[[DecoderType], None]
    _do_decode: DecoderType
    _register_encoder: Callable[[EncoderType], None]
    _register_post_encoder: Callable[[EncoderType], None]
    _unregister_encoder: Callable[[EncoderType], None]
    _unregister_post_encoder: Callable[[EncoderType], None]
    _do_encode: EncoderType
    _feature_options: Incomplete
    _features: Incomplete
    def __init__(self) -> None: ...
    def _set_feature(self, feature: str, option: Any): ...
    def is_valid(self, key: Tuple) -> bool: ...
    @staticmethod
    @abstractmethod
    def minor_is_valid(key: int): ...
    def get_translator(self, max_world_version: VersionIdentifierType, data: ChunkDataType = ...) -> Tuple['Translator', int]: ...
    def get_layer_obj(self, obj: ChunkDataType, data: Tuple[str, Sequence[Tuple[Union[str, int], Type[AbstractBaseTag]]], Union[None, AnyNBT, Type[AbstractBaseTag]]], *, pop_last: bool = ...) -> Any:
        """
        Get an object from a nested NBT structure layer

        :param obj: The chunk data object
        :param data: The data layer name, the nbt path and the default
        :param pop_last: If true the last key will be popped
        :return: The found data or the default
        """
    def set_layer_obj(self, obj: ChunkDataType, data: Tuple[str, Sequence[Tuple[Union[str, int], Type[AbstractBaseTag]]], Union[None, AnyNBT, Type[AbstractBaseTag]]], default_tag: AnyNBT = ..., *, setdefault: bool = ...) -> AnyNBT:
        """
        Setdefault on a ChunkDataType object

        :param obj: The ChunkDataType object to use
        :param data: The data to set
        :param setdefault: If True will behave like setdefault. If False will replace existing data.
        :return: The existing data found or the default that was set
        """
    @abstractmethod
    def decode(self, cx: int, cz: int, data: ChunkDataType, bounds: Tuple[int, int]) -> Tuple['Chunk', AnyNDArray]:
        """
        Create an amulet.api.chunk.Chunk object from raw data.
        :param cx: chunk x coordinate
        :param cz: chunk z coordinate
        :param data: The chunk data
        :param bounds: The minimum and maximum bounds of the chunk. In 1.17 this is required to define where the biome array sits.
        :return: Chunk object in version-specific format, along with the block_palette for that chunk.
        """
    def _decode_entity_list(self, entities: ListTag) -> List['Entity']: ...
    def _decode_block_entity_list(self, block_entities: ListTag) -> List['BlockEntity']: ...
    @abstractmethod
    def encode(self, chunk: Chunk, palette: AnyNDArray, max_world_version: Tuple[str, int], bounds: Tuple[int, int]) -> ChunkDataType:
        """
        Encode a version-specific chunk to raw data for the format to store.

        :param chunk: The already translated version-specific chunk to encode.
        :param palette: The block_palette the ids in the chunk correspond to.
        :type palette: numpy.ndarray[Block]
        :param max_world_version: The key to use to find the encoder.
        :param bounds: The minimum and maximum bounds of the chunk. In 1.17 this is required to define where the biome array sits.
        :return: Raw data to be stored by the Format.
        """
    def _encode_entity_list(self, entities: Iterable['Entity']) -> ListTag: ...
    def _encode_block_entity_list(self, block_entities: Iterable['BlockEntity']) -> ListTag: ...
