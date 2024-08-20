from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "file" ALTER COLUMN "path" DROP NOT NULL;
        ALTER TABLE "file" ALTER COLUMN "description" DROP NOT NULL;
        ALTER TABLE "file" ALTER COLUMN "mime_type" DROP NOT NULL;
        ALTER TABLE "file" ALTER COLUMN "size" DROP NOT NULL;
        ALTER TABLE "file" ALTER COLUMN "title" DROP NOT NULL;
        ALTER TABLE "file" ALTER COLUMN "slug" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "file" ALTER COLUMN "path" SET NOT NULL;
        ALTER TABLE "file" ALTER COLUMN "description" SET NOT NULL;
        ALTER TABLE "file" ALTER COLUMN "mime_type" SET NOT NULL;
        ALTER TABLE "file" ALTER COLUMN "size" SET NOT NULL;
        ALTER TABLE "file" ALTER COLUMN "title" SET NOT NULL;
        ALTER TABLE "file" ALTER COLUMN "slug" SET NOT NULL;"""
