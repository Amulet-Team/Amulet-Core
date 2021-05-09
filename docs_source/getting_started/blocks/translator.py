import amulet

# load the level
level = amulet.load_level("level")

level.translation_manager.platforms()
# ['bedrock', 'java', 'universal']

level.translation_manager.version_numbers("bedrock")
# [(1, 10, 0), (1, 11, 0), (1, 12, 0), (1, 13, 0), (1, 14, 0), ...]

# close the world
level.close()
