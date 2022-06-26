# Provides an python wrapper for the ctypes wrapper for the c wrapper for leveldb.

import ctypes
import os
import shutil
import sys
from typing import Dict, Iterator, Tuple

if sys.platform == "win32":
    if sys.maxsize > 2**32:  # 64 bit python
        lib_name = "leveldb_mcpe_win_amd64.dll"
    else:  # 32 bit python
        lib_name = "leveldb_mcpe_win32.dll"
elif sys.platform == "darwin":
    lib_name = "leveldb_mcpe_macosx_10_9_x86_64.dylib"
else:  # linux, compile your own .so if this errors!
    lib_name = "leveldb_mcpe_linux_x86_64.so"

lib_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), lib_name)
assert os.path.isfile(
    lib_path
), f"Could not find the leveldb shared library at {lib_path}"
ldb = ctypes.cdll.LoadLibrary(lib_path)

# Setup ctypes arguments and return types for all of the leveldb functions.
# Most of this pulled from Podshot/MCEdit-Unified
ldb.leveldb_filterpolicy_create_bloom.argtypes = [ctypes.c_int]
ldb.leveldb_filterpolicy_create_bloom.restype = ctypes.c_void_p
ldb.leveldb_filterpolicy_destroy.argtypes = [ctypes.c_void_p]
ldb.leveldb_filterpolicy_destroy.restype = None
ldb.leveldb_cache_create_lru.argtypes = [ctypes.c_size_t]
ldb.leveldb_cache_create_lru.restype = ctypes.c_void_p
ldb.leveldb_cache_destroy.argtypes = [ctypes.c_void_p]
ldb.leveldb_cache_destroy.restype = None

ldb.leveldb_options_create.argtypes = []
ldb.leveldb_options_create.restype = ctypes.c_void_p
ldb.leveldb_options_set_filter_policy.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
ldb.leveldb_options_set_filter_policy.restype = None
ldb.leveldb_options_set_create_if_missing.argtypes = [ctypes.c_void_p, ctypes.c_ubyte]
ldb.leveldb_options_set_create_if_missing.restype = None
ldb.leveldb_options_set_error_if_exists.argtypes = [ctypes.c_void_p, ctypes.c_ubyte]
ldb.leveldb_options_set_error_if_exists.restype = None
ldb.leveldb_options_set_paranoid_checks.argtypes = [ctypes.c_void_p, ctypes.c_ubyte]
ldb.leveldb_options_set_paranoid_checks.restype = None
ldb.leveldb_options_set_write_buffer_size.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
ldb.leveldb_options_set_write_buffer_size.restype = None
ldb.leveldb_options_set_max_open_files.argtypes = [ctypes.c_void_p, ctypes.c_int]
ldb.leveldb_options_set_max_open_files.restype = None
ldb.leveldb_options_set_cache.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
ldb.leveldb_options_set_cache.restype = None
ldb.leveldb_options_set_block_size.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
ldb.leveldb_options_set_block_size.restype = None
ldb.leveldb_options_destroy.argtypes = [ctypes.c_void_p]
ldb.leveldb_options_destroy.restype = None

ldb.leveldb_options_set_compression.argtypes = [ctypes.c_void_p, ctypes.c_int]
ldb.leveldb_options_set_compression.restype = None

ldb.leveldb_repair_db.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p]
ldb.leveldb_repair_db.restype = None

ldb.leveldb_open.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_void_p]
ldb.leveldb_open.restype = ctypes.c_void_p
ldb.leveldb_close.argtypes = [ctypes.c_void_p]
ldb.leveldb_close.restype = None
ldb.leveldb_put.argtypes = [
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.c_void_p,
]
ldb.leveldb_put.restype = None
ldb.leveldb_delete.argtypes = [
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.c_void_p,
]
ldb.leveldb_delete.restype = None
ldb.leveldb_write.argtypes = [
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_void_p,
]
ldb.leveldb_write.restype = None
ldb.leveldb_get.argtypes = [
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.c_void_p,
    ctypes.c_void_p,
]
ldb.leveldb_get.restype = ctypes.POINTER(ctypes.c_char)

ldb.leveldb_writeoptions_create.argtypes = []
ldb.leveldb_writeoptions_create.restype = ctypes.c_void_p
ldb.leveldb_writeoptions_destroy.argtypes = [ctypes.c_void_p]
ldb.leveldb_writeoptions_destroy.restype = None
ldb.leveldb_writeoptions_set_sync.argtypes = [ctypes.c_void_p, ctypes.c_ubyte]
ldb.leveldb_writeoptions_set_sync.restype = None

ldb.leveldb_readoptions_create.argtypes = []
ldb.leveldb_readoptions_create.restype = ctypes.c_void_p
ldb.leveldb_readoptions_destroy.argtypes = [ctypes.c_void_p]
ldb.leveldb_readoptions_destroy.restype = None
ldb.leveldb_readoptions_set_verify_checksums.argtypes = [
    ctypes.c_void_p,
    ctypes.c_ubyte,
]
ldb.leveldb_readoptions_set_verify_checksums.restype = None
ldb.leveldb_readoptions_set_fill_cache.argtypes = [ctypes.c_void_p, ctypes.c_ubyte]
ldb.leveldb_readoptions_set_fill_cache.restype = None
ldb.leveldb_readoptions_set_snapshot.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
ldb.leveldb_readoptions_set_snapshot.restype = None

ldb.leveldb_create_iterator.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
ldb.leveldb_create_iterator.restype = ctypes.c_void_p
ldb.leveldb_iter_destroy.argtypes = [ctypes.c_void_p]
ldb.leveldb_iter_destroy.restype = None
ldb.leveldb_iter_valid.argtypes = [ctypes.c_void_p]
ldb.leveldb_iter_valid.restype = ctypes.c_bool
ldb.leveldb_iter_key.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t)]
ldb.leveldb_iter_key.restype = ctypes.c_void_p
ldb.leveldb_iter_value.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t)]
ldb.leveldb_iter_value.restype = ctypes.c_void_p
ldb.leveldb_iter_next.argtypes = [ctypes.c_void_p]
ldb.leveldb_iter_next.restype = None
ldb.leveldb_iter_prev.argtypes = [ctypes.c_void_p]
ldb.leveldb_iter_prev.restype = None
ldb.leveldb_iter_seek_to_first.argtypes = [ctypes.c_void_p]
ldb.leveldb_iter_seek_to_first.restype = None
ldb.leveldb_iter_seek_to_last.argtypes = [ctypes.c_void_p]
ldb.leveldb_iter_seek_to_last.restype = None
ldb.leveldb_iter_seek.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
ldb.leveldb_iter_seek.restype = None
ldb.leveldb_iter_get_error.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
ldb.leveldb_iter_get_error.restype = None

ldb.leveldb_writebatch_create.argtypes = []
ldb.leveldb_writebatch_create.restype = ctypes.c_void_p
ldb.leveldb_writebatch_destroy.argtypes = [ctypes.c_void_p]
ldb.leveldb_writebatch_destroy.restype = None
ldb.leveldb_writebatch_clear.argtypes = [ctypes.c_void_p]
ldb.leveldb_writebatch_clear.restype = None

ldb.leveldb_writebatch_put.argtypes = [
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.c_void_p,
    ctypes.c_size_t,
]
ldb.leveldb_writebatch_put.restype = None
ldb.leveldb_writebatch_delete.argtypes = [
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
]
ldb.leveldb_writebatch_delete.restype = None

ldb.leveldb_approximate_sizes.argtypes = [
    ctypes.c_void_p,
    ctypes.c_int,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_void_p,
]
ldb.leveldb_approximate_sizes.restype = None

ldb.leveldb_compact_range.argtypes = [
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.c_void_p,
    ctypes.c_size_t,
]
ldb.leveldb_compact_range.restype = None

ldb.leveldb_create_snapshot.argtypes = [ctypes.c_void_p]
ldb.leveldb_create_snapshot.restype = ctypes.c_void_p
ldb.leveldb_release_snapshot.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
ldb.leveldb_release_snapshot.restype = None

ldb.leveldb_free.argtypes = [ctypes.c_void_p]
ldb.leveldb_free.restype = None


class LevelDBException(Exception):
    """
    The exception thrown for all leveldb related errors.
    """

    pass


class LevelDBEncrypted(LevelDBException):
    pass


def _checkError(err):
    """Utility function for checking the error code returned by some leveldb functions."""
    if bool(err):  # Not an empty null-terminated string
        message = ctypes.string_at(err).decode("utf-8")
        ldb.leveldb_free(ctypes.cast(err, ctypes.c_void_p))
        raise LevelDBException(message)


class LevelDB:
    def __init__(self, path: str, create_if_missing: bool = False):
        """
        Construct a new :class:`LevelDB` instance from the database at the given path.

        A leveldb database is like a dictionary that only contains bytes as the keys and values and exists entirely on the disk.

        :param path: The path to the database directory.
        :param create_if_missing: If True and there is no database at the given path a new database will be created.
        """
        self.db = None
        self._path = path
        self._open(path, create_if_missing)

    def __del__(self):
        self.close()

    def _open(self, path: str, create_if_missing: bool = False):
        # Bloom filter: an efficient way to tell if something is in a cache.
        if not os.path.isdir(path):
            if create_if_missing:
                os.makedirs(path)
            else:
                raise LevelDBException(f"No database exists to open at {path}")
        filter_policy = ldb.leveldb_filterpolicy_create_bloom(10)
        cache = ldb.leveldb_cache_create_lru(40 * 1024 * 1024)
        options = ldb.leveldb_options_create()
        # Many of these options were pulled from Podshot/MCEdit-Unified
        ldb.leveldb_options_set_compression(options, 4)
        ldb.leveldb_options_set_filter_policy(options, filter_policy)
        ldb.leveldb_options_set_create_if_missing(options, create_if_missing)
        ldb.leveldb_options_set_write_buffer_size(options, 4 * 1024 * 1024)
        ldb.leveldb_options_set_cache(options, cache)
        ldb.leveldb_options_set_block_size(options, 163840)

        db = None

        def open_db():
            nonlocal db
            open_error = ctypes.POINTER(ctypes.c_char)()
            db = ldb.leveldb_open(
                options, path.encode("utf-8"), ctypes.byref(open_error)
            )
            _checkError(open_error)

        # remove old lost directory if it exists
        shutil.rmtree(os.path.join(self._path, "lost"), ignore_errors=True)

        try:
            open_db()
        except OSError:
            raise LevelDBEncrypted
        except LevelDBException as e:
            try:
                repair_error = ctypes.POINTER(ctypes.c_char)()
                ldb.leveldb_repair_db(
                    options, path.encode("utf-8"), ctypes.byref(repair_error)
                )
                _checkError(repair_error)
                open_db()
            except:
                raise e
        finally:
            ldb.leveldb_options_destroy(options)

        self.db = db

    def close(self, compact=True):
        """
        Close the leveldb database.

        :param compact: If True will compact the database making it take less memory.
        """
        if self.db:
            if compact:
                ldb.leveldb_compact_range(self.db, None, 0, None, 0)
            ldb.leveldb_close(self.db)
            self.db = None

    def get(self, key: bytes):
        """
        Get a key from the database.

        :param key: The key to get from the database.
        :return: The data stored behind the given key.
        :raises: KeyError if the requested key is not present.
        """
        assert isinstance(key, bytes)
        ro = ldb.leveldb_readoptions_create()
        size = ctypes.c_size_t(0)
        error = ctypes.POINTER(ctypes.c_char)()
        valPtr = ldb.leveldb_get(
            self.db, ro, key, len(key), ctypes.byref(size), ctypes.byref(error)
        )
        ldb.leveldb_readoptions_destroy(ro)
        _checkError(error)
        if bool(valPtr):
            val = ctypes.string_at(valPtr, size.value)
            ldb.leveldb_free(ctypes.cast(valPtr, ctypes.c_void_p))
        else:
            raise KeyError("Key {} not found in database.".format(key))
        return val

    def put(self, key: bytes, val: bytes):
        """
        Add a key to the database.

        :param key: The key to store the value under.
        :param val: The value to store.
        """
        assert isinstance(key, bytes) and isinstance(val, bytes)
        wo = ldb.leveldb_writeoptions_create()
        error = ctypes.POINTER(ctypes.c_char)()
        ldb.leveldb_put(self.db, wo, key, len(key), val, len(val), ctypes.byref(error))
        ldb.leveldb_writeoptions_destroy(wo)
        _checkError(error)

    def putBatch(self, data: Dict[bytes, bytes]):
        batch = ldb.leveldb_writebatch_create()
        for k, v in data.items():
            assert isinstance(k, bytes) and isinstance(v, bytes)
            ldb.leveldb_writebatch_put(batch, k, len(k), v, len(v))
        wo = ldb.leveldb_writeoptions_create()
        error = ctypes.POINTER(ctypes.c_char)()
        ldb.leveldb_write(self.db, wo, batch, ctypes.byref(error))
        ldb.leveldb_writeoptions_destroy(wo)
        _checkError(error)

    def delete(self, key: bytes):
        """
        Delete a key from the database.

        :param key: The key to delete from the database.
        """
        assert isinstance(key, bytes)
        wo = ldb.leveldb_writeoptions_create()
        error = ctypes.POINTER(ctypes.c_char)()
        ldb.leveldb_delete(self.db, wo, key, len(key), ctypes.byref(error))
        ldb.leveldb_writeoptions_destroy(wo)
        _checkError(error)

    def iterate(
        self, start: bytes = None, end: bytes = None
    ) -> Iterator[Tuple[bytes, bytes]]:
        """
        Iterate through all keys and data that exist between the given keys.

        :param start: The key to start at. Leave as None to start at the beginning.
        :param end: The key to end at. Leave as None to start at the beginning.
        """
        ro = ldb.leveldb_readoptions_create()
        it = ldb.leveldb_create_iterator(self.db, ro)
        ldb.leveldb_readoptions_destroy(ro)
        if start is None:
            ldb.leveldb_iter_seek_to_first(it)
        else:
            assert isinstance(start, bytes)
            ldb.leveldb_iter_seek(it, start, len(start))
        assert end is None or isinstance(end, bytes)
        try:
            while ldb.leveldb_iter_valid(it):
                size = ctypes.c_size_t(0)
                keyPtr = ldb.leveldb_iter_key(it, ctypes.byref(size))
                key = ctypes.string_at(keyPtr, size.value)
                if end is not None and key >= end:
                    break
                valPtr = ldb.leveldb_iter_value(it, ctypes.byref(size))
                val = ctypes.string_at(valPtr, size.value)
                yield key, val
                ldb.leveldb_iter_next(it)
        finally:
            ldb.leveldb_iter_destroy(it)

    def keys(self) -> Iterator[bytes]:
        """An iterable of all the keys in the database."""
        ro = ldb.leveldb_readoptions_create()
        it = ldb.leveldb_create_iterator(self.db, ro)
        ldb.leveldb_readoptions_destroy(ro)
        ldb.leveldb_iter_seek_to_first(it)
        try:
            while ldb.leveldb_iter_valid(it):
                size = ctypes.c_size_t(0)
                keyPtr = ldb.leveldb_iter_key(it, ctypes.byref(size))
                key = ctypes.string_at(keyPtr, size.value)
                yield key
                ldb.leveldb_iter_next(it)
        finally:
            ldb.leveldb_iter_destroy(it)

    def __contains__(self, key: bytes):
        assert isinstance(key, bytes)
        keys = list(self.iterate(key, key + b"\x00"))
        return keys and keys[0][0] == key

    def __iter__(self) -> Iterator[bytes]:
        return self.keys()
