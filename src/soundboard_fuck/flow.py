import asyncio
from asyncio import Queue
from typing import Any, AsyncGenerator, Callable, Generic, TypeVar


_T = TypeVar("_T")


class HotFlow(Generic[_T]):
    value: _T | None = None

    def __init__(self, initial_value: _T):
        self.queue = Queue[_T]()
        self.value = initial_value

    async def emit(self, value: _T):
        await self.queue.put(value)

    async def observe(self) -> AsyncGenerator[_T, None]:
        if self.value is not None:
            yield self.value
        while True:
            value = await self.queue.get()
            self.value = value
            yield value

    async def map(self, func: Callable[[_T], Any]):
        observer = self.observe()
        while True:
            value = await anext(observer)
            yield func(value)

    def collect(self, func: Callable[[_T], Any]):
        async def _collect(_func):
            observer = self.observe()
            while True:
                value = await anext(observer)
                _func(value)

        coro = _collect(func)
        asyncio.create_task(coro)


async def main():
    hot_flow = HotFlow[int](0)

    def collector(v: int):
        print(f"collector: new valuer {v}")

    hot_flow.collect(collector)

    await asyncio.sleep(1)
    await hot_flow.emit(1)
    await hot_flow.emit(2)

    await asyncio.sleep(1)

    print("New value (3) will be received by all observers")
    await hot_flow.emit(3)

    def collector2(v: int):
        print(f"collector2: new valuer {v}")

    hot_flow.collect(collector2)
    await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
