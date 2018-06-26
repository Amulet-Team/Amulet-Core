class SimpleStack:

    def __init__(self, initial_data=None):
        if initial_data:
            self._data = initial_data
        else:
            self._data = []
        self.__contains__ = self._data.__contains__
        self.__len__ = self._data.__len__
        self.pop = self._data.pop
        self.append = self._data.append

    def peek(self):
        if len(self._data) == 0:
            return None

        return self._data[-1]

    def is_empty(self) -> bool:
        return len(self._data) == 0
