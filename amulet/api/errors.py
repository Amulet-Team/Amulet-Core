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


class LevelDoesNotExist(Exception):
    pass


class ChunkLoadError(Exception):
    pass


class ChunkDoesNotExist(ChunkLoadError):
    pass


class WorldDatabaseAccessException(Exception):
    pass
