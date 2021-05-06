##################
 Blocks in Amulet
##################

In Amulet, blocks are stored as an array of arbitrary integer values
which refer to a global block palette stored in the level's
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

Third party code however should not be directly editing the data in this
universal format because it can and will change to support new game
versions as they are released.

The preferred way to edit data is to first use the translator to convert
the universal representation to a platform and game version of your
choice, edit the data in that format and then convert back to the
universal format to write back to the chunk.

Hard coding block states from the chosen game format is okay because
they are tied to a historical version of the game so they cannot change.
You must not hard code block states in the universal format because any
changes we make will cause your code to break.

The translator for the level is found in
:attr:`~amulet.api.level.BaseLevel.translation_manager` and can be used
to find which platforms and versions are supported.
:meth:`~PyMCTranslate.py3.api.translation_manager.translation_manager.TranslationManager.platforms`
will give a list of the valid platforms and
:meth:`~PyMCTranslate.py3.api.translation_manager.translation_manager.TranslationManager.version_numbers`
will give a list of versions numbers for a given platform. Using
:meth:`~PyMCTranslate.py3.api.translation_manager.translation_manager.TranslationManager.get_version`
with a version of your choice will give you a translator for that
version which can be used to translate to and from the universal format.
