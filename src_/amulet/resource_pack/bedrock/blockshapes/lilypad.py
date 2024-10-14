from amulet.resource_pack.bedrock.blockshapes.flat import Flat


class LilyPad(Flat):
    @property
    def blockshape(self) -> str:
        return "lilypad"

    @property
    def tint(self) -> tuple[float, float, float]:
        return 0, 1, 0


BlockShape = LilyPad()
