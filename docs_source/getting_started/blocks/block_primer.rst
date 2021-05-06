##############
 Block Primer
##############

Blocks in Amulet are stored very differently to other editors such as
MCEdit.

Older editors like MCEdit stored an array of fixed numerical block id
and data values because this is what was stored in the chunk at the
time. These values were hard coded by the game and the editor was
constantly updated to know how to interpret these hard coded values.

To make things worse modded clients could add blocks and switch around
the numerical values which would break some things in MCEdit.

Newer versions of the game have modified the chunk format to contain a
single array of arbitrary integers that are indexes into a block palette
(a list of block states) which is also stored with the chunk.

A block state is made up of a namespaced name separated by a colon and a
dictionary of properties.

For example a spruce leaf block in Java Edition looks like this
(displayed in SNBT format)

.. code::

   {
       "Name": "minecraft:spruce_leaves",
       "Properties": {
           "distance": "1",
           "persistent": "false"
       }
   }

The old numerical system and the new blockstate system are very
different which is why old editors are not able to support the new
format.
