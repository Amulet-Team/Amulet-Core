Block Definitions
=================

Relevant classes: :class:`version_definitions.definition_manager.DefinitionManager`

Intro
-----
One of the biggest problems with `Minecraft: Java Edition 1.13` is that it switched the structure
of the world save data from using pairs of numerical IDs to define blocks in the world. Previously
these IDs were constant and represented a single block. However, 1.13 changed it so blocks were
identified by blockstates as strings. Some blocks, like Noteblocks for example, went from storing
their data as NBT to using blockstates, this caused an issue where not all blocks have a clear
``(ID, data) <-> blockstate`` translation. This has prompted us to use blockstate strings as
block identifiers in the editor and only numerical IDs where absolutely needed.

Versioned Blocks
----------------
Each supported Minecraft version must define all blocks and provide the following information:

* The blockstate string that the version uses (IE: ``minecraft:stone[variant=stone]`` for Java 1.12)
  as a dictionary/JSON key for the rest of the following information. If there's information inside
  the square brackets, the blockstate identifiers should be a child key with the base blockstate
  (``stone``) being the parent key.
* The ID of that blockstate for that version (IE: ``[1,0]`` for Java 1.12, ``minecraft:stone`` for
  Java 1.13)
* The ``map_to`` key that links the version defined block to a block that we have internally defined
* `Optional`: The ``nbt`` key if the block originally stored it's data as NBT before 1.13 and
  switched to blockstates in 1.13+ (IE: Noteblocks) **!!Incomplete!!**

Identifying and Loading Worlds
------------------------------
Each version definition is required to have a ``identify()`` and ``load()`` function in a python file with the same name as
the directory containing it and the version definitions, but with underscores instead of dots (IE: ``1.12`` definitions
would have ``1_12.py``). The identify function doesn't do any loading but is given the directory path to the world and using
the directory structure and NBT structure in the `level.dat`. This function returns ``True`` if it matches criteria to be
loaded by that format loader, if not, ``False`` is to be returned.

``load()``'s function is to load a world with the
appropriate format loader for the version definitions (IE: ``1.12`` loads via ``anvil`` and ``1.13`` loads via ``anvil2``).
When calling ``load()``, the path to the world directory is given (it can be assumed that the accompanying ``identify()``
function has been called and has returned ``True``) and the method is to return the resulting :class:`api.world.World` object created from
the world format loader.

This python file is also expected to have a global variable named ``FORMAT``, which allows Amulet to output what format
loader will be used when loading the world to the user.
