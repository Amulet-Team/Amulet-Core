import argparse
import os

parser = argparse.ArgumentParser(
    description="Generate all interfaces up to a given level."
)
parser.add_argument(
    "interfaceversion", type=int, help="Generate all interfaces up to this level."
)


if __name__ == "__main__":
    args = parser.parse_args()
    for i in range(1, args.interfaceversion):
        path = os.path.join(os.path.dirname(__file__), f"leveldb_{i}.py")
        if not os.path.isfile(path):
            with open(path, "w") as f:
                f.write(
                    f"""from .leveldb_{i-1} import (
    LevelDB{i-1}Interface as ParentInterface,
)


class LevelDB{i}Interface(ParentInterface):
    chunk_version = {i}


export = LevelDB{i}Interface

"""
                )
