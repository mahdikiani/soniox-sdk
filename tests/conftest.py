"""Test fixtures for Soniox tests."""

import pytest

from src.soniox import SonioxClient


@pytest.fixture
def api_key() -> str:
    """Return a test API key."""
    return "test_api_key_12345"


@pytest.fixture
def mock_env_api_key(monkeypatch: pytest.MonkeyPatch, api_key: str) -> None:
    """Set SONIOX_API_KEY environment variable."""
    monkeypatch.setenv("SONIOX_API_KEY", api_key)


@pytest.fixture
def client(api_key: str) -> SonioxClient:
    """Return a Soniox client instance."""
    return SonioxClient(api_key=api_key)


@pytest.fixture
def mock_file_upload_response() -> dict:
    """Return mock file upload response."""
    return {
        "id": "file_123",
        "filename": "test.wav",
        "size": 1024,
        "created_at": "2024-01-01T00:00:00Z",
        "client_reference_id": None,
    }


@pytest.fixture
def mock_transcription_job_response() -> dict:
    """Return mock transcription job response."""
    return {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "completed",
        "created_at": "2024-01-01T00:00:00Z",
        "model": "stt-async-preview",
        "file_id": "file_123",
        "filename": "test.wav",
        "audio_duration_ms": 5000,
        "language_hints": None,
        "enable_language_identification": False,
        "enable_speaker_diarization": False,
        "context": None,
        "client_reference_id": None,
        "webhook_url": None,
        "webhook_auth_header_name": None,
        "webhook_auth_header_value": None,
        "audio_url": None,
        "error_message": None,
        "webhook_status_code": None,
    }


@pytest.fixture
def mock_transcription_result_response() -> dict:
    """Return mock transcription result response."""
    return {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "text": "Hello world",
        "tokens": [
            {
                "text": "Hello",
                "start_ms": 0,
                "end_ms": 500,
                "confidence": 0.99,
                "speaker": None,
            },
            {
                "text": "world",
                "start_ms": 500,
                "end_ms": 1000,
                "confidence": 0.98,
                "speaker": None,
            },
        ],
    }


@pytest.fixture
def audio_file(tmp_path: pytest.TempPathFactory) -> str:
    """Create a temporary audio file for testing."""
    audio_path = tmp_path / "test_audio.wav"
    # Create a simple WAV file header
    wav_header = b"RIFF"
    wav_header += (36).to_bytes(4, "little")  # File size - 8
    wav_header += b"WAVE"
    wav_header += b"fmt "
    wav_header += (16).to_bytes(4, "little")  # Subchunk1Size
    wav_header += (1).to_bytes(2, "little")  # AudioFormat (PCM)
    wav_header += (1).to_bytes(2, "little")  # NumChannels
    wav_header += (16000).to_bytes(4, "little")  # SampleRate
    wav_header += (32000).to_bytes(4, "little")  # ByteRate
    wav_header += (2).to_bytes(2, "little")  # BlockAlign
    wav_header += (16).to_bytes(2, "little")  # BitsPerSample
    wav_header += b"data"
    wav_header += (0).to_bytes(4, "little")  # Subchunk2Size

    audio_path.write_bytes(wav_header)
    return str(audio_path)
