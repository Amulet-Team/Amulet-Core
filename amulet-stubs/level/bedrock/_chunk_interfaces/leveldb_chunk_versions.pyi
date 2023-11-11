from amulet.api.data_types import VersionNumberTuple as VersionNumberTuple
from typing import Dict, Tuple

chunk_version_to_max_version: Dict[int, Tuple[VersionNumberTuple, VersionNumberTuple]]

def chunk_to_game_version(max_game_version: VersionNumberTuple, chunk_version: int) -> VersionNumberTuple:
    """Find the game version to use based on the chunk version."""
def game_to_chunk_version(max_game_version: VersionNumberTuple, cnc: bool = ...) -> int:
    """Get the chunk version that should be used for the given game version number."""
