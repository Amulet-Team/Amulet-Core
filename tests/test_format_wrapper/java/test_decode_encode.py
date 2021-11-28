import unittest
from tests.data import worlds_src

from tests.test_format_wrapper.base_test_encode_decode import WrapBaseTestDecodeEncode


def _create_test(world_name):
    cls_name = f"Test{world_name}"

    class TestCase(WrapBaseTestDecodeEncode.BaseTestDecodeEncode):
        WorldName = world_name

    globals()[cls_name] = TestCase


for _path in worlds_src.JavaVanillaLevels:
    _create_test(_path)


if __name__ == "__main__":
    unittest.main()
