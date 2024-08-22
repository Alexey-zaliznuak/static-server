import asyncio

from tortoise import Tortoise

try:
    from src.config import TORTOISE_ORM

except ImportError:
    import os
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
    from src.config import TORTOISE_ORM


async def tortoise_startup():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()


async def tortoise_shutdown():
    await Tortoise.close_connections()


async def _init():
    await Tortoise.init(config=TORTOISE_ORM)
    await tortoise_shutdown()


if __name__ == "__main__":
    asyncio.run(_init())
