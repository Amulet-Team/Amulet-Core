########################
 Open an Existing World
########################

.. code:: python

   import amulet

   # load the level
   # this will automatically find the wrapper that can open the world and set everything up for you.
   level = amulet.load_level("level")

   # read/write the world data here
   # all future examples will assume you have a level open and will start from here.

   # save the changes to the world
   level.save()

   # close the world
   level.close()
