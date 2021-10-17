# A cython (and python) wrapper for leveldb.

import os
import sys
from cpython.bytes cimport PyBytes_FromStringAndSize
from typing import Dict, Iterator, Tuple
cimport cython

if sys.platform == "win32":
    if sys.maxsize > 2 ** 32:  # 64 bit python
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


IF UNAME_SYSNAME == "Windows":
    cdef extern from "<windows.h>":
        pass
    cdef extern from "<libloaderapi.h>":
        void* LoadLibraryA(char *lpLibFileName)
        void* GetProcAddress(void *hModule, char *lpProcName)

    cdef void *module = LoadLibraryA(lib_path.encode("utf-8"))

    cdef void *getFunction(char *functionName):
        return GetProcAddress(module, functionName)

ELIF UNAME_SYSNAME == "Darwin" or UNAME_SYSNAME == "Linux":
    cdef extern from "dlfcn.h":
        void *dlopen(char *filename, int mode)
        void *dlsym(void *handle, char *name)

        ctypedef enum DL_MODES:
            RTLD_LAZY
            RTLD_NOW
            RTLD_BINDING_MASK
            RTLD_NOLOAD
            RTLD_GLOBAL

    cdef void *module = dlopen(lib_path.encode("utf-8"), RTLD_LAZY)

    cdef void *getFunction(char *functionName):
        return dlsym(module, functionName)

ELSE:
    cdef void *getFunction(char *functionName):
        raise Exception(f"{os.uname()[0]} not yet supported")

cdef extern from "leveldb.h":
    struct leveldb_t:
        pass
    struct leveldb_cache_t:
        pass
    struct leveldb_comparator_t:
        pass
    struct leveldb_env_t:
        pass
    struct leveldb_filelock_t:
        pass
    struct leveldb_filterpolicy_t:
        pass
    struct leveldb_iterator_t:
        pass
    struct leveldb_logger_t:
        pass
    struct leveldb_options_t:
        pass
    struct leveldb_randomfile_t:
        pass
    struct leveldb_readoptions_t:
        pass
    struct leveldb_seqfile_t:
        pass
    struct leveldb_snapshot_t:
        pass
    struct leveldb_writablefile_t:
        pass
    struct leveldb_writebatch_t:
        pass
    struct leveldb_writeoptions_t:
        pass

    ctypedef enum compression:
        leveldb_no_compression=0,
        leveldb_zlib_compression=2,
        leveldb_zlib_raw_compression=4,


ctypedef leveldb_t* (*PFNleveldb_openPROC)(const leveldb_options_t* options, const char* name, char** errptr)
cdef PFNleveldb_openPROC leveldb_open = <PFNleveldb_openPROC>getFunction(b"leveldb_open")

ctypedef void (*PFNleveldb_closePROC)(leveldb_t* db)
cdef PFNleveldb_closePROC leveldb_close = <PFNleveldb_closePROC>getFunction(b"leveldb_close")

ctypedef void (*PFNleveldb_putPROC)(leveldb_t* db, const leveldb_writeoptions_t* options, const char* key, size_t keylen, const char* val, size_t vallen, char** errptr)
cdef PFNleveldb_putPROC leveldb_put = <PFNleveldb_putPROC>getFunction(b"leveldb_put")

ctypedef void (*PFNleveldb_deletePROC)(leveldb_t* db, const leveldb_writeoptions_t* options, const char* key, size_t keylen, char** errptr)
cdef PFNleveldb_deletePROC leveldb_delete = <PFNleveldb_deletePROC>getFunction(b"leveldb_delete")

ctypedef void (*PFNleveldb_writePROC)(leveldb_t* db, const leveldb_writeoptions_t* options, leveldb_writebatch_t* batch, char** errptr)
cdef PFNleveldb_writePROC leveldb_write = <PFNleveldb_writePROC>getFunction(b"leveldb_write")

ctypedef char* (*PFNleveldb_getPROC)(leveldb_t* db, const leveldb_readoptions_t* options, const char* key, size_t keylen, size_t* vallen, char** errptr)
cdef PFNleveldb_getPROC leveldb_get = <PFNleveldb_getPROC>getFunction(b"leveldb_get")

ctypedef leveldb_iterator_t* (*PFNleveldb_create_iteratorPROC)(leveldb_t* db, const leveldb_readoptions_t* options)
cdef PFNleveldb_create_iteratorPROC leveldb_create_iterator = <PFNleveldb_create_iteratorPROC>getFunction(b"leveldb_create_iterator")

ctypedef const leveldb_snapshot_t* (*PFNleveldb_create_snapshotPROC)(leveldb_t* db)
cdef PFNleveldb_create_snapshotPROC leveldb_create_snapshot = <PFNleveldb_create_snapshotPROC>getFunction(b"leveldb_create_snapshot")

ctypedef void (*PFNleveldb_release_snapshotPROC)(leveldb_t* db, const leveldb_snapshot_t* snapshot)
cdef PFNleveldb_release_snapshotPROC leveldb_release_snapshot = <PFNleveldb_release_snapshotPROC>getFunction(b"leveldb_release_snapshot")

ctypedef char* (*PFNleveldb_property_valuePROC)(leveldb_t* db, const char* propname)

ctypedef void (*PFNleveldb_approximate_sizesPROC)(leveldb_t* db, int num_ranges, const char* range_start_key, const size_t* range_start_key_len, const char* range_limit_key, const size_t* range_limit_key_len, long long* sizes)
cdef PFNleveldb_approximate_sizesPROC leveldb_approximate_sizes = <PFNleveldb_approximate_sizesPROC>getFunction(b"leveldb_approximate_sizes")

ctypedef void (*PFNleveldb_compact_rangePROC)(leveldb_t* db, const char* start_key, size_t start_key_len, const char* limit_key, size_t limit_key_len)
cdef PFNleveldb_compact_rangePROC leveldb_compact_range = <PFNleveldb_compact_rangePROC>getFunction(b"leveldb_compact_range")

ctypedef void (*PFNleveldb_destroy_dbPROC)(const leveldb_options_t* options, const char* name, char** errptr)

ctypedef void (*PFNleveldb_repair_dbPROC)(const leveldb_options_t* options, const char* name, char** errptr)

ctypedef void (*PFNleveldb_iter_destroyPROC)(leveldb_iterator_t* iter)
cdef PFNleveldb_iter_destroyPROC leveldb_iter_destroy = <PFNleveldb_iter_destroyPROC>getFunction(b"leveldb_iter_destroy")

ctypedef unsigned char (*PFNleveldb_iter_validPROC)(const leveldb_iterator_t* iter)
cdef PFNleveldb_iter_validPROC leveldb_iter_valid = <PFNleveldb_iter_validPROC>getFunction(b"leveldb_iter_valid")

ctypedef void (*PFNleveldb_iter_seek_to_firstPROC)(leveldb_iterator_t* iter)
cdef PFNleveldb_iter_seek_to_firstPROC leveldb_iter_seek_to_first = <PFNleveldb_iter_seek_to_firstPROC>getFunction(b"leveldb_iter_seek_to_first")

ctypedef void (*PFNleveldb_iter_seek_to_lastPROC)(leveldb_iterator_t* iter)
cdef PFNleveldb_iter_seek_to_lastPROC leveldb_iter_seek_to_last = <PFNleveldb_iter_seek_to_lastPROC>getFunction(b"leveldb_iter_seek_to_last")

ctypedef void (*PFNleveldb_iter_seekPROC)(leveldb_iterator_t* iter, const char* k, size_t klen)
cdef PFNleveldb_iter_seekPROC leveldb_iter_seek = <PFNleveldb_iter_seekPROC>getFunction(b"leveldb_iter_seek")

ctypedef void (*PFNleveldb_iter_nextPROC)(leveldb_iterator_t* iter)
cdef PFNleveldb_iter_nextPROC leveldb_iter_next = <PFNleveldb_iter_nextPROC>getFunction(b"leveldb_iter_next")

ctypedef void (*PFNleveldb_iter_prevPROC)(leveldb_iterator_t* iter)
cdef PFNleveldb_iter_prevPROC leveldb_iter_prev = <PFNleveldb_iter_prevPROC>getFunction(b"leveldb_iter_prev")

ctypedef const char* (*PFNleveldb_iter_keyPROC)(const leveldb_iterator_t* iter, size_t* klen)
cdef PFNleveldb_iter_keyPROC leveldb_iter_key = <PFNleveldb_iter_keyPROC>getFunction(b"leveldb_iter_key")

ctypedef const char* (*PFNleveldb_iter_valuePROC)(const leveldb_iterator_t* iter, size_t* vlen)
cdef PFNleveldb_iter_valuePROC leveldb_iter_value = <PFNleveldb_iter_valuePROC>getFunction(b"leveldb_iter_value")

ctypedef void (*PFNleveldb_iter_get_errorPROC)(const leveldb_iterator_t* iter, char** errptr)
cdef PFNleveldb_iter_get_errorPROC leveldb_iter_get_error = <PFNleveldb_iter_get_errorPROC>getFunction(b"leveldb_iter_get_error")

ctypedef leveldb_writebatch_t* (*PFNleveldb_writebatch_createPROC)()
cdef PFNleveldb_writebatch_createPROC leveldb_writebatch_create = <PFNleveldb_writebatch_createPROC>getFunction(b"leveldb_writebatch_create")

ctypedef void (*PFNleveldb_writebatch_destroyPROC)(leveldb_writebatch_t* b)
cdef PFNleveldb_writebatch_destroyPROC leveldb_writebatch_destroy = <PFNleveldb_writebatch_destroyPROC>getFunction(b"leveldb_writebatch_destroy")

ctypedef void (*PFNleveldb_writebatch_clearPROC)(leveldb_writebatch_t* b)
cdef PFNleveldb_writebatch_clearPROC leveldb_writebatch_clear = <PFNleveldb_writebatch_clearPROC>getFunction(b"leveldb_writebatch_clear")

ctypedef void (*PFNleveldb_writebatch_putPROC)(leveldb_writebatch_t* b, const char* key, size_t klen, const char* val, size_t vlen)
cdef PFNleveldb_writebatch_putPROC leveldb_writebatch_put = <PFNleveldb_writebatch_putPROC>getFunction(b"leveldb_writebatch_put")

ctypedef void (*PFNleveldb_writebatch_deletePROC)(leveldb_writebatch_t* b, const char* key, size_t klen)
cdef PFNleveldb_writebatch_deletePROC leveldb_writebatch_delete = <PFNleveldb_writebatch_deletePROC>getFunction(b"leveldb_writebatch_delete")

ctypedef void (*PFNleveldb_writebatch_iteratePROC)(leveldb_writebatch_t* b, void* state, void (*put)(void*, const char* k, size_t klen, const char* v, size_t vlen), void (*deleted)(void*, const char* k, size_t klen))

ctypedef leveldb_options_t* (*PFNleveldb_options_createPROC)()
cdef PFNleveldb_options_createPROC leveldb_options_create = <PFNleveldb_options_createPROC>getFunction(b"leveldb_options_create")

ctypedef void (*PFNleveldb_options_destroyPROC)(leveldb_options_t* options)
cdef PFNleveldb_options_destroyPROC leveldb_options_destroy = <PFNleveldb_options_destroyPROC>getFunction(b"leveldb_options_destroy")

ctypedef void (*PFNleveldb_options_set_comparatorPROC)(leveldb_options_t* options, leveldb_comparator_t* cmp)

ctypedef void (*PFNleveldb_options_set_filter_policyPROC)(leveldb_options_t* options, leveldb_filterpolicy_t* policy)
cdef PFNleveldb_options_set_filter_policyPROC leveldb_options_set_filter_policy = <PFNleveldb_options_set_filter_policyPROC>getFunction(b"leveldb_options_set_filter_policy")

ctypedef void (*PFNleveldb_options_set_create_if_missingPROC)(leveldb_options_t* options, unsigned char v)
cdef PFNleveldb_options_set_create_if_missingPROC leveldb_options_set_create_if_missing = <PFNleveldb_options_set_create_if_missingPROC>getFunction(b"leveldb_options_set_create_if_missing")

ctypedef void (*PFNleveldb_options_set_error_if_existsPROC)(leveldb_options_t* options, unsigned char v)
cdef PFNleveldb_options_set_error_if_existsPROC leveldb_options_set_error_if_exists = <PFNleveldb_options_set_error_if_existsPROC>getFunction(b"leveldb_options_set_error_if_exists")

ctypedef void (*PFNleveldb_options_set_paranoid_checksPROC)(leveldb_options_t* options, unsigned char v)
cdef PFNleveldb_options_set_paranoid_checksPROC leveldb_options_set_paranoid_checks = <PFNleveldb_options_set_paranoid_checksPROC>getFunction(b"leveldb_options_set_paranoid_checks")

ctypedef void (*PFNleveldb_options_set_envPROC)(leveldb_options_t* options, leveldb_env_t* env)

ctypedef void (*PFNleveldb_options_set_info_logPROC)(leveldb_options_t* options, leveldb_logger_t* l)

ctypedef void (*PFNleveldb_options_set_write_buffer_sizePROC)(leveldb_options_t* options, size_t s)
cdef PFNleveldb_options_set_write_buffer_sizePROC leveldb_options_set_write_buffer_size = <PFNleveldb_options_set_write_buffer_sizePROC>getFunction(b"leveldb_options_set_write_buffer_size")

ctypedef void (*PFNleveldb_options_set_max_open_filesPROC)(leveldb_options_t* options, int n)
cdef PFNleveldb_options_set_max_open_filesPROC leveldb_options_set_max_open_files = <PFNleveldb_options_set_max_open_filesPROC>getFunction(b"leveldb_options_set_max_open_files")

ctypedef void (*PFNleveldb_options_set_cachePROC)(leveldb_options_t* options, leveldb_cache_t* c)
cdef PFNleveldb_options_set_cachePROC leveldb_options_set_cache = <PFNleveldb_options_set_cachePROC>getFunction(b"leveldb_options_set_cache")

ctypedef void (*PFNleveldb_options_set_block_sizePROC)(leveldb_options_t* options, size_t s)
cdef PFNleveldb_options_set_block_sizePROC leveldb_options_set_block_size = <PFNleveldb_options_set_block_sizePROC>getFunction(b"leveldb_options_set_block_size")

ctypedef void (*PFNleveldb_options_set_block_restart_intervalPROC)(leveldb_options_t* options, int n)

ctypedef void (*PFNleveldb_options_set_compressionPROC)(leveldb_options_t* options, int t)
cdef PFNleveldb_options_set_compressionPROC leveldb_options_set_compression = <PFNleveldb_options_set_compressionPROC>getFunction(b"leveldb_options_set_compression")

ctypedef leveldb_comparator_t* (*PFNleveldb_comparator_createPROC)(void* state, void (*destructor)(void*), int (*compare)(void*, const char* a, size_t alen, const char* b, size_t blen), const char* (*name)(void*))

ctypedef void (*PFNleveldb_comparator_destroyPROC)(leveldb_comparator_t* cmp)

# ctypedef leveldb_filterpolicy_t* (*PFNleveldb_filterpolicy_createPROC)(void* state, void (*destructor)(void*), char* (*create_filter)(void*, const char* const* key_array, const size_t* key_length_array, int num_keys, size_t* filter_length), unsigned char (*key_may_match)(void*, const char* key, size_t length, const char* filter, size_t filter_length), const char* (*name)(void*))

ctypedef void (*PFNleveldb_filterpolicy_destroyPROC)(leveldb_filterpolicy_t* policy)
cdef PFNleveldb_filterpolicy_destroyPROC leveldb_filterpolicy_destroy = <PFNleveldb_filterpolicy_destroyPROC>getFunction(b"leveldb_filterpolicy_destroy")

ctypedef leveldb_filterpolicy_t* (*PFNleveldb_filterpolicy_create_bloomPROC)(int bits_per_key)
cdef PFNleveldb_filterpolicy_create_bloomPROC leveldb_filterpolicy_create_bloom = <PFNleveldb_filterpolicy_create_bloomPROC>getFunction(b"leveldb_filterpolicy_create_bloom")

ctypedef leveldb_readoptions_t* (*PFNleveldb_readoptions_createPROC)()
cdef PFNleveldb_readoptions_createPROC leveldb_readoptions_create = <PFNleveldb_readoptions_createPROC>getFunction(b"leveldb_readoptions_create")

ctypedef void (*PFNleveldb_readoptions_destroyPROC)(leveldb_readoptions_t* options)
cdef PFNleveldb_readoptions_destroyPROC leveldb_readoptions_destroy = <PFNleveldb_readoptions_destroyPROC>getFunction(b"leveldb_readoptions_destroy")

ctypedef void (*PFNleveldb_readoptions_set_verify_checksumsPROC)(leveldb_readoptions_t* options, unsigned char v)
cdef PFNleveldb_readoptions_set_verify_checksumsPROC leveldb_readoptions_set_verify_checksums = <PFNleveldb_readoptions_set_verify_checksumsPROC>getFunction(b"leveldb_readoptions_set_verify_checksums")

ctypedef void (*PFNleveldb_readoptions_set_fill_cachePROC)(leveldb_readoptions_t* options, unsigned char v)
cdef PFNleveldb_readoptions_set_fill_cachePROC leveldb_readoptions_set_fill_cache = <PFNleveldb_readoptions_set_fill_cachePROC>getFunction(b"leveldb_readoptions_set_fill_cache")

ctypedef void (*PFNleveldb_readoptions_set_snapshotPROC)(leveldb_readoptions_t* options, const leveldb_snapshot_t*)
cdef PFNleveldb_readoptions_set_snapshotPROC leveldb_readoptions_set_snapshot = <PFNleveldb_readoptions_set_snapshotPROC>getFunction(b"leveldb_readoptions_set_snapshot")

ctypedef leveldb_writeoptions_t* (*PFNleveldb_writeoptions_createPROC)()
cdef PFNleveldb_writeoptions_createPROC leveldb_writeoptions_create = <PFNleveldb_writeoptions_createPROC>getFunction(b"leveldb_writeoptions_create")

ctypedef void (*PFNleveldb_writeoptions_destroyPROC)(leveldb_writeoptions_t* options)
cdef PFNleveldb_writeoptions_destroyPROC leveldb_writeoptions_destroy = <PFNleveldb_writeoptions_destroyPROC>getFunction(b"leveldb_writeoptions_destroy")

ctypedef void (*PFNleveldb_writeoptions_set_syncPROC)(leveldb_writeoptions_t* options, unsigned char v)
cdef PFNleveldb_writeoptions_set_syncPROC leveldb_writeoptions_set_sync = <PFNleveldb_writeoptions_set_syncPROC>getFunction(b"leveldb_writeoptions_set_sync")

ctypedef leveldb_cache_t* (*PFNleveldb_cache_create_lruPROC)(size_t capacity)
cdef PFNleveldb_cache_create_lruPROC leveldb_cache_create_lru = <PFNleveldb_cache_create_lruPROC>getFunction(b"leveldb_cache_create_lru")

ctypedef void (*PFNleveldb_cache_destroyPROC)(leveldb_cache_t* cache)
cdef PFNleveldb_cache_destroyPROC leveldb_cache_destroy = <PFNleveldb_cache_destroyPROC>getFunction(b"leveldb_cache_destroy")

ctypedef leveldb_env_t* (*PFNleveldb_create_default_envPROC)()

ctypedef void (*PFNleveldb_env_destroyPROC)(leveldb_env_t* env)

ctypedef void (*PFNleveldb_freePROC)(void* ptr)
cdef PFNleveldb_freePROC leveldb_free = <PFNleveldb_freePROC>getFunction(b"leveldb_free")

ctypedef int (*PFNleveldb_major_versionPROC)()

ctypedef int (*PFNleveldb_minor_versionPROC)()


class LevelDBException(Exception):
    """
    The exception thrown for all leveldb related errors.
    """

    pass


cdef inline void _checkError(char *err):
    """Utility function for checking the error code returned by some leveldb functions."""
    cdef bytes message
    if err is not NULL:  # Not an empty null-terminated string
        message = err
        leveldb_free(err)
        raise LevelDBException(message.decode("utf-8"))

cdef inline void _check_db(void *db):
    if db is NULL:
        raise LevelDBException("The database has been closed.")


@cython.final
cdef class LevelDB:
    cdef leveldb_t* db
    cdef leveldb_readoptions_t* read_options
    cdef leveldb_writeoptions_t* write_options

    def __init__(self, str path, unsigned char create_if_missing = False):
        """
        Construct a new :class:`LevelDB` instance from the database at the given path.

        A leveldb database is like a dictionary that only contains bytes as the keys and values and exists entirely on the disk.

        :param path: The path to the database directory.
        :param create_if_missing: If True and there is no database at the given path a new database will be created.
        :raises: LevelDBException if create_if_missing is False and the db does not exist.
        """
        self._open(path, create_if_missing)

    def __cinit__(self):
        self.db = NULL
        self.read_options = NULL
        self.write_options = NULL

    cdef void _open(self, str path, unsigned char create_if_missing = False) except *:
        if not os.path.isdir(path):
            if create_if_missing:
                os.makedirs(path)
            else:
                raise LevelDBException(f"No database exists to open at {path}")
        filter_policy = leveldb_filterpolicy_create_bloom(10)
        cache = leveldb_cache_create_lru(40 * 1024 * 1024)
        options = leveldb_options_create()
        # Many of these options were pulled from Podshot/MCEdit-Unified
        leveldb_options_set_compression(options, leveldb_zlib_raw_compression)
        leveldb_options_set_filter_policy(options, filter_policy)
        leveldb_options_set_create_if_missing(options, create_if_missing)
        leveldb_options_set_write_buffer_size(options, 4 * 1024 * 1024)
        leveldb_options_set_cache(options, cache)
        leveldb_options_set_block_size(options, 163840)
        cdef char *error = NULL
        db = leveldb_open(options, path.encode("utf-8"), &error)
        leveldb_options_destroy(options)
        _checkError(error)

        self.db = db
        self.read_options = leveldb_readoptions_create()
        self.write_options = leveldb_writeoptions_create()

    cpdef void close(self, unsigned char compact=True) except *:
        """
        Close the leveldb database.

        :param compact: If True will compact the database making it take less memory.
        """
        _check_db(self.db)
        if compact:
            leveldb_compact_range(self.db, NULL, 0, NULL, 0)
        leveldb_close(self.db)
        self.db = NULL
        leveldb_readoptions_destroy(self.read_options)
        leveldb_writeoptions_destroy(self.write_options)

    cpdef bytes get(self, bytes key):
        """
        Get a key from the database.

        :param key: The key to get from the database.
        :return: The data stored behind the given key.
        :raises: KeyError if the requested key is not present.
        """
        cdef size_t vallen = 0
        cdef char *val = self.get_raw(key, len(key), &vallen)
        ret = PyBytes_FromStringAndSize(val, vallen)
        leveldb_free(val)
        return ret

    cdef char* get_raw(self, char *key, size_t keylen, size_t *vallen) except *:
        """
        Low level cython wrapper for the get method.
        Return value must be freed using leveldb_free.
        
        :param key: The key to get from the database.
        :param keylen: The length of the key.
        :param vallen: size_t pointer to put the length of the returned val
        :return: The data stored behind the given key.
        :raises: KeyError if the requested key is not present.
        """
        _check_db(self.db)
        cdef char *error = NULL
        cdef char *val = leveldb_get(self.db, self.read_options, key, keylen, vallen, &error)
        _checkError(error)
        if val is NULL:
            raise KeyError(key)
        return val

    cpdef void put(self, bytes key, bytes val) except *:
        """
        Add a key to the database.

        :param key: The key to store the value under.
        :param val: The value to store.
        """
        self.put_raw(key, len(key), val, len(val))

    cdef void put_raw(self, char *key, size_t keylen, char *val, size_t vallen) except *:
        _check_db(self.db)
        cdef char *error = NULL
        leveldb_put(self.db, self.write_options, key, keylen, val, vallen, &error)
        _checkError(error)

    cpdef void putBatch(self, dict data: Dict[bytes, bytes]):
        """
        Put one or more key and value pair into the database. Works the same as dict.update
        
        :param data: A dictionary of keys and values to add to the database
        """

        _check_db(self.db)
        cdef bytes k, v
        batch = leveldb_writebatch_create()
        for k, v in data.items():
            leveldb_writebatch_put(batch, k, len(k), v, len(v))
        cdef char *error = NULL
        leveldb_write(self.db, self.write_options, batch, &error)
        _checkError(error)

    cpdef void delete(self, bytes key) except *:
        """
        Delete a key from the database.

        :param key: The key to delete from the database.
        """
        self.delete_raw(key, len(key))

    cdef void delete_raw(self, char *key, size_t keylen) except *:
        cdef char *error = NULL
        leveldb_delete(self.db, self.write_options, key, keylen, &error)
        _checkError(error)

    def iterate(
        self, start: bytes = None, end: bytes = None
    ):# -> Iterator[Tuple[bytes, bytes]]:
        """
        Iterate through all keys and data that exist between the given keys.

        :param start: The key to start at. Leave as None to start at the beginning.
        :param end: The key to end at. Leave as None to start at the beginning.
        """
        _check_db(self.db)
        cdef bytes key_bytes
        cdef char *key
        cdef char *val
        cdef size_t keylen, vallen
        it = leveldb_create_iterator(self.db, self.read_options)
        if start is None:
            leveldb_iter_seek_to_first(it)
        else:
            leveldb_iter_seek(it, start, len(start))
        try:
            while leveldb_iter_valid(it):
                key = leveldb_iter_key(it, &keylen)
                key_bytes = PyBytes_FromStringAndSize(key, keylen)
                if end is not None and key_bytes >= end:
                    break
                val = leveldb_iter_value(it, &vallen)
                yield key_bytes, PyBytes_FromStringAndSize(val, vallen)
                leveldb_iter_next(it)
        finally:
            leveldb_iter_destroy(it)

    def keys(self):# -> Iterator[bytes]:
        """An iterable of all the keys in the database."""
        _check_db(self.db)
        cdef char *key
        cdef size_t keylen
        it = leveldb_create_iterator(self.db, self.read_options)
        leveldb_iter_seek_to_first(it)
        try:
            while leveldb_iter_valid(it):
                key = leveldb_iter_key(it, &keylen)
                yield PyBytes_FromStringAndSize(key, keylen)
                leveldb_iter_next(it)
        finally:
            leveldb_iter_destroy(it)

    def items(self):# -> Iterator[Tuple[bytes, bytes]]:
        _check_db(self.db)
        cdef char *key
        cdef char *val
        cdef size_t keylen, vallen
        it = leveldb_create_iterator(self.db, self.read_options)
        leveldb_iter_seek_to_first(it)
        try:
            while leveldb_iter_valid(it):
                key = leveldb_iter_key(it, &keylen)
                val = leveldb_iter_value(it, &vallen)
                yield PyBytes_FromStringAndSize(key, keylen), PyBytes_FromStringAndSize(val, vallen)
                leveldb_iter_next(it)
        finally:
            leveldb_iter_destroy(it)

    def __contains__(self, bytes key):
        keys = list(self.iterate(key, key + b"\x00"))
        return bool(keys) and keys[0][0] == key

    def __iter__(self) -> Iterator[bytes]:
        return self.keys()
