class FormatError(Exception):
    pass


class FormatLoaderInvalidFormat(FormatError):
    pass


class FormatLoaderMismatched(FormatError):
    pass


class FormatLoaderNoneMatched(FormatError):
    pass


class InvalidBlockException(Exception):
    pass


class ChunkDoesntExistException(Exception):  # Possibly change the name in the future
    pass


class VersionLoaderInvalidFormat(Exception):
    pass


class VersionLoaderMismatched(Exception):
    pass
