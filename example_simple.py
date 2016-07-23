import time
import random
import asyncio
import tempfile
import functools

from aiowrap import Async


async def do_async_for(loop, s, e):
    async for i in Async.For(loop, range(s, e)):
        await asyncio.sleep(random.random())
        print('do_async_for', i)


async def do_async_with(loop):
    async with Async.With(loop, tempfile.TemporaryFile()) as f:
        await Async.Call(loop, f.write, b'hello world')
        await asyncio.sleep(random.random())
        await Async.Call(loop, f.seek, 0)
        await asyncio.sleep(random.random())
        data = await Async.Call(loop, f.read)
        print('do_async_with', data)


async def do_async_call(loop, f, t):
    r = await Async.Call(loop, f, t)
    print('do_async_call', f, t, r)
    return r


async def do_async_executor_call(loop, f, t):
    r = await Async.ExecutorCall(loop, f, t)
    print('do_async_executor_call', f, t, r)
    return r


async def do_async_thread_call(loop, f, t):
    r = await Async.ThreadCall(loop, f, t)
    print('do_async_thread_call', f, t, r)
    return r


def blocking_sleep(t):
    time.sleep(t)
    return t


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    tasks = [
        asyncio.ensure_future(do_async_with(loop)),
        asyncio.ensure_future(do_async_with(loop)),
        asyncio.ensure_future(do_async_for(loop, 0, 10)),
        asyncio.ensure_future(do_async_for(loop, 20, 30)),
        
        asyncio.ensure_future(
            do_async_call(loop, blocking_sleep, random.random() * 5)),
        
        asyncio.ensure_future(
            do_async_call(loop, blocking_sleep, random.random() * 5)),

        asyncio.ensure_future(
            do_async_executor_call(loop, blocking_sleep, 5)),

        asyncio.ensure_future(
            do_async_executor_call(loop, blocking_sleep, 5)),

        asyncio.ensure_future(
            do_async_thread_call(loop, blocking_sleep, 5)),

        asyncio.ensure_future(
            do_async_thread_call(loop, blocking_sleep, 4)),

        asyncio.ensure_future(
            do_async_thread_call(loop, blocking_sleep, 3)),

        asyncio.ensure_future(
            do_async_thread_call(loop, blocking_sleep, 2)),
    ]

    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
