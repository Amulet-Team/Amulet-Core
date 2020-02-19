from typing import Union, Dict, List, Tuple
from amulet import log
import weakref

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amulet.api.chunk import Chunk

states = {
    "empty": [["j13", "j14"], -1],
    "structure_starts": [["j14"], -0.9],
    "structure_references": [["j14"], -0.8],
    "biomes": [["j14"], -0.7],
    "noise": [["j14"], -0.6],
    "base": [["j13"], -0.5],
    "surface": [["j14"], -0.5],
    "carved": [["j13"], -0.4],
    "carvers": [["j14"], -0.4],
    "liquid_carved": [["j13"], -0.3],
    "liquid_carvers": [["j14"], -0.3],
    "decorated": [["j13"], -0.2],
    "features": [["j14"], -0.2],
    "lighted": [["j13"], -0.1],
    "light": [["j14"], -0.1],
    # 0.0	needs ticked
    # 1.0	needs population
    "mobs_spawned": [["j13"], 1.1],
    "spawn": [["j14"], 1.1],
    "finalized": [["j13"], 1.5],
    "heightmaps": [["j14"], 1.5],
    "fullchunk": [["j13"], 1.9],
    "postprocessed": [["j13"], 2.0],
    "full": [["j14"], 2.0],
    # 2.0	done
}

versions: Dict[str, List[Tuple[float, str]]] = {}
for key, val in states.items():
    for version_ in val[0]:
        versions.setdefault(version_, []).append((val[1], key))
for data in versions.values():
    data.sort(key=lambda val_: val_[0])
    data.reverse()


class Status:
    def __init__(self, parent_chunk: "Chunk"):
        self._parent_chunk = weakref.ref(parent_chunk)
        self._value = 2.0

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: Union[float, int, str]):
        if isinstance(value, float):
            self._value = value
        elif isinstance(value, int):
            self._value = float(value)
        elif isinstance(value, str) and value in states:
            self._value = states[value][1]
        else:
            log.error(
                f"Unrecognised chunk state {value}. Defaulting to fully generated.\nIf this is a new version report it to the developers."
            )
            self._value = 2.0

    def as_type(self, version: str) -> Union[int, float, str]:
        if version == "float":
            return self._value

        elif version in versions:  # Java 1.13/1.14
            value = next((v for v in versions[version] if v[0] <= self._value), None)
            if value is None:
                value = next((v for v in versions[version] if v[0] <= 2.0), None)
            return value[1]

        elif version == "b":  # Bedrock (0, 1 or 2)
            return int(max(min(2, self._value), 0))
