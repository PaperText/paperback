from typing import Literal, Type

from starlette.responses import JSONResponse

AsyncLibName = Literal["asyncio", "uvloop"]


def get_async_lib_name() -> AsyncLibName:
    try:
        import uvloop

        uvloop.install()
    except ImportError:
        uvloop = None

    if uvloop:
        return "uvloop"
    else:
        return "asyncio"


def get_response_class() -> Type[JSONResponse]:
    try:
        import orjson
        from fastapi.responses import ORJSONResponse
    except ImportError:
        ORJSONResponse = None  # noqa

    if ORJSONResponse:
        return ORJSONResponse
    else:
        return JSONResponse
