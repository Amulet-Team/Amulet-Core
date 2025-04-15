from datetime import datetime
from tempfile import TemporaryDirectory
import os
from contextlib import contextmanager
from typing import Generator

from amulet.level import get_level

from amulet.version import VersionNumber
from amulet.level.loader import LevelLoaderPathToken
from amulet.level.abc import Dimension
from amulet.level.java import (
    JavaLevel,
    JavaCreateArgsV1,
    JavaRawLevel,
    JavaDimension,
)

from tests.data.worlds_src import java_vanilla_1_13
from tests.data.world_utils import WorldTemp
from test_amulet.test_level.test_abc.test_level import LevelTestCases


class JavaLevelTestCase(
    LevelTestCases.LevelTestCase,
    LevelTestCases.CompactibleLevelTestCase,
    LevelTestCases.DiskLevelTestCase,
    LevelTestCases.ReloadableLevelTestCase,
):
    @contextmanager
    def level(self) -> Generator[JavaLevel, None, None]:
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
    def get_expected_modified_time() -> float:
        return 1527647775.463

    @staticmethod
    def get_expected_sub_chunk_size() -> int:
        return 16

    def test_save(self) -> None:
        # TODO
        pass

    def test_history(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            level = JavaLevel.load(world_data.temp_path)
            level.open()
            try:
                self.assertTrue(level.history_enabled)
            finally:
                level.close()
        # TODO

    def test_dimension(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            level = JavaLevel.load(world_data.temp_path)
            with self.assertRaises(RuntimeError):
                _ = level.dimension_ids()
            level.open()
            try:
                dimension_ids = level.dimension_ids()
                self.assertIsInstance(dimension_ids, list)
                self.assertEqual(
                    {
                        "minecraft:overworld",
                        "minecraft:the_end",
                        "minecraft:the_nether",
                    },
                    set(dimension_ids),
                )
                for dimension_id in dimension_ids:
                    self.assertIsInstance(dimension_id, str)
                    dimension = level.get_dimension(dimension_id)
                    self.assertIsInstance(dimension, Dimension)
                    self.assertIsInstance(dimension, JavaDimension)
            finally:
                level.close()

    def test_compact(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            level = JavaLevel.load(world_data.temp_path)
            with self.assertRaises(RuntimeError):
                level.compact()
            level.open()
            try:
                level.compact()
            finally:
                level.close()

    def test_path(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            level = JavaLevel.load(world_data.temp_path)
            path = level.path
            self.assertIsInstance(path, str)
            self.assertEqual(world_data.temp_path, path)

    def test_reload_metadata(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            level = JavaLevel.load(world_data.temp_path)
            level.reload_metadata()
            level.open()
            try:
                with self.assertRaises(RuntimeError):
                    level.reload_metadata()
            finally:
                level.close()

    def test_reload(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            level = JavaLevel.load(world_data.temp_path)
            with self.assertRaises(RuntimeError):
                level.reload()
            level.open()
            try:
                level.reload()
            finally:
                level.close()

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
