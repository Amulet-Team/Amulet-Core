from typing import Iterable
from collections.abc import Mapping
from amulet_nbt import NamedTag


class BedrockRawChunk:
    _keys: frozenset[bytes]
    _chunk_data: dict[bytes, bytes]
    _entity_actor: list[NamedTag]
    _unknown_actor: list[NamedTag]

    def __init__(
        self,
        *,
        chunk_keys: Iterable[bytes] = (),
        chunk_data: Mapping[bytes, bytes] | Iterable[tuple[bytes, bytes]] = (),
        entity_actor: Iterable[NamedTag] = (),
        unknown_actor: Iterable[NamedTag] = (),
    ) -> None:
        self._keys = frozenset(chunk_keys)
        self._chunk_data = dict(chunk_data)
        self._entity_actor = list(entity_actor)
        self._unknown_actor = list(unknown_actor)

    @property
    def keys(self) -> frozenset[bytes]:
        """All keys that make up this chunk data."""
        return self._keys

    @property
    def chunk_data(self) -> dict[bytes, bytes]:
        """
        A dictionary mapping all chunk data keys that have the XXXXZZZZ[DDDD] prefix (without the prefix) to the data
        stored in that key.
        """
        return self._chunk_data

    @property
    def entity_actor(self) -> list[NamedTag]:
        """
        A list of entity actor data.
        UniqueID is stripped out. internalComponents is stripped out if there is no other data.
        """
        return self._entity_actor

    @property
    def unknown_actor(self) -> list[NamedTag]:
        """
        A list of actor data that does not fit in the known actor types.
        UniqueID is stripped out.
        internalComponents.{StorageKeyComponent}.StorageKey is replaced with a blank string.
        All keys matching this pattern will get replaced with the real storage key when saving (at least one must exist)
        """
        return self._unknown_actor
