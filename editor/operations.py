from typing import Union, Sequence
from editor.box import SubBox


class Operation:

    def __init__(self, world):
        self._world = world

    def get_world(self):
        return self._world


class SingleBlockChangeOperation(Operation):

    def __init__(self, world, x: int, y: int, z: int, blockstate: str):
        super(SingleBlockChangeOperation, self).__init__(world)
        self.coords = (x, y, z)
        self._blockstate = blockstate

    def get_block(self):
        return self._blockstate


class BatchBlockChangeOperation(Operation):

    def __init__(self, world, change_map=None):
        super(BatchBlockChangeOperation, self).__init__(world)
        if change_map:
            self._changes = change_map
        else:
            self._changes = {}

    def set_block(self, x: int, y: int, z: int, blockstate: str):
        coords = (x, y, z)
        if blockstate in self._changes:
            self._changes[blockstate].append(coords)
        else:
            self._changes[blockstate] = [coords]

    def get_block(self, x: int, y: int, z: int) -> Union[str, None]:
        coords = (x, y, z)
        for blockstate in self._changes:
            if coords in self._changes[blockstate]:
                return blockstate

        return None


class FillBlockChangeOperation(Operation):

    def __init__(self, world, affected_region: Sequence[SubBox], blockstate: str):
        super(FillBlockChangeOperation, self).__init__(world)
        self._affected_region = affected_region
        self._blockstate = blockstate

    def get_block(self):
        return self._blockstate

    def get_region(self):
        return self._affected_region


class ReplaceBlockChangeOperation(Operation):

    def __init__(
        self,
        world,
        affected_region: Sequence[SubBox],
        target_blockstate: str,
        result_blockstate: str,
    ):
        super(ReplaceBlockChangeOperation, self).__init__(world)
        self._affected_region = affected_region
        self._target = target_blockstate
        self._result = result_blockstate

    def get_target_blockstate(self):
        return self._target

    def get_result_blockstate(self):
        return self._result

    def get_region(self):
        return self._affected_region
