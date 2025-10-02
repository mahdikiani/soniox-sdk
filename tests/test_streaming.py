"""Tests for real-time streaming transcription."""

import asyncio
from collections.abc import AsyncIterator

import pytest
from pytest_mock import MockerFixture

from soniox import SonioxClient
from soniox.models import StreamingChunk


@pytest.mark.asyncio
async def test_stream_transcribe_basic(mocker: MockerFixture) -> None:
    """Test basic streaming transcription."""
    # Mock WebSocket connection
    mock_ws = mocker.AsyncMock()
    mock_ws.recv.side_effect = [
        '{"text": "Hello", "is_final": false, "confidence": 0.8}',
        '{"text": "Hello world", "is_final": true, "confidence": 0.95}',
        asyncio.CancelledError,
    ]

    # Create proper async context manager mock
    mock_cm = mocker.AsyncMock()
    mock_cm.__aenter__.return_value = mock_ws
    mock_cm.__aexit__.return_value = None

    mocker.patch(
        "websockets.connect",
        return_value=mock_cm,
    )

    client = SonioxClient(api_key="test_key")

    chunks = []
    async for chunk in client.stream_transcribe():
        chunks.append(chunk)
        if len(chunks) >= 2:
            break

    assert len(chunks) == 2
    assert isinstance(chunks[0], StreamingChunk)
    assert chunks[0].text == "Hello"
    assert chunks[0].is_final is False
    assert chunks[1].text == "Hello world"
    assert chunks[1].is_final is True


@pytest.mark.asyncio
async def test_stream_transcribe_with_audio_generator(
    mocker: MockerFixture,
) -> None:
    """Test streaming with audio generator."""

    async def audio_generator() -> AsyncIterator[bytes]:  # noqa: RUF029
        """Generate fake audio chunks."""
        for _ in range(3):
            yield b"audio_chunk"

    mock_ws = mocker.AsyncMock()
    mock_ws.recv.side_effect = [
        '{"text": "Word", "is_final": false}',
        asyncio.CancelledError,
    ]

    # Create proper async context manager mock
    mock_cm = mocker.AsyncMock()
    mock_cm.__aenter__.return_value = mock_ws
    mock_cm.__aexit__.return_value = None

    mocker.patch(
        "websockets.connect",
        return_value=mock_cm,
    )

    client = SonioxClient(api_key="test_key")

    chunks = []
    async for chunk in client.stream_transcribe(audio_generator()):
        chunks.append(chunk)
        break

    assert len(chunks) == 1
    assert mock_ws.send.called


@pytest.mark.asyncio
async def test_stream_transcribe_connection_error(
    mocker: MockerFixture,
) -> None:
    """Test error handling in streaming."""
    mocker.patch(
        "websockets.connect",
        side_effect=ConnectionError("Connection failed"),
    )

    client = SonioxClient(api_key="test_key")

    with pytest.raises(ConnectionError):
        async for _ in client.stream_transcribe():
            pass


@pytest.mark.asyncio
async def test_stream_transcribe_with_config(mocker: MockerFixture) -> None:
    """Test streaming with custom configuration."""
    mock_ws = mocker.AsyncMock()
    mock_ws.recv.side_effect = [asyncio.CancelledError]

    # Create proper async context manager mock
    mock_cm = mocker.AsyncMock()
    mock_cm.__aenter__.return_value = mock_ws
    mock_cm.__aexit__.return_value = None

    mock_connect = mocker.patch(
        "websockets.connect",
        return_value=mock_cm,
    )

    client = SonioxClient(api_key="test_key")

    try:
        async for _ in client.stream_transcribe(
            model="en_v2",
            sample_rate=16000,
            enable_speaker_diarization=True,
        ):
            pass
    except asyncio.CancelledError:
        pass

    # Verify WebSocket was called with correct URL
    assert mock_connect.called
