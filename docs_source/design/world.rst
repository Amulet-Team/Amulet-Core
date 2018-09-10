World Design
============

Relevant Classes: :class:`api.world.World`, :class:`api.world.WorldFormat`

Intro
-----

In order to make world loading simpler and more flexible to future changes with Minecraft,
the Amulet Map Editor only loads/edits a proprietary format. By doing this, to support
a Minecraft world format, the only things required are separate block/entity/tile entity definitions
and a "conversion" wrapper, which converts the world data on disc to the "Amulet format"


The "Amulet Format"
--------------------
The "Amulet Format" in a basic form is a wrapper and temporary storage of world data for editing.
For blocks, the format expects the blocks to be integer-based, however, these integers are dynamic
and are assigned to blocks as new ones are found with newly loaded chunks. IE: ``minecraft:stone``
won't always have an integer ID of 1, but may have one of 20 if it isn't encountered any time earlier
when loading other chunks.

Despite using integer based IDs, these IDs are used only internally, any method that exposes blocks
will normalize the ID to the internal string ID used by the editor (these string IDs are based off
of the blockstates present in 1.13). The only way to reference a block will be through this way, integer
IDs are entirely dynamic and should never be used except for loading/saving chunks.

Format Loaders
---------------
Each world format loader is separated into their own containers and don't do any editing of
their own. Each format loader handles reading the world data then converting the blocks/entities/
tile entities into a format that the Amulet Format expects. Each format loader must inherit from
:class:`api.world.WorldFormat`

Each format loader is required to have a ``identify()`` function. This function doesn't do any
loading but is given the directory path to the world and using the directory structure and NBT
structure in the `level.dat`. This function returns ``True`` if it matches criteria to be loaded
by that format loader, if not, ``False`` is to be returned.

When loading, format loaders are first called via a class method ``load()`` which is expected to
return a :class:`api.world.World` instance. The method receives the path to directory of the world.
Once the world is loaded, the format loader is only used to load and translate new data from the disc.

When saving, format loaders shouldn't make any assumptions about the previous format of the world
since the Amulet Format doesn't keep track of that data. Due to this, while saving various attributes
should be check and either saved or ignored depending on what data is present.