import os
import glob
import importlib.util
import sys
import subprocess
import re
from mypy import stubgen
import pybind11_stubgen
from pybind11_stubgen.structs import Identifier
from pybind11_stubgen.parser.mixins.filter import FilterClassMembers

UnionPattern = re.compile(
    r"^(?P<variable>[a-zA-Z_][a-zA-Z0-9_]*): types\.UnionType\s*#\s*value = (?P<value>.*)$",
    flags=re.MULTILINE,
)
VersionPattern = re.compile(r"(?P<var>[a-zA-Z0-9_].*): str = '.*?'")


def union_sub_func(match: re.Match) -> str:
    return f'{match.group("variable")}: typing.TypeAlias = {match.group("value")}'


def str_sub_func(match: re.Match) -> str:
    return f"{match.group('var')}: str"


def get_module_path(name: str) -> str:
    spec = importlib.util.find_spec(name)
    assert spec is not None
    module_path = spec.origin
    assert module_path is not None
    return module_path


def get_package_dir(name: str) -> str:
    return os.path.dirname(get_module_path(name))


def patch_stubgen():
    # Is there a better way to add items to the blacklist?
    # Pybind11
    FilterClassMembers._FilterClassMembers__class_member_blacklist.add(
        Identifier("_pybind11_conduit_v1_")
    )
    # Python
    FilterClassMembers._FilterClassMembers__class_member_blacklist.add(
        Identifier("__new__")
    )
    FilterClassMembers._FilterClassMembers__class_member_blacklist.add(
        Identifier("__subclasshook__")
    )
    # Pickle
    FilterClassMembers._FilterClassMembers__class_member_blacklist.add(
        Identifier("__getnewargs__")
    )
    FilterClassMembers._FilterClassMembers__class_member_blacklist.add(
        Identifier("__getstate__")
    )
    FilterClassMembers._FilterClassMembers__class_member_blacklist.add(
        Identifier("__setstate__")
    )
    # ABC
    FilterClassMembers._FilterClassMembers__attribute_blacklist.add(
        Identifier("__abstractmethods__")
    )
    FilterClassMembers._FilterClassMembers__attribute_blacklist.add(
        Identifier("__orig_bases__")
    )
    FilterClassMembers._FilterClassMembers__attribute_blacklist.add(
        Identifier("__parameters__")
    )
    FilterClassMembers._FilterClassMembers__attribute_blacklist.add(
        Identifier("_abc_impl")
    )
    # Protocol
    FilterClassMembers._FilterClassMembers__attribute_blacklist.add(
        Identifier("__protocol_attrs__")
    )
    FilterClassMembers._FilterClassMembers__attribute_blacklist.add(
        Identifier("__non_callable_proto_members__")
    )
    FilterClassMembers._FilterClassMembers__attribute_blacklist.add(
        Identifier("_is_protocol")
    )
    FilterClassMembers._FilterClassMembers__attribute_blacklist.add(
        Identifier("_is_runtime_protocol")
    )
    # dataclass
    FilterClassMembers._FilterClassMembers__attribute_blacklist.add(
        Identifier("__dataclass_fields__")
    )
    FilterClassMembers._FilterClassMembers__attribute_blacklist.add(
        Identifier("__dataclass_params__")
    )
    FilterClassMembers._FilterClassMembers__attribute_blacklist.add(
        Identifier("__match_args__")
    )


def main() -> None:
    amulet_path = get_package_dir("amulet")
    src_path = os.path.dirname(amulet_path)

    # Remove all existing stub files
    print("Removing stub files...")
    for stub_path in glob.iglob(
        os.path.join(glob.escape(src_path), "**", "*.pyi"), recursive=True
    ):
        os.remove(stub_path)

    # Extend pybind11-stubgen
    patch_stubgen()

    # Call pybind11-stubgen
    print("Running pybind11-stubgen...")
    sys.argv = [
        "pybind11_stubgen",
        f"--output-dir={src_path}",
        "amulet",
    ]
    pybind11_stubgen.main()
    # If pybind11_stubgen adds args to main
    # pybind11_stubgen.main([
    #     f"--output-dir={src_path}",
    #     "amulet",
    # ])

    # Run normal stubgen on the python files
    # print("Running stubgen...")
    # stubgen.main([
    #     *glob.glob(
    #         os.path.join(glob.escape(src_path), "**", "*.py"), recursive=True
    #     ),
    #     "-o",
    #     src_path,
    #     "--include-docstrings",
    # ])

    # Remove stub files generated for python modules
    for stub_path in glob.iglob(
        os.path.join(glob.escape(src_path), "**", "*.pyi"), recursive=True
    ):
        if os.path.isfile(stub_path[:-1]):
            os.remove(stub_path)

    print("Patching stub files...")
    # Fix some issues and reformat the stub files.
    stub_paths = glob.glob(
        os.path.join(glob.escape(src_path), "**", "*.pyi"), recursive=True
    )
    for stub_path in stub_paths:
        with open(stub_path, encoding="utf-8") as f:
            pyi = f.read()
        pyi = UnionPattern.sub(union_sub_func, pyi)
        pyi = VersionPattern.sub(str_sub_func, pyi)
        with open(stub_path, "w", encoding="utf-8") as f:
            f.write(pyi)

    subprocess.run(
        [
            "isort",
            *stub_paths,
        ]
    )

    subprocess.run(
        [
            "autoflake",
            "--in-place",
            "--remove-unused-variables",
            *stub_paths,
        ]
    )

    subprocess.run([sys.executable, "-m", "black", src_path])


if __name__ == "__main__":
    main()
