from fastapi import status

from paperback.exceptions import PaperBackError


class CantCreateUserError(PaperBackError):
    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, detail={}, headers={}
        )
