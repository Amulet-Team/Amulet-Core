import gzip
from io import StringIO

SECTOR_BYTES = 4096
SECTOR_INTS = SECTOR_BYTES / 4
CHUNK_HEADER_SIZE = 5
VERSION_GZIP = 1
VERSION_DEFLATE = 2

def block_coords_to_chunk_coords(x: int, z: int) -> tuple:
    return x >> 4, z >> 4

def chunk_coords_to_region_coords(cx: int, cz: int) -> tuple:
    return cx >> 5, cz >> 5

def region_coords_to_chunk_coords(rx: int, rz: int) -> tuple:
    return rx << 5, rz << 5

def gunzip(data):
    return gzip.GzipFile(fileobj=StringIO(data)).read()

import sys

def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size

