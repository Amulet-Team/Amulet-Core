from unittest import TestCase

from typing import Any

from tests.test_amulet.test_util.test_signal_ import SignalTest

class SignalTestCase(TestCase):
    def test_signal(self) -> None:
        cls = SignalTest()

        var: Any = None
        count_0 = 0
        count_1 = 0
        count_2 = 0
        count_3 = 0

        def on_0():
            nonlocal count_0, var
            count_0 += 1
            var = ()

        def on_1(a: int):
            nonlocal count_1, var
            count_1 += 1
            var = (a,)

        def on_2(a: int, b: float):
            nonlocal count_2, var
            count_2 += 1
            var = (a, b)

        def on_3(a: int, b: float, c: str):
            nonlocal count_3, var
            count_3 += 1
            var = (a, b, c)

        token_0 = cls.signal_0.connect(on_0)
        token_1 = cls.signal_1.connect(on_1)
        token_2 = cls.signal_2.connect(on_2)
        token_3 = cls.signal_3.connect(on_3)

        cls.signal_0.emit()
        self.assertEqual(1, count_0)
        self.assertEqual((), var)

        cls.signal_1.emit(1)
        self.assertEqual(1, count_1)
        self.assertEqual((1,), var)

        cls.signal_2.emit(2, 2.5)
        self.assertEqual(1, count_2)
        self.assertEqual((2, 2.5), var)

        cls.signal_3.emit(3, 3.5, "3")
        self.assertEqual(1, count_3)
        self.assertEqual((3, 3.5, "3"), var)

        cls.emit()
        self.assertEqual(2, count_0)
        self.assertEqual(2, count_1)
        self.assertEqual(2, count_2)
        self.assertEqual(2, count_3)
        self.assertEqual((1, 1.5, "Hello World"), var)

        cls.signal_0.disconnect(token_0)
        cls.signal_1.disconnect(token_1)
        cls.signal_2.disconnect(token_2)
        cls.signal_3.disconnect(token_3)

        cls.signal_0.emit()
        cls.signal_1.emit(4, )
        cls.signal_2.emit(5, 5.5)
        cls.signal_3.emit(6, 6.5, "6")
        self.assertEqual((1, 1.5, "Hello World"), var)

        self.assertEqual(2, count_0)
        self.assertEqual(2, count_1)
        self.assertEqual(2, count_2)
        self.assertEqual(2, count_3)

    def test_exception(self) -> None:
        cls = SignalTest()

        call_count = 0

        def callback():
            nonlocal call_count
            call_count += 1
            raise Exception()
        cls.signal_0.connect(callback)
        cls.signal_0.emit()
        self.assertEqual(1, call_count)
