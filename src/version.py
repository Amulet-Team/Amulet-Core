VERSION_NUMBER = (0, 0, 0)
VERSION_INT = -1
VERSION_STAGE = "DEV"

if __debug__:
    VERSION_STRING = (
        f"{'.'.join((str(n) for n in VERSION_NUMBER))}-{VERSION_STAGE}-source"
    )
else:
    VERSION_STRING = f"{'.'.join((str(n) for n in VERSION_NUMBER))}-{VERSION_STAGE}"
