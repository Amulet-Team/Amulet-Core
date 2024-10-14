import os

# import shutil
# import zipfile
# import json
# from urllib.request import urlopen
# import io
from typing import Generator, Optional, TypeVar, Any
import logging

from amulet.resource_pack import BedrockResourcePack

T = TypeVar("T")

log = logging.getLogger(__name__)


def generator_unpacker(gen: Generator[Any, Any, T]) -> T:
    try:
        while True:
            next(gen)
    except StopIteration as e:
        return e.value  # type: ignore


def get_latest() -> BedrockResourcePack:
    return generator_unpacker(get_latest_iter())


def get_latest_iter() -> Generator[float, None, BedrockResourcePack]:
    vanilla_rp_path = os.path.join(
        os.environ["CACHE_DIR"], "resource_packs", "bedrock", "vanilla"
    )
    yield 0
    # new_version = launcher_manifest["latest"]["release"]
    # if new_version is None:
    #     if os.path.isdir(vanilla_rp_path):
    #         log.error(
    #             "Could not download the launcher manifest. The resource pack seems to be present so using that."
    #         )
    #     else:
    #         log.error(
    #             "Could not download the launcher manifest. The resource pack is not present, blocks may not be rendered correctly."
    #         )
    # else:
    #     if os.path.isdir(vanilla_rp_path):
    #         if os.path.isfile(os.path.join(vanilla_rp_path, "version")):
    #             with open(os.path.join(vanilla_rp_path, "version")) as f:
    #                 old_version = f.read()
    #             if old_version != new_version:
    #                 yield from _remove_and_download_iter(vanilla_rp_path, new_version)
    #         else:
    #             yield from _remove_and_download_iter(vanilla_rp_path, new_version)
    #     else:
    #         yield from _remove_and_download_iter(vanilla_rp_path, new_version)
    return BedrockResourcePack(vanilla_rp_path)


_bedrock_vanilla_fix: Optional[BedrockResourcePack] = None
_bedrock_vanilla_latest: Optional[BedrockResourcePack] = None


def get_bedrock_vanilla_fix() -> BedrockResourcePack:
    global _bedrock_vanilla_fix
    if _bedrock_vanilla_fix is None:
        _bedrock_vanilla_fix = BedrockResourcePack(
            os.path.join(os.path.dirname(__file__), "bedrock_vanilla_fix")
        )
    return _bedrock_vanilla_fix


def get_bedrock_vanilla_latest() -> BedrockResourcePack:
    global _bedrock_vanilla_latest
    if _bedrock_vanilla_latest is None:
        _bedrock_vanilla_latest = get_latest()
    return _bedrock_vanilla_latest


def get_bedrock_vanilla_latest_iter() -> Generator[float, None, BedrockResourcePack]:
    global _bedrock_vanilla_latest
    if _bedrock_vanilla_latest is None:
        _bedrock_vanilla_latest = yield from get_latest_iter()
    return _bedrock_vanilla_latest


# def _remove_and_download(path, version):
#     for _ in _remove_and_download_iter(path, version):
#         pass


# def _remove_and_download_iter(path, version) -> Generator[float, None, None]:
#     if os.path.isdir(path):
#         shutil.rmtree(path, ignore_errors=True)
#     exists = yield from download_resources_iter(path, version)
#     if exists:
#         with open(os.path.join(path, "version"), "w") as f:
#             f.write(version)


# def download_resources(path, version) -> bool:
#     return generator_unpacker(download_resources_iter(path, version))


# def download_resources_iter(
#     path, version, chunk_size=4096
# ) -> Generator[float, None, bool]:
#     log.info(f"Downloading Bedrock resource pack for version {version}")
#     version_url = next(
#         (v["url"] for v in launcher_manifest["versions"] if v["id"] == version), None
#     )
#     if version_url is None:
#         log.error(f"Could not find Bedrock resource pack for version {version}.")
#         return False
#
#     try:
#         version_manifest = json.load(urlopen(version_url))
#         version_client_url = version_manifest["downloads"]["client"]["url"]
#
#         response = urlopen(version_client_url)
#         data = []
#         data_size = int(response.headers["content-length"].strip())
#         index = 0
#         chunk = b"hello"
#         while chunk:
#             chunk = response.read(chunk_size)
#             data.append(chunk)
#             index += 1
#             yield min(1.0, (index * chunk_size) / (data_size * 2))
#
#         client = zipfile.ZipFile(io.BytesIO(b"".join(data)))
#         paths = [fpath for fpath in client.namelist() if fpath.startswith("assets/")]
#         path_count = len(paths)
#         for path_index, fpath in enumerate(paths):
#             if not path_index % 30:
#                 yield path_index / (path_count * 2) + 0.5
#             client.extract(fpath, path)
#         client.extract("pack.mcmeta", path)
#         client.extract("pack.png", path)
#
#     except:
#         log.error(
#             f"Failed to download and extract the Bedrock resource pack for version {version}. Make sure you have a connection to the internet.",
#             exc_info=True,
#         )
#         return False
#     log.info(f"Finished downloading Bedrock resource pack for version {version}")
#     return True
