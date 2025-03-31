from unittest import TestCase
import os

from PIL import Image

from amulet.image import (
    get_missing_no_icon,
    get_missing_pack_icon,
    get_missing_world_icon,
    missing_no_icon_path,
    missing_world_icon_path,
    missing_pack_icon_path,
)


class ImageTestCase(TestCase):
    def test_get_image(self) -> None:
        missing_no_icon = get_missing_no_icon()
        try:
            self.assertIsInstance(missing_no_icon, Image.Image)
        finally:
            missing_no_icon.close()

        missing_pack_icon = get_missing_pack_icon()
        try:
            self.assertIsInstance(missing_pack_icon, Image.Image)
        finally:
            missing_pack_icon.close()

        missing_world_icon = get_missing_world_icon()
        try:
            self.assertIsInstance(missing_world_icon, Image.Image)
        finally:
            missing_world_icon.close()

    def test_image_paths(self) -> None:
        self.assertIsInstance(missing_no_icon_path, str)
        self.assertIsInstance(missing_world_icon_path, str)
        self.assertIsInstance(missing_pack_icon_path, str)
        self.assertTrue(os.path.isfile(missing_no_icon_path))
        self.assertTrue(os.path.isfile(missing_world_icon_path))
        self.assertTrue(os.path.isfile(missing_pack_icon_path))
