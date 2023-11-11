from .base_leveldb_interface import BaseLevelDBInterface as BaseLevelDBInterface
from _typeshed import Incomplete
from amulet.api.errors import LoaderNoneMatched as LoaderNoneMatched
from typing import Dict, Optional

_interfaces: Optional[Dict[int, BaseLevelDBInterface]]
log: Incomplete

def get_interface(interface_version: int): ...
