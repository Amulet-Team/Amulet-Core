from _typeshed import Incomplete
from amulet.resource_pack.bedrock.blockshapes.furnace import Furnace as Furnace

class FurnaceLit(Furnace):
    @property
    def blockshape(self) -> str: ...
    @property
    def rotation_map(self) -> dict[int, int]: ...

BlockShape: Incomplete
