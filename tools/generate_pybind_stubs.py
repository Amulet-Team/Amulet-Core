import os
import glob
import importlib.util
from concurrent.futures import ThreadPoolExecutor
import subprocess


def main() -> None:
    amulet_spec = importlib.util.find_spec("amulet")
    assert amulet_spec is not None
    amulet_init_path = amulet_spec.origin
    assert amulet_init_path is not None
    amulet_path = os.path.dirname(amulet_init_path)
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
                "python",
                "-m",
                "pybind11_stubgen",
                "--output-dir=src",
                "--root-suffix=-stubs",
                module_name,
            ]
        )

    # with ThreadPoolExecutor() as executor:
    #     results = executor.map(
    #         lambda module_name_: subprocess.run(["python", "-m", "pybind11_stubgen", "--output-dir=src", "--root-suffix=-stubs", module_name_]),
    #         compiled_modules
    #     )
    #     list(results)


if __name__ == "__main__":
    main()
