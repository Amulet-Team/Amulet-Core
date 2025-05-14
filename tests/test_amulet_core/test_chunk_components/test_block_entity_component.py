from unittest import TestCase


class BlockEntityComponentTestCase(TestCase):
    def test_cpp(self) -> None:
        from test_amulet_core.test_chunk_components.test_block_entity_component_ import (
            test_block_entity_component,
        )

        test_block_entity_component()
