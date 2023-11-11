import PyMCTranslate
from .chunk_manager import ChunkManager as ChunkManager
from .clone import clone as clone
from .player_manager import PlayerManager as PlayerManager
from _typeshed import Incomplete
from amulet.api import level as api_level, wrapper as api_wrapper
from amulet.api.cache import TempDir as TempDir
from amulet.api.chunk import Chunk as Chunk, EntityList as EntityList
from amulet.api.chunk.status import StatusFormats as StatusFormats
from amulet.api.data_types import BlockCoordinates as BlockCoordinates, ChunkCoordinates as ChunkCoordinates, Dimension as Dimension, FloatTriplet as FloatTriplet, VersionIdentifierType as VersionIdentifierType
from amulet.api.errors import ChunkDoesNotExist as ChunkDoesNotExist, ChunkLoadError as ChunkLoadError, DimensionDoesNotExist as DimensionDoesNotExist
from amulet.api.history.history_manager import MetaHistoryManager as MetaHistoryManager
from amulet.block import Block as Block, UniversalAirBlock as UniversalAirBlock
from amulet.block_entity import BlockEntity as BlockEntity
from amulet.entity import Entity as Entity
from amulet.palette import BiomePalette as BiomePalette, BlockPalette as BlockPalette
from amulet.player import Player as Player
from amulet.selection import SelectionBox as SelectionBox, SelectionGroup as SelectionGroup
from amulet.utils.generator import generator_unpacker as generator_unpacker
from amulet.utils.world_utils import block_coords_to_chunk_coords as block_coords_to_chunk_coords
from typing import Callable, Generator, Iterable, Optional, Set, Tuple, Union

log: Incomplete

class BaseLevel:
    """
    BaseLevel is a base class for all world-like data.

    It exposes chunk data and other data using a history system to track and enable undoing changes.
    """
    _path: Incomplete
    _level_wrapper: Incomplete
    _block_palette: Incomplete
    _biome_palette: Incomplete
    _history_manager: Incomplete
    _temp_dir: Incomplete
    _history_db: Incomplete
    _chunks: Incomplete
    _players: Incomplete
    def __init__(self, path: str, format_wrapper: api_wrapper.BaseFormatWrapper) -> None:
        """
        Construct a :class:`BaseLevel` object from the given data.

        This should not be used directly. You should instead use :func:`amulet.load_level`.

        :param path: The path to the data being loaded. May be a file or directory. If blank there is no data on disk associated with this.
        :param format_wrapper: The :class:`BaseFormatWrapper` instance that the level will wrap around.
        """
    def __del__(self) -> None: ...
    @property
    def level_wrapper(self) -> api_wrapper.BaseFormatWrapper:
        """A class to access data directly from the level."""
    @property
    def sub_chunk_size(self) -> int:
        """The normal dimensions of the chunk."""
    @property
    def level_path(self) -> str:
        """
        The system path where the level is located.

        This may be a directory, file or an empty string depending on the level that is loaded.
        """
    @property
    def translation_manager(self) -> PyMCTranslate.TranslationManager:
        """An instance of the translation class for use with this level."""
    @property
    def block_palette(self) -> BlockPalette:
        """The manager for the universal blocks in this level. New blocks must be registered here before adding to the level."""
    @property
    def biome_palette(self) -> BiomePalette:
        """The manager for the universal blocks in this level. New biomes must be registered here before adding to the level."""
    @property
    def selection_bounds(self) -> SelectionGroup:
        """The selection(s) that all chunk data must fit within. Usually +/-30M for worlds. The selection for structures."""
    def bounds(self, dimension: Dimension) -> SelectionGroup:
        """
        The selection(s) that all chunk data must fit within.
        This specifies the volume that can be built in.
        Worlds will have a single cuboid volume.
        Structures may have one or more cuboid volumes.

        :param dimension: The dimension to get the bounds of.
        :return: The build volume for the dimension.
        """
    @property
    def dimensions(self) -> Tuple[Dimension, ...]:
        """The dimensions strings that are valid for this level."""
    def get_block(self, x: int, y: int, z: int, dimension: Dimension) -> Block:
        """
        Gets the universal Block object at the specified coordinates.

        To get the block in a given format use :meth:`get_version_block`

        :param x: The X coordinate of the desired block
        :param y: The Y coordinate of the desired block
        :param z: The Z coordinate of the desired block
        :param dimension: The dimension of the desired block
        :return: The universal Block object representation of the block at that location
        :raises:
            :class:`~amulet.api.errors.ChunkDoesNotExist`: If the chunk does not exist (was deleted or never created)

            :class:`~amulet.api.errors.ChunkLoadError`: If the chunk was not able to be loaded. Eg. If the chunk is corrupt or some error occurred when loading.
        """
    def _chunk_box(self, cx: int, cz: int, sub_chunk_size: Optional[int] = ...):
        """Get a SelectionBox containing the whole of a given chunk"""
    def _sanitise_selection(self, selection: Union[SelectionGroup, SelectionBox, None], dimension: Dimension) -> SelectionGroup: ...
    def get_coord_box(self, dimension: Dimension, selection: Union[SelectionGroup, SelectionBox, None] = ..., yield_missing_chunks: bool = ...) -> Generator[Tuple[ChunkCoordinates, SelectionBox], None, None]:
        """
        Given a selection will yield chunk coordinates and :class:`SelectionBox` instances into that chunk

        If not given a selection will use the bounds of the object.

        :param dimension: The dimension to take effect in.
        :param selection: SelectionGroup or SelectionBox into the level. If None will use :meth:`bounds` for the dimension.
        :param yield_missing_chunks: If a chunk does not exist an empty one will be created (defaults to false). Use this with care.
        """
    def get_chunk_boxes(self, dimension: Dimension, selection: Union[SelectionGroup, SelectionBox, None] = ..., create_missing_chunks: bool = ...) -> Generator[Tuple[Chunk, SelectionBox], None, None]:
        """
        Given a selection will yield :class:`Chunk` and :class:`SelectionBox` instances into that chunk

        If not given a selection will use the bounds of the object.

        :param dimension: The dimension to take effect in.
        :param selection: SelectionGroup or SelectionBox into the level. If None will use :meth:`bounds` for the dimension.
        :param create_missing_chunks: If a chunk does not exist an empty one will be created (defaults to false). Use this with care.
        """
    def get_chunk_slice_box(self, dimension: Dimension, selection: Union[SelectionGroup, SelectionBox] = ..., create_missing_chunks: bool = ...) -> Generator[Tuple[Chunk, Tuple[slice, slice, slice], SelectionBox], None, None]:
        """
        Given a selection will yield :class:`Chunk`, slices, :class:`SelectionBox` for the contents of the selection.

        :param dimension: The dimension to take effect in.
        :param selection: SelectionGroup or SelectionBox into the level. If None will use :meth:`bounds` for the dimension.
        :param create_missing_chunks: If a chunk does not exist an empty one will be created (defaults to false)

        >>> for chunk, slices, box in level.get_chunk_slice_box(selection):
        >>>     chunk.blocks[slice] = ...
        """
    def get_moved_coord_slice_box(self, dimension: Dimension, destination_origin: BlockCoordinates, selection: Optional[Union[SelectionGroup, SelectionBox]] = ..., destination_sub_chunk_shape: Optional[int] = ..., yield_missing_chunks: bool = ...) -> Generator[Tuple[ChunkCoordinates, Tuple[slice, slice, slice], SelectionBox, ChunkCoordinates, Tuple[slice, slice, slice], SelectionBox], None, None]:
        """
        Iterate over a selection and return slices into the source object and destination object
        given the origin of the destination. When copying a selection to a new area the slices will
        only be equal if the offset is a multiple of the chunk size. This will rarely be the case
        so the slices need to be split up into parts that intersect a chunk in the source and destination.

        :param dimension: The dimension to iterate over.
        :param destination_origin: The location where the minimum point of the selection will end up
        :param selection: An optional selection. The overlap of this and the dimensions bounds will be used
        :param destination_sub_chunk_shape: the chunk shape of the destination object (defaults to self.sub_chunk_size)
        :param yield_missing_chunks: Generate empty chunks if the chunk does not exist.
        :return:
        """
    def get_moved_chunk_slice_box(self, dimension: Dimension, destination_origin: BlockCoordinates, selection: Optional[Union[SelectionGroup, SelectionBox]] = ..., destination_sub_chunk_shape: Optional[int] = ..., create_missing_chunks: bool = ...) -> Generator[Tuple[Chunk, Tuple[slice, slice, slice], SelectionBox, ChunkCoordinates, Tuple[slice, slice, slice], SelectionBox], None, None]:
        """
        Iterate over a selection and return slices into the source object and destination object
        given the origin of the destination. When copying a selection to a new area the slices will
        only be equal if the offset is a multiple of the chunk size. This will rarely be the case
        so the slices need to be split up into parts that intersect a chunk in the source and destination.

        :param dimension: The dimension to iterate over.
        :param destination_origin: The location where the minimum point of self.selection will end up
        :param selection: An optional selection. The overlap of this and self.selection will be used
        :param destination_sub_chunk_shape: the chunk shape of the destination object (defaults to self.sub_chunk_size)
        :param create_missing_chunks: Generate empty chunks if the chunk does not exist.
        :return:
        """
    def pre_save_operation(self) -> Generator[float, None, bool]:
        """
        Logic to run before saving. Eg recalculating height maps or lighting.
        Is a generator yielding progress from 0 to 1 and returning a bool saying if changes have been made.

        :return: Have any modifications been made.
        """
    def save(self, wrapper: api_wrapper.BaseFormatWrapper = ..., progress_callback: Callable[[int, int], None] = ...):
        """
        Save the level to the given :class:`BaseFormatWrapper`.

        :param wrapper: If specified will save the data to this wrapper instead of self.level_wrapper
        :param progress_callback: Optional progress callback to let the calling program know the progress. Input format chunk_index, chunk_count
        :return:
        """
    def save_iter(self, wrapper: api_wrapper.BaseFormatWrapper = ...) -> Generator[Tuple[int, int], None, None]:
        """
        Save the level to the given :class:`BaseFormatWrapper`.

        This will yield the progress which can be used to update a UI.

        :param wrapper: If specified will save the data to this wrapper instead of self.level_wrapper
        :return: A generator of the number of chunks completed and the total number of chunks
        """
    def purge(self) -> None:
        """
        Unload all loaded and cached data.

        This is functionally the same as closing and reopening the world without creating a new class.
        """
    def close(self) -> None:
        """
        Close the attached level and remove temporary files.

        Use changed method to check if there are any changes that should be saved before closing.
        """
    def unload(self, safe_area: Optional[Tuple[Dimension, int, int, int, int]] = ...):
        """
        Unload all chunk data not in the safe area.

        :param safe_area: The area that should not be unloaded [dimension, min_chunk_x, min_chunk_z, max_chunk_x, max_chunk_z]. If None will unload all chunk data.
        """
    def unload_unchanged(self) -> None:
        """Unload all data that has not been marked as changed."""
    @property
    def chunks(self) -> ChunkManager:
        """
        The chunk container.

        Most methods from :class:`ChunkManager` also exists in the level class.
        """
    def all_chunk_coords(self, dimension: Dimension) -> Set[Tuple[int, int]]:
        """
        The coordinates of every chunk in this dimension of the level.

        This is the combination of chunks saved to the level and chunks yet to be saved.
        """
    def has_chunk(self, cx: int, cz: int, dimension: Dimension) -> bool:
        """
        Does the chunk exist. This is a quick way to check if the chunk exists without loading it.

        :param cx: The x coordinate of the chunk.
        :param cz: The z coordinate of the chunk.
        :param dimension: The dimension to load the chunk from.
        :return: True if the chunk exists. Calling get_chunk on this chunk may still throw ChunkLoadError
        """
    def get_chunk(self, cx: int, cz: int, dimension: Dimension) -> Chunk:
        """
        Gets a :class:`Chunk` class containing the data for the requested chunk.

        :param cx: The X coordinate of the desired chunk
        :param cz: The Z coordinate of the desired chunk
        :param dimension: The dimension to get the chunk from
        :return: A Chunk object containing the data for the chunk
        :raises:
            :class:`~amulet.api.errors.ChunkDoesNotExist`: If the chunk does not exist (was deleted or never created)

            :class:`~amulet.api.errors.ChunkLoadError`: If the chunk was not able to be loaded. Eg. If the chunk is corrupt or some error occurred when loading.
        """
    def create_chunk(self, cx: int, cz: int, dimension: Dimension) -> Chunk:
        """
        Create an empty chunk and put it at the given location.

        If a chunk exists at the given location it will be overwritten.

        :param cx: The X coordinate of the chunk
        :param cz: The Z coordinate of the chunk
        :param dimension: The dimension to put the chunk in.
        :return: The newly created :class:`Chunk`.
        """
    def put_chunk(self, chunk: Chunk, dimension: Dimension):
        """
        Add a given chunk to the level.

        :param chunk: The :class:`Chunk` to add to the level. It will be added at the location stored in :attr:`Chunk.coordinates`
        :param dimension: The dimension to add the chunk to.
        """
    def delete_chunk(self, cx: int, cz: int, dimension: Dimension):
        """
        Delete a chunk from the level.

        :param cx: The X coordinate of the chunk
        :param cz: The Z coordinate of the chunk
        :param dimension: The dimension to delete the chunk from.
        """
    def extract_structure(self, selection: SelectionGroup, dimension: Dimension) -> api_level.ImmutableStructure:
        """
        Extract the region of the dimension specified by ``selection`` to an :class:`~api_level.ImmutableStructure` class.

        :param selection: The selection to extract.
        :param dimension: The dimension to extract the selection from.
        :return: The :class:`~api_level.ImmutableStructure` containing the extracted region.
        """
    def extract_structure_iter(self, selection: SelectionGroup, dimension: Dimension) -> Generator[float, None, api_level.ImmutableStructure]:
        """
        Extract the region of the dimension specified by ``selection`` to an :class:`~api_level.ImmutableStructure` class.

        Also yields the progress as a float from 0-1

        :param selection: The selection to extract.
        :param dimension: The dimension to extract the selection from.
        :return: The :class:`~api_level.ImmutableStructure` containing the extracted region.
        """
    def paste(self, src_structure: BaseLevel, src_dimension: Dimension, src_selection: SelectionGroup, dst_dimension: Dimension, location: BlockCoordinates, scale: FloatTriplet = ..., rotation: FloatTriplet = ..., include_blocks: bool = ..., include_entities: bool = ..., skip_blocks: Tuple[Block, ...] = ..., copy_chunk_not_exist: bool = ...):
        """Paste a level into this level at the given location.
        Note this command may change in the future.

        :param src_structure: The structure to paste into this structure.
        :param src_dimension: The dimension of the source structure to copy from.
        :param src_selection: The selection to copy from the source structure.
        :param dst_dimension: The dimension to paste the structure into.
        :param location: The location where the centre of the structure will be in the level
        :param scale: The scale in the x, y and z axis. These can be negative to mirror.
        :param rotation: The rotation in degrees around each of the axis.
        :param include_blocks: Include blocks when pasting the structure.
        :param include_entities: Include entities when pasting the structure.
        :param skip_blocks: If a block matches a block in this list it will not be copied.
        :param copy_chunk_not_exist: If a chunk does not exist in the source should it be copied over as air. Always False where level is a World.
        :return:
        """
    def paste_iter(self, src_structure: BaseLevel, src_dimension: Dimension, src_selection: SelectionGroup, dst_dimension: Dimension, location: BlockCoordinates, scale: FloatTriplet = ..., rotation: FloatTriplet = ..., include_blocks: bool = ..., include_entities: bool = ..., skip_blocks: Tuple[Block, ...] = ..., copy_chunk_not_exist: bool = ...) -> Generator[float, None, None]:
        """Paste a structure into this structure at the given location.
        Note this command may change in the future.

        :param src_structure: The structure to paste into this structure.
        :param src_dimension: The dimension of the source structure to copy from.
        :param src_selection: The selection to copy from the source structure.
        :param dst_dimension: The dimension to paste the structure into.
        :param location: The location where the centre of the structure will be in the level
        :param scale: The scale in the x, y and z axis. These can be negative to mirror.
        :param rotation: The rotation in degrees around each of the axis.
        :param include_blocks: Include blocks when pasting the structure.
        :param include_entities: Include entities when pasting the structure.
        :param skip_blocks: If a block matches a block in this list it will not be copied.
        :param copy_chunk_not_exist: If a chunk does not exist in the source should it be copied over as air. Always False where level is a World.
        :return: A generator of floats from 0 to 1 with the progress of the paste operation.
        """
    def get_version_block(self, x: int, y: int, z: int, dimension: Dimension, version: VersionIdentifierType) -> Union[Tuple[Block, BlockEntity], Tuple[Entity, None]]:
        '''
        Get a block at the specified location and convert it to the format of the version specified

        Note the odd return format. In most cases this will return (Block, None) or (Block, BlockEntity) if a block entity is present.

        In select cases (like item frames) it may return (Entity, None)

        :param x: The X coordinate of the desired block
        :param y: The Y coordinate of the desired block
        :param z: The Z coordinate of the desired block
        :param dimension: The dimension of the desired block
        :param version: The version to get the block converted to.

            >>> ("java", (1, 16, 2))  # Java 1.16.2 format
            >>> ("java", 2578)  # Java 1.16.2 format (using the data version)
            >>> ("bedrock", (1, 16, 210))  # Bedrock 1.16.210 format
        :return: The block at the given location converted to the `version` format. Note the odd return format.
        :raises:
            :class:`~amulet.api.errors.ChunkDoesNotExist`: If the chunk does not exist (was deleted or never created)

            :class:`~amulet.api.errors.ChunkLoadError`: If the chunk was not able to be loaded. Eg. If the chunk is corrupt or some error occurred when loading.
        '''
    def set_version_block(self, x: int, y: int, z: int, dimension: Dimension, version: VersionIdentifierType, block: Block, block_entity: BlockEntity = ...):
        '''
        Convert the block and block_entity from the given version format to the universal format and set at the location.

        :param x: The X coordinate of the desired block.
        :param y: The Y coordinate of the desired block.
        :param z: The Z coordinate of the desired block.
        :param dimension: The dimension of the desired block.
        :param version: The version the given ``block`` and ``block_entity`` come from.

            >>> ("java", (1, 16, 2))  # Java 1.16.2 format
            >>> ("java", 2578)  # Java 1.16.2 format (using the data version)
            >>> ("bedrock", (1, 16, 210))  # Bedrock 1.16.210 format
        :param block: The block to set. Must be valid in the specified version.
        :param block_entity: The block entity to set. Must be valid in the specified version.
        :return: The block at the given location converted to the `version` format. Note the odd return format.
        :raises:
            ChunkLoadError: If the chunk was not able to be loaded. Eg. If the chunk is corrupt or some error occurred when loading.
        '''
    def get_native_entities(self, cx: int, cz: int, dimension: Dimension) -> Tuple[EntityList, VersionIdentifierType]:
        """
        Get a list of entities in the native format from a given chunk.
        This currently returns the raw data from the chunk but in the future will convert to the world version format.

        :param cx: The chunk x position
        :param cz: The chunk z position
        :param dimension: The dimension of the chunk.
        :return: A copy of the list of entities and the version format they are in.
        """
    def set_native_entites(self, cx: int, cz: int, dimension: Dimension, entities: Iterable[Entity]):
        """
        Set the entities in the native format.
        Note that the format must be compatible with `level_wrapper.max_world_version`.

        :param cx: The chunk x position
        :param cz: The chunk z position
        :param dimension: The dimension of the chunk.
        :param entities: The entities to set on the chunk.
        """
    @property
    def history_manager(self) -> MetaHistoryManager:
        """The class that manages undoing and redoing changes."""
    def create_undo_point(self, world: bool = ..., non_world: bool = ...) -> bool:
        """
        Create a restore point for all the data that has changed.

        :param world: If True the restore point will include world based data.
        :param non_world: If True the restore point will include data not related to the world.
        :return: If True a restore point was created. If nothing changed no restore point will be created.
        """
    def create_undo_point_iter(self, world: bool = ..., non_world: bool = ...) -> Generator[float, None, bool]:
        """
        Create a restore point for all the data that has changed.

        Also yields progress from 0-1

        :param world: If True the restore point will include world based data.
        :param non_world: If True the restore point will include data not related to the world.
        :return: If True a restore point was created. If nothing changed no restore point will be created.
        """
    @property
    def changed(self) -> bool:
        """Has any data been modified but not saved to disk"""
    def undo(self) -> None:
        """Undoes the last set of changes to the level."""
    def redo(self) -> None:
        """Redoes the last set of changes to the level."""
    def restore_last_undo_point(self) -> None:
        """
        Restore the level to the state it was when self.create_undo_point was last called.

        If an operation errors there may be modifications made that did not get tracked.

        This will revert those changes.
        """
    @property
    def players(self) -> PlayerManager:
        """
        The player container.

        Most methods from :class:`PlayerManager` also exists in the level class.
        """
    def all_player_ids(self) -> Set[str]:
        """
        Returns a set of all player ids that are present in the level.
        """
    def has_player(self, player_id: str) -> bool:
        """
        Is the given player id present in the level

        :param player_id: The player id to check
        :return: True if the player id is present, False otherwise
        """
    def get_player(self, player_id: str) -> Player:
        """
        Gets the :class:`Player` object that belongs to the specified player id

        If no parameter is supplied, the data of the local player will be returned

        :param player_id: The desired player id
        :return: A Player instance
        """
