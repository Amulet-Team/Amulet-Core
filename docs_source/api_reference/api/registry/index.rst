####################################
 :mod:`amulet.api.registry` package
####################################

The block and biome data is stored as numerical values in arrays.

The block and biome registries exist to give these numerical values
meaning.

Put simply, the registry class is a two way mapping to allow converting
a numerical value to a :class:`amulet.api.block.Block` object or a biome
string and back to a numerical value.

These are stored in the level at
:attr:`~amulet.api.level.BaseLevel.block_palette` and
:attr:`~amulet.api.level.BaseLevel.biome_palette` and also in the chunk.

Before adding a block or biome to the array data it first needs
registering with the palette which will return the integer value that
represents that data.

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :glob:

   *
