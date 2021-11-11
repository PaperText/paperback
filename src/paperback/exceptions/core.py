from __future__ import annotations

from typing import Any, Optional

from fastapi import HTTPException


class DuplicateModuleError(Exception):
    pass


class InheritanceError(Exception):
    pass


class PaperBackError(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)
