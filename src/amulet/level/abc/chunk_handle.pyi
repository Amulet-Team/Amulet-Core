from __future__ import annotations

import amulet.chunk
import amulet.utils.lock
import amulet.utils.signal

__all__ = ["ChunkHandle"]

class ChunkHandle:
    def delete_chunk(self) -> None:
        """
        Delete the chunk from the level.
        You must acquire the chunk lock before deleting.
        """

    def exists(self) -> bool:
        """
        Does the chunk exist. This is a quick way to check if the chunk exists without loading it.

        This state may change if the lock is not acquired.

        :return: True if the chunk exists. Calling get on this chunk handle may still throw ChunkLoadError
        """

    def get_chunk(self) -> amulet.chunk.Chunk:
        """
        Get a unique copy of the chunk data.

        If you want to edit the chunk, use :meth:`edit` instead.

        If you only want to access/modify parts of the chunk data you can specify the components you want to load.
        This makes it faster because you don't need to load unneeded parts.

        :param components: None to load all components or an iterable of component strings to load.
        :return: A unique copy of the chunk data.
        """

    def set_chunk(self, chunk: amulet.chunk.Chunk) -> None:
        """
        Overwrite the chunk data.
        You must acquire the chunk lock before setting.
        If you want to edit the chunk, use :meth:`edit` instead.

        :param chunk: The chunk data to set.
        """

    @property
    def changed(self) -> amulet.utils.signal.Signal[()]:
        """
        Signal emitted when the chunk data changes.
        """

    @property
    def cx(self) -> int:
        """
        The chunk x coordinate.
        """

    @property
    def cz(self) -> int:
        """
        The chunk z coordinate.
        """

    @property
    def dimension_id(self) -> str:
        """
        The dimension identifier this chunk is from.
        """

    @property
    def lock(self) -> amulet.utils.lock.OrderedLock:
        """
        The public lock.
        Thread safe.
        """
