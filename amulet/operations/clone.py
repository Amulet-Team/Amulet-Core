from amulet.api.selection import SelectionBox


def clone(world, source_box: SelectionBox, target_box: SelectionBox):
    if len(source_box) != len(target_box):
        raise Exception(
            "Source Box and Target Box must have the same amount of subboxes"
        )

    for source, target in zip(source_box.subboxes(), target_box.subboxes()):
        if source.shape != target.shape:
            raise Exception("The shape of the selections needs to be the same")

    for source, target in zip(source_box.subboxes(), target_box.subboxes()):
        source_generator = world.get_sub_chunks(*source.to_slice())
        target_generator = world.get_sub_chunks(*target.to_slice())
        for source_selection, target_selection in zip(
            source_generator, target_generator
        ):
            target_selection.blocks = source_selection.blocks
