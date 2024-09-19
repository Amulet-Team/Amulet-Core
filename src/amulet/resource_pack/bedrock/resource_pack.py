import os
import json

from amulet.resource_pack.abc import BaseResourcePack
from amulet.utils import comment_json


class BedrockResourcePack(BaseResourcePack):
    """A class to hold the bare-bones information about the resource pack.
    Holds the pack format, description and if the pack is valid.
    This information can be used in a viewer to display the packs to the user."""

    def __init__(self, resource_pack_path: str):
        super().__init__(resource_pack_path)
        meta_path = os.path.join(resource_pack_path, "manifest.json")
        if os.path.isfile(meta_path):
            try:
                with open(meta_path) as f:
                    pack_mcmeta = comment_json.load(f)
            except json.JSONDecodeError:
                pass
            else:
                if isinstance(pack_mcmeta, dict):
                    header = pack_mcmeta.get("header", None)
                    if isinstance(header, dict):
                        description = header.get("description", None)
                        if isinstance(description, str):
                            self._pack_description = description
                            self._valid_pack = True

        pack_icon_path = os.path.join(resource_pack_path, "pack_icon.png")
        if os.path.isfile(pack_icon_path):
            self._pack_icon = pack_icon_path

    @staticmethod
    def is_valid(pack_path: str) -> bool:
        return os.path.isfile(os.path.join(pack_path, "manifest.json"))

    def __repr__(self) -> str:
        return f"BedrockResourcePack({self._root_dir})"
