import numpy


class Selection:
    def __init__(self, blocks: numpy.ndarray):
        self._blocks = blocks

    @property
    def blocks(self):
        return self._blocks

    @blocks.setter
    def blocks(self, value):
        self._blocks = value
