import unittest


class SelectionEllipsoidTestCase(unittest.TestCase):
    def test_cpp(self) -> None:
        from test_amulet_core.test_selection.test_selection_ellipsoid_ import get_tests

        for test in get_tests():
            with self.subTest(test=test.__name__):
                test()


if __name__ == "__main__":
    unittest.main()
