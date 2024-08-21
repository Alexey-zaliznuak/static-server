from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "file" ALTER COLUMN "mime_type" TYPE VARCHAR(200) USING "mime_type"::VARCHAR(200);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "file" ALTER COLUMN "mime_type" TYPE VARCHAR(50) USING "mime_type"::VARCHAR(50);"""
