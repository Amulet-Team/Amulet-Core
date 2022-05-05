from typing import Dict, Union, Iterable, Tuple, List, Optional
from amulet_nbt import NBTFile


class ChunkData(Dict[bytes, Optional[bytes]]):
    def __init__(
        self,
        chunk_data: Union[Dict[bytes, bytes], Iterable[Tuple[bytes, bytes]]] = (),
        *,
        entity_actor: Iterable[NBTFile] = (),
        unknown_actor: Iterable[NBTFile] = (),
    ):
        super().__init__(chunk_data)
        self._entity_actor = list(entity_actor)
        self._unknown_actor = list(unknown_actor)

    @property
    def entity_actor(self) -> List[NBTFile]:
        """
        A list of entity actor data.
        UniqueID is stripped out. internalComponents is stripped out if there is no other data.
        """
        return self._entity_actor

    @property
    def unknown_actor(self) -> List[NBTFile]:
        """
        A list of actor data that does not fit in the known actor types.
        UniqueID is stripped out.
        internalComponents.{StorageKeyComponent}.StorageKey is replaced with a blank string.
        All keys matching this pattern will get replaced with the real storage key when saving (at least one must exist)
        """
        return self._unknown_actor
