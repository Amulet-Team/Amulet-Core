class WorldFormat(object):
    """
    Base class for World objects
    """

    @classmethod
    def fromUnifiedFormat(cls, unified: object) -> object:
        """
        Converts the passed object to the specific implementation

        :param unified: The object to convert
        :return object: The result of the conversion, None if not successful
        """
        raise NotImplementedError()

    def toUnifiedFormat(self) -> object:
        """
        Converts the current object to the Unified format
        """
        raise NotImplementedError()

    def save(self) -> None:
        """
        Saves the current WorldFormat to disk
        """
        raise NotImplementedError()
