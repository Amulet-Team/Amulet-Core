from setuptools import setup, find_packages

from json import load
import os.path as op
import os

from tools.generate_version import generate_version_py, generate_version_from_dict


version_py_path = op.join(op.dirname(__file__), "amulet", "version.py")

VERSION_NUMBER = (0, 0, 0)
VERSION_INT = -1
VERSION_STAGE = "DEV"
if op.exists(op.join(".", "version.json")):
    with open(op.join(".", "version.json")) as fp:
        generate_version_py(
            save_path=version_py_path, *generate_version_from_dict(load(fp))
        )
else:
    generate_version_py(
        VERSION_NUMBER, VERSION_INT, VERSION_STAGE, save_path=version_py_path
    )


def remove_git_and_http_package_links(uris):
    for uri in uris:
        if uri.startswith("git+") or uri.startswith("https:"):
            continue
        yield uri


world_interface_path = op.join(op.dirname(__file__), "amulet", "world_interface")
operations_path = op.join(op.dirname(__file__), "amulet", "operations")
libraries_path = op.join(op.dirname(__file__), "amulet", "libs")

packs = find_packages(
    include=["amulet*"], exclude=["*.command_line", "*.command_line.*"]
)

with open("./requirements.txt") as requirements_fp:
    required_packages = [
        line for line in remove_git_and_http_package_links(requirements_fp.readlines())
    ]

package_data = [
    op.join(root, filename)
    for root, _, filenames in os.walk(world_interface_path)
    for filename in filenames
    if "__pycache__" not in root
]

package_data.extend(
    [
        op.join(root, filename)
        for root, _, filenames in os.walk(operations_path)
        for filename in filenames
        if "__pycache__" not in root
    ]
)
package_data.extend(
    [
        op.join(root, filename)
        for root, _, filenames in os.walk(libraries_path)
        for filename in filenames
        if "__pycache__" not in root
    ]
)

setup(
    name="amulet-core",
    version=".".join(map(str, VERSION_NUMBER)),
    packages=packs,
    include_package_data=True,
    package_data={"amulet": package_data},
    install_requires=required_packages,
    setup_requires=required_packages,
    dependency_links=[
        "https://github.com/Amulet-Team/Amulet-NBT",
        "https://github.com/gentlegiantJGC/PyMCTranslate",
    ],
)
