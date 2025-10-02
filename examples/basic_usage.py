"""Basic usage examples for Soniox SDK."""

import logging

from soniox import SonioxClient

# Set up logging to see SDK logs
logging.basicConfig(level=logging.INFO)

# Initialize client with API key (or set SONIOX_API_KEY environment variable)
client = SonioxClient(api_key="your-api-key-here")


def transcribe_local_file(audio_file: str) -> None:
    """Transcribe a local audio file."""

    response = client.transcribe_file(
        audio_file,
        model="en_v2",
    )

    # Access word-level details
    for _word in response.result.words[:5]:  # First 5 words
        pass


def transcribe_from_url(audio_url: str) -> None:
    """Transcribe audio from a URL."""

    client.transcribe_url(audio_url)


def transcribe_with_diarization() -> None:
    """Transcribe with speaker diarization."""

    response = client.transcribe_file(
        "path/to/conversation.wav",
        enable_speaker_diarization=True,
    )

    # Group words by speaker
    speakers: dict[str, list[str]] = {}
    for word in response.result.words:
        speaker = word.speaker or "UNKNOWN"
        if speaker not in speakers:
            speakers[speaker] = []
        speakers[speaker].append(word.text)

    # Print each speaker's text
    for words in speakers.values():
        " ".join(words)


def transcribe_with_translation() -> None:
    """Transcribe and translate to English."""

    client.transcribe_url(
        "https://example.com/spanish_audio.mp3",
        enable_translation=True,
    )


if __name__ == "__main__":
    # Run examples (comment/uncomment as needed)
    try:
        transcribe_local_file(audio_file="path/to/your/audio.wav")
        transcribe_from_url(audio_url="https://example.com/audio.mp3")
        # transcribe_with_diarization()
        # transcribe_with_translation()
    except Exception:
        logging.exception("Basic usage error")
