from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "file" (
    "id" UUID NOT NULL  PRIMARY KEY,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "title" VARCHAR(100) NOT NULL,
    "slug" VARCHAR(100) NOT NULL UNIQUE,
    "description" TEXT NOT NULL,
    "path" VARCHAR(300) NOT NULL,
    "size" INT NOT NULL,
    "mime_type" VARCHAR(50) NOT NULL
);
CREATE INDEX IF NOT EXISTS "idx_file_slug_c85814" ON "file" ("slug");
CREATE INDEX IF NOT EXISTS "idx_file_title_385d2a" ON "file" ("title");
COMMENT ON COLUMN "file"."size" IS 'Size in bytes';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
