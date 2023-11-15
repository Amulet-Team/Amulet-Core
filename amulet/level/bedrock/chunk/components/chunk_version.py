class ChunkVersionComponent:
    def __init__(
        self, min_chunk_version: int, max_chunk_version: int, chunk_version
    ) -> None:
        self.__min_chunk_version = min_chunk_version
        self.__max_chunk_version = max_chunk_version
        self.__chunk_version = chunk_version

    @property
    def min_chunk_version(self) -> int:
        return self.__min_chunk_version

    @property
    def max_chunk_version(self) -> int:
        return self.__max_chunk_version

    @property
    def chunk_version(self) -> int:
        return self.__chunk_version

    @chunk_version.setter
    def chunk_version(self, chunk_version: int) -> None:
        chunk_version = int(chunk_version)
        if self.min_chunk_version <= chunk_version <= self.max_chunk_version:
            self.__chunk_version = chunk_version
        else:
            raise ValueError(chunk_version)
