import os
import json
import itertools
from typing import Any
from types import MappingProxyType
from collections.abc import Iterable, Mapping, Iterator
import urllib.request
import urllib.parse
from dataclasses import dataclass
from packaging.version import Version, InvalidVersion
from packaging.specifiers import SpecifierSet
from packaging.requirements import Requirement
from functools import lru_cache


github_api_url = os.environ.get("GITHUB_API_URL", "https://api.github.com")


@lru_cache(maxsize=None)
def _get_github_releases(repo: str, page: int):
    print(f"Github REST request {repo} page {page}")
    query = urllib.parse.urlencode({"per_page": 100, "page": page})
    url = f"{github_api_url}/repos/{repo}/releases?{query}"
    headers = {"Accept": "application/vnd.github+json"}
    if os.environ.get("REST_TOKEN"):
        headers["Authorization"] = f"token {os.environ.get('REST_TOKEN')}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
    return data


@lru_cache(maxsize=None)
def _get_tags(repo: str) -> Iterator[Version]:
    for page in itertools.count(1):
        data = _get_github_releases(repo, page)
        if not data:
            break
        for release in data:
            try:
                v = Version(release["tag_name"])
            except InvalidVersion:
                continue
            else:
                yield v


def _get_compatible_tags(repo: str, specifier: SpecifierSet) -> Iterator[Version]:
    return (v for v in _get_tags(repo) if v in specifier)


@dataclass(frozen=True)
class Library:
    lib_name: str
    repo_name: str


@lru_cache(maxsize=None)
def _exec_module(module_str: str) -> dict[str, Any]:
    m = {}
    exec(module_str, m, m)
    return m


@lru_cache(maxsize=None)
def _get_requirements_module(repo: str, tag: str) -> dict[str, Any]:
    url = f"https://raw.githubusercontent.com/{repo}/{tag}/requirements.py"
    with urllib.request.urlopen(url) as resp:
        module_str = resp.read().decode()
    return _exec_module(module_str)


def parse_requirements(requirements: Iterable[str]) -> Mapping[str, SpecifierSet]:
    split_requirements = {}
    for req_s in requirements:
        req = Requirement(req_s)
        split_requirements[_fix_library_name(req.name)] = req.specifier
    return MappingProxyType(split_requirements)


@lru_cache(maxsize=None)
def _get_requirements(repo: str, tag: str) -> Mapping[str, SpecifierSet]:
    m = _get_requirements_module(repo, tag)
    return parse_requirements(m["get_runtime_dependencies"]())


@lru_cache(maxsize=None)
def _get_pypi_releases(lib_name: str) -> MappingProxyType[str, Any]:
    print(f"Getting PyPI releases for {lib_name}")
    url = f"https://pypi.org/pypi/{lib_name}/json"
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read().decode())
    return data["releases"]


class NoValidVersion(Exception):
    pass


@lru_cache(maxsize=None)
def _get_pypi_release(lib_name: str, specifier: SpecifierSet) -> Version:
    releases = _get_pypi_releases(lib_name)
    for version_str, files in releases.items():
        version = Version(version_str)
        # release must match the specifier and have a source distribution
        if version in specifier and any(
            file.get("packagetype", None) == "sdist" for file in files
        ):
            return version
    raise NoValidVersion


def _fix_library_name(name: str) -> str:
    return name.replace("_", "-")


def _find_compatible_libraries(
    libraries: tuple[Library, ...],
    requirements: Mapping[str, SpecifierSet],
    libraries_todo: tuple[Library, ...],
    libraries_frozen: Mapping[str, Version] = MappingProxyType({}),
) -> Mapping[str, Version]:
    # Get the library to freeze and the libraries left to freeze
    library_freeze = libraries_todo[0]
    libraries_todo = tuple(libraries_todo[1:])

    # Verify that this library has not already been frozen
    if library_freeze.lib_name in libraries_frozen:
        raise RuntimeError(f"Library {library_freeze.lib_name} listed more than once.")

    processed_requirement_configurations = []

    # Iterate through all versions that match the specifier
    for v in _get_compatible_tags(
        library_freeze.repo_name,
        requirements.get(library_freeze.lib_name, SpecifierSet()),
    ):
        print(f"Trying {library_freeze.lib_name}=={v}")
        # Get the requirements this library adds
        library_requirements = _get_requirements(library_freeze.repo_name, str(v))

        # If the library_requirements match a previous version, skip
        if library_requirements in processed_requirement_configurations:
            continue
        else:
            processed_requirement_configurations.append(library_requirements)

        # Extend the existing requirements.
        new_requirements = dict(requirements)
        for name, specifier in library_requirements.items():
            if name in new_requirements:
                specifier = new_requirements[name] & specifier

            # check the frozen requirements are still valid.
            if name in libraries_frozen and libraries_frozen[name] not in specifier:
                raise NoValidVersion

            new_requirements[name] = specifier

        # Add the library to the frozen libraries
        new_libraries_frozen = {**libraries_frozen, library_freeze.lib_name: v}

        if libraries_todo:
            # if we have more libraries to freeze go to the next one
            try:
                return _find_compatible_libraries(
                    libraries,
                    MappingProxyType(new_requirements),
                    libraries_todo,
                    MappingProxyType(new_libraries_frozen),
                )
            except NoValidVersion:
                # If dependency resolution failed below this, try the next version of the library
                continue
        else:
            # Make sure all libraries have a compatible pypi release
            try:
                for name, specifier in new_requirements.items():
                    if name not in new_libraries_frozen:
                        new_libraries_frozen[name] = _get_pypi_release(name, specifier)
            except NoValidVersion:
                continue
            # No more libraries to freeze.
            return MappingProxyType(new_libraries_frozen)
    # Raise if no version matched
    raise NoValidVersion


def find_compatible_libraries(
    libraries: Iterable[tuple[str, str]], requirements: Iterable[str]
) -> Mapping[str, Version]:
    libraries_ = tuple(
        Library(_fix_library_name(lib_name), repo_name)
        for lib_name, repo_name in libraries
    )
    return _find_compatible_libraries(
        libraries_,
        parse_requirements(requirements),
        libraries_,
    )


def find_and_save_compatible_libraries(
    compiled_library_data: Iterable[tuple[str, str]], requirements: Iterable[str]
) -> None:
    libraries = find_compatible_libraries(compiled_library_data, requirements)
    print(libraries)
    with open(
        os.path.join(os.path.dirname(__file__), "libraries.json"), "w", encoding="utf-8"
    ) as f:
        json.dump({name: str(specifier) for name, specifier in libraries.items()}, f)
