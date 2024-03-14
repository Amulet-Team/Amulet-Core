"""Extension to the builtin weakref module."""

from typing import Any
from weakref import WeakMethod


# Classes have an __del__ method to run code at object destruction.
# This is usually sufficient if the object gets deleted before the interpreter exits.
# In some cases global variables are set to None causing the __del__ to fail if run after interpreter shutdown.
# I have noticed this while debugging.
#
# In the following example when debugging sys is None when __del__ is called after interpreter shutdown.
#
# >>> import sys
# >>>
# >>> class Cls:
# >>>     def __init__(self) -> None:
# >>>         self._sys_modules = sys.modules
# >>>         print(self._sys_modules)
# >>>
# >>>     def __del__(self) -> None:
# >>>         print(self._sys_modules)
# >>>         print(sys)
# >>>
# >>> t = Cls()
#
# weakref.finalize takes care of this. It can be manually called in the __del__ method if the object is garbage
# collected before interpreter shutdown or automatically run at interperter exit. It can only be called once.
# It must be given a weak method otherwise the instance will be kept alive until interpreter exit.
# weakref.WeakMethod is not directly callable so CallableWeakMethod is implemented to allow this.


class CallableWeakMethod(WeakMethod):
    """
    A wrapper around WeakMethod that makes the method directly callable.
    If the method no longer exists, this does nothing.
    """

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        meth = super().__call__()
        if meth is not None:
            return meth(*args, **kwargs)
