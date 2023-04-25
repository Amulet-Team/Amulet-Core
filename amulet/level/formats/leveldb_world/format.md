# Bedrock Level Format

All the data for Minecraft Bedrock levels is stored in either the level.dat file or in the db folder as leveldb database.

This documentation will describe binary structures using 010 Editor's template format which is based on C code.
`BigEndian()` and `LittleEndian()` will be used to denote the endianness for everything that follows in that code block.

## level.dat

The level.dat file is a binary file structured as follows

```c
LittleEndian();
struct LevelDat {
    uint32 version_number;
    uint32 nbt_payload_length;
    char[nbt_payload_length] nbt_payload; 
}
```

The nbt_playload is a binary NBT tag stored uncompressed in little endian format with utf-8 strings.

I suggest [this site](https://wiki.vg/NBT) to understand the binary NBT format.


## leveldb

The `db` folder in the level is a `{key: value}` database stored using a modified version of Google's leveldb format.

This can be viewed like a dictionary with keys and values as bytes. `dict[bytes, bytes]`

There are a large number of keys in the database, but they all fit into a small number of categories.


### Global data

#### LevelChunkMetaDataDictionary

This stores chunk height data.

```c
LittleEndian();
struct LevelChunkMetaDataDictionary {
    uint32 count;
    struct {
        char[8] key;
        NBTTag tag;
    }[count];
}
```

scoreboard
mobevents

~local_player
portals
BiomeData

schedulerWT
AutonomousEntities
mVillages
VillageManager
PositionTrackDB-LastId

game_flatworldlayers

### Dimension data

dimension0
Overworld
Nether
TheEnd

### Chunk data

The key for the chunk data is stored as follows.

```c
LittleEndian();
struct OverworldChunkKey {
    int32 chunk_x;
    int32 chunk_z;
    char tag;
    if (tag == 0x2F)
        // The sub-chunk tag has an extra byte
        char sub_chunk_index
}

struct DimensionChunkKey {
    int32 chunk_x;
    int32 chunk_z;
    uint32 dimension_id;
    char tag;
    if (tag == 0x2F)
        // The sub-chunk tag has an extra byte
        char sub_chunk_index
}
```

`dimension_id` is 1 for the Nether and 2 for the End.

#### Tag

The tag byte in the chunk data key can have the following values which dictates the data contained in the value.
There may be more values that are either unused or yet to be used.

##### Dec | Hex | ASCII | Name
##### `43` | `0x2B` | `+` | Data3D

```c
struct Data2D {
    uint16[256] height_arr;  // 16x16
    PalettedStorage biome_arr;  // 16x16x16
}
```

PalettedStorage format can be found [here](https://gist.github.com/Tomcc/a96af509e275b1af483b25c543cfbf37)

##### `44` | `0x2C` | `,` | ChunkVersion

```c
char chunk_version;
```

##### `45` | `0x2D` | `-` | Data2D

```c
struct Data2D {
    uint16[256] height_arr;  // 16x16
    uint8[256] biome_arr;  // 16x16
}
```

##### `46` | `0x2E` | `.` | Data2DLegacy
##### `47` | `0x2F` | `/` | SubChunk

The block data for a 16x16x16 volume.
This key has an extra byte dictating the index in the chunk.

PalettedStorage format can be found [here](https://gist.github.com/Tomcc/a96af509e275b1af483b25c543cfbf37)

##### `48` | `0x30` | `0` | LegacyTerrain
##### `49` | `0x31` | `1` | BlockEntity

```c
NBTTag[] block_entity_arr;
```

##### `50` | `0x32` | `2`   Entity

```c
NBTTag[] entity_arr;
```

##### `51` | `0x33` | `3` | PendingTicks
##### `52` | `0x34` | `4` | BlockExtraData
##### `53` | `0x35` | `5` | BiomeState
##### `54` | `0x36` | `6` | FinalisedState

Prior to ? version
```c
char finalised_state;
```

Since version ?
```c
uint32 finalised_state
```

##### `55` | `0x37` | `7` | 
##### `56` | `0x38` | `8` | BorderBlocks
##### `57` | `0x39` | `9` | HardCodedSpawnAreas
##### `58` | `0x3A` | `:` | RandomTicks
##### `59` | `0x3B` | `;` | Checksums
##### `61` | `0x3D` | `=` |
##### `62` | `0x3E` | `>` |
##### `63` | `0x3F` | `?` | LevelChunkMetaDataKey

This is a key find data in [LevelChunkMetaDataDictionary](#levelchunkmetadatadictionary)

```c
char[8] level_chunk_meta_data_key
```

##### `64` | `0x40` | `@` |
##### `65` | `0x41` | `A` |
##### `118` | `0x76` | `V` | OldChunkVersion

Moved to `0x2C` in 1.16.100

```c
char chunk_version;
```
