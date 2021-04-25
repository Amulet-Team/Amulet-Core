import unittest
from amulet.api.block import Block
from amulet.api.registry import BlockManager
from amulet.api.errors import BlockException

import amulet_nbt as nbt


class BlockTestCase(unittest.TestCase):
    def test_get_from_blockstate(self):  # This is mostly just sanity checks
        air = Block.from_string_blockstate("minecraft:air")

        self.assertIsInstance(air, Block)
        self.assertEqual("minecraft", air.namespace)
        self.assertEqual("air", air.base_name)
        self.assertEqual({}, air.properties)
        self.assertEqual((), air.extra_blocks)
        self.assertEqual("minecraft:air", air.blockstate)
        self.assertEqual("minecraft:air", air.snbt_blockstate)
        self.assertEqual("minecraft:air", air.full_blockstate)

        stone = Block.from_string_blockstate("minecraft:stone")

        self.assertIsInstance(stone, Block)
        self.assertEqual("minecraft", stone.namespace)
        self.assertEqual("stone", stone.base_name)
        self.assertEqual({}, stone.properties)
        self.assertEqual((), stone.extra_blocks)
        self.assertEqual("minecraft:stone", stone.blockstate)
        self.assertEqual("minecraft:stone", stone.snbt_blockstate)
        self.assertEqual("minecraft:stone", stone.full_blockstate)

        self.assertNotEqual(air, stone)

        oak_leaves = Block.from_snbt_blockstate(
            'minecraft:oak_leaves[distance="1",persistent="true"]'
        )

        self.assertIsInstance(oak_leaves, Block)
        self.assertEqual("minecraft", oak_leaves.namespace)
        self.assertEqual("oak_leaves", oak_leaves.base_name)
        self.assertEqual(
            {"distance": nbt.TAG_String("1"), "persistent": nbt.TAG_String("true")},
            oak_leaves.properties,
        )
        self.assertEqual((), oak_leaves.extra_blocks)
        self.assertEqual(
            "minecraft:oak_leaves[distance=1,persistent=true]",
            oak_leaves.blockstate,
        )
        self.assertEqual(
            'minecraft:oak_leaves[distance="1",persistent="true"]',
            oak_leaves.snbt_blockstate,
        )
        self.assertEqual(
            'minecraft:oak_leaves[distance="1",persistent="true"]',
            oak_leaves.full_blockstate,
        )

        oak_leaves_2 = Block(
            namespace="minecraft",
            base_name="oak_leaves",
            properties={
                "persistent": nbt.TAG_String("true"),
                "distance": nbt.TAG_String("1"),
            },
        )
        self.assertEqual("minecraft", oak_leaves_2.namespace)
        self.assertEqual("oak_leaves", oak_leaves_2.base_name)
        self.assertEqual(
            {"distance": nbt.TAG_String("1"), "persistent": nbt.TAG_String("true")},
            oak_leaves_2.properties,
        )
        self.assertEqual((), oak_leaves_2.extra_blocks)
        self.assertEqual(
            "minecraft:oak_leaves[distance=1,persistent=true]",
            oak_leaves_2.blockstate,
        )
        self.assertEqual(
            'minecraft:oak_leaves[distance="1",persistent="true"]',
            oak_leaves_2.snbt_blockstate,
        )
        self.assertEqual(
            'minecraft:oak_leaves[distance="1",persistent="true"]',
            oak_leaves_2.full_blockstate,
        )
        self.assertEqual(oak_leaves, oak_leaves_2)

        oak_leaves_3 = Block.from_snbt_blockstate(
            'minecraft:oak_leaves[persistent="true",distance="1"]'
        )
        self.assertEqual("minecraft", oak_leaves_3.namespace)
        self.assertEqual("oak_leaves", oak_leaves_3.base_name)
        self.assertEqual(
            {"distance": nbt.TAG_String("1"), "persistent": nbt.TAG_String("true")},
            oak_leaves_3.properties,
        )
        self.assertEqual((), oak_leaves_3.extra_blocks)
        self.assertEqual(
            "minecraft:oak_leaves[distance=1,persistent=true]",
            oak_leaves_3.blockstate,
        )
        self.assertEqual(
            'minecraft:oak_leaves[distance="1",persistent="true"]',
            oak_leaves_3.snbt_blockstate,
        )
        self.assertEqual(
            'minecraft:oak_leaves[distance="1",persistent="true"]',
            oak_leaves_3.full_blockstate,
        )
        self.assertEqual(oak_leaves, oak_leaves_3)

    def test_extra_blocks(self):
        stone = Block.from_string_blockstate("minecraft:stone")
        water = Block.from_string_blockstate("minecraft:water[level=1]")
        granite = Block.from_string_blockstate("minecraft:granite")
        dirt = Block.from_string_blockstate("minecraft:dirt")

        conglomerate_1 = stone + water + dirt
        self.assertIsInstance(conglomerate_1, Block)
        self.assertEqual("minecraft", conglomerate_1.namespace)
        self.assertEqual("stone", conglomerate_1.base_name)
        self.assertEqual({}, conglomerate_1.properties)
        self.assertEqual(2, len(conglomerate_1.extra_blocks))
        for block_1, block_2 in zip(conglomerate_1.extra_blocks, (water, dirt)):
            self.assertEqual(block_1, block_2)
            self.assertEqual(0, len(block_1.extra_blocks))

        conglomerate_2 = conglomerate_1 + granite
        self.assertIsInstance(conglomerate_2, Block)
        self.assertEqual("minecraft", conglomerate_2.namespace)
        self.assertEqual("stone", conglomerate_2.base_name)
        self.assertEqual({}, conglomerate_2.properties)
        self.assertEqual(3, len(conglomerate_2.extra_blocks))
        for block_1, block_2 in zip(
            conglomerate_2.extra_blocks, (water, dirt, granite)
        ):
            self.assertEqual(block_1, block_2)
            self.assertEqual(0, len(block_1.extra_blocks))

        self.assertNotEqual(conglomerate_1, conglomerate_2)

        conglomerate_3 = conglomerate_2 - dirt
        self.assertIsInstance(conglomerate_3, Block)
        self.assertEqual("minecraft", conglomerate_3.namespace)
        self.assertEqual("stone", conglomerate_3.base_name)
        self.assertEqual({}, conglomerate_3.properties)
        self.assertEqual(2, len(conglomerate_3.extra_blocks))
        for block_1, block_2 in zip(conglomerate_3.extra_blocks, (water, granite)):
            self.assertEqual(block_1, block_2)
            self.assertEqual(0, len(block_1.extra_blocks))

        self.assertRaises(TypeError, lambda: stone + 1)
        self.assertRaises(TypeError, lambda: stone - 1)

    def test_extra_blocks_immutable(self):
        stone = Block.from_string_blockstate("minecraft:stone")
        dirt = Block.from_string_blockstate("minecraft:dirt")

        stone2 = stone
        self.assertIs(stone, stone2)
        stone2 += dirt
        self.assertIsNot(stone, stone2)

        stone3 = stone2
        self.assertIs(stone2, stone3)
        stone3 -= dirt
        self.assertIsNot(stone, stone3)

    def test_remove_layer(self):
        stone = Block.from_string_blockstate("minecraft:stone")
        water = Block.from_string_blockstate("minecraft:water[level=1]")
        granite = Block.from_string_blockstate("minecraft:granite")
        dirt = Block.from_string_blockstate("minecraft:dirt")
        oak_log_axis_x = Block.from_string_blockstate("minecraft:oak_log[axis=x]")

        conglomerate_1 = stone + water + dirt + dirt + granite
        self.assertIsInstance(conglomerate_1, Block)
        self.assertEqual("minecraft", conglomerate_1.namespace)
        self.assertEqual("stone", conglomerate_1.base_name)
        self.assertEqual({}, conglomerate_1.properties)
        self.assertEqual(4, len(conglomerate_1.extra_blocks))
        for block_1, block_2 in zip(
            conglomerate_1.extra_blocks, (water, dirt, dirt, granite)
        ):
            self.assertEqual(block_1, block_2)
            self.assertEqual(0, len(block_1.extra_blocks))

        new_conglomerate = conglomerate_1.remove_layer(2)
        for block_1, block_2 in zip(
            new_conglomerate.extra_blocks, (water, dirt, granite)
        ):
            self.assertEqual(block_1, block_2)
            self.assertEqual(0, len(block_1.extra_blocks))

        conglomerate_2 = granite + water + stone + dirt + oak_log_axis_x
        self.assertIsInstance(conglomerate_2, Block)
        self.assertEqual("minecraft", conglomerate_2.namespace)
        self.assertEqual("granite", conglomerate_2.base_name)
        self.assertEqual({}, conglomerate_2.properties)
        self.assertEqual(4, len(conglomerate_2.extra_blocks))
        for block_1, block_2 in zip(
            conglomerate_2.extra_blocks, (water, stone, dirt, oak_log_axis_x)
        ):
            self.assertEqual(block_1, block_2)
            self.assertEqual(0, len(block_1.extra_blocks))

        new_conglomerate = conglomerate_2.remove_layer(3)
        self.assertEqual(3, len(new_conglomerate.extra_blocks))
        for block_1, block_2 in zip(
            new_conglomerate.extra_blocks, (water, stone, oak_log_axis_x)
        ):
            self.assertEqual(block_1, block_2)
            self.assertEqual(0, len(block_1.extra_blocks))

        new_base = conglomerate_2.remove_layer(0)
        self.assertEqual(3, len(new_base.extra_blocks))
        self.assertEqual("minecraft", new_base.namespace)
        self.assertEqual("water", new_base.base_name)
        self.assertEqual({"level": nbt.TAG_String("1")}, new_base.properties)
        for block_1, block_2 in zip(
            new_base.extra_blocks, (stone, dirt, oak_log_axis_x)
        ):
            self.assertEqual(block_1, block_2)
            self.assertEqual(0, len(block_1.extra_blocks))

        self.assertNotEqual(new_base, new_base.remove_layer(1))

        with self.assertRaises(BlockException):
            no_block = granite.remove_layer(0)

        with self.assertRaises(BlockException):
            non_present_layer = granite.remove_layer(7)
            non_present_layer = conglomerate_2.remove_layer(5)

        conglomerate_2.remove_layer(4)  # Check if last layer can still be removed

    def test_hash(self):
        stone = Block.from_string_blockstate("minecraft:stone")
        water = Block.from_string_blockstate("minecraft:water[level=1]")
        granite = Block.from_string_blockstate("minecraft:granite")
        dirt = Block.from_string_blockstate("minecraft:dirt")

        conglomerate_1 = stone + water + dirt
        conglomerate_2 = stone + dirt + water

        self.assertNotEqual(conglomerate_1, conglomerate_2)
        self.assertNotEqual(hash(conglomerate_1), hash(conglomerate_2))

        conglomerate_3 = dirt + water + dirt
        conglomerate_4 = dirt + dirt + water

        self.assertNotEqual(conglomerate_3, conglomerate_4)
        self.assertNotEqual(hash(conglomerate_3), hash(conglomerate_4))

        conglomerate_5 = conglomerate_1 + granite
        conglomerate_6 = conglomerate_3 + granite

        self.assertNotEqual(conglomerate_1, conglomerate_5)
        self.assertNotEqual(conglomerate_3, conglomerate_6)
        self.assertNotEqual(conglomerate_5, conglomerate_6)
        self.assertNotEqual(hash(conglomerate_5), hash(conglomerate_6))


class BlockManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.manager = BlockManager()

        initial_dirt = Block.from_string_blockstate("minecraft:dirt")
        initial_stone = Block.from_string_blockstate("minecraft:stone")
        initial_granite = Block.from_string_blockstate("minecraft:granite")

        initial_dirt_water = initial_dirt + Block.from_string_blockstate(
            "minecraft:water"
        )

        # Partially populate the manager
        self.manager.get_add_block(initial_dirt)
        self.manager.get_add_block(initial_stone)
        self.manager.get_add_block(initial_granite)
        self.manager.get_add_block(initial_dirt_water)

    def test_get_index_from_manager(self):
        dirt = Block.from_string_blockstate("minecraft:dirt")
        stone = Block.from_string_blockstate("minecraft:stone")
        granite = Block.from_string_blockstate("minecraft:granite")

        self.assertEqual(0, self.manager[dirt])
        self.assertEqual(1, self.manager[stone])
        self.assertEqual(2, self.manager[granite])

        water = Block.from_string_blockstate("minecraft:water")

        dirt_water = dirt + water

        self.assertNotEqual(dirt, dirt_water)
        self.assertIsNot(dirt, dirt_water)
        self.assertEqual(3, self.manager[dirt_water])

        with self.assertRaises(KeyError):
            random_block = self.manager[10000]

    def test_get_block_from_manager(self):
        dirt = Block.from_string_blockstate("minecraft:dirt")
        stone = Block.from_string_blockstate("minecraft:stone")
        granite = Block.from_string_blockstate("minecraft:granite")
        water = Block.from_string_blockstate("minecraft:water")
        dirt_water = dirt + water

        self.assertEqual(dirt, self.manager[0])
        self.assertEqual(stone, self.manager[1])
        self.assertEqual(granite, self.manager[2])
        self.assertEqual(dirt_water, self.manager[3])

        with self.assertRaises(KeyError):
            brain_coral = Block.from_string_blockstate("minecraft:brain_coral")
            internal_id = self.manager[brain_coral]


if __name__ == "__main__":
    unittest.main()
