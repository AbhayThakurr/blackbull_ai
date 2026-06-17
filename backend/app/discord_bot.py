import asyncio
import io
import uuid

import discord
import soundfile as sf
import speech_recognition as sr

from app.config.settings import settings
from app.graph.builder import graph

# ---------------------------------------------------------------------------
# In-memory conversation history (per Discord thread/channel)
# Falls back gracefully when PostgreSQL isn't configured.
# ---------------------------------------------------------------------------
_conversation_history: dict[str, list[dict[str, str]]] = {}


def _conversation_key(channel_id: int, author_id: int) -> str:
    return f"{channel_id}:{author_id}"


def get_conversation_history(channel_id: int, author_id: int) -> list[dict[str, str]]:
    """Return the accumulated message history for a (channel, author) pair."""
    return _conversation_history.setdefault(
        _conversation_key(channel_id, author_id), []
    )


def append_to_history(channel_id: int, author_id: int, role: str, content: str) -> None:
    key = _conversation_key(channel_id, author_id)
    history = _conversation_history.setdefault(key, [])
    history.append({"role": role, "content": content})
    # Keep only the last 20 messages to avoid unbounded growth
    if len(history) > 20:
        _conversation_history[key] = history[-20:]


# ---------------------------------------------------------------------------
# Audio transcription
# ---------------------------------------------------------------------------


def transcribe_audio_bytes(audio_bytes: bytes) -> str:
    """Transcribes OGG/audio bytes using SpeechRecognition and soundfile."""
    try:
        # Read audio bytes using soundfile (supports OGG Opus natively via libsndfile)
        data, samplerate = sf.read(io.BytesIO(audio_bytes), dtype="int16")

        # Convert stereo to mono if necessary for optimal speech recognition
        if len(data.shape) > 1:
            data = data.mean(axis=1).astype("int16")

        # Create SpeechRecognition AudioData instance (int16 is 2 bytes sample width)
        audio_data = sr.AudioData(data.tobytes(), samplerate, 2)

        # Recognize speech using Google's free public STT API
        r = sr.Recognizer()
        text = r.recognize_google(audio_data)
        return text
    except Exception as e:
        print(f"Transcription failure: {e}")
        raise e


# ---------------------------------------------------------------------------
# Discord Bot
# ---------------------------------------------------------------------------


class YamiBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print(f"Discord Bot Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    async def on_message(self, message):
        # Don't reply to ourselves
        if message.author == self.user:
            return

        # Check if message is a DM or if the bot is mentioned in a server
        is_dm = isinstance(message.channel, discord.DMChannel)
        is_mentioned = self.user in message.mentions

        if is_dm or is_mentioned:
            # Clean up the mention from the message text if it was in a server
            content = message.content
            if is_mentioned:
                content = content.replace(f"<@{self.user.id}>", "").strip()

            # Check if there is a voice message / audio attachment
            if not content and message.attachments:
                attachment = message.attachments[0]
                if attachment.filename.endswith(
                    (".ogg", ".mp3", ".wav", ".m4a", ".flac")
                ):
                    try:
                        # Send typing indicator while transcribing
                        async with message.channel.typing():
                            audio_bytes = await attachment.read()
                            content = await asyncio.to_thread(
                                transcribe_audio_bytes, audio_bytes
                            )
                            print(f"Transcribed voice message: '{content}'")
                    except Exception as e:
                        print(f"Audio transcription error: {e}")
                        await message.reply(
                            "Sorry, I couldn't transcribe your voice message."
                        )
                        return

            if not content:
                content = "Hello"  # Default text if user just pings the bot

            # ---- Persist user message to conversation history ----
            user_id = str(message.author.id)
            channel_id = message.channel.id
            session_id = str(uuid.uuid4())

            append_to_history(channel_id, message.author.id, "user", content)

            # Send a typing indicator while AI is processing
            async with message.channel.typing():
                try:
                    # Load prior conversation history for this user in this channel
                    prior_messages = get_conversation_history(
                        channel_id, message.author.id
                    )

                    initial_state = {
                        "user_input": content,
                        "response": "",
                        "user_id": user_id,
                        "session_id": session_id,
                        "current_agent": "yami",
                        "memory_context": "",
                        "messages": list(prior_messages[:-1]),
                        "agent_memory": {},
                        "retrieved_context": [],
                        "extracted_memories": [],
                    }

                    # Call the LangGraph agent
                    result = await graph.ainvoke(initial_state)
                    response_text = result.get(
                        "response", "Captain Yami is currently unavailable."
                    )
                    if not response_text or not response_text.strip():
                        response_text = "Task completed successfully."

                    # Persist assistant response to history
                    append_to_history(
                        channel_id, message.author.id, "assistant", response_text
                    )

                    # Send response back to Discord
                    await message.reply(response_text)

                except Exception as e:
                    print(f"Error invoking graph: {e}")
                    await message.reply(f"An error occurred: {e}")


# Define intents (requires Message Content intent enabled in Discord Developer Portal)
intents = discord.Intents.default()
intents.message_content = True

# Create bot instance
bot = YamiBot(intents=intents)


async def start_discord_bot():
    """Starts the Discord bot connection"""
    try:
        await bot.start(settings.DISCORD_BOT_TOKEN)
    except Exception as e:
        print(f"Failed to start Discord bot: {e}")
