"""Soniox Python SDK for Speech-to-Text API."""

from soniox.client import SonioxClient
from soniox.exceptions import (
    SonioxAPIError,
    SonioxAuthenticationError,
    SonioxError,
    SonioxRateLimitError,
)
from soniox.models import (
    StreamingChunk,
    TranscriptionRequest,
    TranscriptionResponse,
    TranscriptionResult,
    Word,
)

__version__ = "0.0.1"

__all__ = [
    "SonioxAPIError",
    "SonioxAuthenticationError",
    "SonioxClient",
    "SonioxError",
    "SonioxRateLimitError",
    "StreamingChunk",
    "TranscriptionRequest",
    "TranscriptionResponse",
    "TranscriptionResult",
    "Word",
]
