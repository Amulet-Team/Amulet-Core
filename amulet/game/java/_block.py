from amulet.game.abc import BlockData, NumericalBlockDataComponent


class JavaBlockData(BlockData, NumericalBlockDataComponent):
    def numerical_id_to_namespace_id(self, numerical_id: int) -> tuple[str, str]:
        pass

    def namespace_id_to_numerical_id(self, namespace: str, base_name: str) -> int:
        pass
