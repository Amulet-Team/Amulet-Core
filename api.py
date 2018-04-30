class WorldFormat(object):

    @classmethod
    def fromUnifiedFormat(cls, unified):
        raise NotImplementedError()

    def toUnifiedFormat(self):
        raise NotImplementedError()
