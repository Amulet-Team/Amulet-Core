import os
import glob
import importlib.util
import sys
import subprocess
import re

UnionPattern = re.compile(
    r"^(?P<variable>[a-zA-Z_][a-zA-Z0-9_]*): types\.UnionType\s*#\s*value = (?P<value>.*)$",
    flags=re.MULTILINE,
)


def union_sub_func(match: re.Match) -> str:
    return f'{match.group("variable")}: typing.TypeAlias = {match.group("value")}'


def get_module_path(name: str) -> str:
    spec = importlib.util.find_spec(name)
    assert spec is not None
    module_path = spec.origin
    assert module_path is not None
    return module_path


def get_package_dir(name: str) -> str:
    return os.path.dirname(get_module_path(name))


def main() -> None:
    amulet_path = get_package_dir("amulet")
    src_path = os.path.dirname(amulet_path)

    for stub_path in glob.iglob(
        os.path.join(glob.escape(src_path), "**", "*.pyi"), recursive=True
    ):
        os.remove(stub_path)

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pybind11_stubgen",
            f"--output-dir={src_path}",
            "amulet",
        ]
    )

    for stub_path in glob.iglob(
        os.path.join(glob.escape(src_path), "**", "*.pyi"), recursive=True
    ):
        with open(stub_path, encoding="utf-8") as f:
            pyi = f.read()
        pyi = UnionPattern.sub(union_sub_func, pyi)
        with open(stub_path, "w", encoding="utf-8") as f:
            f.write(pyi)

    subprocess.run([sys.executable, "-m", "black", src_path])


if __name__ == "__main__":
    main()
