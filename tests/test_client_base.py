"""Tests for base Soniox client functionality."""

import pytest

from src.soniox import SonioxClient
from src.soniox.types import TranscriptionConfig


class TestClientInitialization:
    """Tests for client initialization."""

    def test_client_with_api_key(self, api_key: str) -> None:
        """Test client initialization with API key."""
        client = SonioxClient(api_key=api_key)
        assert client.api_key == api_key
        assert client.base_url == "https://api.soniox.com"
        assert client.timeout == 60.0

    def test_client_with_env_var(
        self,
        monkeypatch: pytest.MonkeyPatch,
        api_key: str,
    ) -> None:
        """Test client initialization with environment variable."""
        monkeypatch.setenv("SONIOX_API_KEY", api_key)
        client = SonioxClient()
        assert client.api_key == api_key

    def test_client_with_custom_base_url(self, api_key: str) -> None:
        """Test client initialization with custom base URL."""
        custom_url = "https://custom.api.com"
        client = SonioxClient(api_key=api_key, base_url=custom_url)
        assert client.base_url == custom_url

    def test_client_with_custom_timeout(self, api_key: str) -> None:
        """Test client initialization with custom timeout."""
        client = SonioxClient(api_key=api_key, timeout=120.0)
        assert client.timeout == 120.0


class TestClientHeaders:
    """Tests for client headers."""

    def test_get_headers(self, client: SonioxClient) -> None:
        """Test _get_headers returns correct authorization header."""
        headers = client._get_headers()
        assert "Authorization" in headers
        assert headers["Authorization"].startswith("Bearer ")
        assert headers["Authorization"] == f"Bearer {client.api_key}"


class TestClientConfig:
    """Tests for client configuration methods."""

    def test_get_config_with_file_id(self, client: SonioxClient) -> None:
        """Test _get_config with file_id."""
        config = TranscriptionConfig(model="stt-async-v2")
        result = client._get_config(file_id="file_123", config=config)
        assert result["file_id"] == "file_123"
        assert result["model"] == "stt-async-v2"
        assert "audio" not in result

    def test_get_config_with_audio_url(self, client: SonioxClient) -> None:
        """Test _get_config with audio_url."""
        config = TranscriptionConfig(model="stt-async-v2")
        result = client._get_config(
            audio_url="https://example.com/audio.wav",
            config=config,
        )
        assert result["audio_url"] == "https://example.com/audio.wav"
        assert result["model"] == "stt-async-v2"
        assert "file_id" not in result

    def test_get_config_with_additional_options(
        self,
        client: SonioxClient,
    ) -> None:
        """Test _get_config with additional configuration options."""
        config = TranscriptionConfig(
            model="stt-async-v2",
            enable_speaker_diarization=True,
            context="Medical context",
        )
        result = client._get_config(file_id="file_123", config=config)
        assert result["file_id"] == "file_123"
        assert result["enable_speaker_diarization"] is True
        assert result["context"] == "Medical context"


class TestClientContextManagers:
    """Tests for client context managers."""

    def test_get_client_context_manager(self, client: SonioxClient) -> None:
        """Test _get_client context manager."""
        with client._get_client() as http_client:
            assert http_client is not None
            assert "Authorization" in http_client.headers
            assert http_client.base_url == client.base_url

    async def test_get_async_client_context_manager(
        self,
        client: SonioxClient,
    ) -> None:
        """Test _get_async_client context manager."""
        async with client._get_async_client() as http_client:
            assert http_client is not None
            assert "Authorization" in http_client.headers
            assert str(http_client.base_url) == client.base_url
