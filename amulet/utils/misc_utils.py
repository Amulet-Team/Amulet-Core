from __future__ import annotations

import collections
from typing import Any, Dict, Union

from numpy import integer

Int = Union[int, integer]


def dict_deep_update(
    orig_dict: Dict[Any, Any], new_dict: Dict[Any, Any]
) -> Dict[Any, Any]:
    for key, val in new_dict.items():
        if isinstance(val, collections.Mapping):
            if orig_dict.get(key, {}) == val:
                continue
            tmp = dict_deep_update(orig_dict.get(key, {}), val)
            orig_dict[key] = tmp
        elif isinstance(val, list):
            if orig_dict.get(key, []) == val:
                continue
            orig_dict[key] = orig_dict.get(key, []) + val
        else:
            if orig_dict.get(key, None) == new_dict[key]:
                continue
            orig_dict[key] = new_dict[key]
    return orig_dict
