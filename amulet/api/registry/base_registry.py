from abc import ABC, abstractmethod
from typing import Union, Tuple, Generator, Iterable, Any

BaseType = Any


class BaseRegistry(ABC):
    @abstractmethod
    def __len__(self):
        raise NotImplementedError

    @abstractmethod
    def __contains__(self, item: Union[int, BaseType]):
        raise NotImplementedError

    @abstractmethod
    def __iter__(self) -> Iterable[BaseType]:
        raise NotImplementedError

    @abstractmethod
    def values(self) -> Tuple[BaseType]:
        raise NotImplementedError

    @abstractmethod
    def items(self) -> Generator[Tuple[int, BaseType], None, None]:
        raise NotImplementedError

    @abstractmethod
    def __getitem__(self, item):
        raise NotImplementedError

    @abstractmethod
    def register(self, item: BaseType) -> int:
        raise NotImplementedError
