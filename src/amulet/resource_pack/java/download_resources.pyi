from typing import Any, Generator, TypeVar

from _typeshed import Incomplete
from amulet.resource_pack import JavaResourcePack as JavaResourcePack

T = TypeVar("T")
log: Incomplete
launcher_manifest: dict | None
INCLUDE_SNAPSHOT: bool

def get_launcher_manifest() -> dict: ...
def generator_unpacker(gen: Generator[Any, Any, T]) -> T: ...
def get_latest() -> JavaResourcePack: ...
def get_latest_iter() -> Generator[float, None, JavaResourcePack]:
    """Download the latest resource pack if required.

    :return: The loaded Java resource pack.
    :raises:
        Exception: If the
    """

def get_java_vanilla_fix() -> JavaResourcePack: ...
def get_java_vanilla_latest() -> JavaResourcePack: ...
def get_java_vanilla_latest_iter() -> Generator[float, None, JavaResourcePack]: ...
def download_with_retry(
    url: str, chunk_size: int = 4096, attempts: int = 5
) -> Generator[float, None, bytes]: ...
def download_resources(path: str, version: str) -> None: ...
def download_resources_iter(
    path: str, version: str, chunk_size: int = 4096
) -> Generator[float, None, None]: ...
