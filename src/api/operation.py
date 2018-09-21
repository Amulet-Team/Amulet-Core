from __future__ import annotations

from abc import abstractmethod


class Operation:

    @abstractmethod
    def run_operation(self, world):
        pass
