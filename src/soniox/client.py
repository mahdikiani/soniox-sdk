"""Soniox API client implementation."""

import json
import logging
import os
from collections.abc import AsyncIterator
from pathlib import Path

import httpx
import websockets

from soniox.exceptions import (
    SonioxAPIError,
    SonioxAuthenticationError,
    SonioxRateLimitError,
)
from soniox.models import StreamingChunk, TranscriptionResponse

# Set up logger
logger = logging.getLogger("soniox")


class SonioxClient:
    """Soniox API client for speech-to-text operations."""

    BASE_URL = "https://api.soniox.com"
    WS_URL = "wss://api.soniox.com/ws"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        """Initialize Soniox client.

        Args:
            api_key: Soniox API key. If not provided,
                     reads from SONIOX_API_KEY env var.
            base_url: Base URL for API (default: https://api.soniox.com)
            timeout: Request timeout in seconds (default: 60.0)

        Raises:
            SonioxAuthenticationError: If API key is not provided or is empty.
        """
        self.api_key = api_key or os.getenv("SONIOX_API_KEY")

        if not self.api_key:
            msg = (
                "API key must be provided either as parameter "
                "or SONIOX_API_KEY environment variable"
            )
            logger.error(msg)
            raise SonioxAuthenticationError(msg)

        if not self.api_key.strip():
            msg = (
                "API key must be provided either as parameter "
                "or SONIOX_API_KEY environment variable"
            )
            logger.error("API key is empty")
            raise SonioxAuthenticationError(msg)

        self.base_url = base_url or self.BASE_URL
        self.timeout = timeout

        logger.info("Soniox client initialized")

    def _get_headers(self) -> dict[str, str]:
        """Get HTTP headers for API requests."""
        return {
            "api-key": self.api_key,
            "Content-Type": "application/json",
        }

    def _handle_response(self, response: httpx.Response) -> dict[str, object]:
        """Handle API response and raise appropriate errors.

        Args:
            response: HTTP response object

        Returns:
            Parsed JSON response

        Raises:
            SonioxRateLimitError: If rate limit is exceeded (429)
            SonioxAPIError: For other API errors
        """
        if response.status_code == 200:
            return response.json()

        error_body = response.text
        try:
            error_data = response.json()
            error_message = error_data.get("error", error_body)
        except Exception:
            error_message = error_body

        logger.error(
            "API error: status=%d, message=%s",
            response.status_code,
            error_message,
        )

        if response.status_code == 429:
            raise SonioxRateLimitError(
                error_message,
                status_code=response.status_code,
                response_body=error_body,
            )

        raise SonioxAPIError(
            error_message,
            status_code=response.status_code,
            response_body=error_body,
        )

    def transcribe_file(
        self,
        file_path: str,
        model: str = "en_v2",
        language: str | None = None,
        enable_speaker_diarization: bool = False,
        enable_translation: bool = False,
        **kwargs: object,
    ) -> TranscriptionResponse:
        """Transcribe audio file synchronously.

        Args:
            file_path: Path to audio file
            model: Model to use (default: en_v2)
            language: Language code (e.g., 'en', 'es')
            enable_speaker_diarization: Enable speaker diarization
            enable_translation: Enable translation to English
            **kwargs: Additional parameters

        Returns:
            TranscriptionResponse object

        Raises:
            FileNotFoundError: If file doesn't exist
            SonioxAPIError: If API returns an error
        """
        logger.info("Transcribing file: %s", file_path)

        # Check if file exists
        path = Path(file_path)
        if not path.exists():
            logger.error("File not found: %s", file_path)
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        # Read audio file
        audio_data = path.read_bytes()

        # Prepare request payload
        payload = {
            "audio": audio_data.hex(),  # Convert bytes to hex string
            "model": model,
            "enable_speaker_diarization": enable_speaker_diarization,
            "enable_translation": enable_translation,
        }

        if language:
            payload["language"] = language

        payload.update(kwargs)

        # Make request
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url}/transcribe",
                json=payload,
                headers=self._get_headers(),
            )

        result = self._handle_response(response)
        logger.info("Transcription completed successfully")
        return TranscriptionResponse(**result)

    async def transcribe_file_async(
        self,
        file_path: str,
        model: str = "en_v2",
        language: str | None = None,
        enable_speaker_diarization: bool = False,
        enable_translation: bool = False,
        **kwargs: object,
    ) -> TranscriptionResponse:
        """Transcribe audio file asynchronously.

        Args:
            file_path: Path to audio file
            model: Model to use (default: en_v2)
            language: Language code (e.g., 'en', 'es')
            enable_speaker_diarization: Enable speaker diarization
            enable_translation: Enable translation to English
            **kwargs: Additional parameters

        Returns:
            TranscriptionResponse object

        Raises:
            FileNotFoundError: If file doesn't exist
            SonioxAPIError: If API returns an error
        """
        logger.info("Transcribing file (async): %s", file_path)

        # Check if file exists
        path = Path(file_path)
        if not path.exists():
            logger.error("File not found: %s", file_path)
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        # Read audio file
        audio_data = path.read_bytes()

        # Prepare request payload
        payload = {
            "audio": audio_data.hex(),  # Convert bytes to hex string
            "model": model,
            "enable_speaker_diarization": enable_speaker_diarization,
            "enable_translation": enable_translation,
        }

        if language:
            payload["language"] = language

        payload.update(kwargs)

        # Make request
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/transcribe",
                json=payload,
                headers=self._get_headers(),
            )

        result = self._handle_response(response)
        logger.info("Transcription completed successfully (async)")
        return TranscriptionResponse(**result)

    def transcribe_url(
        self,
        audio_url: str,
        model: str = "en_v2",
        language: str | None = None,
        enable_speaker_diarization: bool = False,
        enable_translation: bool = False,
        **kwargs: object,
    ) -> TranscriptionResponse:
        """Transcribe audio from URL synchronously.

        Args:
            audio_url: URL to audio file
            model: Model to use (default: en_v2)
            language: Language code (e.g., 'en', 'es')
            enable_speaker_diarization: Enable speaker diarization
            enable_translation: Enable translation to English
            **kwargs: Additional parameters

        Returns:
            TranscriptionResponse object

        Raises:
            SonioxAPIError: If API returns an error
        """
        logger.info("Transcribing URL: %s", audio_url)

        # Prepare request payload
        payload = {
            "audio_url": audio_url,
            "model": model,
            "enable_speaker_diarization": enable_speaker_diarization,
            "enable_translation": enable_translation,
        }

        if language:
            payload["language"] = language

        payload.update(kwargs)

        # Make request
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                f"{self.base_url}/transcribe",
                json=payload,
                headers=self._get_headers(),
            )

        result = self._handle_response(response)
        logger.info("Transcription from URL completed successfully")
        return TranscriptionResponse(**result)

    async def transcribe_url_async(
        self,
        audio_url: str,
        model: str = "en_v2",
        language: str | None = None,
        enable_speaker_diarization: bool = False,
        enable_translation: bool = False,
        **kwargs: object,
    ) -> TranscriptionResponse:
        """Transcribe audio from URL asynchronously.

        Args:
            audio_url: URL to audio file
            model: Model to use (default: en_v2)
            language: Language code (e.g., 'en', 'es')
            enable_speaker_diarization: Enable speaker diarization
            enable_translation: Enable translation to English
            **kwargs: Additional parameters

        Returns:
            TranscriptionResponse object

        Raises:
            SonioxAPIError: If API returns an error
        """
        logger.info("Transcribing URL (async): %s", audio_url)

        # Prepare request payload
        payload = {
            "audio_url": audio_url,
            "model": model,
            "enable_speaker_diarization": enable_speaker_diarization,
            "enable_translation": enable_translation,
        }

        if language:
            payload["language"] = language

        payload.update(kwargs)

        # Make request
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/transcribe",
                json=payload,
                headers=self._get_headers(),
            )

        result = self._handle_response(response)
        logger.info("Transcription from URL completed successfully (async)")
        return TranscriptionResponse(**result)

    async def stream_transcribe(
        self,
        audio_stream: AsyncIterator[bytes] | None = None,
        model: str = "en_v2",
        sample_rate: int = 16000,
        enable_speaker_diarization: bool = False,
        **kwargs: object,
    ) -> AsyncIterator[StreamingChunk]:
        """Stream audio for real-time transcription.

        Args:
            audio_stream: Async iterator yielding audio chunks
            model: Model to use (default: en_v2)
            sample_rate: Audio sample rate in Hz (default: 16000)
            enable_speaker_diarization: Enable speaker diarization
            **kwargs: Additional parameters

        Yields:
            StreamingChunk objects with partial transcription results

        Raises:
            ConnectionError: If WebSocket connection fails
        """
        logger.info("Starting streaming transcription")

        # Prepare WebSocket URL with parameters
        ws_url = f"{self.WS_URL}/stream"

        # Prepare config message
        config = {
            "model": model,
            "sample_rate": sample_rate,
            "enable_speaker_diarization": enable_speaker_diarization,
            **kwargs,
        }

        try:
            async with websockets.connect(
                ws_url,
                extra_headers={"api-key": self.api_key},
            ) as websocket:
                # Send configuration
                await websocket.send(json.dumps(config))
                logger.debug("Sent configuration to WebSocket")

                # Send audio chunks if provided
                if audio_stream:
                    async for audio_chunk in audio_stream:
                        await websocket.send(audio_chunk)
                        logger.debug(
                            "Sent audio chunk: %d bytes",
                            len(audio_chunk),
                        )

                # Receive transcription results
                while True:
                    try:
                        message = await websocket.recv()
                        data = json.loads(message)
                        chunk = StreamingChunk(**data)
                        logger.debug("Received chunk: %s", chunk.text)
                        yield chunk
                    except websockets.exceptions.ConnectionClosed:
                        logger.info("WebSocket connection closed")
                        break

        except Exception:
            logger.exception("Streaming error")
            raise
