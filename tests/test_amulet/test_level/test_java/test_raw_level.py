from unittest import TestCase
from tempfile import TemporaryDirectory
import os
import datetime

from PIL import Image

from amulet_nbt import NamedTag, StringTag

from amulet.version import VersionNumber
from amulet.utils.lock import OrderedLock
from amulet.utils.signal import Signal
from amulet.level.abc import IdRegistry
from amulet.level.java import JavaRawLevel, JavaCreateArgsV1, JavaRawDimension

from tests.data.worlds_src import java_vanilla_1_13
from tests.data.world_utils import WorldTemp


class JavaRawLevelTestCase(TestCase):
    def test_load(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            raw_level = JavaRawLevel.load(world_data.temp_path)
            self.assertIsInstance(raw_level, JavaRawLevel)
            self.assertEqual("1.13 World", raw_level.level_name)

    def test_create(self) -> None:
        with TemporaryDirectory() as temp_dir:
            raw_level = JavaRawLevel.create(
                JavaCreateArgsV1(
                    False,
                    os.path.join(temp_dir, "amulet_level"),
                    VersionNumber(1631),
                    "AmuletLevel",
                )
            )
            self.assertIsInstance(raw_level, JavaRawLevel)
            self.assertTrue(os.path.isdir(os.path.join(temp_dir, "amulet_level")))
            self.assertEqual("AmuletLevel", raw_level.level_name)

    def test_metadata(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            raw_level = JavaRawLevel.load(world_data.temp_path)
            self.assertIsInstance(raw_level.lock, OrderedLock)
            self.assertTrue(raw_level.is_supported())
            self.assertEqual(1527647775.463, raw_level.modified_time.timestamp())
            self.assertEqual("java", raw_level.platform)
            self.assertEqual(VersionNumber(1497), raw_level.data_version)
            self.assertEqual(world_data.temp_path, raw_level.path)
            self.assertEqual("1.13 World", raw_level.level_name)
            thumbnail = raw_level.thumbnail
            self.assertIsInstance(thumbnail, Image.Image)
            thumbnail.close()
            self.assertIsInstance(raw_level.opened, Signal)
            self.assertIsInstance(raw_level.closed, Signal)
            self.assertIsInstance(raw_level.reloaded, Signal)
            with self.assertRaises(RuntimeError):
                raw_level.reload()

    def test_reload_metadata(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            raw_level_1 = JavaRawLevel.load(world_data.temp_path)
            raw_level_2 = JavaRawLevel.load(world_data.temp_path)
            raw_level_1.open()
            try:
                raw_level_1.level_name = "HelloWorld"
                self.assertEqual("HelloWorld", raw_level_1.level_name)
                self.assertEqual("1.13 World", raw_level_2.level_name)
                raw_level_2.reload_metadata()
                self.assertEqual("HelloWorld", raw_level_2.level_name)
            finally:
                raw_level_1.close()

    def test_open_close(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            raw_level = JavaRawLevel.load(world_data.temp_path)

            opened_count = 0
            closed_count = 0
            reloaded_count = 0

            def on_open() -> None:
                nonlocal opened_count
                opened_count += 1

            def on_close() -> None:
                nonlocal closed_count
                closed_count += 1

            def on_reload() -> None:
                nonlocal reloaded_count
                reloaded_count += 1

            opened_token = raw_level.opened.connect(on_open)
            closed_token = raw_level.closed.connect(on_close)
            reloaded_token = raw_level.reloaded.connect(on_reload)

            self.assertFalse(raw_level.is_open())

            raw_level.open()
            self.assertTrue(raw_level.is_open())
            self.assertEqual(1, opened_count)
            self.assertEqual(0, closed_count)
            self.assertEqual(0, reloaded_count)

            opened_count = 0
            raw_level.reload()
            self.assertTrue(raw_level.is_open())
            self.assertEqual(0, opened_count)
            self.assertEqual(0, closed_count)
            self.assertEqual(1, reloaded_count)

            with self.assertRaises(RuntimeError):
                raw_level.reload_metadata()

            reloaded_count = 0
            raw_level.close()
            self.assertFalse(raw_level.is_open())
            self.assertEqual(0, opened_count)
            self.assertEqual(1, closed_count)
            self.assertEqual(0, reloaded_count)

    def test_level_dat(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            raw_level = JavaRawLevel.load(world_data.temp_path)
            raw_level.open()
            try:
                level_dat = raw_level.level_dat
                self.assertIsInstance(level_dat, NamedTag)
                level_dat.compound["HelloWorld"] = StringTag("HelloWorld")
                raw_level.level_dat = level_dat
            finally:
                raw_level.close()
            del raw_level

            raw_level_2 = JavaRawLevel.load(world_data.temp_path)
            self.assertEqual(
                StringTag("HelloWorld"), raw_level_2.level_dat.compound["HelloWorld"]
            )

    def test_dimensions(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            raw_level = JavaRawLevel.load(world_data.temp_path)
            raw_level.open()
            try:
                dimension_ids = raw_level.dimension_ids
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
                    dimension = raw_level.get_dimension(dimension_id)
                    self.assertIsInstance(dimension, JavaRawDimension)
            finally:
                raw_level.close()

    def test_compact(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:

            def get_region_size() -> int:
                return sum(
                    entry.stat().st_size
                    for entry in os.scandir(
                        os.path.join(world_data.temp_path, "region")
                    )
                    if entry.is_file()
                )

            start_size = get_region_size()
            raw_level = JavaRawLevel.load(world_data.temp_path)
            with self.assertRaises(RuntimeError):
                raw_level.compact()
            raw_level.open()
            try:
                raw_level.compact()
            finally:
                raw_level.close()
            end_size = get_region_size()
            self.assertLessEqual(end_size, start_size)

    def test_id_override(self) -> None:
        with WorldTemp(java_vanilla_1_13) as world_data:
            raw_level = JavaRawLevel.load(world_data.temp_path)
            with self.assertRaises(RuntimeError):
                _ = raw_level.block_id_override
            with self.assertRaises(RuntimeError):
                _ = raw_level.biome_id_override

            raw_level.open()
            try:
                self.assertIsInstance(raw_level.block_id_override, IdRegistry)
                self.assertIsInstance(raw_level.biome_id_override, IdRegistry)
            finally:
                raw_level.close()
