from .anvil_world import AnvilFormat as AnvilFormat
from amulet.utils.format_utils import check_all_exist as check_all_exist

class AnvilForgeFormat(AnvilFormat):
    """
    This FormatWrapper class is a modification on the :class:`AnvilFormat` class that separates Forge worlds from vanilla worlds.

    Currently there is no extra logic here but this should extend the :class:`AnvilFormat` class to support Forge worlds.
    """
    @staticmethod
    def is_valid(token) -> bool: ...
    @property
    def game_version_string(self) -> str: ...
export = AnvilForgeFormat
