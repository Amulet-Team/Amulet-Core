class FastWritable:
    def __init__(self) -> None:
        self._data: list[bytes] = []

    def getvalue(self) -> bytes:
        return b"".join(self._data)

    def write(self, data: bytes) -> None:
        self._data.append(data)
