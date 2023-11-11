import subprocess
import os
import importlib.util
import shutil


def main():
    amulet_dir = os.path.dirname(importlib.util.find_spec("amulet").origin)
    amulet_container_dir = os.path.dirname(amulet_dir)
    amulet_stub_dir = os.path.join(amulet_container_dir, "amulet-stubs")

    if os.path.isdir(amulet_stub_dir):
        shutil.rmtree(amulet_stub_dir)

    temp_stub_dir = os.path.join(amulet_container_dir, "stubs")

    subprocess.run(["stubgen", amulet_dir, "--include-docstrings", "--include-private", "-o", temp_stub_dir])
    os.rename(os.path.join(temp_stub_dir, "amulet"), amulet_stub_dir)
    with open(os.path.join(amulet_stub_dir, "py.typed"), "w"):
        pass


if __name__ == '__main__':
    main()
