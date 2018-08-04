from typing import List, Type, Sequence, Union
import re

_coordinate_regex = re.compile(r"<(?P<x>\d+),(?P<y>\d+),(?P<z>\d+)>")


def parse_coordinate(coord: str) -> Union[Sequence[int], None]:
    match = _coordinate_regex.match(coord)
    if match:
        return int(match.group("x")), int(match.group("y")), int(match.group("z"))
    return None


class SimpleCommand:
    """
    Represents a command that can be executed within the command line
    """

    def __init__(self, cmd_line_handler):
        self.handler = cmd_line_handler

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


class ComplexCommand:
    """
    Represents a base command that holds sub-commands
    """

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
    def get_children(cls) -> Sequence[Type[SimpleCommand]]:
        """
        Returns the classes of the sub-commands that this base command holds

        :return: All sub-commands of this base command
        """
        raise NotImplementedError()

    @classmethod
    def help(cls):
        """
        Abstract method that prints a detailed description of all the commands held by the base command

        This method expects all information to be printed, nothing returned will be used
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
