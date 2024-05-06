"""Varint encoder/decoder

varints are a common encoding for variable length integer data, used in
libraries such as sqlite, protobuf, v8, and more.

Here's a quick and dirty module to help avoid reimplementing the same thing
over and over again.

With modifications to allow reading and writing an array of varints.
"""

from io import BytesIO
from typing import List, Iterable


def _read_byte(stream: BytesIO) -> int:
    """Read a byte from the file (as an integer)

    :param stream: The stream to read the byte from.
    :return: The integer value of the byte.
    :raises:
        EOFError: if the stream ends while reading bytes.
    """
    c = stream.read(1)
    if not c:
        raise EOFError("Unexpected EOF while reading bytes")
    return ord(c)


def decode_stream_one(stream: BytesIO) -> int:
    """Read a varint from `stream`"""
    shift = 0
    result = 0
    while True:
        i = _read_byte(stream)
        result |= (i & 0x7F) << shift
        shift += 7
        if not (i & 0x80):
            break
    return result


def decode_bytes_one(buf: bytes):
    """Read a varint from `buf` bytes"""
    return decode_stream_one(BytesIO(buf))


def decode_stream(stream: BytesIO) -> List[int]:
    """Read varint(s) from `stream` until the stream has been exhausted."""
    start = stream.tell()
    end = stream.seek(0, 2)
    stream.seek(start)

    result = []
    while stream.tell() < end:
        result.append(decode_stream_one(stream))
    return result


def decode_bytes(buf: bytes) -> List[int]:
    """Read varint(s) from `buf` bytes until all the bytes have been exhausted."""
    return decode_stream(BytesIO(buf))


def decode_byte_array(buf: Iterable[int]) -> List[int]:
    """Read varint(s) from an iterable of ints until the iterable has been exhausted.
    All ints must be in range(0, 256)"""
    return decode_bytes(bytes(buf))


def encode(number: int):
    """Pack `number` into varint bytes"""
    buf = []
    while True:
        towrite = number & 0x7F
        number >>= 7
        if number:
            buf.append(bytes((towrite | 0x80,)))
        else:
            buf.append(bytes((towrite,)))
            break
    return b"".join(buf)


def encode_array(array: Iterable[int]) -> bytes:
    """Pack an array of integers into a sequence of packed varint(s)."""
    return b"".join(encode(n) for n in array)
