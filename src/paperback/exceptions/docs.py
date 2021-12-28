from fastapi import status

from paperback.exceptions import PaperBackError


class DocumentNameError(PaperBackError):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A document with the same ID already exists",
        )


class CorpusDoesntExist(PaperBackError):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A corpus with specified ID doesn't exists",
        )


class DictNameError(PaperBackError):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A dictionary with specified ID already exists",
        )
