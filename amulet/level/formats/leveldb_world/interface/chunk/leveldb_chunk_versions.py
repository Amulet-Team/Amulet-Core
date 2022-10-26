from typing import Dict, Tuple
from amulet.api.data_types import VersionNumberTuple

# This is a dictionary of the first and last times each chunk version was written by a game version
# It is used to convert the chunk version to the game version that could have saved that chunk.
# It is also used to convert back to the chunk version when saving based on the game version.
chunk_version_to_max_version: Dict[
    int, Tuple[VersionNumberTuple, VersionNumberTuple]
] = {
    0: ((0, 9, 0, 0), (0, 9, 1, 9999)),
    1: ((0, 9, 2, 0), (0, 9, 4, 9999)),
    2: ((0, 9, 5, 0), (0, 16, 999, 9999)),
    3: ((0, 17, 0, 0), (0, 17, 999, 9999)),
    4: ((0, 18, 0, 0), (0, 18, 0, 0)),
    5: ((0, 18, 0, 0), (1, 1, 999, 9999)),
    6: ((1, 2, 0, 0), (1, 2, 0, 0)),
    7: ((1, 2, 0, 0), (1, 2, 999, 9999)),
    8: ((1, 3, 0, 0), (1, 7, 999, 9999)),
    9: ((1, 8, 0, 0), (1, 8, 999, 9999)),
    10: ((1, 9, 0, 0), (1, 9, 999, 9999)),
    11: ((1, 10, 0, 0), (1, 10, 999, 9999)),
    12: ((1, 11, 0, 0), (1, 11, 0, 9999)),
    13: ((1, 11, 1, 0), (1, 11, 1, 9999)),
    14: ((1, 11, 2, 0), (1, 11, 999, 999)),
    15: ((1, 12, 0, 0), (1, 15, 999, 9999)),
    16: ((1, 15, 999, 9999), (1, 15, 999, 9999)),
    17: ((1, 15, 999, 9999), (1, 15, 999, 9999)),
    18: ((1, 16, 0, 0), (1, 16, 0, 0)),
    19: ((1, 16, 0, 0), (1, 16, 100, 55)),
    20: ((1, 16, 100, 56), (1, 16, 100, 57)),
    21: ((1, 16, 100, 58), (1, 16, 210, 0)),
    22: ((1, 16, 210, 0), (1, 17, 999, 999)),  # caves and cliffs disabled
    # used with experimental features
    23: ((1, 17, 0, 0), (1, 17, 0, 0)),  # ?
    24: ((1, 17, 0, 0), (1, 17, 0, 0)),  # ?
    25: ((1, 17, 0, 0), (1, 17, 20, 999)),  # 1.17.0-20 caves and cliffs enabled
    26: ((1, 17, 0, 0), (1, 17, 0, 0)),  # ?
    27: ((1, 17, 0, 0), (1, 17, 0, 0)),  # ?
    28: ((1, 17, 0, 0), (1, 17, 0, 0)),  # ?
    29: ((1, 17, 30, 0), (1, 17, 30, 999)),  # 1.17.30 caves and cliffs enabled
    30: ((1, 17, 0, 0), (1, 17, 0, 0)),  # ?
    31: ((1, 17, 40, 0), (1, 17, 999, 999)),  # 1.17.40 caves and cliffs enabled
    32: ((1, 17, 0, 0), (1, 17, 0, 0)),  # ?
    33: ((1, 17, 0, 0), (1, 17, 0, 0)),  # ?
    34: ((1, 17, 0, 0), (1, 17, 0, 0)),  # ?
    35: ((1, 17, 0, 0), (1, 17, 0, 0)),  # ?
    36: ((1, 17, 0, 0), (1, 17, 0, 0)),  # ?
    37: ((1, 17, 0, 0), (1, 17, 0, 0)),  # ?
    38: ((1, 17, 0, 0), (1, 17, 0, 0)),  # ?
    # continue without experimental gameplay
    39: ((1, 18, 0, 0), (1, 18, 29, 999)),
    40: ((1, 18, 30, 0), (999, 999, 999, 999)),
}  # TODO: fill this list with the actual last game version number each chunk version was last used in


def chunk_to_game_version(
    max_game_version: VersionNumberTuple, chunk_version: int
) -> VersionNumberTuple:
    """Find the game version to use based on the chunk version."""
    return min(chunk_version_to_max_version[chunk_version][1], max_game_version)


def game_to_chunk_version(max_game_version: VersionNumberTuple, cnc=False) -> int:
    """Get the chunk version that should be used for the given game version number."""
    cnc = cnc or max_game_version >= (1, 18, 0)
    for chunk_version, (first, last) in chunk_version_to_max_version.items():
        if (
            first <= max_game_version <= last  # if the version is in the range
            and cnc
            == (
                chunk_version > 22
            )  # and it is in the correct range (caves and cliffs or not)
        ):
            return chunk_version
