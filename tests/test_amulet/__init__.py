if __name__ != "test_amulet":
    raise RuntimeError(
        f"Module name is incorrect. Expected: 'test_amulet' got '{__name__}'"
    )


def _init() -> None:
    import sys

    # Import dependencies
    import amulet
    from amulet.utils.logging import set_default_log_level
    # Enable debug logging when running tests.
    set_default_log_level(0)

    # This needs to be an absolute path otherwise it may get called twice
    # on different module objects and crash when the interpreter shuts down.
    from test_amulet._test_amulet import init

    init(sys.modules[__name__])


_init()
