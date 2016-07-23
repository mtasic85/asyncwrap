import time
import random
import asyncio
import tempfile
import functools

from aiowrap import AsyncCall, AsyncFor, AsyncWith


async def do_async_for(loop, s, e):
    async for i in AsyncFor(loop, range(s, e)):
        await asyncio.sleep(random.random())
        print('do_async_for', i)


async def do_async_with(loop):
    async with AsyncWith(loop, tempfile.TemporaryFile()) as f:
        await f.write(b'hello world')
        await asyncio.sleep(random.random())
        await f.seek(0)
        await asyncio.sleep(random.random())
        data = await f.read()
        print('do_async_with', data)


async def do_async_call(loop, f, t):
    a = AsyncCall(loop, f)
    r = await a(t)
    print('do_async_call', f, t, r)
    return r


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    tasks = [
        asyncio.ensure_future(do_async_with(loop)),
        asyncio.ensure_future(do_async_with(loop)),
        asyncio.ensure_future(do_async_for(loop, 0, 10)),
        asyncio.ensure_future(do_async_for(loop, 20, 30)),
        
        asyncio.ensure_future(
            do_async_call(loop, time.sleep, random.random() * 5)),
        
        asyncio.ensure_future(
            do_async_call(loop, time.sleep, random.random() * 5)),
    ]

    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
