def load_world(directory: str, _format: str = None, forced: bool = False) -> World:
    """
    Creates a Format loader from the given inputs and wraps it in a World class
    :param directory:
    :param _format:
    :param forced:
    :return:
    """
    log.info(f"Loading world {directory}")
    return World(directory, load_format(directory, _format, forced))


def load_format(
    directory: str, _format: str = None, forced: bool = False
) -> "WorldFormatWrapper":
    """
    Loads the world located at the given directory with the appropriate format loader.

    :param directory: The directory of the world
    :param _format: The format name to use
    :param forced: Whether to force load the world even if incompatible
    :return: The loaded world
    """
    if not os.path.isdir(directory):
        if os.path.exists(directory):
            log.error(f'The path "{directory}" does exist but it is not a directory')
            raise Exception(
                f'The path "{directory}" does exist but it is not a directory'
            )
        else:
            log.error(
                f'The path "{directory}" is not a valid path on this file system.'
            )
            raise Exception(
                f'The path "{directory}" is not a valid path on this file system.'
            )
    if _format is not None:
        if _format not in formats.loader:
            log.error(f"Could not find _format loader {_format}")
            raise FormatLoaderInvalidFormat(f"Could not find _format loader {_format}")
        if not forced and not formats.loader.identify(directory) == _format:
            log.error(f"{_format} is incompatible")
            raise FormatLoaderMismatched(f"{_format} is incompatible")
        format_class = formats.loader.get_by_id(_format)
    else:
        format_class = formats.loader.get(directory)
    return format_class(directory)
