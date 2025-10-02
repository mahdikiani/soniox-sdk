"""Tests for asynchronous Soniox client methods."""

import pytest
from pytest_httpx import HTTPXMock

from src.soniox import SonioxClient
from src.soniox.exceptions import SonioxAPIError
from src.soniox.types import (
    TranscriptionConfig,
)


class TestAsyncFileUpload:
    """Tests for asynchronous file upload."""

    async def test_upload_file_async_success(
        self,
        client: SonioxClient,
        audio_file: str,
        mock_file_upload_response: dict,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test successful async file upload."""
        httpx_mock.add_response(
            url=f"{client.base_url}/v1/files",
            method="POST",
            json=mock_file_upload_response,
            status_code=201,
        )

        async with client._get_async_client() as http_client:
            result = await client._upload_file_async(
                audio_file,
                client=http_client,
            )

        assert result.id == "file_123"
        assert result.filename == "test.wav"
        assert result.size == 1024

    async def test_upload_file_async_not_found(
        self,
        client: SonioxClient,
    ) -> None:
        """Test async file upload with non-existent file."""
        with pytest.raises(FileNotFoundError, match="Audio file not found"):
            async with client._get_async_client() as http_client:
                await client._upload_file_async(
                    "/path/to/nonexistent.wav",
                    client=http_client,
                )


class TestAsyncTranscribeFile:
    """Tests for asynchronous file transcription."""

    async def test_transcribe_file_async_success(
        self,
        client: SonioxClient,
        audio_file: str,
        mock_file_upload_response: dict,
        mock_transcription_job_response: dict,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test successful async file transcription."""
        # Mock file upload
        httpx_mock.add_response(
            url=f"{client.base_url}/v1/files",
            method="POST",
            json=mock_file_upload_response,
            status_code=201,
        )

        # Mock transcription request
        httpx_mock.add_response(
            url=f"{client.base_url}/v1/transcriptions",
            method="POST",
            json=mock_transcription_job_response,
            status_code=201,
        )

        result = await client.transcribe_file_async(audio_file)

        assert result.id == "550e8400-e29b-41d4-a716-446655440000"
        assert result.status == "completed"
        assert result.filename == "test.wav"
        assert hasattr(result, "model")

    async def test_transcribe_file_async_with_config(
        self,
        client: SonioxClient,
        audio_file: str,
        mock_file_upload_response: dict,
        mock_transcription_job_response: dict,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test async file transcription with custom config."""
        # Mock file upload
        httpx_mock.add_response(
            url=f"{client.base_url}/v1/files",
            method="POST",
            json=mock_file_upload_response,
            status_code=201,
        )

        # Mock transcription request
        httpx_mock.add_response(
            url=f"{client.base_url}/v1/transcriptions",
            method="POST",
            json=mock_transcription_job_response,
            status_code=201,
        )

        config = TranscriptionConfig(
            model="stt-async-v2",
            enable_speaker_diarization=True,
        )
        result = await client.transcribe_file_async(audio_file, config=config)

        assert result.id == "550e8400-e29b-41d4-a716-446655440000"
        assert hasattr(result, "status")

    async def test_transcribe_file_async_with_kwargs(
        self,
        client: SonioxClient,
        audio_file: str,
        mock_file_upload_response: dict,
        mock_transcription_job_response: dict,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test async file transcription with kwargs."""
        # Mock file upload
        httpx_mock.add_response(
            url=f"{client.base_url}/v1/files",
            method="POST",
            json=mock_file_upload_response,
            status_code=201,
        )

        # Mock transcription request
        httpx_mock.add_response(
            url=f"{client.base_url}/v1/transcriptions",
            method="POST",
            json=mock_transcription_job_response,
            status_code=201,
        )

        result = await client.transcribe_file_async(
            audio_file,
            model="stt-async-v2",
            enable_speaker_diarization=True,
        )

        assert hasattr(result, "id")
        assert hasattr(result, "status")

    async def test_transcribe_file_async_not_found(
        self,
        client: SonioxClient,
    ) -> None:
        """Test async transcription with non-existent file."""
        with pytest.raises(FileNotFoundError):
            await client.transcribe_file_async("/path/to/nonexistent.wav")


class TestAsyncGetTranscriptionJob:
    """Tests for getting transcription job asynchronously."""

    async def test_get_transcription_job_async_success(
        self,
        client: SonioxClient,
        mock_transcription_job_response: dict,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test successful get transcription job async."""
        job_id = "550e8400-e29b-41d4-a716-446655440000"
        httpx_mock.add_response(
            url=f"{client.base_url}/v1/transcriptions/{job_id}",
            method="GET",
            json=mock_transcription_job_response,
            status_code=200,
        )

        result = await client.get_transcription_job_async(job_id)

        assert result.id == job_id
        assert hasattr(result, "status")
        assert result.status == "completed"

    async def test_get_transcription_job_async_not_found(
        self,
        client: SonioxClient,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test get transcription job async with non-existent ID."""
        job_id = "550e8400-e29b-41d4-a716-446655440000"
        httpx_mock.add_response(
            url=f"{client.base_url}/v1/transcriptions/{job_id}",
            method="GET",
            json={"error": "Job not found"},
            status_code=404,
        )

        with pytest.raises((SonioxAPIError, Exception)) as exc_info:
            await client.get_transcription_job_async(job_id)

        assert hasattr(exc_info.value, "status_code") or hasattr(
            exc_info.value,
            "response",
        )


class TestAsyncGetTranscriptionResult:
    """Tests for getting transcription result asynchronously."""

    async def test_get_transcription_result_async_success(
        self,
        client: SonioxClient,
        mock_transcription_result_response: dict,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test successful get transcription result async."""
        job_id = "550e8400-e29b-41d4-a716-446655440000"
        httpx_mock.add_response(
            url=f"{client.base_url}/v1/transcriptions/{job_id}/transcript",
            method="GET",
            json=mock_transcription_result_response,
            status_code=200,
        )

        result = await client.get_transcription_result_async(job_id)

        assert result.id == job_id
        assert result.text == "Hello world"
        assert len(result.tokens) == 2
        assert hasattr(result, "tokens")

    async def test_get_transcription_result_async_not_found(
        self,
        client: SonioxClient,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test get transcription result async with non-existent ID."""
        job_id = "550e8400-e29b-41d4-a716-446655440000"
        httpx_mock.add_response(
            url=f"{client.base_url}/v1/transcriptions/{job_id}/transcript",
            method="GET",
            json={"error": "Transcript not found"},
            status_code=404,
        )

        with pytest.raises((SonioxAPIError, Exception)) as exc_info:
            await client.get_transcription_result_async(job_id)

        assert hasattr(exc_info.value, "status_code") or hasattr(
            exc_info.value,
            "response",
        )


class TestAsyncErrorHandling:
    """Tests for error handling in async methods."""

    async def test_async_api_error_propagation(
        self,
        client: SonioxClient,
        audio_file: str,
        mock_file_upload_response: dict,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test API error propagation in async methods."""
        # Mock file upload
        httpx_mock.add_response(
            url=f"{client.base_url}/v1/files",
            method="POST",
            json=mock_file_upload_response,
            status_code=201,
        )

        # Mock transcription request with error
        httpx_mock.add_response(
            url=f"{client.base_url}/v1/transcriptions",
            method="POST",
            json={"error": "Invalid request"},
            status_code=400,
        )

        with pytest.raises((SonioxAPIError, Exception)) as exc_info:
            await client.transcribe_file_async(audio_file)

        assert "400" in str(exc_info.value) or "Invalid request" in str(
            exc_info.value,
        )
