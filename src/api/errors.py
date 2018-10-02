class FormatError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class FormatLoaderInvalidFormat(FormatError):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class FormatLoaderMismatched(FormatError):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class FormatLoaderNoneMatched(FormatError):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
