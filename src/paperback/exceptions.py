class DuplicateModuleError(Exception):
    pass


class InheritanceError(Exception):
    pass


class TokenException(Exception):
    def __init__(self, name: str):
        self.name = name
