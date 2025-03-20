from datetime import datetime
from tempfile import TemporaryDirectory
import os
from contextlib import contextmanager

from amulet.level import get_level

from amulet.version import VersionNumber
from amulet.level.loader import LevelLoaderPathToken
from amulet.level.java import JavaLevel, JavaCreateArgsV1, JavaRawLevel

from tests.data.worlds_src import java_vanilla_1_13
from tests.data.world_utils import WorldTemp
from test_amulet.test_level.test_abc.test_level import LevelTestCases


class JavaLevelTestCase(LevelTestCases.LevelTestCase):
    @contextmanager
    def level(self) -> JavaLevel:
        with WorldTemp(java_vanilla_1_13) as world_data:
            level = JavaLevel.load(world_data.temp_path)
            yield level

    @staticmethod
    def get_expected_platform() -> str:
        return "java"

    @staticmethod
    def get_expected_max_version() -> VersionNumber:
        return VersionNumber(1497)

    @staticmethod
    def get_expected_level_name() -> str:
        return "1.13 World"

    @staticmethod
    def get_expected_modified_time() -> datetime:
        return datetime(2018, 5, 30, 3, 36, 15, 463000)

    @staticmethod
    def get_expected_sub_chunk_size() -> int:
        return 16

    def test_load_level(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            level = JavaLevel.load(world_data.temp_path)
            self.assertIsInstance(level, JavaLevel)
            self.assertFalse(level.is_open())

    def test_create_level(self) -> None:
        with TemporaryDirectory() as temp_dir:
            path = os.path.join(temp_dir, "level")
            level = JavaLevel.create(
                JavaCreateArgsV1(False, path, VersionNumber(1631), "AnvilLevel")
            )
            self.assertIsInstance(level, JavaLevel)
            self.assertEqual("AnvilLevel", level.level_name)

    def test_get_level(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            level_1 = get_level(LevelLoaderPathToken(world_data.temp_path))
            self.assertIsInstance(level_1, JavaLevel)
            level_2 = get_level(LevelLoaderPathToken(world_data.temp_path))
            self.assertIs(level_1, level_2)

    def test_raw_level(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            level = JavaLevel.load(world_data.temp_path)
            self.assertIsInstance(level.raw_level, JavaRawLevel)
