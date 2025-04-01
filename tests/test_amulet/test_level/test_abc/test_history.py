from unittest import TestCase

from test_amulet.test_level.test_abc.test_history_ import (
    test_history,
    test_undo_overwrite,
)


class HistoryTestCase(TestCase):
    def test_history(self) -> None:
        test_history()

    def test_undo_overwrite(self) -> None:
        test_undo_overwrite()
