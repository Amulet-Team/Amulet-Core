import os
from typing import List, Type, Tuple, Union, Callable, Any, Optional
import re

from api.data_structures import SimpleStack
from api.world import World
from formats.format_loader import loader

_coordinate_regex = re.compile(r"<(?P<x>\d+),(?P<y>\d+),(?P<z>\d+)>")


def parse_coordinates(coord: str) -> Union[Tuple[int, int, int], None]:
    """
    Utility function for parsing X,Y,Z coordinates from a string

    :param coord: The coordinate string to parse
    :return: A tuple of the coordinates as ints in X,Y,Z order
    """
    match = _coordinate_regex.match(coord)
    if match:
        return int(match.group("x")), int(match.group("y")), int(match.group("z"))

    return None


def command(command_name: str) -> Type[Union["SimpleCommand", "ComplexCommand"]]:
    """
    Registers a class as a command. If the class' parent is SimpleCommand, then it will use the abstracted methods.
    If the class' parent is ComplexCommand, then any method decorated with the `subcommand` decorator is registered as
    a sub-command of the given command name.

    :param command_name: The name used to identify the command, or the base command if using ComplexCommand
    """

    def decorator(command_class):
        command_class.registered = False
        if isinstance(command_class, type):
            if issubclass(command_class, SimpleCommand):
                command_class.command = (command_class.run, command_name)
                command_class.registered = True
            elif issubclass(command_class, ComplexCommand):
                command_class.base_command = command_name
                command_class.registered = True
        return command_class

    return decorator


class _CommandBase:
    """
    Abstract class that both :class:`SimpleCommand` and :class:`ComplexCommand` inherit from

    Note: Any class that inherits this class won't be registered as a command, you must
    inherit from :class:`SimpleCommand` or :class:`ComplexCommand`
    """

    def get_mode(self, mode_class: Type["Mode"]) -> "Mode":
        """
        Method for getting a Mode that the program is in

        :param mode_class: The class of the Mode instance to get
        :return: The instance of the specified Mode, None if the mode hasn't been entered
        """
        return self.handler.get_mode(mode_class)

    def in_mode(self, mode_class: Type["Mode"]) -> bool:
        """
        Method for checking whether the program is in the specified Mode

        :param mode_class: The class of the Mode to check for
        :return: True if the program is in the specified Mode, False otherwise
        """
        return self.handler.in_mode(mode_class)

    def __init__(self, cmd_handler):
        self.handler = cmd_handler

    # self.in_mode = self.handler.in_mode
    # self.get_mode = self.handler.get_mode

    def error(self, message: Any):
        """
        Utility method for printing an error message

        :param message: The error message
        """
        print(f"=== Error: {message}")

    def warning(self, message: Any):
        """
        Utility method for printing a warning message

        :param message: The warning message
        """
        print(f"== Warning: {message}")

    def get_shared_data(self, entry_path: str) -> Optional[object]:
        """
        Allows parsing and access to the shared data pool from a data accessor entry marked by a ``$``

        :param entry_path: The path to search for an entry, can start with a "$" but isn't required to
        :return: The value stored at the entry path, or None if the entry path couldn't be found
        """
        if entry_path.startswith("$"):
            entry_path = entry_path[1:]

        depth = entry_path.split(":")
        current_dict = self.handler.shared_data

        for key in depth[:-1]:
            if key not in current_dict:
                return None

            current_dict = current_dict[key]

        if depth[-1] not in current_dict:
            return None

        return current_dict[depth[-1]]


class SimpleCommand(_CommandBase):
    """
    Represents a command that can be executed within the command line
    """

    @classmethod
    def get_subclasses(cls) -> List[Type["SimpleCommand"]]:
        """
        Utility function to get all classes that extend this one

        :return: A list of all subclasses
        """
        result = []
        for subcls in cls.__subclasses__():
            result.append(subcls)
            result.extend(subcls.get_subclasses())
        return result

    def run(self, args: List[str]):
        """
        Abstract method where the command logic is ran when the command is executed

        :param args: The arguments of the full command
        """
        raise NotImplementedError()

    def help(self):
        """
        Abstract method for displaying a detailed help message about the command

        This method expects all information to be printed, nothing returned will be used
        """
        raise NotImplementedError()

    def short_help(self) -> str:
        """
        Abstract method for displaying a short help/summary message about the command

        This method should return a string that is <= 50 characters in length, anything
        longer will be truncated to 50 characters
        """
        raise NotImplementedError


def subcommand(sub_command_name: str) -> Callable[[List[str]], None]:
    """
    Registers the decorated method as a subcommand of the containing ComplexCommand.

    :param sub_command_name: The name/identifier of the subcommand
    """

    def decorator(f):
        f.command = (f, sub_command_name)
        return f

    return decorator


class ComplexCommand(_CommandBase):
    """
    Represents a base command that holds sub-commands
    """

    def __init_subclass__(cls, **kwargs):
        cls._persistent_data = {}
        cls.sub_commands = {}
        for key, val in cls.__dict__.items():
            sub_cmd = getattr(val, "command", None)
            if sub_cmd:
                cls.sub_commands[sub_cmd[1]] = sub_cmd[0]

    @classmethod
    def get_subclasses(cls) -> List[Type["ComplexCommand"]]:
        """
        Utility function to get all classes that extend this one

        :return: A list of all subclasses
        """
        result = []
        for sub in cls.__subclasses__():
            result.append(sub)
            result.extend(sub.get_subclasses())
        return result

    @classmethod
    def help(cls, command_name: str = None):
        """
        Abstract method that prints a detailed description of all the commands held by the base command if called
        with default arguments. If help is called on a specific command, the subcommand's name will supplied with `command_name`

        This method expects all information to be printed, nothing returned will be used

        :arg command_name: The name/identifier of the specific command help was called on, None if help was called on the base command of the ComplexCommand
        """
        raise NotImplementedError()

    @classmethod
    def short_help(cls) -> str:
        """
        Abstract method for displaying a short help/summary message about the general purpose of the sub-commands

        This method should return a string that is <= 50 characters in length, anything
        longer will be truncated to 50 characters
        """
        raise NotImplementedError()


class Mode:
    """
    Represents a configurable state that the command line can enter. This is useful for controlling the execution of various
    commands
    """

    def __init__(self, cmd_line_handler):
        self.handler = cmd_line_handler

    def __init_subclass__(cls, **kwargs):
        cls._persistent_data = {}

    def display(self) -> str:
        raise NotImplementedError()

    def before_execution(self, command: List[str]) -> bool:
        """
        Called before the execution of a command. Return True to run the given command, False to halt the execution.

        :param command: The command that is to be executed
        """
        raise NotImplementedError()

    def enter(self) -> bool:
        """
        Called when the mode is entered

        :return: Return False if the mode is not ready to be entered, otherwise return True.
        """
        raise NotImplementedError()

    def exit(self) -> bool:
        """
        Called when the mode is exited

        :return: Return False if the mode is not ready to be exited, otherwise return True. If the exit command is supplied a '-f' argument, then the return value is ignored
        """
        raise NotImplementedError()


class WorldMode(Mode):

    def __init__(self, cmd_line_handler, **kwargs):
        super(WorldMode, self).__init__(cmd_line_handler)
        self._world_path = kwargs.get("world")
        self._world_name = os.path.basename(self._world_path)
        self._unsaved_changes = SimpleStack()
        self._world: World = loader.load_world(self._world_path)

    @property
    def world_path(self) -> str:
        return self._world_path

    @property
    def world(self) -> World:
        return self._world

    def display(self) -> str:
        return self._world_name

    def before_execution(self, cmd) -> bool:
        if cmd[0] == "load" and not self._unsaved_changes.is_empty():
            print("You can't load a new world if you currently have unsaved changes")
            return False

        return True

    def enter(self) -> bool:
        if self.handler.in_mode(WorldMode):
            print("You cannot load a world if another world is already loaded!")
            return False

        if __debug__:
            print("Entered world mode")
        return True

    def exit(self) -> bool:
        if __debug__:
            print("Exiting world mode")
        if not self._unsaved_changes.is_empty():
            print("You have unsaved changes, do you really want to quit?")
            ans = input("(y/n)> ")
            if ans == "y":
                return True

            return False

        return True
