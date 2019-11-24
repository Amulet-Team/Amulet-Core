from setuptools import setup, find_packages

from amulet import version

packs = find_packages(
    include=["amulet*"], exclude=["*.command_line", "*.command_line.*"]
)

with open("./requirements.txt") as requirements_fp:
    required_packages = [
        line
        for line in requirements_fp.readlines()
        if not line.startswith("git+") and not line.startswith("https:")
    ]

setup(
    name="amulet",
    version=".".join(map(str, version.VERSION_NUMBER)),
    packages=packs,
    include_package_data=True,
    install_requires=required_packages,
    dependency_links=["https://github.com/Amulet-Team/Amulet-NBT"],
)
