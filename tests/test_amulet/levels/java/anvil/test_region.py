import unittest
from tempfile import TemporaryDirectory
import os
import shutil
import glob

from amulet.level.java.anvil import AnvilRegion
import tests.data.worlds_src


class JavaSectorManagerTestCase(unittest.TestCase):
    def test_compact(self) -> None:
        with TemporaryDirectory() as tempdir:
            # Create a temporary directory and copy all Java worlds to it.
            shutil.copytree(os.path.join(tests.data.worlds_src.__path__[0], "java"), os.path.join(tempdir, "java"))

            for region_file_path in glob.glob(os.path.join(glob.escape(tempdir), "**", "r.*.*.mca"), recursive=True):
                rel_path = os.path.relpath(region_file_path, tempdir)
                with self.subTest(rel_path):
                    region = AnvilRegion(region_file_path, mcc=True)
                    original_file_size = os.stat(region.path).st_size
                    original_chunk_data = {(cx, cz): region.get_data(cx, cz) for cx, cz in region.all_coords()}

                    for (cx, cz), nbt_file in original_chunk_data.items():
                        path = os.path.join(r"C:\Users\james_000\AppData\Local\Temp\chunk_data", f"{rel_path}.{cx}.{cz}.bin")
                        os.makedirs(os.path.dirname(path), exist_ok=True)
                        with open(path, "wb") as f:
                            f.write(nbt_file.to_nbt(compressed=False))

                    region.compact()
                    self.assertEqual(
                        original_chunk_data,
                        {(cx, cz): region.get_data(cx, cz) for cx, cz in region.all_coords()}
                    )
                    del region
                    region = AnvilRegion(region_file_path, mcc=True)
                    self.assertEqual(
                        original_chunk_data,
                        {(cx, cz): region.get_data(cx, cz) for cx, cz in region.all_coords()}
                    )
                    if original_file_size >= 0x2000:
                        self.assertLessEqual(os.stat(region.path).st_size, original_file_size)


if __name__ == "__main__":
    unittest.main()
