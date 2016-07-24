import asyncio
import functools
import threading
import contextlib


class Async:
    loop = None


    @classmethod
    def set_default_loop(cls, loop):
        cls.loop = loop


    @classmethod
    async def Call(cls, *args, **kwargs):
        if cls.loop:
            loop = cls.loop
            o = args[0]
            args = args[1:]
        else:
            loop = args[0]
            o = args[1]
            args = args[2:]

        a = AsyncCall(loop, o)
        r = await a(*args, **kwargs)
        return r


    @classmethod
    async def ExecutorCall(cls, *args, **kwargs):
        if cls.loop:
            loop = cls.loop
            o = args[0]
            args = args[1:]
        else:
            loop = args[0]
            o = args[1]
            args = args[2:]

        a = AsyncExecutorCall(loop, o)
        r = await a(*args, **kwargs)
        return r


    @classmethod
    async def ThreadCall(cls, *args, **kwargs):
        if cls.loop:
            loop = cls.loop
            o = args[0]
            args = args[1:]
        else:
            loop = args[0]
            o = args[1]
            args = args[2:]

        a = AsyncThreadCall(loop, o)
        r = await a(*args, **kwargs)
        return r


    @classmethod
    def For(cls, *args):
        if cls.loop:
            loop = cls.loop
            o = args[0]
        else:
            loop = args[0]
            o = args[1]

        return AsyncFor(loop, o)


    @classmethod
    def With(cls, *args):
        if cls.loop:
            loop = cls.loop
            o = args[0]
        else:
            loop = args[0]
            o = args[1]

        return AsyncWith(loop, o)


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


class AsyncThreadCall:
    def __init__(self, loop, o, t=None):
        self.loop = loop
        self.o = o
        self.t = t


    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, repr(self.o))


    def _thread_call(self, p, future):
        try:
            r = p()
            future.set_result(r)
        except Exception as e:
            future.set_exception(e)

        self.t = None


    async def _call(self, p, future):
        t = threading.Thread(target=self._thread_call, args=(p, future))
        t.start()
        self.t = t


    async def __call__(self, *args, **kwargs):
        p = functools.partial(self.o, *args, **kwargs)
        future = asyncio.Future()
        _future = asyncio.ensure_future(self._call(p, future), loop=self.loop)
        r = None

        while True:
            if future.done():
                r = future.result()
                break

            await asyncio.sleep(0)

        return r


class AsyncFor:
    def __init__(self, loop, o):
        self.loop = loop
        self.o = o
        self.it = None


    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, repr(self.o))


    async def __aiter__(self):
        self.it = self.o.__iter__()
        return self


    async def __anext__(self):
        await asyncio.sleep(0)      # manually switch coroutine

        try:
            n = self.it.__next__()
        except StopIteration as e:
            self.it = None
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
        self.__dict__['ctx'] = self.o.__enter__()   # this could be long running
        return self


    async def __aexit__(self, exc_type, exc, tb):
        self.o.__exit__(exc_type, exc, tb)


    def __getattr__(self, attr):
        return getattr(self.ctx, attr)


    def __setattr__(self, attr, value):
        setattr(self.ctx, attr, value)
