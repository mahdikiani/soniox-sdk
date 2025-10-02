"""Tests for Soniox exceptions."""

from typing import Never

import pytest

from src.soniox.exceptions import (
    SonioxAPIError,
    SonioxAuthenticationError,
    SonioxError,
    SonioxRateLimitError,
)


class TestSonioxError:
    """Tests for SonioxError base class."""

    def test_soniox_error_creation(self) -> None:
        """Test SonioxError can be created."""
        error = SonioxError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_soniox_error_raise(self) -> Never:
        """Test SonioxError can be raised and caught."""
        with pytest.raises(SonioxError, match="Test error"):
            raise SonioxError("Test error")


class TestSonioxAuthenticationError:
    """Tests for SonioxAuthenticationError."""

    def test_authentication_error_creation(self) -> None:
        """Test SonioxAuthenticationError can be created."""
        error = SonioxAuthenticationError("Authentication failed")
        assert str(error) == "Authentication failed"
        assert isinstance(error, SonioxError)

    def test_authentication_error_raise(self) -> Never:
        """Test SonioxAuthenticationError can be raised and caught."""
        with pytest.raises(
            SonioxAuthenticationError,
            match="Authentication failed",
        ):
            raise SonioxAuthenticationError("Authentication failed")

    def test_authentication_error_is_soniox_error(self) -> None:
        """Test SonioxAuthenticationError is a SonioxError."""
        error = SonioxAuthenticationError("Test")
        assert isinstance(error, SonioxError)
        assert isinstance(error, Exception)


class TestSonioxAPIError:
    """Tests for SonioxAPIError."""

    def test_api_error_basic(self) -> None:
        """Test SonioxAPIError with basic message."""
        error = SonioxAPIError("API error occurred")
        assert str(error) == "API error occurred"
        assert error.status_code is None
        assert error.response_body is None

    def test_api_error_with_status_code(self) -> None:
        """Test SonioxAPIError with status code."""
        error = SonioxAPIError("API error", status_code=500)
        assert str(error) == "API error"
        assert error.status_code == 500
        assert error.response_body is None

    def test_api_error_with_response_body(self) -> None:
        """Test SonioxAPIError with response body."""
        response_body = '{"error": "Internal server error"}'
        error = SonioxAPIError(
            "API error",
            status_code=500,
            response_body=response_body,
        )
        assert str(error) == "API error"
        assert error.status_code == 500
        assert error.response_body == response_body

    def test_api_error_is_soniox_error(self) -> None:
        """Test SonioxAPIError is a SonioxError."""
        error = SonioxAPIError("Test")
        assert isinstance(error, SonioxError)
        assert isinstance(error, Exception)

    def test_api_error_raise(self) -> Never:
        """Test SonioxAPIError can be raised and caught."""
        with pytest.raises(SonioxAPIError, match="API error"):
            raise SonioxAPIError("API error", status_code=404)


class TestSonioxRateLimitError:
    """Tests for SonioxRateLimitError."""

    def test_rate_limit_error_basic(self) -> None:
        """Test SonioxRateLimitError with basic message."""
        error = SonioxRateLimitError("Rate limit exceeded")
        assert str(error) == "Rate limit exceeded"
        assert error.status_code is None

    def test_rate_limit_error_with_status_code(self) -> None:
        """Test SonioxRateLimitError with status code."""
        error = SonioxRateLimitError("Rate limit exceeded", status_code=429)
        assert str(error) == "Rate limit exceeded"
        assert error.status_code == 429

    def test_rate_limit_error_is_api_error(self) -> None:
        """Test SonioxRateLimitError is a SonioxAPIError."""
        error = SonioxRateLimitError("Test")
        assert isinstance(error, SonioxAPIError)
        assert isinstance(error, SonioxError)
        assert isinstance(error, Exception)

    def test_rate_limit_error_raise(self) -> Never:
        """Test SonioxRateLimitError can be raised and caught."""
        with pytest.raises(SonioxRateLimitError, match="Rate limit"):
            raise SonioxRateLimitError("Rate limit exceeded", status_code=429)

    def test_rate_limit_error_caught_as_api_error(self) -> Never:
        """Test SonioxRateLimitError can be caught as SonioxAPIError."""
        with pytest.raises(SonioxAPIError):
            raise SonioxRateLimitError("Rate limit exceeded")
