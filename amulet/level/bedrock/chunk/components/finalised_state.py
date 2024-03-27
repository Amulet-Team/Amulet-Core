class FinalisedStateComponent:
    def __init__(self) -> None:
        self.__finalised_state = 2

    @property
    def finalised_state(self) -> int:
        return self.__finalised_state

    @finalised_state.setter
    def finalised_state(
        self,
        finalised_state: int,
    ) -> None:
        if not isinstance(finalised_state, int):
            raise TypeError
        if finalised_state < 0:
            raise ValueError
        self.__finalised_state = int(finalised_state)
