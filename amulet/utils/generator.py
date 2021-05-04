from typing import Generator


def generator_unpacker(gen: Generator):
    """
    Unpack a generator and return the value returned by the generator.

    :param gen: The generator to unpack.
    :return: The value that was returned by the generator.
    """
    try:
        while True:
            next(gen)
    except StopIteration as e:
        return e.value
