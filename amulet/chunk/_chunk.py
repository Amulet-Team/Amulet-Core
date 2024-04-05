from __future__ import annotations
from typing import ClassVar, Self
from abc import ABC, abstractmethod

from .components.abc import ChunkComponent, GetT, SetT, UnloadedComponent


class Chunk(ABC):
    components: ClassVar[frozenset[type[ChunkComponent]]] = frozenset()
    _component_data: dict[type[ChunkComponent[GetT, SetT]], GetT | UnloadedComponent]

    def __init__(self):
        self._component_data = dict.fromkeys(self.components, UnloadedComponent)

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
        """Get the data for the requested component."""
        return self._component_data[component_class]

    def set_component(self, component_class: type[ChunkComponent[GetT, SetT]], component_data: SetT) -> None:
        """Set the component data."""
        if component_class not in self._component_data:
            raise ValueError
        old_component_data = self._component_data[component_class]
        new_component_data = component_class.fix_set_data(old_component_data, component_data)
        self._component_data[component_class] = new_component_data

    @property
    def component_data(self) -> dict[type[ChunkComponent[GetT, SetT]], GetT | UnloadedComponent]:
        """All the components and their data for this chunk."""
        return self._component_data.copy()

    @classmethod
    def from_component_data(cls, components: dict[type[ChunkComponent[GetT, SetT]], GetT | UnloadedComponent]) -> Self:
        """For internal use only.

        Create a new chunk from component data.
        """
        self = cls()
        if components.keys() != cls.components:
            raise ValueError("Components do not match the components for this class.")
        self._component_data.update(components)
        return self
