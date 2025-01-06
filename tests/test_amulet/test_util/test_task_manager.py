from unittest import TestCase

from amulet.utils.task_manager import TaskCancelled, AbstractCancelManager, CancelManager, VoidCancelManager, AbstractProgressManager, ProgressManager, VoidProgressManager

class CancelManagerTestCase(TestCase):
    def test_task_cancelled(self) -> None:
        with self.assertRaises(TaskCancelled):
            raise TaskCancelled()
        with self.assertRaises(TaskCancelled):
            raise TaskCancelled("Hello World")

    def test_inheritance(self) -> None:
        self.assertIsInstance(CancelManager(), AbstractCancelManager)
        self.assertIsInstance(VoidCancelManager(), AbstractCancelManager)

    def test_cancel_manager(self) -> None:
        cancelled_count = 0

        def callback() -> None:
            nonlocal cancelled_count
            cancelled_count += 1

        manager = CancelManager()

        self.assertFalse(manager.is_cancel_requested())
        manager.cancel()
        self.assertTrue(manager.is_cancel_requested())
        manager.cancel()
        self.assertTrue(manager.is_cancel_requested())

        manager.register_cancel_callback(callback)
        manager.cancel()
        self.assertEqual(0, cancelled_count)

        manager = CancelManager()
        manager.register_cancel_callback(callback)
        manager.cancel()
        self.assertEqual(1, cancelled_count)
        manager.cancel()
        self.assertEqual(1, cancelled_count)

        cancelled_count = 0
        manager = CancelManager()
        manager.register_cancel_callback(callback)
        manager.unregister_cancel_callback(callback)
        manager.cancel()
        self.assertEqual(0, cancelled_count)

    def test_void_cancel_manager(self) -> None:
        cancelled_count = 0

        def callback() -> None:
            nonlocal cancelled_count
            cancelled_count += 1

        manager = VoidCancelManager()

        self.assertFalse(manager.is_cancel_requested())
        manager.cancel()
        self.assertFalse(manager.is_cancel_requested())

        manager.register_cancel_callback(callback)
        manager.cancel()
        self.assertEqual(0, cancelled_count)

        manager = VoidCancelManager()
        manager.register_cancel_callback(callback)
        manager.cancel()
        self.assertEqual(0, cancelled_count)
        manager.cancel()
        self.assertEqual(0, cancelled_count)

        cancelled_count = 0
        manager = VoidCancelManager()
        manager.register_cancel_callback(callback)
        manager.unregister_cancel_callback(callback)
        manager.cancel()
        self.assertEqual(0, cancelled_count)


class ProgressManagerTestCase(TestCase):
    def test_inheritance(self) -> None:
        self.assertIsInstance(ProgressManager(), AbstractProgressManager)
        self.assertIsInstance(VoidProgressManager(), AbstractProgressManager)

    def test_progress_manager(self) -> None:
        progress = 0.0
        text = ""

        def progress_callback(p: float) -> None:
            nonlocal progress
            progress = p

        def text_callback(t: str) -> None:
            nonlocal text
            text = t

        manager = ProgressManager()
        manager.register_progress_callback(progress_callback)
        manager.register_progress_text_callback(text_callback)
        manager.update_progress(0.5)
        self.assertEqual(0.5, progress)
        manager.update_progress_text("Hello World")
        self.assertEqual("Hello World", text)
        manager.unregister_progress_callback(progress_callback)
        manager.unregister_progress_text_callback(text_callback)
        manager.update_progress(0.6)
        self.assertEqual(0.5, progress)
        manager.update_progress_text("Hello World2")
        self.assertEqual("Hello World", text)

        sub_manager = manager.get_child(0.5, 1.0)
        manager.register_progress_callback(progress_callback)
        manager.register_progress_text_callback(text_callback)
        sub_manager.update_progress(0.5)
        self.assertEqual(0.75, progress)
        sub_manager.update_progress_text("Hello World2")
        self.assertEqual("Hello World2", text)

    def test_void_progress_manager(self) -> None:
        progress = 0.0
        text = ""

        def progress_callback(p: float) -> None:
            nonlocal progress
            progress = p

        def text_callback(t: str) -> None:
            nonlocal text
            text = t

        manager = VoidProgressManager()
        manager.register_progress_callback(progress_callback)
        manager.register_progress_text_callback(text_callback)
        manager.update_progress(0.5)
        self.assertEqual(0.0, progress)
        manager.update_progress_text("Hello World")
        self.assertEqual("", text)
        manager.unregister_progress_callback(progress_callback)
        manager.unregister_progress_text_callback(text_callback)
        manager.update_progress(0.6)
        self.assertEqual(0.0, progress)
        manager.update_progress_text("Hello World2")
        self.assertEqual("", text)

        sub_manager = manager.get_child(0.5, 1.0)
        manager.register_progress_callback(progress_callback)
        manager.register_progress_text_callback(text_callback)
        sub_manager.update_progress(0.5)
        self.assertEqual(0.0, progress)
        sub_manager.update_progress_text("Hello World2")
        self.assertEqual("", text)
