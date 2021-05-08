######################################
 Blocks in Amulet - The Complex Route
######################################

The previous example showed off the two simple
:meth:`~amulet.api.level.BaseLevel.get_version_block` and
:meth:`~amulet.api.level.BaseLevel.set_version_block` methods which are
useful helper methods for small scale operations but on larger scale
operations they can add quite a bit of overhead which will slow things
down.

This will explain how the data is structured under the hood and how you
can directly manipulate it.

In Amulet, blocks are stored as an array of arbitrary integer values
which refer to a global block palette.

See :class:`~amulet.api.chunk.blocks.Blocks` for the block array class
which is stored in the chunk's
:attr:`~amulet.api.chunk.chunk.Chunk.blocks` property.

See :class:`~amulet.api.registry.block_manager.BlockManager` for the
block palette class which is stored in the level's
:attr:`~amulet.api.level.BaseLevel.block_palette` property as well as
the chunk's :attr:`~amulet.api.chunk.chunk.Chunk.block_palette`
property.

The block palette is a two way mapping between the arbitrary block index
and the :class:`~amulet.api.block.Block` object. As new block states are
found they are registered with the block palette which gives them the
next sequential index. As such the block indices will change each time a
world is loaded.

These :class:`~amulet.api.block.Block` objects will look very different
to the block states you will see in the game.

They are stored in a custom format we refer to as the universal format.
This is a custom block format created by us that is designed to be a
`superset <https://en.wikipedia.org/wiki/Subset>`_ of all the different
block formats from every platform and game version.

In summary every block from any platform or game version can be
represented in our universal system without any data loss.

This allows a world from any platform or version to be loaded into one
consistent format and simplifies all editing code.

Third party code must not directly hard code data in this universal
format because it can and will change to support new game versions as
they are released.

The preferred way to edit data is to first use the translator to convert
the universal representation to a platform and game version of your
choice, edit the data in that format and then convert back to the
universal format to write back to the chunk.

Hard coding block states from the chosen game format is okay because
they are tied to a historical version of the game so they cannot change.
You must not hard code block states in the universal format because any
changes we make will cause your code to break.
