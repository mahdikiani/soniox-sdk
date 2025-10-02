"""Tests for transcribing audio files."""

from pathlib import Path

import httpx
import pytest
import respx

from soniox import SonioxClient
from soniox.exceptions import SonioxAPIError
from soniox.models import TranscriptionResponse


@pytest.fixture
def mock_audio_file(tmp_path: Path) -> Path:
    """Create a mock audio file."""
    audio_file = tmp_path / "test_audio.wav"
    audio_file.write_bytes(b"fake audio data")
    return audio_file


@respx.mock
def test_transcribe_file_sync(mock_audio_file: Path) -> None:
    """Test synchronous file transcription."""
    # Mock API response
    mock_response = {
        "result": {
            "text": "Hello world",
            "words": [],
            "confidence": 0.95,
            "audio_duration_ms": 1000,
        },
        "request_id": "req_123",
    }

    route = respx.post("https://api.soniox.com/transcribe").mock(
        return_value=httpx.Response(200, json=mock_response),
    )

    client = SonioxClient(api_key="test_key")
    response = client.transcribe_file(str(mock_audio_file))

    assert isinstance(response, TranscriptionResponse)
    assert response.result.text == "Hello world"
    assert response.result.confidence == 0.95
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_transcribe_file_async(mock_audio_file: Path) -> None:
    """Test asynchronous file transcription."""
    mock_response = {
        "result": {
            "text": "Hello world",
            "words": [],
            "confidence": 0.95,
            "audio_duration_ms": 1000,
        },
        "request_id": "req_123",
    }

    route = respx.post("https://api.soniox.com/transcribe").mock(
        return_value=httpx.Response(200, json=mock_response),
    )

    client = SonioxClient(api_key="test_key")
    response = await client.transcribe_file_async(str(mock_audio_file))

    assert isinstance(response, TranscriptionResponse)
    assert response.result.text == "Hello world"
    assert route.called


@respx.mock
def test_transcribe_file_with_options(mock_audio_file: Path) -> None:
    """Test file transcription with custom options."""
    mock_response = {
        "result": {
            "text": "Hello world",
            "words": [
                {
                    "text": "Hello",
                    "start_ms": 0,
                    "duration_ms": 500,
                    "confidence": 0.98,
                    "speaker": "SPEAKER_1",
                },
            ],
            "confidence": 0.95,
            "audio_duration_ms": 1000,
        },
        "request_id": "req_123",
    }

    respx.post("https://api.soniox.com/transcribe").mock(
        return_value=httpx.Response(200, json=mock_response),
    )

    client = SonioxClient(api_key="test_key")
    response = client.transcribe_file(
        str(mock_audio_file),
        model="en_v2",
        enable_speaker_diarization=True,
    )

    assert response.result.text == "Hello world"
    assert len(response.result.words) == 1
    assert response.result.words[0].speaker == "SPEAKER_1"


@respx.mock
def test_transcribe_file_error_handling(mock_audio_file: Path) -> None:
    """Test error handling for file transcription."""
    respx.post("https://api.soniox.com/transcribe").mock(
        return_value=httpx.Response(
            400,
            json={"error": "Invalid audio format"},
        ),
    )

    client = SonioxClient(api_key="test_key")
    with pytest.raises(SonioxAPIError):
        client.transcribe_file(str(mock_audio_file))


def test_transcribe_file_not_found() -> None:
    """Test error when file doesn't exist."""
    client = SonioxClient(api_key="test_key")
    with pytest.raises(FileNotFoundError):
        client.transcribe_file("/nonexistent/file.wav")
