import os
import json


def main() -> None:
    with open(os.path.join(os.path.dirname(__file__), "blockshapes.json")) as f:
        shapes = json.load(f)
        shapes_tuple = tuple(sorted(shapes.items(), key=lambda i: (i[1], i[0])))
        shapes2 = dict(shapes_tuple)
    with open(os.path.join(os.path.dirname(__file__), "blockshapes.json"), "w") as f:
        json.dump(shapes2, f, indent=4)


if __name__ == "__main__":
    main()
