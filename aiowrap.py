import asyncio
import functools
import contextlib


class Async:
    @classmethod
    async def call(cls, loop, o, *args, **kwargs):
        a = AsyncCall(loop, o)
        r = await a(*args, **kwargs)
        return r


class AsyncCall:
    def __init__(self, loop, o):
        self.loop = loop
        self.o = o


    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, repr(self.o))


    async def __call__(self, *args, **kwargs):
        v = self.o(*args, **kwargs)
        return v


class AsyncExecutorCall:
    def __init__(self, loop, o):
        self.loop = loop
        self.o = o


    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, repr(self.o))


    async def __call__(self, *args, **kwargs):
        p = functools.partial(self.o, *args, **kwargs)
        v = await self.loop.run_in_executor(None, p)
        return v


class AsyncFor:
    def __init__(self, loop, o):
        self.loop = loop
        self.o = o


    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, repr(self.o))


    def __aiter__(self):
        self.it = self.o.__iter__()
        return self


    async def __anext__(self):
        await asyncio.sleep(0)      # manually switch coroutine

        try:
            n = self.it.__next__()
        except StopIteration as e:
            raise StopAsyncIteration(e)

        return n


class AsyncWith:
    def __init__(self, loop, o):
        self.__dict__['loop'] = loop
        self.__dict__['o'] = o
        self.__dict__['ctx'] = None


    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, repr(self.o))


    async def __aenter__(self):
        self.__dict__['ctx'] = self.o.__enter__()
        return self


    async def __aexit__(self, exc_type, exc, tb):
        self.o.__exit__(exc_type, exc, tb)


    def __getattr__(self, attr):
        v = getattr(self.ctx, attr)

        if callable(v):
            return AsyncCall(self.loop, v)
        
        return v


    def __setattr__(self, attr, value):
        setattr(self.ctx, attr, value)
