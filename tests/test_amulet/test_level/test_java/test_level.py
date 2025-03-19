from unittest import TestCase
from tempfile import TemporaryDirectory
import os

from amulet.level import get_level

from amulet.version import VersionNumber
from amulet.level.loader import LevelLoaderPathToken
from amulet.level.java import JavaLevel, JavaCreateArgsV1, JavaRawLevel

from tests.data.worlds_src import java_vanilla_1_13
from tests.data.world_utils import WorldTemp

# TODO: add tests for the virtual functions

class JavaLevelTestCase(TestCase):
    def test_load_level(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            level = JavaLevel.load(world_data.temp_path)
            self.assertIsInstance(level, JavaLevel)
            self.assertFalse(level.is_open())

    def test_create_level(self) -> None:
        with TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "level")
            level = JavaLevel.create(
                JavaCreateArgsV1(
                    False,
                    path,
                    VersionNumber(1631),
                    "AnvilLevel"
                )
            )
            self.assertIsInstance(level, JavaLevel)
            self.assertEqual("AnvilLevel", level.level_name)

    def test_get_level(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            level_1 = get_level(
                LevelLoaderPathToken(world_data.temp_path)
            )
            self.assertIsInstance(level_1, JavaLevel)
            level_2 = get_level(
                LevelLoaderPathToken(world_data.temp_path)
            )
            self.assertIs(level_1, level_2)

    def test_raw_level(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            level = JavaLevel.load(world_data.temp_path)
            self.assertIsInstance(level.raw_level, JavaRawLevel)
