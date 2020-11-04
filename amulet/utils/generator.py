from typing import Generator


def generator_unpacker(gen: Generator):
    try:
        while True:
            next(gen)
    except StopIteration as e:
        return e.value
