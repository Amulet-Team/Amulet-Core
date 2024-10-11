from amulet.resource_pack.bedrock.blockshapes.furnace import Furnace


class FurnaceLit(Furnace):
    @property
    def blockshape(self) -> str:
        return "furnace_lit"

    @property
    def rotation_map(self) -> dict[int, int]:
        return {2: 3, 3: 1, 4: 2, 5: 0}


BlockShape = FurnaceLit()
