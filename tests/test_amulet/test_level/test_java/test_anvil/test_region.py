import unittest
from tempfile import TemporaryDirectory
import os
import shutil
import glob
from concurrent.futures import ThreadPoolExecutor

from amulet_nbt import NamedTag

from amulet.level.java.anvil import AnvilRegion
import tests.data.worlds_src


class JavaSectorManagerTestCase(unittest.TestCase):
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
