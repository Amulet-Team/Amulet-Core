from amulet.block import Block
from amulet.resource_pack.bedrock.blockshapes.partial_block import (
    PartialBlock,
)
from amulet_nbt import AbstractBaseIntTag, IntTag


class Cake(PartialBlock):
    def is_valid(self, block: Block) -> bool:
        return isinstance(block.properties.get("bite_counter"), IntTag)

    @property
    def blockshape(self) -> str:
        return "cake"

    def bounds(
        self, block: Block
    ) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
        bite_count = block.properties["bite_counter"]
        return (
            (
                1 / 16
                + (
                    bite_count.py_int
                    if isinstance(bite_count, AbstractBaseIntTag)
                    else 0
                )
                * 2
                / 16,
                15 / 16,
            ),
            (0, 0.5),
            (1 / 16, 15 / 16),
        )

    def texture_index(self, block: Block, aux_value: int) -> int:
        bite_counter = block.properties["bite_counter"]
        assert isinstance(bite_counter, AbstractBaseIntTag)
        return min(1, bite_counter.py_int)

    @property
    def do_not_cull(self) -> tuple[bool, bool, bool, bool, bool, bool]:
        return False, True, True, True, True, True


BlockShape = Cake()
