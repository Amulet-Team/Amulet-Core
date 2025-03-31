from amulet.image import missing_pack_icon_path


class BaseResourcePack:
    """The base class that all resource packs must inherit from. Defines the base api."""

    def __init__(self, root_dir: str):
        self._valid_pack = False
        self._root_dir = root_dir
        self._pack_description = ""
        self._pack_icon = missing_pack_icon_path

    def __repr__(self) -> str:
        raise NotImplementedError

    @staticmethod
    def is_valid(pack_path: str) -> bool:
        raise NotImplementedError

    @property
    def valid_pack(self) -> bool:
        """bool - does the pack meet the minimum requirements to be a resource pack"""
        return self._valid_pack

    @property
    def root_dir(self) -> str:
        """str - the root directory of the pack"""
        return self._root_dir

    @property
    def pack_description(self) -> str:
        """str - the description as described in the pack"""
        return self._pack_description

    @property
    def pack_icon(self) -> str:
        """str - path to the pack icon"""
        return self._pack_icon
