from abc import ABC, abstractmethod


class BiomeData(ABC):
    @abstractmethod
    def numerical_id_to_namespace_id(self, numerical_id: int) -> tuple[str, str]:
        """Convert the numerical id to its namespace id"""
        raise NotImplementedError

    @abstractmethod
    def namespace_id_to_numerical_id(self, namespace: str, base_name: str) -> int:
        raise NotImplementedError
