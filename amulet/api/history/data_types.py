from typing import Optional, Any
from .changeable import Changeable

EntryKeyType = Any  # The key an entry is stored under
EntryType = Optional[
    Changeable
]  # None is reserved for if the entry was deleted/did not exist
