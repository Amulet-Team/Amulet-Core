import os
import copy
import numpy
from typing import Optional, Tuple, Iterable, TYPE_CHECKING, BinaryIO, Dict, List, Union

from amulet_nbt import (
    ShortTag,
    IntTag,
    ListTag,
    CompoundTag,
    ByteArrayTag,
    IntArrayTag,
    NamedTag,
    load as load_nbt,
)

from amulet.api.data_types import (
    VersionNumberAny,
    VersionNumberInt,
    ChunkCoordinates,
    AnyNDArray,
    Dimension,
    PlatformType,
)

from amulet.api.wrapper import StructureFormatWrapper
from amulet.api.chunk import Chunk
from amulet.api.selection import SelectionGroup, SelectionBox
from amulet.api.errors import ChunkDoesNotExist, ObjectWriteError, ObjectReadError
from amulet.api.block import Block
from amulet.utils.numpy_helpers import brute_sort_objects_no_hash

from .chunk import SpongeSchemChunk
from .interface import SpongeSchemInterface
from .varint import decode_byte_array, encode_array

if TYPE_CHECKING:
    from amulet.api.wrapper import Translator, Interface


class SpongeSchemReadError(ObjectReadError):
    pass


class SpongeSchemWriteError(ObjectWriteError):
    pass


sponge_schem_interface = SpongeSchemInterface()

max_schem_version = 3


def _is_sponge(path: str) -> bool:
    """
    Check if a file is actually a sponge schematic file.
    """

    try:
        root = load_nbt(path).compound
    except Exception as e:
        return False

    inner = root.get("Schematic")
    if isinstance(inner, CompoundTag):
        root = inner

    bd = root.get("BlockData")
    if isinstance(bd, ByteArrayTag):
        return True

    blocks = root.get("Blocks")
    if isinstance(blocks, CompoundTag):
        data_tag = blocks.get("Data")

        has_data = isinstance(data_tag, (ByteArrayTag, IntArrayTag))
        pal_tag = blocks.get("BlockPalette") or blocks.get("Palette")
        has_palette = isinstance(pal_tag, CompoundTag)
        if has_data and has_palette:
            return True
        else:
            return False
    return False


def _detect_sponge_version(root: CompoundTag) -> int:
    """
    Return the detected Sponge schematic version (2 or 3), using:
      1) 'Version' IntTag if present and valid
      2) root-level 'BlockData' ByteArrayTag → v2
      3) nested 'Blocks' CompoundTag with 'Data' + 'BlockPalette'/'Palette' → v3
    """

    ver_tag = root.get("Version")
    if isinstance(ver_tag, IntTag):
        v = ver_tag.py_int
        if v in (2, 3):
            return v

    if isinstance(root.get("BlockData"), ByteArrayTag):
        return 2

    blocks = root.get("Blocks")
    if isinstance(blocks, CompoundTag):
        data_tag = blocks.get("Data")
        palette_tag = blocks.get("BlockPalette") or blocks.get("Palette")
        if isinstance(data_tag, (ByteArrayTag, IntArrayTag)) and isinstance(
            palette_tag, CompoundTag
        ):
            return 3

    raise SpongeSchemReadError("Could not detect Sponge schematic format")


class SpongeSchemFormatWrapper(StructureFormatWrapper[VersionNumberInt]):
    """
    This FormatWrapper class exists to interface with the sponge schematic structure format.
    """

    def __init__(self, path: str):
        """
        Construct a new instance of :class:`SpongeSchemFormatWrapper`.

        This should not be used directly. You should instead use :func:`amulet.load_format`.

        :param path: The file path to the serialised data.
        """
        super().__init__(path)
        self._chunks: Dict[
            ChunkCoordinates,
            SpongeSchemChunk,
        ] = {}
        self._schem_version: int = max_schem_version

    def _create(
        self,
        overwrite: bool,
        bounds: Union[
            SelectionGroup, Dict[Dimension, Optional[SelectionGroup]], None
        ] = None,
        **kwargs,
    ):
        if not overwrite and os.path.isfile(self.path):
            raise SpongeSchemWriteError(f"There is already a file at {self.path}")
        translator_version = self.translation_manager.get_version("java", self._version)
        self._platform = translator_version.platform
        self._version = translator_version.data_version
        self._chunks = {}
        self._set_selection(bounds)
        self._is_open = True
        self._has_lock = True

    def open_from(self, f: BinaryIO):

        sponge_schem = load_nbt(f).compound
        wrapper = sponge_schem.get("Schematic")
        if isinstance(wrapper, CompoundTag):
            sponge_schem = wrapper

        version = _detect_sponge_version(sponge_schem)
        if version == 1:
            raise SpongeSchemReadError("Unsupported Sponge schematic version 1")

        offset_tag = sponge_schem.get("Offset")
        if isinstance(offset_tag, IntArrayTag) and len(offset_tag) == 3:
            min_point = numpy.array(offset_tag, dtype=numpy.int32)
        else:
            min_point = numpy.array([0, 0, 0], dtype=numpy.int32)

        size = []
        for key in ("Width", "Height", "Length"):
            tag = sponge_schem.get(key)
            if not isinstance(tag, ShortTag):
                raise SpongeSchemReadError(f"Missing or invalid '{key}' tag")
            size.append(tag.py_int & 0xFFFF)
        max_point = min_point + size

        selection = SelectionBox(min_point, max_point)
        self._bounds[self.dimensions[0]] = SelectionGroup(selection)

        dv = sponge_schem.get("DataVersion")
        if not isinstance(dv, IntTag):
            raise SpongeSchemReadError("Missing or invalid 'DataVersion' tag")
        tv = self.translation_manager.get_version("java", dv.py_int)
        self._platform, self._version = tv.platform, tv.data_version

        if version == 2:
            blk_ctn = sponge_schem
            palette_tag = blk_ctn.get("Palette")
            data_tag = blk_ctn.get("BlockData")
            block_entities_tag = blk_ctn.get("BlockEntities")
        else:
            blk_ctn = sponge_schem.get("Blocks")
            if not isinstance(blk_ctn, CompoundTag):
                raise SpongeSchemReadError(
                    "Missing or invalid 'Blocks' container for v3 schema"
                )
            palette_tag = blk_ctn.get("BlockPalette") or blk_ctn.get("Palette")
            data_tag = blk_ctn.get("Data")
            block_entities_tag = blk_ctn.get("BlockEntities")

        if not isinstance(palette_tag, CompoundTag):
            raise SpongeSchemReadError("Missing or invalid palette tag")
        if not isinstance(data_tag, (ByteArrayTag, IntArrayTag)):
            raise SpongeSchemReadError("Missing or invalid 'Data' tag")

        block_palette = {
            idx.py_int: Block.from_string_blockstate(state)
            for state, idx in palette_tag.items()
        }

        if isinstance(data_tag, IntArrayTag):
            unpacked = data_tag.np_array.tolist()
        else:
            raw = numpy.array(data_tag, dtype=numpy.uint8)
            unpacked = decode_byte_array(raw)

        expected = size[0] * size[1] * size[2]
        if len(unpacked) != expected:
            raise SpongeSchemReadError("Block data length does not match dimensions")

        dy, dz, dx = size[1], size[2], size[0]
        blocks_array = (
            numpy.array(unpacked, dtype=numpy.uint32)
            .reshape((dy, dz, dx))
            .transpose((2, 0, 1))
        )

        for cx, cz in selection.chunk_locations():
            cbox = SelectionBox.create_chunk_box(cx, cz).intersection(selection)
            sl = cbox.create_moved_box(selection.min, subtract=True).slice
            sub = blocks_array[sl]
            ids, remap = numpy.unique(sub, return_inverse=True)
            remap = remap.reshape(sub.shape)

            pal = numpy.empty(len(ids), dtype=object)
            for i, orig in enumerate(ids):
                pal[i] = block_palette[orig]

            self._chunks[(cx, cz)] = SpongeSchemChunk(cbox, remap, pal, [], [])

        if isinstance(block_entities_tag, ListTag):
            for be in block_entities_tag:
                pos = be.get("Pos")
                if isinstance(pos, IntArrayTag) and len(pos) == 3:
                    world_pos = pos.np_array + min_point
                    x, y, z = world_pos
                    be["Pos"] = IntArrayTag(world_pos)
                    key = (x >> 4, z >> 4)
                    if key in self._chunks and (x, y, z) in self._chunks[key].selection:
                        self._chunks[key].block_entities.append(be)

        entities = sponge_schem.get("Entities")
        if isinstance(entities, ListTag):
            for ent in entities:
                pos = ent.get("Pos")
                if isinstance(pos, ListTag) and len(pos) == 3:
                    x = int(pos[0].py_float + min_point[0])
                    y = int(pos[1].py_float + min_point[1])
                    z = int(pos[2].py_float + min_point[2])
                    ent["Pos"] = ListTag([IntTag(x), IntTag(y), IntTag(z)])
                    key = (x >> 4, z >> 4)
                    if key in self._chunks and (x, y, z) in self._chunks[key].selection:
                        self._chunks[key].entities.append(ent)

    @staticmethod
    def is_valid(path: str) -> bool:
        return (
            os.path.isfile(path)
            and path.endswith((".schem", ".schematic"))
            and _is_sponge(path)
        )

    @property
    def valid_formats(self) -> Dict[PlatformType, Tuple[bool, bool]]:
        return {"java": (False, True)}

    @property
    def extensions(self) -> Tuple[str, ...]:
        return (".schem", ".schematic")

    def _get_interface(self, raw_chunk_data=None) -> "SpongeSchemInterface":
        return sponge_schem_interface

    def _get_interface_and_translator(
        self, raw_chunk_data=None
    ) -> Tuple["Interface", "Translator", VersionNumberAny]:
        interface = self._get_interface(raw_chunk_data)
        translator, version_identifier = interface.get_translator(
            self.max_world_version, raw_chunk_data, self.translation_manager
        )
        return interface, translator, version_identifier

    def save_to(self, f: BinaryIO):
        if self._schem_version == 1:
            raise SpongeSchemReadError(
                "Sponge Schematic Version 1 is not supported currently."
            )
        elif self._schem_version == 2:
            selection = self._bounds[self.dimensions[0]].selection_boxes[0]
            if any(s > 2**16 - 1 for s in selection.shape):
                raise SpongeSchemWriteError(
                    "The structure is too large to be exported to a Sponge Schematic file. It must be 2^16 - 1 at most in each dimension."
                )
            overflowed_shape = [s if s < 2**15 else s - 2**16 for s in selection.shape]
            tag = CompoundTag(
                {
                    "Version": IntTag(2),
                    "DataVersion": IntTag(self._version),
                    "Width": ShortTag(overflowed_shape[0]),
                    "Height": ShortTag(overflowed_shape[1]),
                    "Length": ShortTag(overflowed_shape[2]),
                    "Offset": IntArrayTag(selection.min),
                }
            )

            entities = []
            block_entities = []
            blocks = numpy.zeros(selection.shape, dtype=numpy.uint32)
            palette: List[AnyNDArray] = []
            if self._version < 1500:
                raise Exception(
                    "Writing to Sponge Schematic files in pre-1.13 format is not currently supported."
                )
            else:
                arr = numpy.empty(1, dtype=object)
                arr[0] = Block("minecraft", "air")
                palette.append(arr)

            palette_len = 1

            for chunk in self._chunks.values():
                if chunk.selection.intersects(selection):
                    box = chunk.selection.create_moved_box(selection.min, subtract=True)
                    blocks[box.slice] = chunk.blocks + palette_len
                    palette.append(chunk.palette)
                    palette_len += len(chunk.palette)
                    for be in chunk.block_entities:
                        be = copy.deepcopy(be)
                        be["Pos"] = IntArrayTag(be["Pos"].np_array - selection.min)
                        block_entities.append(be)

                    for e in chunk.entities:
                        e = copy.deepcopy(e)
                        x, y, z = e["Pos"]
                        e["Pos"] = ListTag(
                            [
                                IntTag(x - selection.min_x),
                                IntTag(y - selection.min_y),
                                IntTag(z - selection.min_z),
                            ]
                        )
                        entities.append(e)

            compact_palette, lut = brute_sort_objects_no_hash(
                numpy.concatenate(palette)
            )
            blocks = numpy.transpose(lut[blocks], (1, 2, 0)).ravel()
            block_palette = []
            for index, block in enumerate(compact_palette):
                block: Block
                block_palette.append(block.blockstate)

            tag["PaletteMax"] = IntTag(len(compact_palette))
            tag["Palette"] = CompoundTag(
                {
                    blockstate: IntTag(index)
                    for index, blockstate in enumerate(block_palette)
                }
            )
            tag["BlockData"] = ByteArrayTag(list(encode_array(blocks)))
            if block_entities:
                tag["BlockEntities"] = ListTag(block_entities)
            if entities:
                tag["Entities"] = ListTag(entities)

            NamedTag(tag, "Schematic").save_to(f)
        else:
            raise SpongeSchemReadError(
                f"Sponge Schematic Version {self._schem_version} is not supported currently."
            )

    def _close(self):
        """Close the disk database"""
        self._chunks.clear()

    def unload(self):
        pass

    def all_chunk_coords(
        self, dimension: Optional[Dimension] = None
    ) -> Iterable[ChunkCoordinates]:
        yield from self._chunks.keys()

    def has_chunk(self, cx: int, cz: int, dimension: Dimension) -> bool:
        return (cx, cz) in self._chunks

    def _encode(
        self,
        interface: SpongeSchemInterface,
        chunk: Chunk,
        dimension: Dimension,
        chunk_palette: AnyNDArray,
    ):
        return interface.encode(
            chunk,
            chunk_palette,
            self.max_world_version,
            SelectionBox.create_chunk_box(chunk.cx, chunk.cz).intersection(
                self._bounds[dimension].to_box()
            ),
        )

    def _delete_chunk(self, cx: int, cz: int, dimension: Optional[Dimension] = None):
        if (cx, cz) in self._chunks:
            del self._chunks[(cx, cz)]

    def _put_raw_chunk_data(
        self,
        cx: int,
        cz: int,
        section: SpongeSchemChunk,
        dimension: Optional[Dimension] = None,
    ):
        self._chunks[(cx, cz)] = copy.deepcopy(section)

    def _get_raw_chunk_data(
        self, cx: int, cz: int, dimension: Optional[Dimension] = None
    ) -> SpongeSchemChunk:
        """
        Return the raw data as loaded from disk.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the data from.
        :return: The raw chunk data.
        """
        if (cx, cz) in self._chunks:
            return copy.deepcopy(self._chunks[(cx, cz)])
        else:
            raise ChunkDoesNotExist
