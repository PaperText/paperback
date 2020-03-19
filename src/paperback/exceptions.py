class DuplicateModuleError(Exception):
    pass


class InheritanceError(Exception):
    pass


class GeneralException(Exception):
    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message


class TokenException(Exception):
    def __init__(self, name: str):
        self.name = name
