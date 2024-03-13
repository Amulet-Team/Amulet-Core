"""
Classes have an __del__ method to run code at object destruction.
This is usually sufficient if the object gets deleted before the interpreter exits.
In some cases global variables are set to None causing the __del__ to fail if run after interpreter shutdown.
I have noticed this while debugging.

In the following example when debugging sys is None when __del__ is called after interpreter shutdown.

>>> import sys
>>>
>>> class Cls:
>>>     def __init__(self) -> None:
>>>         self._sys_modules = sys.modules
>>>         print(self._sys_modules)
>>>
>>>     def __del__(self) -> None:
>>>         print(self._sys_modules)
>>>         print(sys)
>>>
>>> t = Cls()

I am not sure what triggers this behaviour, but it is best if destruction is run at object deletion or at exit whichever
comes first.
"""

from typing import Any
from abc import ABC, abstractmethod
from weakref import WeakMethod
import atexit
from runtime_final import final


class CallableWeakMethod(WeakMethod):
    """
    A wrapper around WeakMethod that makes the method directly callable.
    If the method no longer exists, this does nothing.
    """

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        meth = super().__call__()
        if meth is not None:
            return meth(*args, **kwargs)


class AtExitDestructor(ABC):
    """
    A class to streamline object destruction.
    Inherit from this class an implement :meth:`_del` and optionally :meth:`_atexit`.
    """

    def __init__(self) -> None:
        self.__deleted = False
        self.__atexit = CallableWeakMethod(self.__atexit__)
        atexit.register(self.__atexit)

    @final
    def __atexit__(self) -> None:
        self.__deleted = True
        self._atexit()

    def _atexit(self) -> None:
        """Method run when the interpreter is about to exit.

        Calls _del by default.
        Implement to get a custom atexit destructor.
        """
        self._del()

    @final
    def __del__(self) -> None:
        if not self.__deleted:
            self.__deleted = True
            atexit.unregister(self.__atexit)
            self._del()

    @abstractmethod
    def _del(self) -> None:
        """Method run when the object is deleted.

        This will not be called after the interpreter exits.
        See also :meth:`_atexit`"""
        raise NotImplementedError
