from _typeshed import Incomplete

log: Incomplete

def _get_cache_dir() -> str: ...

TempPattern: Incomplete

def _clear_temp_dirs() -> None:
    """
    Try and delete historic temporary directories.
    If things went very wrong in past sessions temporary directories may still exist.
    """

class TempDir(str):
    '''
    A temporary directory to do with as you wish.

    >>> t = TempDir()
    >>> path = os.path.join(t, "your_file.txt")  # TempDir is a subclass of str
    >>> # make sure all files in the temporary directory are closed before releasing or closing this object.
    >>> # The temporary directory will be deleted when the last reference to `t` is lost or when `t.close()` is called
    '''
    def __new__(cls): ...
    __lock: Incomplete
    def __init__(self) -> None: ...
    def close(self) -> None:
        """Close the lock and delete the directory."""
    def __del__(self) -> None: ...
