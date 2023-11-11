from io import BytesIO
from typing import Iterable, List

def _read_byte(stream: BytesIO) -> int:
    """Read a byte from the file (as an integer)

    :param stream: The stream to read the byte from.
    :return: The integer value of the byte.
    :raises:
        EOFError: if the stream ends while reading bytes.
    """
def decode_stream_one(stream: BytesIO) -> int:
    """Read a varint from `stream`"""
def decode_bytes_one(buf: bytes):
    """Read a varint from `buf` bytes"""
def decode_stream(stream: BytesIO) -> List[int]:
    """Read varint(s) from `stream` until the stream has been exhausted."""
def decode_bytes(buf: bytes) -> List[int]:
    """Read varint(s) from `buf` bytes until all the bytes have been exhausted."""
def decode_byte_array(buf: Iterable[int]) -> List[int]:
    """Read varint(s) from an iterable of ints until the iterable has been exhausted.
    All ints must be in range(0, 256)"""
def encode(number: int):
    """Pack `number` into varint bytes"""
def encode_array(array: Iterable[int]) -> bytes:
    """Pack an array of integers into a sequence of packed varint(s)."""
