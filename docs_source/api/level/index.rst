###############
 level package
###############

The level classes are the containers for all data related to a given world or structure.

The level contains chunk data as well as some other data and methods to read and write this data.
The class also has a history management system to enable reverting changes.

The data in these classes is stored in what we refer to as the universal format.
This is a single consistent format that all data is converted to regardless of origin.
This enables editing data from different platforms and versions in one consistent way rather than having custom logic for each.
This also enables world conversion because this universal format can be converted out to any format not just the one it came from.

.. note::
    These classes should not be directly initialised by your code.

    You should instead call :func:`amulet.load_level` which will work out how to load the data and set up the correct level class for you and return it.

Most of the logic is implemented in
:class:`~amulet.api.level.BaseLevel`
with slight modifications in
:class:`~amulet.api.level.World`,
:class:`~amulet.api.level.Structure`
and
:class:`~amulet.api.level.ImmutableStructure`.

:class:`~amulet.api.level.World` is the class that will be used when editing world data.

:class:`~amulet.api.level.Structure` is the class that will be used when editing structure files such as .schematic, .mcstructure, .schem

:class:`~amulet.api.level.ImmutableStructure` is used when a section of a world needs extracting without modifying the original world. Eg copying. see :meth:`~amulet.api.level.BaseLevel.extract_structure`


.. inheritance-diagram:: amulet.api.level.World
                         amulet.api.level.Structure
                         amulet.api.level.ImmutableStructure
    :parts: 1

.. toctree::
   :maxdepth: 1
   :caption: Contents:
   :glob:

   base_level/index
   world
   structure
   immutable_structure/index
