if __name__ != "test_amulet_core":
    raise RuntimeError(
        f"Module name is incorrect. Expected: 'test_amulet_core' got '{__name__}'"
    )


import faulthandler

faulthandler.enable()


def _init() -> None:
    import sys

    # Import dependencies
    import amulet
    from amulet.utils.logging import set_min_log_level

    # Enable debug logging when running tests.
    set_min_log_level(0)

    # This needs to be an absolute path otherwise it may get called twice
    # on different module objects and crash when the interpreter shuts down.
    from test_amulet_core._test_amulet_core import init

    init(sys.modules[__name__])


_init()
