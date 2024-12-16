import unittest
from tempfile import TemporaryDirectory
import os
import shutil
import glob
from concurrent.futures import ThreadPoolExecutor

from amulet_nbt import NamedTag, CompoundTag, StringTag, ListTag, ByteArrayTag

from amulet.level.java.anvil import AnvilRegion
import tests.data.worlds_src
import tests.data.region


class JavaSectorManagerTestCase(unittest.TestCase):
    def test_methods(self) -> None:
        with TemporaryDirectory() as tmpdir:
            region = AnvilRegion(tmpdir, 0, 0)
            self.assertFalse(os.path.exists(region.path))
            self.assertEqual([], region.get_coords())
            self.assertFalse(region.has_value(0, 0))
            self.assertFalse(os.path.exists(region.path))
            value = NamedTag(CompoundTag(test=StringTag("test")), "test")
            region.set_value(0, 0, value)
            self.assertEqual([(0, 0)], region.get_coords())
            self.assertTrue(region.has_value(0, 0))
            self.assertTrue(os.path.exists(region.path))
            self.assertEqual(value, region.get_value(0, 0))
            region.close()
            self.assertEqual(value, region.get_value(0, 0))
            region.destroy()
            self.assertTrue(os.path.exists(region.path))
            region = AnvilRegion(tmpdir, 0, 0)
            self.assertEqual([(0, 0)], region.get_coords())
            self.assertTrue(region.has_value(0, 0))
            self.assertEqual(value, region.get_value(0, 0))
            region.delete_value(0, 0)
            self.assertEqual([], region.get_coords())
            self.assertFalse(region.has_value(0, 0))
            region.compact()
            self.assertEqual([], region.get_coords())
            self.assertFalse(region.has_value(0, 0))
            self.assertFalse(os.path.exists(region.path))
            region.destroy()

    def test_properties(self) -> None:
        with TemporaryDirectory() as tmpdir:
            region = AnvilRegion(tmpdir, 10, 20)
            self.assertEqual(10, region.rx)
            self.assertEqual(20, region.rz)
            self.assertEqual(os.path.join(tmpdir, "r.10.20.mca"), region.path)

    def test_compression(self) -> None:
        with TemporaryDirectory() as tempdir:
            shutil.rmtree(tempdir)
            shutil.copytree(tests.data.region.__path__[0], tempdir)
            zlib_region = AnvilRegion(os.path.join(tempdir, "zlib"), 5, 5)
            lz4_region = AnvilRegion(os.path.join(tempdir, "lz4"), 5, 5)
            try:
                self.assertEqual(zlib_region.get_coords(), lz4_region.get_coords())
                for x, z in zlib_region.get_coords():
                    zlib_chunk = zlib_region.get_value(x, z)
                    lz4_chunk = lz4_region.get_value(x, z)
                    lz4_chunk.compound["DataVersion"] = zlib_chunk.compound["DataVersion"]
                    lz4_chunk.compound["LastUpdate"] = zlib_chunk.compound["LastUpdate"]
                    lz4_chunk.compound["InhabitedTime"] = zlib_chunk.compound["InhabitedTime"]
                    def remove_sections(sections: ListTag) -> None:
                        for i, section in enumerate(reversed(sections)):
                            if "block_states" not in section:
                                sections.pop(len(sections) - 1 - i)
                            else:
                                if isinstance(section, CompoundTag) and "SkyLight" in section:
                                    section.pop("SkyLight")
                                if isinstance(section, CompoundTag) and "BlockLight" in section:
                                    section.pop("BlockLight")
                        
                    remove_sections(zlib_chunk.compound.get_list("sections"))
                    remove_sections(lz4_chunk.compound.get_list("sections"))

                    self.assertEqual(zlib_chunk, lz4_chunk)
            finally:
                zlib_region.destroy()
                lz4_region.destroy()

    def test_compact(self) -> None:
        with TemporaryDirectory() as tempdir:
            # Create a temporary directory and copy all Java worlds to it.
            shutil.copytree(
                os.path.join(tests.data.worlds_src.__path__[0], "java"),
                os.path.join(tempdir, "java"),
            )

            def compact(path) -> None:
                region = AnvilRegion(path, mcc=True)
                original_file_size = os.stat(region.path).st_size

                def get_data() -> dict[tuple[int, int], NamedTag]:
                    return {
                        (cx, cz): region.get_value(cx, cz)
                        for cx, cz in region.get_coords()
                    }

                original_chunk_data = get_data()

                # Compact the region
                region.compact()

                # Verify that the data is the same
                self.assertEqual(
                    original_chunk_data,
                    get_data()
                )

                # Close, reopen and verify that the data is the same
                region.destroy()
                region = AnvilRegion(path, mcc=True)
                self.assertEqual(
                    original_chunk_data,
                    get_data()
                )

                if original_chunk_data:
                    self.assertLessEqual(
                        os.stat(path).st_size, original_file_size
                    )
                else:
                    self.assertFalse(os.path.isfile(path))
                region.destroy()

            with ThreadPoolExecutor() as executor:
                for region_file_path in glob.glob(
                    os.path.join(glob.escape(tempdir), "**", "r.*.*.mca"), recursive=True
                ):
                    executor.submit(compact, region_file_path)


if __name__ == "__main__":
    unittest.main()
