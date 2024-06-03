# amulet.level

The following is a style guide for implementing levels.
Mostly written for myself when I need to remind myself how I implemented it.

### amulet.level.abc

The level base classes are stored in here

### amulet.level.*

Each level implementation has its own package in amulet.level.

### _load.py

_load.py implements logic to find the correct level class for the data and create an instance of it.

This is implemented as a plugin system to allow third party code to implement their own level formats.

```py
from amulet.level import Level, register_level_class, get_level

class MyLevelClass(Level):
    ...

register_level_class(MyLevelClass)

level = get_level(...)
# Amulet will consider MyLevelClass when getting a new level. 
```

### Function convention

Long running and potentially blocking functions must optionally take a TaskManager instance to support canceling the call
and to relay the progress to the caller. CancelManager and ProgressManager also exist if only a subset is required.

### Signals

Signals should exist and be emitted for every case where there could be need to know that an action happened.

### Level implementation

The requirements differ quite a lot for each level implementation however there are shared aspects.

amulet.level.abc.Level stores the core shared components.

There are a collection of extension classes for other behaviour that is shared by some levels but not by all levels.

#### Constructors

The default `__init__` must not be directly used when creating a new instance.

If the level is an instance of `CreatableLevel` then `create` can be used to create an instance without existing data.

If the level is an instance of `LoadableLevel` then `load` can be used to load existing data.
`reload` can be used to reload inplace.

After running these methods the level will be in its closed state. Only read-only metadata will be accessible.
It is safe to run these methods even if the level is open in Minecraft.
This allows a GUI to display all the levels and metadata without having acquire the lock on the level.

`open` can then be run which will open the level and make the contained data accessible.
If the level needs to be locked to open this will be performed here and unlocked when the level is closed.

### Structure

The level class is split into two parts.
The RawLevel class enables read and write access to the raw level data. These changes cannot be undone.
The Level class exposes the data in a more editable format and supports undoing and redoing changes.

The RawLevel instance can be acquired through the Level instance but when making changes the level must be locked in
unique mode and once finished Level.purge must be called to force the level to reload from the new raw data.
Purge will delete all loaded data so you should ask the user if they want to save or lose their changes.

Read-only metadata may be stored as attributes in the Level or RawLevel classes but data that is only valid while the
level is open must be stored in the `_o` attribute which is cleared when the level is closed.

### Chunk implementation

The chunk format varies between levels and between game versions within the same level.
To support this variation each level defines its own chunk classes to fit the needs of the level.
To simplify the API the chunk classes are built from components which can be reused.
This means that editing code can be reused for all chunk formats that implement the required components.
Common components are stored in `amulet.chunk.components` and levels may add their own components.

The data in the chunk is the raw data unpacked into a more editable format.
Arrays are unpacked and stored in numpy arrays.
Blocks, block entities and entities are stored in classes.
Data which can vary between platforms and versions has the platform and version number it is defined in as an attribute.
