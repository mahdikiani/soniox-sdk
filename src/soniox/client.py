"""Soniox API client implementation."""

import logging
import mimetypes
import os
from collections.abc import AsyncGenerator, Generator
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path

import httpx

from .exceptions import (
    SonioxAPIError,
    SonioxAuthenticationError,
    SonioxRateLimitError,
)
from .types import (
    FileUploadResponse,
    TranscriptionConfig,
    TranscriptionJob,
    TranscriptionResult,
)

# Set up logger
logger = logging.getLogger("soniox")


class _BaseSonioxClient:
    """Base class for Soniox API clients."""

    BASE_URL = "https://api.soniox.com"
    WS_URL = "wss://stt-rt.soniox.com/transcribe-websocket"

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 60.0,
        **kwargs: object,
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
        return {"Authorization": f"Bearer {self.api_key}"}

    def _get_config(
        self,
        audio_url: str | None = None,
        file_id: str | None = None,
        *,
        config: TranscriptionConfig,
    ) -> dict:
        config_dict = config.model_dump()
        config_dict.update(
            {"audio_url": audio_url} if audio_url else {"file_id": file_id},
        )
        return config_dict

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
        if response.status_code in [200, 201]:
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

    @contextmanager
    def _get_client(self) -> Generator[httpx.Client]:
        with httpx.Client(
            timeout=self.timeout,
            headers=self._get_headers(),
            base_url=self.base_url,
        ) as client:
            yield client

    @asynccontextmanager
    async def _get_async_client(self) -> AsyncGenerator[httpx.AsyncClient]:
        async with httpx.AsyncClient(
            timeout=self.timeout,
            headers=self._get_headers(),
            base_url=self.base_url,
        ) as client:
            yield client


class _SonioxClientSync(_BaseSonioxClient):
    """Soniox API client for speech-to-text operations."""

    def _upload_file(
        self,
        file_path: str,
        client: httpx.Client,
    ) -> FileUploadResponse:
        # Check if file exists
        filepath = Path(file_path)
        if not filepath.exists():
            logger.error("File not found: %s", file_path)
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        mime_type = mimetypes.guess_type(filepath.name)[0]
        with open(filepath, "rb") as f:
            files = {"file": (filepath.name, f, mime_type)}
            res = client.post(f"{self.base_url}/v1/files", files=files)
            # res.raise_for_status()
            file_response = FileUploadResponse(**res.json())
        logger.info("File ID: %s", file_response.id)
        return file_response

    def transcribe_file(
        self,
        file_path: str,
        config: TranscriptionConfig | None = None,
        **kwargs: object,
    ) -> TranscriptionJob:
        """Transcribe audio file synchronously.

        Args:
            file_path: Path to audio file
            model: Model to use (default: stt-async-preview)
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
        if not config:
            config = TranscriptionConfig(**kwargs)

        with self._get_client() as client:
            file_response = self._upload_file(file_path, client=client)

            # Prepare request payload
            payload = self._get_config(file_id=file_response.id, config=config)

            # Make request
            response = client.post("/v1/transcriptions", json=payload)
            # response.raise_for_status()
            result = self._handle_response(response)

        logger.info("Transcription completed successfully")
        return TranscriptionJob(**result)

    def transcribe_url(
        self,
        url: str,
        config: TranscriptionConfig | None = None,
        **kwargs: object,
    ) -> TranscriptionJob:
        """Transcribe audio file synchronously.

        Args:
            url: URL to audio file
            model: Model to use (default: stt-async-preview)
            language: Language code (e.g., 'en', 'es')
            enable_speaker_diarization: Enable speaker diarization
            enable_translation: Enable translation to English
            **kwargs: Additional parameters

        Returns:
            TranscriptionResponse object

        Raises:
            SonioxAPIError: If API returns an error
        """
        logger.info("Transcribing file: %s", url)
        if not config:
            config = TranscriptionConfig(**kwargs)

        with self._get_client() as client:
            # Prepare request payload
            payload = self._get_config(audio_url=url, config=config)

            # Make request
            response = client.post("/v1/transcriptions", json=payload)
            # response.raise_for_status()
            result = self._handle_response(response)

        logger.info("Transcription completed successfully")
        return TranscriptionJob(**result)

    def get_transcription_job(self, job_id: str) -> TranscriptionJob:
        """Get transcription job."""

        with self._get_client() as client:
            response = client.get(f"/v1/transcriptions/{job_id}")
            # response.raise_for_status()
            result = self._handle_response(response)
        return TranscriptionJob(**result)

    def get_transcription_result(self, job_id: str) -> TranscriptionResult:
        """Get transcription job."""

        with self._get_client() as client:
            response = client.get(f"/v1/transcriptions/{job_id}/transcript")
            # response.raise_for_status()
            result = self._handle_response(response)
        return TranscriptionResult(**result)


class _SonioxClientAsync(_BaseSonioxClient):
    """Soniox API client for speech-to-text operations asynchronously."""

    async def _upload_file_async(
        self,
        file_path: str,
        client: httpx.AsyncClient,
    ) -> FileUploadResponse:
        # Check if file exists
        filepath = Path(file_path)
        if not filepath.exists():
            logger.error("File not found: %s", file_path)
            raise FileNotFoundError(f"Audio file not found: {file_path}")

        mime_type = mimetypes.guess_type(filepath.name)[0]
        with open(filepath, "rb") as f:  # noqa: ASYNC230
            files = {"file": (filepath.name, f, mime_type)}
            res = await client.post(f"{self.base_url}/v1/files", files=files)
            # res.raise_for_status()
            file_response = FileUploadResponse(**res.json())
        logger.info("File ID: %s", file_response.id)
        return file_response

    async def transcribe_file_async(
        self,
        file_path: str,
        config: TranscriptionConfig | None = None,
        **kwargs: object,
    ) -> TranscriptionJob:
        """Transcribe audio file synchronously.

        Args:
            file_path: Path to audio file
            model: Model to use (default: stt-async-preview)
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
        if not config:
            config = TranscriptionConfig(**kwargs)

        async with self._get_async_client() as client:
            file_response = await self._upload_file_async(
                file_path,
                client=client,
            )

            # Prepare request payload
            payload = self._get_config(file_id=file_response.id, config=config)

            # Make request
            response = await client.post("/v1/transcriptions", json=payload)
            # response.raise_for_status()
            result = self._handle_response(response)

        logger.info("Transcription completed successfully")
        return TranscriptionJob(**result)

    async def transcribe_url_async(
        self,
        url: str,
        config: TranscriptionConfig | None = None,
        **kwargs: object,
    ) -> TranscriptionJob:
        """Transcribe audio file synchronously."""
        logger.info("Transcribing file: %s", url)
        if not config:
            config = TranscriptionConfig(**kwargs)

        async with self._get_async_client() as client:
            payload = self._get_config(audio_url=url, config=config)

            response = await client.post("/v1/transcriptions", json=payload)
            # response.raise_for_status()
            result = self._handle_response(response)

        logger.info("Transcription completed successfully")
        return TranscriptionJob(**result)

    async def get_transcription_job_async(
        self,
        job_id: str,
    ) -> TranscriptionJob:
        """Get transcription job."""

        async with self._get_async_client() as client:
            response = await client.get(f"/v1/transcriptions/{job_id}")
            # response.raise_for_status()
            result = self._handle_response(response)
        return TranscriptionJob(**result)

    async def get_transcription_result_async(
        self,
        job_id: str,
    ) -> TranscriptionResult:
        """Get transcription job."""

        async with self._get_async_client() as client:
            response = await client.get(
                f"/v1/transcriptions/{job_id}/transcript",
            )
            # response.raise_for_status()
            result = self._handle_response(response)
        return TranscriptionResult(**result)


class SonioxClient(
    _SonioxClientSync,
    _SonioxClientAsync,
):
    """Soniox API client."""
