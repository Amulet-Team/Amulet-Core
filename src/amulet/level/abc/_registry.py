from typing import overload
from collections.abc import Mapping, Iterator


class IdRegistry(Mapping[int, tuple[str, str]]):
    def __init__(self) -> None:
        self._str_to_int: dict[tuple[str, str], int] = {}
        self._int_to_str: dict[int, tuple[str, str]] = {}

    def numerical_id_to_namespace_id(self, index: int) -> tuple[str, str]:
        return self._int_to_str[index]

    def namespace_id_to_numerical_id(self, namespace: str, base_name: str) -> int:
        return self._str_to_int[(namespace, base_name)]

    def register(self, index: int, block_id: tuple[str, str]) -> None:
        if block_id in self._str_to_int:
            raise RuntimeError(f"id {block_id} has already been registered")
        if index in self._int_to_str:
            raise RuntimeError(f"index {index} has already been registered")
        self._str_to_int[block_id] = index
        self._int_to_str[index] = block_id

    @overload
    def __getitem__(self, key: int) -> tuple[str, str]: ...

    @overload
    def __getitem__(self, key: tuple[str, str]) -> int: ...

    def __getitem__(self, key: int | tuple[str, str]) -> int | tuple[str, str]:
        if isinstance(key, int):
            return self._int_to_str[key]
        else:
            return self._str_to_int[key]

    def __len__(self) -> int:
        return len(self._int_to_str)

    def __iter__(self) -> Iterator[int]:
        yield from self._int_to_str
