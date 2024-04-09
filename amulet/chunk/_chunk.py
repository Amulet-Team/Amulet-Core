from __future__ import annotations
from typing import ClassVar, Self, Protocol, KeysView, ValuesView, ItemsView, Any
from collections.abc import Iterable, Iterator
from abc import ABC, abstractmethod

from .components.abc import ChunkComponent, GetT, SetT, UnloadedComponent


class ComponentDataMapping(Protocol[GetT, SetT]):
    """A MutableMapping with values that match the first generic argument of ChunkComponent."""
    def __contains__(self, item: type[ChunkComponent[GetT, SetT]]) -> bool:
        ...

    def keys(self) -> KeysView[type[ChunkComponent[GetT, SetT]]]:
        ...

    def items(self) -> ItemsView[type[ChunkComponent[GetT, SetT]], GetT | UnloadedComponent]:
        ...

    def values(self) -> ValuesView[GetT | UnloadedComponent]:
        ...

    def get(self, key: type[ChunkComponent[GetT, SetT]]) -> GetT | UnloadedComponent:
        ...

    def __eq__(self, other: Any) -> bool:
        ...

    def __ne__(self, other: Any) -> bool:
        ...

    def pop(self, key: type[ChunkComponent[GetT, SetT]]) -> GetT | UnloadedComponent:
        ...

    def popitem(self) -> GetT | UnloadedComponent:
        ...

    def clear(self) -> None:
        ...

    def update(self, value: ComponentDataMapping | Iterable[tuple[type[ChunkComponent[GetT, SetT]], GetT | UnloadedComponent]]) -> None:
        ...

    def setdefault(self, key: type[ChunkComponent[GetT, SetT]], default: GetT | UnloadedComponent | None = None) -> GetT | None:
        ...

    def __getitem__(self, key: type[ChunkComponent[GetT, SetT]]) -> GetT | UnloadedComponent:
        ...

    def __setitem__(self, key: type[ChunkComponent[GetT, SetT]], value: GetT | UnloadedComponent) -> None:
        ...

    def __delitem__(self, key: type[ChunkComponent[GetT, SetT]]) -> None:
        ...

    def __len__(self) -> int:
        ...

    def __iter__(self) -> Iterator[type[ChunkComponent[GetT, SetT]]]:
        ...

    def copy(self) -> Self:
        ...


class Chunk(ABC):
    components: ClassVar[frozenset[type[ChunkComponent]]] = frozenset()
    _component_data: ComponentDataMapping

    def __init__(self):
        self._component_data = dict.fromkeys(self.components, UnloadedComponent.value)  # type: ignore

    @classmethod
    @abstractmethod
    def new(cls, *args, **kwargs) -> Self:
        """Create a new empty chunk with all components defined."""
        raise NotImplementedError

    @classmethod
    def has_component(cls, component_class: type[ChunkComponent]) -> bool:
        """Check if this chunk has the requested component."""
        return component_class in cls.components

    def get_component(self, component_class: type[ChunkComponent[GetT, SetT]]) -> GetT:
        """Get the data for the requested component.

        :param component_class: The component class to get the data for.
        :return: The components data.
        :raises:
            RuntimeError
        """
        if component_class not in self._component_data:
            raise ValueError(f"This chunk does not have component {component_class}")
        component_data: GetT | UnloadedComponent = self._component_data[component_class]
        if component_data is UnloadedComponent.value:
            raise RuntimeError(f"Component {component_class} has not been loaded.")
        return component_data

    def set_component(self, component_class: type[ChunkComponent[GetT, SetT]], component_data: SetT) -> None:
        """Set the component data."""
        if component_class not in self._component_data:
            raise ValueError(f"This chunk does not have component {component_class}")
        old_component_data = self._component_data[component_class]
        new_component_data = component_class.fix_set_data(old_component_data, component_data)
        self._component_data[component_class] = new_component_data

    @property
    def component_data(self) -> ComponentDataMapping:
        """All the components and their data for this chunk."""
        return self._component_data.copy()

    @classmethod
    def from_component_data(cls, components: ComponentDataMapping) -> Self:
        """For internal use only.

        Create a new chunk from component data.
        """
        self = cls()
        if components.keys() != cls.components:
            raise ValueError("Components do not match the components for this class.")
        self._component_data.update(components)
        return self
