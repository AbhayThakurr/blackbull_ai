import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.chat import router as chat_router
from app.discord_bot import bot, start_discord_bot

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pre-load the embedding model so it's ready before the first request
    try:
        from app.memory.vector.embedding_service import embedding_service

        logger.info("Pre-loading embedding model...")
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, embedding_service.is_available)
        logger.info("Embedding model loaded.")
    except Exception:
        logger.info("Embedding model not available (non-critical).")

    # Start the discord bot as a background task when FastAPI starts
    bot_task = asyncio.create_task(start_discord_bot())
    yield
    # Cleanly shut down the bot when FastAPI stops
    if not bot.is_closed():
        await bot.close()
    await bot_task


app = FastAPI(title="BlackBull AI", version="1.0.0", lifespan=lifespan)

app.include_router(chat_router)


@app.get("/")
async def root():
    return {"message": "BlackBull AI Backend Running"}
