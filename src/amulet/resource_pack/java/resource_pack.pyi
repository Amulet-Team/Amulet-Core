from amulet.resource_pack.abc import BaseResourcePack as BaseResourcePack

class JavaResourcePack(BaseResourcePack):
    """A class to hold the bare bones information about the resource pack.
    Holds the pack format, description and if the pack is valid.
    This information can be used in a viewer to display the packs to the user."""

    def __init__(self, resource_pack_path: str) -> None: ...
    @staticmethod
    def is_valid(pack_path: str) -> bool: ...
    @property
    def pack_format(self) -> int:
        """int - pack format number"""
