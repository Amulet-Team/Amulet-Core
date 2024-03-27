# There are cases where it would be useful to type hint a class that must inherit from two or more ABCs.
# Python doesn't currently have an intersection type but all cases that need it should refer here to make renaming
# easier if Python implements it.
from typing import Union as Intersection  # noqa
