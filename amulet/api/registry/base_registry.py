from typing import Union, Tuple, Generator, Iterable, Any

BaseType = Any


class BaseRegistry:
    def __len__(self):
        raise NotImplementedError

    def __contains__(self, item: Union[int, BaseType]):
        raise NotImplementedError

    def __iter__(self) -> Iterable[BaseType]:
        raise NotImplementedError

    def values(self) -> Tuple[BaseType]:
        raise NotImplementedError

    def items(self) -> Generator[Tuple[int, BaseType], None, None]:
        raise NotImplementedError

    def __getitem__(self, item):
        raise NotImplementedError

    def register(self, item: BaseType) -> int:
        raise NotImplementedError
