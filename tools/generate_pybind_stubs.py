import os
import glob
import importlib.util
import sys
from concurrent.futures import ThreadPoolExecutor
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
    compiled_module_paths = glob.glob(
        os.path.join(glob.escape(amulet_path), "**", "*.pyd"), recursive=True
    )
    compiled_modules = list[str]()
    for compiled_module_path in compiled_module_paths:
        package_dir, module_path = os.path.split(compiled_module_path)
        module_name = module_path.split(".", 1)[0]
        package_name = os.path.normpath(os.path.relpath(package_dir, src_path)).replace(
            os.sep, "."
        )
        if package_name:
            module_name = f"{package_name}.{module_name}"
        compiled_modules.append(module_name)
    print(compiled_modules)

    for module_name in compiled_modules:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pybind11_stubgen",
                f"--output-dir={src_path}",
                module_name,
            ]
        )
        module_path = get_module_path(module_name)
        pyi_path = os.path.join(
            os.path.dirname(module_path),
            os.path.basename(module_path).split(".", 1)[0] + ".pyi",
        )
        with open(pyi_path, encoding="utf-8") as f:
            pyi = f.read()
        pyi = UnionPattern.sub(union_sub_func, pyi)
        with open(pyi_path, "w", encoding="utf-8") as f:
            f.write(pyi)

    # with ThreadPoolExecutor() as executor:
    #     results = executor.map(
    #         lambda module_name_: subprocess.run(["python", "-m", "pybind11_stubgen", "--output-dir=src", "--root-suffix=-stubs", module_name_]),
    #         compiled_modules
    #     )
    #     list(results)


if __name__ == "__main__":
    main()
