# Amulet Importing Guidelines

Due to the Amulet API being an python module/package and also utilizing dynamic importing for various systems (such as format wrappers, 
version definitions, operations, etc.) `import` statements need to accomodate for this.

## Relative versus Absolute Imports

### When to use Relative Imports
Relative imports can be used when an internal, non-dynamically imported module needs to import other parts of the Amulet API. 

Take this experpt from `api/world_loader.py` for example:
```python
from __future__ import annotations

from typing import Tuple

from . import version_loader
from . import format_loader
from .world import World
from .errors import (
    FormatLoaderNoneMatched,
    FormatLoaderInvalidFormat,
    FormatLoaderMismatched,
    VersionLoaderInvalidFormat,
    VersionLoaderMismatched,
)
```

### When to use Absolute Imports
Absolute imports are to be used when a module will be imported dynamically at runtime. This is due to dynamic imports not always being set up to support relative imports in some cases, so trying to use relative imports may cause a `ImportError` at runtime.

Take an experpt from `version_definitions/java_1_13.py` for example:
```python
from __future__ import annotations

from amulet.api.block import Block

from amulet.utils.format_utils import (
    check_all_exist,
    load_leveldat,
    check_version_leveldat,
)
```

Absolute import statements can also be used internally within the Amulet API even when not located in a dynamically imported module, but this is highly discouraged unless an exception occurs otherwise.

## Using the `api.paths` module
Due to the Amulet API not having a single/central entry point or instance, a few variables need to be assigned before the rest of the API is imported in order for the API to work as desired. Majority of these variables are located in the `api/paths.py` file and can be changed during runtime. 

Example Usage:
```python
from amulet.api import paths

paths.FORMATS_DIR = r"./path/to/formats"
paths.DEFINITIONS_DIR = r"./path/to/version_definitions"

from amulet.api.block import Block
from amulet import world_loader

...

if __name__ == '__main__':
    ...
```

Technically, the path variables can be set anytime/anywhere before importing a module that uses the variables to dynamically load modules, but it is safest to assign them as early as possible in your code. Failure to reassign these variables will result in Amulet searching empty or missing directories and could cause unexpected behaviour.

## Changelog
- 7.23.2019: Initial Revision
