import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator


class AsyncRWLock:
    """
    A minimal async readers-writer lock for single-process use.
    """

    def __init__(self) -> None:
        self._readers = 0
        self._writer = False
        self._condition = asyncio.Condition()

    async def acquire_read(self) -> None:
        async with self._condition:
            while self._writer:
                await self._condition.wait()
            self._readers += 1

    async def release_read(self) -> None:
        async with self._condition:
            self._readers -= 1
            if self._readers == 0:
                self._condition.notify_all()

    async def acquire_write(self) -> None:
        async with self._condition:
            while self._writer or self._readers > 0:
                await self._condition.wait()
            self._writer = True

    async def release_write(self) -> None:
        async with self._condition:
            self._writer = False
            self._condition.notify_all()

    @asynccontextmanager
    async def read(self) -> AsyncIterator[None]:
        await self.acquire_read()
        try:
            yield
        finally:
            await self.release_read()

    @asynccontextmanager
    async def write(self) -> AsyncIterator[None]:
        await self.acquire_write()
        try:
            yield
        finally:
            await self.release_write()
