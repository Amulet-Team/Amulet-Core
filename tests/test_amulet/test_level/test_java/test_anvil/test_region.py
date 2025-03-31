import unittest
from tempfile import TemporaryDirectory
import os
import shutil
import glob
from concurrent.futures import ThreadPoolExecutor
from weakref import ref
from threading import Thread, Condition, Lock
import time

from amulet_nbt import NamedTag, CompoundTag, StringTag, ListTag

from amulet.chunk import ChunkDoesNotExist
from amulet.level.java.anvil import AnvilRegion, RegionDoesNotExist
import tests.data.worlds_src
import tests.data.region
from test_amulet.test_level.test_java.test_anvil.test_region_ import (
    throw_region_does_not_exist,
)


class AnvilRegionTestCase(unittest.TestCase):
    def test_region_does_not_exist(self) -> None:
        with self.assertRaises(RuntimeError):
            raise RegionDoesNotExist
        with self.assertRaises(RegionDoesNotExist):
            raise RegionDoesNotExist
        with self.assertRaises(RuntimeError):
            throw_region_does_not_exist()
        with self.assertRaises(RegionDoesNotExist):
            throw_region_does_not_exist()

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

    def test_lock(self) -> None:
        sleep_time = 1
        with TemporaryDirectory() as tmpdir:
            condition = Condition()
            region = AnvilRegion(tmpdir, 0, 0)

            exec_order: list[int] = []
            end_times: list[float] = []
            thread_count = 0

            def increment_thread_count() -> None:
                nonlocal thread_count
                thread_count += 1
                with condition:
                    condition.notify_all()

            def f1() -> None:
                increment_thread_count()
                with condition:
                    condition.wait_for(lambda: thread_count == 3)
                with region.lock():
                    increment_thread_count()
                    exec_order.append(1)
                    region.set_value(
                        0, 0, NamedTag(CompoundTag(val=StringTag("0")), "")
                    )
                    region.set_value(
                        0, 1, NamedTag(CompoundTag(val=StringTag("1")), "")
                    )
                    region.set_value(
                        0, 2, NamedTag(CompoundTag(val=StringTag("2")), "")
                    )
                    self.assertEqual({(0, 0), (0, 1), (0, 2)}, set(region.get_coords()))
                    self.assertEqual(
                        NamedTag(CompoundTag(val=StringTag("0")), ""),
                        region.get_value(0, 0),
                    )
                    self.assertEqual(
                        NamedTag(CompoundTag(val=StringTag("1")), ""),
                        region.get_value(0, 1),
                    )
                    self.assertEqual(
                        NamedTag(CompoundTag(val=StringTag("2")), ""),
                        region.get_value(0, 2),
                    )
                    time.sleep(sleep_time)
                    exec_order.append(2)
                end_times.append(time.time())

            def f2() -> None:
                increment_thread_count()
                with condition:
                    condition.wait_for(lambda: thread_count == 4)
                with region.lock():
                    increment_thread_count()
                    exec_order.append(3)
                    region.set_value(
                        0, 2, NamedTag(CompoundTag(val=StringTag("3")), "")
                    )
                    region.set_value(
                        0, 3, NamedTag(CompoundTag(val=StringTag("4")), "")
                    )
                    self.assertEqual(
                        {(0, 0), (0, 1), (0, 2), (0, 3)}, set(region.get_coords())
                    )
                    self.assertEqual(
                        NamedTag(CompoundTag(val=StringTag("0")), ""),
                        region.get_value(0, 0),
                    )
                    self.assertEqual(
                        NamedTag(CompoundTag(val=StringTag("1")), ""),
                        region.get_value(0, 1),
                    )
                    self.assertEqual(
                        NamedTag(CompoundTag(val=StringTag("3")), ""),
                        region.get_value(0, 2),
                    )
                    self.assertEqual(
                        NamedTag(CompoundTag(val=StringTag("4")), ""),
                        region.get_value(0, 3),
                    )
                    time.sleep(sleep_time)
                    exec_order.append(4)
                end_times.append(time.time())

            thread_1 = Thread(target=f1)
            thread_2 = Thread(target=f2)

            thread_1.start()
            thread_2.start()

            with condition:
                condition.wait_for(lambda: thread_count == 2)
            t = time.time()
            increment_thread_count()

            thread_1.join()
            thread_2.join()

            self.assertEqual([1, 2, 3, 4], exec_order)

            dt = max(end_times) - t
            self.assertTrue(
                sleep_time * 2 - 0.01 <= dt <= sleep_time * 2 + 0.5,
                f"Expected {sleep_time * 2}s. Got {dt}s",
            )
            region_ref = ref(region)
            lock = region.lock
            del region
            self.assertIsNotNone(region_ref())
            del lock
            self.assertIsNone(region_ref())

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
                    lz4_chunk.compound["DataVersion"] = zlib_chunk.compound[
                        "DataVersion"
                    ]
                    lz4_chunk.compound["LastUpdate"] = zlib_chunk.compound["LastUpdate"]
                    lz4_chunk.compound["InhabitedTime"] = zlib_chunk.compound[
                        "InhabitedTime"
                    ]

                    def remove_sections(sections: ListTag) -> None:
                        for i, section in enumerate(reversed(sections)):
                            if "block_states" not in section:
                                sections.pop(len(sections) - 1 - i)
                            else:
                                if (
                                    isinstance(section, CompoundTag)
                                    and "SkyLight" in section
                                ):
                                    section.pop("SkyLight")
                                if (
                                    isinstance(section, CompoundTag)
                                    and "BlockLight" in section
                                ):
                                    section.pop("BlockLight")

                    remove_sections(
                        zlib_chunk.compound.get_list("sections", raise_errors=True)
                    )
                    remove_sections(
                        lz4_chunk.compound.get_list("sections", raise_errors=True)
                    )

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

            def compact(path: str) -> None:
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
                self.assertEqual(original_chunk_data, get_data())

                # Close, reopen and verify that the data is the same
                region.destroy()
                region = AnvilRegion(path, mcc=True)
                self.assertEqual(original_chunk_data, get_data())

                if original_chunk_data:
                    self.assertLessEqual(os.stat(path).st_size, original_file_size)
                else:
                    self.assertFalse(os.path.isfile(path))
                region.destroy()

            with ThreadPoolExecutor() as executor:
                for region_file_path in glob.glob(
                    os.path.join(glob.escape(tempdir), "**", "r.*.*.mca"),
                    recursive=True,
                ):
                    executor.submit(compact, region_file_path)

    def test_exceptions(self) -> None:
        with TemporaryDirectory() as tmpdir:
            region = AnvilRegion(tmpdir, 0, 0)

            with self.assertRaises(ChunkDoesNotExist):
                region.get_value(0, 0)

            with self.assertRaises(ValueError):
                region.has_value(-1, -1)
            with self.assertRaises(ValueError):
                region.has_value(32, 0)
            with self.assertRaises(ChunkDoesNotExist):
                region.get_value(0, 0)

            value = NamedTag(CompoundTag(test=StringTag("test")), "test")
            with self.assertRaises(ValueError):
                region.set_value(-1, -1, value)
            with self.assertRaises(ValueError):
                region.set_value(32, 0, value)
            with self.assertRaises(ValueError):
                region.set_value(0, 32, value)

            with self.assertRaises(ValueError):
                region.delete_value(-1, -1)
            with self.assertRaises(ValueError):
                region.delete_value(32, 0)
            with self.assertRaises(ValueError):
                region.delete_value(0, 32)

    def test_del(self) -> None:
        with TemporaryDirectory() as tmpdir:
            region = AnvilRegion(tmpdir, 0, 0)
            value = NamedTag(CompoundTag(test=StringTag("test")), "test")
            region.set_value(0, 0, value)
            del region


if __name__ == "__main__":
    unittest.main()
