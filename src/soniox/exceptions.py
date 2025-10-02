"""Exception classes for Soniox SDK."""


class SonioxError(Exception):
    """Base exception for all Soniox errors."""


class SonioxAuthenticationError(SonioxError):
    """Raised when authentication fails."""


class SonioxAPIError(SonioxError):
    """Raised when API returns an error response."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        """Initialize API error."""
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class SonioxRateLimitError(SonioxAPIError):
    """Raised when rate limit is exceeded."""
