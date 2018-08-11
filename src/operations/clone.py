from api.box import SubBox
from api.operation import Operation


class Clone(Operation):
    def __init__(self, source_selection: SubBox, target_selection: SubBox):
        self.source_selection = source_selection
        self.target_selection = target_selection

    def run_operation(self, world):
        source_selection = world.get_blocks_slice(*self.source_selection.to_slice())
        target_selection = world.get_blocks_slice(*self.target_selection.to_slice())
        if source_selection.shape != target_selection.shape:
            raise Exception("The shape of the selections needs to be the same")
        target_selection[:, :, :] = source_selection
