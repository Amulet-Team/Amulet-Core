import amulet
from amulet.api.errors import ChunkLoadError, ChunkDoesNotExist
from amulet.api.chunk import Chunk

# load the level
level = amulet.load_level("level")

# create a new chunk at cx=1, cz=2. This is an empty chunk containing no data.
new_chunk = Chunk(1, 2)

# populate the chunk with any data you want (if any)

# add the newly created chunk to the given dimension.
level.put_chunk(new_chunk, "overworld")

# we have changed the chunk data so we need to set this value otherwise it won't get saved.
new_chunk.changed = True

# save the changes to the world
level.save()

# close the world
level.close()
