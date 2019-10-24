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


class ChunkDoesNotExist(Exception):
    pass
