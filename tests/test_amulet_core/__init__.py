if __name__ != "test_amulet_core":
    raise RuntimeError(
        f"Module name is incorrect. Expected: 'test_amulet_core' got '{__name__}'"
    )


import faulthandler as _faulthandler

_faulthandler.enable()


def _init() -> None:
    import sys

    # Import dependencies
    import amulet.core

    # This needs to be an absolute path otherwise it may get called twice
    # on different module objects and crash when the interpreter shuts down.
    from test_amulet_core._test_amulet_core import init

    init(sys.modules[__name__])


_init()
