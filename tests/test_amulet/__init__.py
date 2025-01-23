def _init() -> None:
    import sys

    # Import dependencies
    import amulet

    # This needs to be an absoulte path otherwise it may get called twice
    # on different module objects and crash when the interpreter shuts down.
    from tests.test_amulet._test_amulet import init

    init(sys.modules[__name__])


_init()
