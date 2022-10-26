from typing import Union, Dict, List, Tuple
from enum import Enum
import logging

log = logging.getLogger(__name__)


class StatusFormats(Enum):
    """
    The different formats the status value can be converted to.

    >>> StatusFormats.Raw  # The raw float value
    >>> StatusFormats.Bedrock  # as an integer between 0 and 2
    >>> StatusFormats.Java_13  # as a string
    >>> StatusFormats.Java_14  # as a string
    """

    Raw = 0  # The raw float value
    Bedrock = 1  # as an integer between 0 and 2
    Java_13 = 2  # as a string
    Java_14 = 3  # as a string


J13 = StatusFormats.Java_13
J14 = StatusFormats.Java_14

states = {
    "empty": [[J13, J14], -1],
    "structure_starts": [[J14], -0.9],
    "structure_references": [[J14], -0.8],
    "biomes": [[J14], -0.7],
    "noise": [[J14], -0.6],
    "base": [[J13], -0.5],
    "surface": [[J14], -0.5],
    "carved": [[J13], -0.4],
    "carvers": [[J14], -0.4],
    "liquid_carved": [[J13], -0.3],
    "liquid_carvers": [[J14], -0.3],
    "decorated": [[J13], -0.2],
    "features": [[J14], -0.2],
    "lighted": [[J13], -0.1],
    "light": [[J14], -0.1],
    # 0.0	needs ticked
    # 1.0	needs population
    "mobs_spawned": [[J13], 1.1],
    "spawn": [[J14], 1.1],
    "finalized": [[J13], 1.5],
    "heightmaps": [[J14], 1.5],
    "fullchunk": [[J13], 1.9],
    "postprocessed": [[J13], 2.0],
    "full": [[J14], 2.0],
    # 2.0	done
}

versions: Dict[StatusFormats, List[Tuple[float, str]]] = {}
for key, val in states.items():
    for version_ in val[0]:
        versions.setdefault(version_, []).append((val[1], key))
for data in versions.values():
    data.sort(key=lambda val_: val_[0], reverse=True)


class Status:
    """
    A class to represent the generation state of a chunk.

    This stores the chunk status as a float in the range -1 to 2 where -1 is nothing generated and 2 being fully generated.
    """

    def __init__(self):
        """
        Construct an instance of the :class:`Status` class.
        """
        self._value = 2.0

    @property
    def value(self) -> float:
        """
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
        """
        return self._value

    @value.setter
    def value(self, value: Union[float, int, str]):
        """
        Set the status value.

        >>> chunk.status.value = 2
        >>> chunk.status.value = "full"

        This can be a float/int or a string. If it is a string it is looked up in the states look up table to find the float value it corresponds with.

        :param value: The value to set as the generation stage.
        """
        if isinstance(value, float):
            self._value = value
        elif isinstance(value, int):
            self._value = float(value)
        elif isinstance(value, str) and value in states:
            self._value = states[value][1]
        else:
            log.error(
                f"Unrecognised chunk state {value}. Defaulting to fully generated.\nIf this is a new version report it to the developers."
            )
            self._value = 2.0

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
        if isinstance(status_format, StatusFormats):
            if status_format == StatusFormats.Raw:
                return self._value
            elif status_format == StatusFormats.Bedrock:  # Bedrock (0, 1 or 2)
                return int(max(min(2, self._value), 0))
            elif status_format in versions:  # Java 1.13/1.14
                value = next(
                    (v for v in versions[status_format] if v[0] <= self._value), None
                )
                if value is None:
                    value = next(
                        (v for v in versions[status_format] if v[0] <= 2.0), None
                    )
                return value[1]
            else:
                raise ValueError(f"Unsupported status format {status_format}")
        else:
            raise ValueError("Version must be one of the states of StatusFormats")
