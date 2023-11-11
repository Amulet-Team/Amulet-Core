from _typeshed import Incomplete
from amulet_nbt import NamedTag as NamedTag
from typing import Iterable, Optional, Union

class BedrockRawChunk:
    _keys: Incomplete
    _chunk_data: Incomplete
    _entity_actor: Incomplete
    _unknown_actor: Incomplete
    def __init__(self, *, chunk_keys: Iterable[bytes] = ..., chunk_data: Union[dict[bytes, bytes], Iterable[tuple[bytes, bytes]]] = ..., entity_actor: Iterable[NamedTag] = ..., unknown_actor: Iterable[NamedTag] = ...) -> None: ...
    @property
    def keys(self) -> frozenset[bytes]:
        """All keys that make up this chunk data."""
    @property
    def chunk_data(self) -> dict[bytes, Optional[bytes]]:
        """
        A dictionary mapping all chunk data keys that have the XXXXZZZZ[DDDD] prefix (without the prefix) to the data
        stored in that key.
        """
    @property
    def entity_actor(self) -> list[NamedTag]:
        """
        A list of entity actor data.
        UniqueID is stripped out. internalComponents is stripped out if there is no other data.
        """
    @property
    def unknown_actor(self) -> list[NamedTag]:
        """
        A list of actor data that does not fit in the known actor types.
        UniqueID is stripped out.
        internalComponents.{StorageKeyComponent}.StorageKey is replaced with a blank string.
        All keys matching this pattern will get replaced with the real storage key when saving (at least one must exist)
        """
