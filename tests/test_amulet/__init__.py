def _init() -> None:
    import sys

    # Import dependencies
    import amulet

    from ._test_amulet import init

    init(sys.modules[__name__])


_init()
