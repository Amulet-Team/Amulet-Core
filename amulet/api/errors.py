class FormatError(Exception):
    pass


class LoaderNoneMatched(FormatError):
    pass


class FormatLoaderInvalidFormat(FormatError):
    pass


class FormatLoaderMismatched(FormatError):
    pass


class InvalidBlockException(Exception):
    pass


class EntryLoadError(Exception):
    pass


class EntryDoesNotExist(EntryLoadError):
    pass


class ChunkLoadError(EntryLoadError):
    pass


class ChunkSaveError(Exception):
    pass


class LevelDoesNotExist(Exception):
    pass


class ChunkDoesNotExist(EntryDoesNotExist, ChunkLoadError):
    pass


class ObjectReadError(Exception):
    pass


class ObjectWriteError(Exception):
    pass


class ObjectReadWriteError(ObjectReadError, ObjectWriteError):
    pass
