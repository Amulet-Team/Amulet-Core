from _typeshed import Incomplete
from amulet.resource_pack.bedrock.blockshapes.cross_texture import Cross as Cross

class CrossGreen(Cross):
    @property
    def blockshape(self) -> str: ...
    @property
    def tint(self) -> tuple[float, float, float]: ...

BlockShape: Incomplete
