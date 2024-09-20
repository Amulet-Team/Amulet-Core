from _typeshed import Incomplete
from amulet.resource_pack.bedrock.blockshapes.flat import Flat as Flat

class RedDust(Flat):
    @property
    def blockshape(self) -> str: ...
    @property
    def tint(self) -> tuple[float, float, float]: ...

BlockShape: Incomplete
