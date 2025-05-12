from unittest import TestCase
from typing import Any


def test_component(self: TestCase, component: Any) -> None:
    self.assertIsInstance(component.ComponentID, str)
