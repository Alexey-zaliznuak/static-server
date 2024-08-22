import asyncio
import logging

from tortoise import Tortoise

try:
    from src.config import TORTOISE_ORM

except ImportError:
    import os
    import sys

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

    from src.config import TORTOISE_ORM


logger = logging.getLogger(__name__)


async def tortoise_startup():
    logger.info("Beginning tortoise startup")

    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    logger.info("Success startup tortoise")


async def tortoise_shutdown():
    logger.warning("Start closing connections")

    await Tortoise.close_connections()

    logger.info("Success close tortoise connections")


async def _init():
    await Tortoise.init(config=TORTOISE_ORM)
    await tortoise_shutdown()


if __name__ == "__main__":
    asyncio.run(_init())
