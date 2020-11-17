from typing import Any, Union, Generator, Callable, Tuple, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from amulet.api.world import World
    from .world_types import Dimension

# Operation types
OperationYieldType = Union[int, float, Tuple[Union[int, float], str]]
OperationReturnType = Optional[Union[Generator[OperationYieldType, None, Any], Any]]
OperationType = Callable[["World", "Dimension", Any], OperationReturnType]
