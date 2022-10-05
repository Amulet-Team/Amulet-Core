import warnings

warnings.warn(
    "`amulet.libs.leveldb` is depreciated and will be removed in the future. It is replaced by the `leveldb` package.",
    DeprecationWarning,
)
from leveldb import LevelDB, LevelDBException, LevelDBEncrypted
