from amulet.resource_pack.bedrock.blockshapes.cross_texture import (
    Cross,
)


class CrossGreen(Cross):
    @property
    def blockshape(self) -> str:
        return "cross_texture_green"

    @property
    def tint(self) -> tuple[float, float, float]:
        return 0, 1, 0


BlockShape = CrossGreen()
