from api.selection import SelectionBox
from api.operation import Operation


class DeleteChunk(Operation):
    def __init__(self, source_box: SelectionBox):
        self.source_box = source_box

    def run_operation(self, world):
        already_deleted_chunks = set()
        for subbox in self.source_box.subboxes():
            sub_chunks = world.get_sub_chunks(*subbox.to_slice())
            for sub_chunk in sub_chunks:
                chunk_coords = sub_chunk.parent_coordinates
                if chunk_coords in already_deleted_chunks:
                    continue
                sub_chunk._parent.delete()
                already_deleted_chunks.add(chunk_coords)
