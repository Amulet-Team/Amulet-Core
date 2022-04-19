import logging
import sys
import os

log = logging.getLogger("amulet")


def _init_logging():
    log.setLevel(logging.DEBUG if "amulet-debug" in sys.argv else logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # TODO: remove the file logger from here so that the application has to set it up
    os.makedirs("./logs", exist_ok=True)
    file_handler = logging.FileHandler("./logs/amulet_core.log", "w", encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    log.addHandler(file_handler)
    log.addHandler(console_handler)


_init_logging()


def factory_reset():
    """
    Disable the handlers implemented here and reset to the factory state.
    This exists so that calling code can implement the handlers as desired.
    It is suggested that libraries should not implement their own handlers however this library can be
    used on its own so having a console handler set up by default is beneficial in that case.
    """
    while log.hasHandlers():
        handler = log.handlers[0]
        log.removeHandler(handler)
        handler.close()
    log.setLevel(logging.NOTSET)
