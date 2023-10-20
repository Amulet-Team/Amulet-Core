# Amulet Importing Guidelines

Due to the Amulet API being a python package and also utilizing dynamic importing for various systems (such as format wrappers, 
version definitions, operations, etc.) `import` statements need to accommodate for this.

## Relative versus Absolute Imports

### When to use Relative Imports
Relative imports can be used when an internal, non-dynamically imported module needs to import other parts of the Amulet API. 

Take this experpt from `api/block.py` for example:
```python
from __future__ import annotations

from sys import getsizeof
import re
from typing import Dict, Iterable, Tuple, Union
import amulet_nbt

from .errors import BlockException
```

### When to use Absolute Imports
Absolute imports are to be used when a module will be imported dynamically at runtime. This is due to dynamic imports not always being set up to support relative imports in some cases, so trying to use relative imports may cause a `ImportError` at runtime.

```python
from __future__ import annotations

from amulet.block import Block

from amulet.utils.format_utils import check_all_exist
```

Absolute import statements can also be used internally within the Amulet API even when not located in a dynamically imported module, but this is highly discouraged unless an exception occurs otherwise. 

Example Usage:

```python
from amulet.api import paths

from amulet.block import Block
from amulet import level

...

if __name__ == '__main__':
    ...
```

## Changelog
- 7.23.2019: Initial Revision
- 3.2.2020: Removed out of date paths information
- 5.4.2021: Updated code to remove old references
