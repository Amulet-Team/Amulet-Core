from __future__ import annotations

from typing import Sequence, Self

from amulet.api.data_types import BlockCoordinates
from amulet.api.errors import ChunkLoadError
from .abc import (
    AbstractBaseTranslationFunction,
    JSONCompatible,
    JSONDict,
    Data,
    from_json,
)
from ._state import SrcData, SrcDataExtra, StateData, DstData


class MultiBlock(AbstractBaseTranslationFunction):
    # Class variables
    Name = "multiblock"
    _instances: dict[MultiBlock, MultiBlock] = {}

    _blocks: tuple[tuple[BlockCoordinates, AbstractBaseTranslationFunction], ...]

    def __new__(
        cls, blocks: Sequence[tuple[BlockCoordinates, AbstractBaseTranslationFunction]]
    ) -> MultiBlock:
        self = super().__new__(cls)
        self._blocks = tuple[
            tuple[BlockCoordinates, AbstractBaseTranslationFunction], ...
        ](blocks)
        for coords, func in self._blocks:
            if (
                not isinstance(coords, tuple)
                and len(coords) == 3
                and all(isinstance(v, int) for v in coords)
            ):
                raise TypeError
            assert isinstance(func, AbstractBaseTranslationFunction)
        return cls._instances.setdefault(self, self)

    def _data(self) -> Data:
        return self._blocks

    @classmethod
    def from_json(cls, data: JSONCompatible) -> Self:
        assert isinstance(data, dict)
        assert data.get("function") == "multiblock"
        options = data["options"]
        assert isinstance(options, list)
        blocks: list[tuple[BlockCoordinates, AbstractBaseTranslationFunction]] = []
        for block in options:
            assert isinstance(block, dict)
            raw_coords = block["coords"]
            assert isinstance(raw_coords, list)
            x = raw_coords[0]
            y = raw_coords[1]
            z = raw_coords[2]
            assert isinstance(x, int)
            assert isinstance(y, int)
            assert isinstance(z, int)
            coords = (x, y, z)
            function = from_json(block["functions"])
            blocks.append((coords, function))
        return cls(blocks)

    def to_json(self) -> JSONDict:
        return {
            "function": "multiblock",
            "options": [
                {"coords": list(coords), "functions": func.to_json()}
                for coords, func in self._blocks
            ],
        }

    def run(self, src: SrcData, state: StateData, dst: DstData) -> None:
        dst.cacheable = False
        if src.extra is None:
            dst.extra_needed = True
            return

        for (dx, dy, dz), func in self._blocks:
            rx, ry, rz = state.relative_location
            new_relative_location = (
                rx + dx,
                ry + dy,
                rz + dz,
            )
            try:
                new_block, new_block_entity = src.extra.get_block_callback(
                    new_relative_location
                )
            except ChunkLoadError:
                continue
            else:
                ax, ay, az = src.extra.absolute_coordinates
                new_absolute_location = (
                    ax + dx,
                    ay + dy,
                    az + dz,
                )
                # src is now the block at the new location
                new_src = SrcData(
                    new_block,
                    None if new_block_entity is None else new_block_entity.nbt,
                    SrcDataExtra(
                        new_absolute_location,
                        src.extra.get_block_callback,
                    ),
                )
                new_state = StateData(new_relative_location)
                func.run(new_src, new_state, dst)
