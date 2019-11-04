from typing import Tuple

# this is a dictionary of the first and last times each chunk version was written by a game version
chunk_version_to_max_version = {
    0: ((1, 0, 0), (1, 0, 0)),
    1: ((1, 0, 0), (1, 0, 0)),
    2: ((1, 0, 0), (1, 0, 0)),
    3: ((1, 0, 0), (1, 0, 0)),
    4: ((1, 0, 0), (1, 0, 0)),
    5: ((1, 0, 0), (1, 0, 0)),
    6: ((1, 0, 0), (1, 0, 0)),
    7: ((1, 5, 0), (1, 5, 1)),
    8: ((1, 0, 0), (1, 0, 0)),
    9: ((1, 8, 0), (1, 8, 0)),
    10: ((1, 10, 0), (1, 10, 1)),
    11: ((1, 0, 0), (1, 0, 0)),
    12: ((1, 0, 0), (1, 0, 0)),
    13: ((1, 0, 0), (1, 0, 0)),
    14: ((1, 11, 1), (1, 11, 4)),
    15: ((1, 13, 0), (999, 999, 999))
}  # TODO: fill this list with the actual last game version number each chunk verison was last used in


def chunk_to_game_version(max_game_version: Tuple[int, int, int], chunk_version: int) -> Tuple[int, int, int]:
    return min(chunk_version_to_max_version[chunk_version][1], max_game_version)


def game_to_chunk_version(max_game_version: Tuple[int, int, int]) -> int:
    for chunk_version, (first, last) in chunk_version_to_max_version.items():
        if first <= max_game_version <= last:
            return chunk_version
