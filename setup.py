from setuptools import setup, find_packages

from amulet import version


def get_egg_name_from_git_uri(uri):
    if uri.startswith("git+") or uri.startswith("https:"):
        return uri[uri.index("#egg=") + len("#egg=") :]
    return uri


packs = find_packages(
    include=["amulet*"], exclude=["*.command_line", "*.command_line.*"]
)

with open("./requirements.txt") as requirements_fp:
    required_packages = [
        get_egg_name_from_git_uri(line) for line in requirements_fp.readlines()
    ]

setup(
    name="amulet-core",
    version=".".join(map(str, version.VERSION_NUMBER)),
    packages=packs,
    include_package_data=True,
    install_requires=required_packages,
    setup_requires=required_packages,
    dependency_links=["https://github.com/Amulet-Team/Amulet-NBT"],
)
