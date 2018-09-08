from api.box import SelectionBox
from api.operation import Operation


class Clone(Operation):
    def __init__(self, source_box: SelectionBox, target_box: SelectionBox):
        self.source_box = source_box
        self.target_box = target_box

    def run_operation(self, world):
        if len(self.source_box) != len(self.target_box):
            raise Exception(
                "Source Box and Target Box must have the same amount of subboxes"
            )

        for source, target in zip(
            self.source_box.subboxes(), self.target_box.subboxes()
        ):
            if source.shape != target.shape:
                raise Exception("The shape of the selections needs to be the same")

        for source, target in zip(
            self.source_box.subboxes(), self.target_box.subboxes()
        ):
            source_generator = world.get_sub_chunks(*source.to_slice())
            target_generator = world.get_sub_chunks(*target.to_slice())
            for source_selection, target_selection in zip(
                source_generator, target_generator
            ):
                target_selection.blocks = source_selection.blocks
