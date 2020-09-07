import asyncio

async_lib_name: str = "asyncio"

try:
    import uvloop
    uvloop.install()
    async_lib_name = "uvloop"
except ImportError:
    pass
