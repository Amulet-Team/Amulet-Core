import amulet

# load the level
# this will automatically find the wrapper that can open the world and set everything up for you.
level = amulet.load_level("level")

# read/write the world data here

# save the changes to the world
level.save()

# close the world
level.close()
