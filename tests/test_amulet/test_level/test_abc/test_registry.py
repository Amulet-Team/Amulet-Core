from unittest import TestCase

from amulet.level.abc import IdRegistry


class IdRegistryTestCase(TestCase):
    def test_methods(self) -> None:
        registry = IdRegistry()

        # len
        self.assertEqual(0, len(registry))
        registry.register_id(0, ("minecraft", "stone"))
        self.assertEqual(1, len(registry))

        registry.register_id(1, ("minecraft", "water"))
        registry.register_id(5, ("minecraft", "grass"))

        # numerical_id_to_namespace_id
        self.assertEqual(
            ("minecraft", "stone"), registry.numerical_id_to_namespace_id(0)
        )
        self.assertEqual(
            ("minecraft", "water"), registry.numerical_id_to_namespace_id(1)
        )
        self.assertEqual(
            ("minecraft", "grass"), registry.numerical_id_to_namespace_id(5)
        )
        with self.assertRaises(KeyError):
            registry.numerical_id_to_namespace_id(2)

        # namespace_id_to_numerical_id
        self.assertEqual(
            0, registry.namespace_id_to_numerical_id(("minecraft", "stone"))
        )
        self.assertEqual(
            1, registry.namespace_id_to_numerical_id(("minecraft", "water"))
        )
        self.assertEqual(
            5, registry.namespace_id_to_numerical_id(("minecraft", "grass"))
        )
        self.assertEqual(0, registry.namespace_id_to_numerical_id("minecraft", "stone"))
        self.assertEqual(1, registry.namespace_id_to_numerical_id("minecraft", "water"))
        self.assertEqual(5, registry.namespace_id_to_numerical_id("minecraft", "grass"))
        with self.assertRaises(KeyError):
            registry.namespace_id_to_numerical_id(("minecraft", "bedrock"))
        with self.assertRaises(KeyError):
            registry.namespace_id_to_numerical_id("minecraft", "bedrock")

        # __getitem__
        self.assertEqual(("minecraft", "stone"), registry[0])
        self.assertEqual(("minecraft", "water"), registry[1])
        self.assertEqual(("minecraft", "grass"), registry[5])
        self.assertEqual(0, registry[("minecraft", "stone")])
        self.assertEqual(1, registry[("minecraft", "water")])
        self.assertEqual(5, registry[("minecraft", "grass")])
        with self.assertRaises(KeyError):
            registry[2]
        with self.assertRaises(KeyError):
            registry[("minecraft", "bedrock")]

        # Keys
        self.assertEqual({0, 1, 5}, set(registry))
        self.assertEqual({0, 1, 5}, set(registry.keys()))
        # Values
        self.assertEqual(
            {("minecraft", "stone"), ("minecraft", "water"), ("minecraft", "grass")},
            set(registry.values()),
        )
        # Items
        self.assertEqual(
            {
                0: ("minecraft", "stone"),
                1: ("minecraft", "water"),
                5: ("minecraft", "grass"),
            },
            dict(registry.items()),
        )
        self.assertEqual(
            {
                0: ("minecraft", "stone"),
                1: ("minecraft", "water"),
                5: ("minecraft", "grass"),
            },
            dict(registry),
        )
        # Get
        self.assertEqual(("minecraft", "stone"), registry.get(0))
        self.assertIs(None, registry.get(2))
        self.assertEqual(
            ("minecraft", "stone"), registry.get(0, ("minecraft", "bedrock"))
        )
        self.assertEqual(
            ("minecraft", "bedrock"), registry.get(2, ("minecraft", "bedrock"))
        )

    def test_iter_lifespan(self) -> None:
        registry = IdRegistry()
        registry.register_id(0, ("minecraft", "stone"))
        registry.register_id(1, ("minecraft", "water"))
        registry.register_id(5, ("minecraft", "grass"))
        it = iter(registry)
        del registry
        self.assertEqual({0, 1, 5}, set(it))

    def test_keys_lifespan(self) -> None:
        registry = IdRegistry()
        registry.register_id(0, ("minecraft", "stone"))
        registry.register_id(1, ("minecraft", "water"))
        registry.register_id(5, ("minecraft", "grass"))
        keys = registry.keys()
        del registry
        self.assertEqual({0, 1, 5}, set(keys))

    def test_values_lifespan(self) -> None:
        registry = IdRegistry()
        registry.register_id(0, ("minecraft", "stone"))
        registry.register_id(1, ("minecraft", "water"))
        registry.register_id(5, ("minecraft", "grass"))
        values = registry.values()
        del registry
        self.assertEqual(
            {("minecraft", "stone"), ("minecraft", "water"), ("minecraft", "grass")},
            set(values),
        )

    def test_items_lifespan(self) -> None:
        registry = IdRegistry()
        registry.register_id(0, ("minecraft", "stone"))
        registry.register_id(1, ("minecraft", "water"))
        registry.register_id(5, ("minecraft", "grass"))
        items = registry.items()
        del registry
        self.assertEqual(
            {
                0: ("minecraft", "stone"),
                1: ("minecraft", "water"),
                5: ("minecraft", "grass"),
            },
            dict(items),
        )
