"""Tests for transcribing audio from URL."""

import httpx
import pytest
import respx

from soniox import SonioxClient
from soniox.exceptions import SonioxAPIError
from soniox.models import TranscriptionResponse


@respx.mock
def test_transcribe_url_sync() -> None:
    """Test synchronous URL transcription."""
    mock_response = {
        "result": {
            "text": "Transcribed from URL",
            "words": [],
            "confidence": 0.92,
            "audio_duration_ms": 2000,
        },
        "request_id": "req_456",
    }

    route = respx.post("https://api.soniox.com/transcribe").mock(
        return_value=httpx.Response(200, json=mock_response),
    )

    client = SonioxClient(api_key="test_key")
    response = client.transcribe_url("https://example.com/audio.mp3")

    assert isinstance(response, TranscriptionResponse)
    assert response.result.text == "Transcribed from URL"
    assert response.result.confidence == 0.92
    assert route.called


@respx.mock
@pytest.mark.asyncio
async def test_transcribe_url_async() -> None:
    """Test asynchronous URL transcription."""
    mock_response = {
        "result": {
            "text": "Async transcription",
            "words": [],
            "confidence": 0.93,
            "audio_duration_ms": 1500,
        },
        "request_id": "req_789",
    }

    route = respx.post("https://api.soniox.com/transcribe").mock(
        return_value=httpx.Response(200, json=mock_response),
    )

    client = SonioxClient(api_key="test_key")
    response = await client.transcribe_url_async(
        "https://example.com/audio.mp3",
    )

    assert isinstance(response, TranscriptionResponse)
    assert response.result.text == "Async transcription"
    assert route.called


@respx.mock
def test_transcribe_url_with_translation() -> None:
    """Test URL transcription with translation enabled."""
    mock_response = {
        "result": {
            "text": "Translated text",
            "words": [],
            "language": "es",
            "confidence": 0.88,
            "audio_duration_ms": 3000,
        },
        "request_id": "req_999",
    }

    respx.post("https://api.soniox.com/transcribe").mock(
        return_value=httpx.Response(200, json=mock_response),
    )

    client = SonioxClient(api_key="test_key")
    response = client.transcribe_url(
        "https://example.com/spanish_audio.mp3",
        enable_translation=True,
    )

    assert response.result.text == "Translated text"
    assert response.result.language == "es"


@respx.mock
def test_transcribe_url_invalid_url() -> None:
    """Test error handling for invalid URL."""
    respx.post("https://api.soniox.com/transcribe").mock(
        return_value=httpx.Response(
            400,
            json={"error": "Invalid audio URL"},
        ),
    )

    client = SonioxClient(api_key="test_key")
    with pytest.raises(SonioxAPIError):
        client.transcribe_url("not_a_valid_url")


@respx.mock
def test_transcribe_url_rate_limit() -> None:
    """Test rate limit error handling."""
    respx.post("https://api.soniox.com/transcribe").mock(
        return_value=httpx.Response(
            429,
            json={"error": "Rate limit exceeded"},
        ),
    )

    client = SonioxClient(api_key="test_key")
    with pytest.raises(SonioxAPIError) as exc_info:
        client.transcribe_url("https://example.com/audio.mp3")

    assert exc_info.value.status_code == 429
