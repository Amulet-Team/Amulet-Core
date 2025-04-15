from unittest import TestCase
from contextlib import AbstractContextManager
from abc import ABC, abstractmethod
from datetime import datetime

from PIL import Image

from amulet.level.abc.level import (
    LevelMetadata,
    Level,
    ReloadableLevel,
)
from amulet.version import VersionNumber
from amulet.utils.lock import OrderedLock


class LevelTestCases:
    class LevelMetadataTestCase(ABC, TestCase):
        @abstractmethod
        def level(self) -> AbstractContextManager[LevelMetadata]:
            raise NotImplementedError

        def test_lock(self) -> None:
            with self.level() as level:
                self.assertIsInstance(level.lock, OrderedLock)

        def test_is_open(self) -> None:
            with self.level() as level:
                self.assertIsInstance(level.is_open(), bool)
                self.assertFalse(level.is_open())

        @staticmethod
        @abstractmethod
        def get_expected_platform() -> str:
            raise NotImplementedError

        def test_platform(self) -> None:
            with self.level() as level:
                self.assertIsInstance(level.platform, str)
                self.assertEqual(self.get_expected_platform(), level.platform)

        @staticmethod
        @abstractmethod
        def get_expected_max_version() -> VersionNumber:
            raise NotImplementedError

        def test_max_game_version(self) -> None:
            with self.level() as level:
                self.assertIsInstance(level.max_game_version, VersionNumber)
                self.assertEqual(
                    self.get_expected_max_version(), level.max_game_version
                )

        def test_is_supported(self) -> None:
            with self.level() as level:
                self.assertIsInstance(level.is_supported(), bool)
                self.assertTrue(level.is_supported())

        def test_thumbnail(self) -> None:
            with self.level() as level:
                thumbnail = level.thumbnail
                self.assertIsInstance(thumbnail, Image.Image)
                thumbnail.close()

        @staticmethod
        @abstractmethod
        def get_expected_level_name() -> str:
            raise NotImplementedError

        def test_level_name(self) -> None:
            with self.level() as level:
                level_name = level.level_name
                self.assertIsInstance(level_name, str)
                self.assertEqual(self.get_expected_level_name(), level_name)

        @staticmethod
        @abstractmethod
        def get_expected_modified_time() -> float:
            raise NotImplementedError

        def test_modified_time(self) -> None:
            with self.level() as level:
                modified_time = level.modified_time
                self.assertIsInstance(modified_time, datetime)
                self.assertEqual(
                    self.get_expected_modified_time(), modified_time.timestamp()
                )

        @staticmethod
        @abstractmethod
        def get_expected_sub_chunk_size() -> int:
            raise NotImplementedError

        def test_sub_chunk_size(self) -> None:
            with self.level() as level:
                sub_chunk_size = level.sub_chunk_size
                self.assertIsInstance(sub_chunk_size, int)
                self.assertEqual(self.get_expected_sub_chunk_size(), sub_chunk_size)

    class LevelTestCase(LevelMetadataTestCase):
        @abstractmethod
        def level(self) -> AbstractContextManager[Level]:
            raise NotImplementedError

        def test_open_close(self) -> None:
            with self.level() as level:
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

                opened_token = level.opened.connect(on_open)
                closed_token = level.closed.connect(on_close)
                if isinstance(level, ReloadableLevel):
                    reloaded_token = level.reloaded.connect(on_reload)

                self.assertFalse(level.is_open())

                level.open()
                self.assertTrue(level.is_open())
                self.assertEqual(1, opened_count)
                self.assertEqual(0, closed_count)
                self.assertEqual(0, reloaded_count)

                opened_count = 0

                if isinstance(level, ReloadableLevel):
                    level.reload()
                    self.assertTrue(level.is_open())
                    self.assertEqual(0, opened_count)
                    self.assertEqual(0, closed_count)
                    self.assertEqual(1, reloaded_count)

                    with self.assertRaises(RuntimeError):
                        level.reload_metadata()

                    reloaded_count = 0
                level.close()
                self.assertFalse(level.is_open())
                self.assertEqual(0, opened_count)
                self.assertEqual(1, closed_count)
                self.assertEqual(0, reloaded_count)

        @abstractmethod
        def test_save(self) -> None:
            raise NotImplementedError

        @abstractmethod
        def test_history(self) -> None:
            raise NotImplementedError

        @abstractmethod
        def test_dimension(self) -> None:
            raise NotImplementedError

    class CompactibleLevelTestCase(TestCase):
        @abstractmethod
        def test_compact(self) -> None:
            raise NotImplementedError

    class DiskLevelTestCase(ABC, TestCase):
        @abstractmethod
        def test_path(self) -> None:
            raise NotImplementedError

    class ReloadableLevelTestCase(ABC, TestCase):
        @abstractmethod
        def test_reload_metadata(self) -> None:
            raise NotImplementedError

        @abstractmethod
        def test_reload(self) -> None:
            raise NotImplementedError
