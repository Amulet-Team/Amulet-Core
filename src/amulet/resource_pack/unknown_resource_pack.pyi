from amulet.resource_pack.abc.resource_pack import BaseResourcePack as BaseResourcePack

class UnknownResourcePack(BaseResourcePack):
    @staticmethod
    def is_valid(pack_path: str) -> bool: ...
