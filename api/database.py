from prisma import Prisma
from contextlib import asynccontextmanager

prisma = Prisma()


async def connect_db():
    await prisma.connect()


async def disconnect_db():
    if prisma.is_connected():
        await prisma.disconnect()


@asynccontextmanager
async def get_db():
    if not prisma.is_connected():
        await prisma.connect()
    try:
        yield prisma
    finally:
        pass
