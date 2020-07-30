def get_async_lib() -> str:
    import asyncio

    try:
        import uvloop

        uvloop.install()
        return "uvloop"
    except Exception:
        return "asyncio"


async_lib_name = get_async_lib()
