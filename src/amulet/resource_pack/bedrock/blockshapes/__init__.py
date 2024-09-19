import importlib
import pkgutil

from .base_blockshape import BaseBlockShape

BlockShapeClasses: dict[str, BaseBlockShape] = {}
_class_names = set()


def _load_blockshape(module_name: str) -> None:
    blockshape_module = importlib.import_module(module_name)
    if hasattr(blockshape_module, "BlockShape"):
        blockshape = getattr(blockshape_module, "BlockShape")
        if isinstance(blockshape, BaseBlockShape):
            if blockshape.blockshape in BlockShapeClasses:
                print(f"Name conflict with blockshape {blockshape.blockshape}")
            if blockshape.__class__.__name__ in _class_names:
                print(f"Duplicate class name {blockshape.__class__.__name__}")
            else:
                _class_names.add(blockshape.__class__.__name__)
            BlockShapeClasses[blockshape.blockshape] = blockshape


def _load_blockshapes() -> None:
    package_prefix = __name__ + "."

    for _, name, _ in pkgutil.walk_packages(__path__, package_prefix):
        _load_blockshape(name)


_load_blockshapes()
