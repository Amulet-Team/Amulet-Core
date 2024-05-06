import unittest
from typing import Type
import os

from amulet import load_format
from amulet.api.data_types import VersionNumberAny
from amulet.api.wrapper import FormatWrapper
from amulet.selection import SelectionGroup, SelectionBox
from amulet.errors import LevelWriteError

from amulet.level.formats.anvil_world import AnvilFormat
from amulet.level.formats.leveldb_world import LevelDBFormat
from amulet.level.formats.construction import ConstructionFormatWrapper
from amulet.level.formats.mcstructure import MCStructureFormatWrapper
from amulet.level.formats.schematic import SchematicFormatWrapper
from amulet.level.formats.sponge_schem import SpongeSchemFormatWrapper

from data.util import clean_temp_world, clean_path


class CreateWorldTestCase(unittest.TestCase):
    def _test_create(
        self,
        cls: Type[FormatWrapper],
        level_name: str,
        platform: str,
        version: VersionNumberAny,
    ):
        path = clean_temp_world(level_name)

        # create, initialise and save the level
        if cls.requires_selection():
            level = cls.create(
                path=path,
                platform=platform,
                version=version,
                bounds=SelectionGroup([SelectionBox((0, 0, 0), (1, 1, 1))]),
                overwrite=True,
            )
        else:
            level = cls.create(
                path=path, platform=platform, version=version, overwrite=True
            )

        self.assertFalse(level.is_open, "The level was opened by create.")
        self.assertFalse(level.has_lock, "The level was locked by create.")

        level.open()

        self.assertTrue(level.is_open, "The level was not opened")
        self.assertTrue(level.has_lock, "The lock was not acquired")

        platform_ = level.platform
        version_ = level.version
        dimension_selections = {dim: level.bounds(dim) for dim in level.dimensions}

        level.save()
        level.close()

        self.assertFalse(level.is_open, "The level was not closed by close()")
        self.assertFalse(level.has_lock, "The lock was not lost by close()")

        self.assertTrue(os.path.exists(level.path))

        # reopen the level
        level2 = load_format(path)
        # check that the class is the same
        self.assertIs(level.__class__, level2.__class__)
        level2.open()

        self.assertTrue(level2.is_open, "The level was not opened by open()")
        self.assertTrue(level2.has_lock, "The lock was not acquired by open()")

        # check that the platform and version are the same
        self.assertEqual(level2.platform, platform_)
        self.assertEqual(level2.version, version_)
        self.assertEqual(set(level2.dimensions), set(dimension_selections))
        for dim, selection in dimension_selections.items():
            self.assertEqual(level2.bounds(dim), selection)
        level2.close()

        self.assertFalse(level2.is_open, "The level was not closed by close()")
        self.assertFalse(level2.has_lock, "The lock was not lost by close()")

        self.assertTrue(os.path.exists(level.path))

        with self.assertRaises(LevelWriteError):
            if cls.requires_selection():
                cls.create(
                    path=path,
                    platform=platform,
                    version=version,
                    bounds=SelectionGroup([SelectionBox((0, 0, 0), (1, 1, 1))]),
                )
            else:
                cls.create(path=path, platform=platform, version=version)

        clean_path(path)

    def test_anvil(self):
        self._test_create(
            AnvilFormat,
            "anvil_world",
            "java",
            (1, 16, 0),
        )

    def test_bedrock(self):
        self._test_create(
            LevelDBFormat,
            "leveldb_world",
            "bedrock",
            (1, 16, 0),
        )

    def test_construction(self):
        self._test_create(
            ConstructionFormatWrapper,
            "java.construction",
            "java",
            (1, 16, 0),
        )
        self._test_create(
            ConstructionFormatWrapper,
            "bedrock.construction",
            "bedrock",
            (1, 16, 0),
        )

    def test_mcstructure(self):
        self._test_create(
            MCStructureFormatWrapper,
            "bedrock.mcstructure",
            "bedrock",
            (1, 16, 0),
        )

    def test_schematic(self):
        self._test_create(
            SchematicFormatWrapper,
            "java.schematic",
            "java",
            (1, 12, 2),
        )
        self._test_create(
            SchematicFormatWrapper,
            "bedrock.schematic",
            "bedrock",
            (1, 12, 0),
        )

    def test_sponge_schematic(self):
        self._test_create(
            SpongeSchemFormatWrapper,
            "java.schem",
            "java",
            (1, 19, 0),
        )


if __name__ == "__main__":
    unittest.main()
