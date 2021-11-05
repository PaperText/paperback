# TODO: better library detection
# usefull link: https://stackoverflow.com/questions/1051254/check-if-python-package-is-installed

import asyncio

async_lib_name: str

try:
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    async_lib_name = "uvloop"
except ImportError:
    async_lib_name = "asyncio"

