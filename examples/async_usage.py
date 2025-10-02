"""Async usage examples for Soniox SDK."""

import asyncio
import logging

from soniox import SonioxClient

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize client
client = SonioxClient(api_key="your-api-key-here")


async def transcribe_file_async(audio_file: str) -> None:
    """Transcribe a file asynchronously."""
    logging.info("\n=== Async File Transcription ===")

    response = await client.transcribe_file_async(audio_file)

    logging.info("Text: %s", response.result.text)
    logging.info("Confidence: %s", response.result.confidence)


async def transcribe_url_async(audio_url: str) -> None:
    """Transcribe from URL asynchronously."""
    logging.info("\n=== Async URL Transcription ===")

    response = await client.transcribe_url_async(audio_url)

    logging.info("Text: %s", response.result.text)


async def transcribe_multiple_files() -> None:
    """Transcribe multiple files concurrently."""
    logging.info("\n=== Transcribing Multiple Files Concurrently ===")

    files = [
        "path/to/audio1.wav",
        "path/to/audio2.wav",
        "path/to/audio3.wav",
    ]

    # Transcribe all files concurrently
    tasks = [client.transcribe_file_async(file) for file in files]
    responses = await asyncio.gather(*tasks)

    for i, response in enumerate(responses, 1):
        logging.info("\nFile %s: %s...", i, response.result.text[:50])


async def main() -> None:
    """Run async examples."""
    try:
        await transcribe_file_async(audio_file="path/to/your/audio.wav")
        await transcribe_url_async()
        # await transcribe_multiple_files()
        logging.info("\nAsync examples completed!")
    except Exception as e:
        logging.info("Error: %s", e)


if __name__ == "__main__":
    asyncio.run(main())
