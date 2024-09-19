from amulet.resource_pack.bedrock.blockshapes.flat import Flat


class RedDust(Flat):
    @property
    def blockshape(self) -> str:
        return "red_dust"

    @property
    def tint(self) -> tuple[float, float, float]:
        return 1, 0, 0


BlockShape = RedDust()
