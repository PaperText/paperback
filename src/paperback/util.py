from typing import Literal, Any, Union


AsyncLibName = Literal["asyncio", "uvloop"]


def get_async_lib_name() -> AsyncLibName:
    try:
        import uvloop
        uvloop.install()
    except ImportError:
        uvloop = None

    return "uvloop" if uvloop else "asyncio"


def get_response_class() -> Any:
    from starlette.responses import JSONResponse

    try:
        from fastapi.responses import ORJSONResponse
    except ImportError:
        ORJSONResponse = None # noqa

    return ORJSONResponse or JSONResponse


