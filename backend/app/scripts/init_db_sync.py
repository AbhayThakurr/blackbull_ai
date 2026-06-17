"""Initialize the database — create tables and extensions (sync version).

Usage:
    python -m app.scripts.init_db_sync

Make sure DATABASE_URL is set in your .env file and PostgreSQL is running
with the pgvector extension available.
"""

import logging

from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("init_db")

SQL = """
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS user_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    agent_name VARCHAR(100) NOT NULL DEFAULT 'shared',
    key VARCHAR(255) NOT NULL,
    value TEXT NOT NULL,
    embedding VECTOR(1536),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_user_memory_user_id ON user_memory(user_id);
CREATE INDEX IF NOT EXISTS ix_user_memory_user_agent ON user_memory(user_id, agent_name);
CREATE UNIQUE INDEX IF NOT EXISTS ix_user_memory_user_key ON user_memory(user_id, key);

CREATE TABLE IF NOT EXISTS conversation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    agent_name VARCHAR(100) NOT NULL DEFAULT 'yami',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_conversation_user_id ON conversation(user_id);

CREATE TABLE IF NOT EXISTS message (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_message_conversation_id ON message(conversation_id);
"""


def init():
    from app.config.settings import settings

    url = settings.DATABASE_URL
    logger.info(f"Connecting to: {url}")
    engine = create_engine(url)

    try:
        with engine.connect() as conn:
            # Execute the full DDL script
            conn.execute(text(SQL))
            conn.commit()
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}")
        raise
    finally:
        engine.dispose()


if __name__ == "__main__":
    init()
