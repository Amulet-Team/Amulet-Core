from typing import Any, Generator, TypeVar

T = TypeVar("T")

def generator_unpacker(gen: Generator[Any, Any, T]) -> T:
    """
    Unpack a generator and return the value returned by the generator.

    :param gen: The generator to unpack.
    :return: The value that was returned by the generator.
    """
