from amulet.level.bedrock._raw import BedrockRawChunk


class RawChunkComponent:
    """Storage for the unhandled raw chunk data."""

    __raw_chunk: BedrockRawChunk | None

    def __init__(self) -> None:
        self.__raw_chunk = None

    @property
    def raw_chunk(self) -> BedrockRawChunk:
        return self.__raw_chunk

    @raw_chunk.setter
    def raw_chunk(
        self,
        raw_chunk: BedrockRawChunk,
    ) -> None:
        if not isinstance(raw_chunk, BedrockRawChunk):
            raise TypeError
        self.__raw_chunk = raw_chunk
