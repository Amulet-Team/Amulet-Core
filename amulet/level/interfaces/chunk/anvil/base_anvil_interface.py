from __future__ import annotations
from abc import abstractmethod, ABC

from typing import (
    List,
    Tuple,
    Iterable,
    TYPE_CHECKING,
    Any,
    Dict,
    Callable,
    Sequence,
    Union,
    Type,
)
import numpy


from amulet_nbt import (
    AbstractBaseTag,
    IntTag,
    ListTag,
    CompoundTag,
    NamedTag,
    AnyNBT,
)

from amulet.api.chunk import Chunk, StatusFormats
from amulet.api.wrapper import Interface
from amulet.level import loader
from amulet.api.data_types import AnyNDArray, VersionIdentifierType
from amulet.api.wrapper import EntityIDType, EntityCoordType

if TYPE_CHECKING:
    from amulet.api.wrapper import Translator
    from amulet.api.block_entity import BlockEntity
    from amulet.api.entity import Entity


ChunkDataType = Dict[str, NamedTag]

ChunkPathType = Tuple[
    str,  # The layer name
    Sequence[
        Tuple[Union[str, int], Type[AbstractBaseTag]],
    ],
    Type[AbstractBaseTag],
]


class BaseDecoderEncoder(ABC):
    def __init__(self):
        self.__decoders = {}
        self.__post_decoders = {}
        self.__encoders = {}
        self.__post_encoders = {}

    def _register_decoder(self, decoder: Callable):
        """Register a function that does the decoding"""
        self.__decoders[decoder] = None

    def _register_post_decoder(self, post_decoder: Callable):
        """Register a function that runs after the decoding"""
        self.__post_decoders[post_decoder] = None

    def _unregister_decoder(self, decoder: Callable):
        """Unregister a function that does the decoding"""
        del self.__decoders[decoder]

    def _unregister_post_decoder(self, post_decoder: Callable):
        """Unregister a function that runs after the decoding"""
        del self.__post_decoders[post_decoder]

    def _do_decode(self, *args, **kwargs):
        for decoder in self.__decoders:
            decoder(*args, **kwargs)
        for post_decoder in self.__post_decoders:
            post_decoder(*args, **kwargs)

    def _register_encoder(self, encoder: Callable):
        """Register a function that does the encoding"""
        self.__encoders[encoder] = None

    def _register_post_encoder(self, post_encoder: Callable):
        """Register a function that runs after the encoding"""
        self.__post_encoders[post_encoder] = None

    def _unregister_encoder(self, encoder: Callable):
        """Unregister a function that does the encoding"""
        del self.__encoders[encoder]

    def _unregister_post_encoder(self, post_encoder: Callable):
        """Unregister a function that runs after the encoding"""
        del self.__post_encoders[post_encoder]

    def _do_encode(self, *args, **kwargs):
        for encoder in self.__encoders:
            encoder(*args, **kwargs)
        for post_encoder in self.__post_encoders:
            post_encoder(*args, **kwargs)


class BaseAnvilInterface(Interface, BaseDecoderEncoder):
    # The chunk object, the chunk data, the floor chunk coord, the chunk height (in sub-chunks)
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

    def __init__(self):
        BaseDecoderEncoder.__init__(self)
        self._feature_options = {
            "status": StatusFormats,
            "height_map": [
                "256IARequired",  # A 256 element Int Array in HeightMap
                "256IA",  # A 256 element Int Array in HeightMap
                "C|V1",  # A Compound of Long Arrays with these keys "LIQUID", "SOLID", "LIGHT", "RAIN"
                "C|V2",  # A Compound of Long Arrays with these keys "WORLD_SURFACE_WG", "OCEAN_FLOOR_WG", "MOTION_BLOCKING", "MOTION_BLOCKING_NO_LEAVES", "OCEAN_FLOOR", "LIGHT_BLOCKING"
                "C|V3",  # A Compound of Long Arrays with these keys "WORLD_SURFACE_WG", "OCEAN_FLOOR_WG", "MOTION_BLOCKING", "MOTION_BLOCKING_NO_LEAVES", "OCEAN_FLOOR", "LIGHT_BLOCKING", "WORLD_SURFACE"
                "C|V4",  # A Compound of Long Arrays with these keys "WORLD_SURFACE_WG", "OCEAN_FLOOR_WG", "MOTION_BLOCKING", "MOTION_BLOCKING_NO_LEAVES", "OCEAN_FLOOR", "WORLD_SURFACE"
            ],
            # 'carving_masks': ['C|?BA'],
            "light_optional": ["false", "true"],
            "block_entity_format": [EntityIDType.namespace_str_id],
            "block_entity_coord_format": [EntityCoordType.xyz_int],
            "entity_format": [EntityIDType.namespace_str_id],
            "entity_coord_format": [EntityCoordType.Pos_list_double],
            # 'lights': [],
        }
        self._features = {key: None for key in self._feature_options.keys()}

    def _set_feature(self, feature: str, option: Any):
        assert feature in self._feature_options, f"{feature} is not a valid feature."
        assert (
            option is None or option in self._feature_options[feature]
        ), f'Invalid option {option} for feature "{feature}"'
        self._features[feature] = option

    def is_valid(self, key: Tuple) -> bool:
        return key[0] == "java" and self.minor_is_valid(key[1])

    @staticmethod
    @abstractmethod
    def minor_is_valid(key: int):
        raise NotImplementedError

    def get_translator(
        self,
        max_world_version: VersionIdentifierType,
        data: ChunkDataType = None,
    ) -> Tuple["Translator", int]:
        if data is None:
            key = max_world_version
            version = max_world_version[1]
        else:
            data_version = (
                data.get("region", {}).compound.get("DataVersion", IntTag(-1)).py_int
            )
            key, version = (("java", data_version), data_version)

        return loader.Translators.get(key), version

    def get_layer_obj(
        self,
        obj: ChunkDataType,
        data: Tuple[
            str,
            Sequence[
                Tuple[Union[str, int], Type[AbstractBaseTag]],
            ],
            Union[None, AnyNBT, Type[AbstractBaseTag]],
        ],
        *,
        pop_last=False,
    ) -> Any:
        """
        Get an object from a nested NBT structure layer

        :param obj: The chunk data object
        :param data: The data layer name, the nbt path and the default
        :param pop_last: If true the last key will be popped
        :return: The found data or the default
        """
        layer_key, path, default = data
        if layer_key in obj:
            return self.get_nested_obj(
                obj[layer_key].compound, path, default, pop_last=pop_last
            )
        elif default is None or isinstance(default, AbstractBaseTag):
            return default
        elif issubclass(default, AbstractBaseTag):
            return default()
        else:
            raise TypeError("default must be None, an NBT instance or an NBT class.")

    def set_layer_obj(
        self,
        obj: ChunkDataType,
        data: Tuple[
            str,
            Sequence[Tuple[Union[str, int], Type[AbstractBaseTag]]],
            Union[None, AnyNBT, Type[AbstractBaseTag]],
        ],
        default_tag: AnyNBT = None,
        *,
        setdefault=False,
    ) -> AnyNBT:
        """
        Setdefault on a ChunkDataType object

        :param obj: The ChunkDataType object to use
        :param data: The data to set
        :param setdefault: If True will behave like setdefault. If False will replace existing data.
        :return: The existing data found or the default that was set
        """
        layer_key, path, default = data
        default = default if default_tag is None else default_tag
        if not path:
            raise ValueError("was not given a path to set")
        tag = obj.setdefault(layer_key, NamedTag()).compound
        *path, (key, dtype) = path
        if path:
            key_path = next(zip(*path))
        else:
            key_path = ()
        return self.set_obj(
            tag, key, dtype, default, path=key_path, setdefault=setdefault
        )

    @abstractmethod
    def decode(
        self, cx: int, cz: int, data: ChunkDataType, bounds: Tuple[int, int]
    ) -> Tuple["Chunk", AnyNDArray]:
        """
        Create an amulet.api.chunk.Chunk object from raw data.
        :param cx: chunk x coordinate
        :param cz: chunk z coordinate
        :param data: The chunk data
        :param bounds: The minimum and maximum bounds of the chunk. In 1.17 this is required to define where the biome array sits.
        :return: Chunk object in version-specific format, along with the block_palette for that chunk.
        """
        raise NotImplementedError

    def _decode_entity_list(self, entities: ListTag) -> List["Entity"]:
        entities_out = []
        if entities.list_data_type == CompoundTag.tag_id:
            for nbt in entities:
                entity = self._decode_entity(
                    NamedTag(nbt),
                    self._features["entity_format"],
                    self._features["entity_coord_format"],
                )
                if entity is not None:
                    entities_out.append(entity)

        return entities_out

    def _decode_block_entity_list(self, block_entities: ListTag) -> List["BlockEntity"]:
        entities_out = []
        if block_entities.list_data_type == CompoundTag.tag_id:
            for nbt in block_entities:
                if not isinstance(nbt, CompoundTag):
                    continue
                entity = self._decode_block_entity(
                    NamedTag(nbt),
                    self._features["block_entity_format"],
                    self._features["block_entity_coord_format"],
                )
                if entity is not None:
                    entities_out.append(entity)

        return entities_out

    @abstractmethod
    def encode(
        self,
        chunk: "Chunk",
        palette: AnyNDArray,
        max_world_version: Tuple[str, int],
        bounds: Tuple[int, int],
    ) -> ChunkDataType:
        """
        Encode a version-specific chunk to raw data for the format to store.

        :param chunk: The already translated version-specific chunk to encode.
        :param palette: The block_palette the ids in the chunk correspond to.
        :type palette: numpy.ndarray[Block]
        :param max_world_version: The key to use to find the encoder.
        :param bounds: The minimum and maximum bounds of the chunk. In 1.17 this is required to define where the biome array sits.
        :return: Raw data to be stored by the Format.
        """
        raise NotImplementedError

    def _encode_entity_list(self, entities: Iterable["Entity"]) -> ListTag:
        entities_out = []
        for entity in entities:
            nbt = self._encode_entity(
                entity,
                self._features["entity_format"],
                self._features["entity_coord_format"],
            )
            if nbt is not None:
                entities_out.append(nbt.compound)

        return ListTag(entities_out)

    def _encode_block_entity_list(
        self, block_entities: Iterable["BlockEntity"]
    ) -> ListTag:
        entities_out = []
        for entity in block_entities:
            nbt = self._encode_block_entity(
                entity,
                self._features["block_entity_format"],
                self._features["block_entity_coord_format"],
            )
            if nbt is not None:
                entities_out.append(nbt.compound)

        return ListTag(entities_out)
