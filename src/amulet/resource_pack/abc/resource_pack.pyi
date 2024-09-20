from amulet.img import missing_pack_icon_path as missing_pack_icon_path

class BaseResourcePack:
    """The base class that all resource packs must inherit from. Defines the base api."""

    def __init__(self, root_dir: str) -> None: ...
    @staticmethod
    def is_valid(pack_path: str) -> bool: ...
    @property
    def valid_pack(self) -> bool:
        """bool - does the pack meet the minimum requirements to be a resource pack"""

    @property
    def root_dir(self) -> str:
        """str - the root directory of the pack"""

    @property
    def pack_description(self) -> str:
        """str - the description as described in the pack"""

    @property
    def pack_icon(self) -> str:
        """str - path to the pack icon"""
