from unittest import TestCase


class Biome3DComponentTestCase(TestCase):
    def test_cpp(self) -> None:
        from test_amulet_core.test_chunk_components.test_biome_3d_component_ import (
            test_biome_3d_component,
        )

        test_biome_3d_component()
