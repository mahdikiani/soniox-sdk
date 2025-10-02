"""Tests for authentication."""


import pytest

from soniox import SonioxClient
from soniox.exceptions import SonioxAuthenticationError


def test_client_with_api_key_parameter() -> None:
    """Test client initialization with API key parameter."""
    client = SonioxClient(api_key="test_api_key")
    assert client.api_key == "test_api_key"


def test_client_with_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test client initialization with environment variable."""
    monkeypatch.setenv("SONIOX_API_KEY", "env_api_key")
    client = SonioxClient()
    assert client.api_key == "env_api_key"


def test_client_parameter_overrides_env(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that parameter API key overrides environment variable."""
    monkeypatch.setenv("SONIOX_API_KEY", "env_api_key")
    client = SonioxClient(api_key="param_api_key")
    assert client.api_key == "param_api_key"


def test_client_without_api_key_raises_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that missing API key raises authentication error."""
    monkeypatch.delenv("SONIOX_API_KEY", raising=False)
    with pytest.raises(SonioxAuthenticationError):
        SonioxClient()


def test_client_with_empty_api_key_raises_error() -> None:
    """Test that empty API key raises authentication error."""
    with pytest.raises(SonioxAuthenticationError):
        SonioxClient(api_key="")


def test_client_sets_auth_header() -> None:
    """Test that client sets correct authorization header."""
    client = SonioxClient(api_key="test_key")
    assert "api-key" in client._get_headers()
    assert client._get_headers()["api-key"] == "test_key"
