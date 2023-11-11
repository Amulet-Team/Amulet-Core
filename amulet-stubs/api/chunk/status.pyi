from _typeshed import Incomplete
from enum import Enum
from typing import Dict, List, Tuple, Union

log: Incomplete

class StatusFormats(Enum):
    """
    The different formats the status value can be converted to.

    >>> StatusFormats.Raw  # The raw float value
    >>> StatusFormats.Bedrock  # as an integer between 0 and 2
    >>> StatusFormats.Java_13  # as a string
    >>> StatusFormats.Java_14  # as a string
    """
    Raw: int
    Bedrock: int
    Java_13: int
    Java_14: int
    Java_20: int

J13: Incomplete
J14: Incomplete
J20: Incomplete
states: Incomplete
versions: Dict[StatusFormats, List[Tuple[float, str]]]

class Status:
    """
    A class to represent the generation state of a chunk.

    This stores the chunk status as a float in the range -1 to 2 where -1 is nothing generated and 2 being fully generated.
    """
    _value: float
    def __init__(self) -> None:
        """
        Construct an instance of the :class:`Status` class.
        """
    @property
    def value(self) -> float:
        '''
        **Getter**

        Get the raw status value.

        >>> status = chunk.status.value

        :return: The float status value in the range -1 to 2

        **Setter**

        Set the status value.

        >>> chunk.status.value = 2
        >>> chunk.status.value = "full"

        This can be a float/int or a string. If it is a string it is looked up in the states look up table to find the float value it corresponds with.

        :param value: The value to set as the generation stage.
        '''
    @value.setter
    def value(self, value: Union[float, int, str]):
        '''
        Set the status value.

        >>> chunk.status.value = 2
        >>> chunk.status.value = "full"

        This can be a float/int or a string. If it is a string it is looked up in the states look up table to find the float value it corresponds with.

        :param value: The value to set as the generation stage.
        '''
    def as_type(self, status_format: StatusFormats) -> Union[int, float, str]:
        """
        Get the generation state in a given format.

        >>> chunk.status.as_type(StatusFormats.Raw)
        2.0
        >>> chunk.status.as_type(StatusFormats.Bedrock)
        2
        >>> chunk.status.as_type(StatusFormats.Java_14)
        'full'

        :param status_format: The format the status should be returned in. Must be from :class:`StatusFormats`.
        :return: The status code in the requested format.
        """
