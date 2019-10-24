class FormatError(Exception):
    pass


class LoaderNoneMatched(FormatError):
    pass


class FormatLoaderInvalidFormat(FormatError):
    pass


class FormatLoaderMismatched(FormatError):
    pass


class FormatLoaderNoneMatched(FormatError):
    pass


class InterfaceLoaderNoneMatched(FormatError):
    pass


class TranslatorLoaderNoneMatched(FormatError):
    pass


class InvalidBlockException(Exception):
    pass


class ChunkDoesntExistException(Exception):  # Possibly change the name in the future
    pass
