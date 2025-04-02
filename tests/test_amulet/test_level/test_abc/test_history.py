from unittest import TestCase

from test_amulet.test_level.test_abc.test_history_ import (
    test_history,
    test_undo_overwrite,
    test_set_value_enum,
    test_set_values_enum,
)


class HistoryTestCase(TestCase):
    def test_history(self) -> None:
        test_history()

    def test_undo_overwrite(self) -> None:
        test_undo_overwrite()

    def test_set_value_enum(self) -> None:
        test_set_value_enum()

    def test_set_values_enum(self) -> None:
        test_set_values_enum()
