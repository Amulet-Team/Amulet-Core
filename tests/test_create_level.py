import unittest
from typing import Type

from amulet import load_format
from amulet.api.errors import ObjectReadWriteError
from amulet.api.data_types import VersionNumberAny
from amulet.api.wrapper import FormatWrapper
from amulet.api.selection import SelectionGroup, SelectionBox

from amulet.level.formats.anvil_world import AnvilFormat
from amulet.level.formats.leveldb_world import LevelDBFormat
from amulet.level.formats.construction import ConstructionFormatWrapper
from amulet.level.formats.mcstructure import MCStructureFormatWrapper
from amulet.level.formats.schematic import SchematicFormatWrapper

from .test_utils import clean_temp_world, clean_path


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
        level = cls(path)
        if level.requires_selection:
            level.create_and_open(
                platform, version, SelectionGroup([SelectionBox((0, 0, 0), (1, 1, 1))])
            )
        else:
            level.create_and_open(platform, version)
        platform_ = level.platform
        version_ = level.version
        selection_ = level.selection
        level.save()
        level.close()

        # reopen the level
        level2 = load_format(path)
        # check that the class is the same
        self.assertIs(level.__class__, level2.__class__)
        # check that the platform and version are the same
        self.assertEqual(level2.platform, platform_)
        self.assertEqual(level2.version, version_)
        self.assertEqual(level2.selection, selection_)
        level2.open()
        level2.close()

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
            (1, 12, 0),
        )
        self._test_create(
            SchematicFormatWrapper,
            "bedrock.schematic",
            "bedrock",
            (1, 12, 0),
        )


if __name__ == "__main__":
    unittest.main()
