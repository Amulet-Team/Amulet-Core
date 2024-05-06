from .json_interface import JSONInterface, JSONCompatible, JSONDict, JSONList
from .version import GameVersion
from .block import (
    BlockData,
    DatabaseBlockData,
    BlockDataNumericalComponent,
    BlockTranslationError,
)
from .biome import (
    BiomeData,
    DatabaseBiomeData,
    BiomeDataNumericalComponent,
    BiomeTranslationError,
    load_json_biome_data,
)
from ._block_specification import (
    BlockSpec,
    NBTSpec,
    PropertySpec,
    PropertyValueSpec,
    load_json_block_spec,
)
