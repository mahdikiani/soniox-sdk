"""Real-time streaming transcription example."""

import asyncio
import logging
from collections.abc import AsyncIterator

import aiofiles

from soniox import SonioxClient

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize client
client = SonioxClient(api_key="your-api-key-here")


async def audio_file_generator(file_path: str) -> AsyncIterator[bytes]:
    """Generate audio chunks from a file.

    Args:
        file_path: Path to audio file

    Yields:
        Audio chunks as bytes
    """
    chunk_size = 4096  # 4KB chunks

    async with aiofiles.open(file_path, "rb") as f:
        while chunk := await f.read(chunk_size):
            yield chunk
            # Simulate real-time streaming with small delay
            await asyncio.sleep(0.1)


async def stream_from_file() -> None:
    """Stream transcription from an audio file."""

    audio_gen = audio_file_generator("path/to/audio.raw")

    async for chunk in client.stream_transcribe(
        audio_stream=audio_gen,
        model="en_v2",
        sample_rate=16000,
    ):
        # Print partial results

        if chunk.is_final:
            pass


async def stream_with_diarization() -> None:
    """Stream with speaker diarization."""

    audio_gen = audio_file_generator("path/to/conversation.raw")

    current_speaker = None

    async for chunk in client.stream_transcribe(
        audio_stream=audio_gen,
        model="en_v2",
        sample_rate=16000,
        enable_speaker_diarization=True,
    ):
        if chunk.words:
            for word in chunk.words:
                if word.speaker != current_speaker:
                    current_speaker = word.speaker


async def stream_basic() -> None:
    """Basic streaming without audio input (for testing)."""

    try:
        async for chunk in client.stream_transcribe(
            model="en_v2",
            sample_rate=16000,
        ):
            if chunk.is_final:
                break
    except Exception:
        logging.exception("Streaming error")


async def main() -> None:
    """Run streaming examples."""
    try:
        # Uncomment the example you want to run
        await stream_from_file()
        # await stream_with_diarization()
        # await stream_basic()
    except Exception:
        logging.exception("Streaming error")


if __name__ == "__main__":
    asyncio.run(main())
