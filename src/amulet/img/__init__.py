import os


def _get_path(file: str) -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), file))


missing_no_icon_path = _get_path("missing_no.png")
missing_pack_icon_path = _get_path("missing_pack.png")
missing_world_icon_path = _get_path("missing_world.png")
