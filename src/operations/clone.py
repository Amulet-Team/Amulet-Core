from api.box import SubBox
from api.operation import Operation


class Clone(Operation):
    def __init__(self, source_box: SubBox, target_box: SubBox):
        self.source_box = source_box
        self.target_box = target_box

    def run_operation(self, world):
        if self.source_box.shape != self.target_box.shape:
            raise Exception("The shape of the selections needs to be the same")
        source_generator = world.get_selections_from_slices(*self.source_box.to_slice())
        target_generator = world.get_selections_from_slices(*self.target_box.to_slice())
        for target_selection in target_generator:
            source_selection = next(source_generator)
            target_selection.blocks = source_selection.blocks
