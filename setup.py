from setuptools import setup, find_packages
import os
import glob
import shutil
import versioneer

# there were issues with other builds carrying over their cache
for d in glob.glob("*.egg-info"):
    shutil.rmtree(d)


def remove_git_and_http_package_links(uris):
    for uri in uris:
        if uri.startswith("git+") or uri.startswith("https:"):
            continue
        yield uri


with open("./requirements.txt") as requirements_fp:
    required_packages = [
        line for line in remove_git_and_http_package_links(requirements_fp.readlines())
    ]

package_data = [
    os.path.relpath(path, "amulet") for path in
    set(
        glob.glob(
            os.path.join(
                "amulet",
                "**",
                "*.*"
            ),
            recursive=True
        )
    ) - set(
        glob.glob(
            os.path.join(
                "amulet",
                "**",
                "*.py[cod]"
            ),
            recursive=True
        )
    )
]

setup(
    name="amulet-core",
    version=versioneer.get_version(),
    description="A Python library for reading/writing Minecraft's various save formats.",
    author="James Clare, Ben Gothard et al.",
    author_email="amuleteditor@gmail.com",
    install_requires=required_packages,
    packages=find_packages(),
    package_data={"amulet": package_data},
    cmdclass=versioneer.get_cmdclass(),
    setup_requires=required_packages,
    dependency_links=[
        "https://github.com/Amulet-Team/Amulet-NBT",
        "https://github.com/gentlegiantJGC/PyMCTranslate",
    ],
)
