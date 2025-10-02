"""Tests for synchronous Soniox client methods."""

import pytest
from pytest_httpx import HTTPXMock

from src.soniox import SonioxClient
from src.soniox.exceptions import SonioxAPIError
from src.soniox.types import (
    TranscriptionConfig,
)


class TestSyncFileUpload:
    """Tests for synchronous file upload."""

    def test_upload_file_success(
        self,
        client: SonioxClient,
        audio_file: str,
        mock_file_upload_response: dict,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test successful file upload."""
        httpx_mock.add_response(
            url=f"{client.base_url}/v1/files",
            method="POST",
            json=mock_file_upload_response,
            status_code=201,
        )

        with client._get_client() as http_client:
            result = client._upload_file(
                audio_file,
                client=http_client,
            )

        assert result.id == "file_123"
        assert result.filename == "test.wav"
        assert result.size == 1024

    def test_upload_file_not_found(self, client: SonioxClient) -> None:
        """Test file upload with non-existent file."""
        with (
            pytest.raises(FileNotFoundError, match="Audio file not found"),
            client._get_client() as http_client,
        ):
            client._upload_file(
                "/path/to/nonexistent.wav",
                client=http_client,
            )


class TestSyncTranscribeFile:
    """Tests for synchronous file transcription."""

    def test_transcribe_file_success(
        self,
        client: SonioxClient,
        audio_file: str,
        mock_file_upload_response: dict,
        mock_transcription_job_response: dict,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test successful file transcription."""
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

        result = client.transcribe_file(audio_file)

        assert result.id == "550e8400-e29b-41d4-a716-446655440000"
        assert result.status == "completed"
        assert result.filename == "test.wav"
        assert hasattr(result, "model")

    def test_transcribe_file_with_config(
        self,
        client: SonioxClient,
        audio_file: str,
        mock_file_upload_response: dict,
        mock_transcription_job_response: dict,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test file transcription with custom config."""
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
        result = client.transcribe_file(audio_file, config=config)

        assert result.id == "550e8400-e29b-41d4-a716-446655440000"
        assert hasattr(result, "status")

    def test_transcribe_file_with_kwargs(
        self,
        client: SonioxClient,
        audio_file: str,
        mock_file_upload_response: dict,
        mock_transcription_job_response: dict,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test file transcription with kwargs."""
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

        result = client.transcribe_file(
            audio_file,
            model="stt-async-v2",
            enable_speaker_diarization=True,
        )

        assert hasattr(result, "id")
        assert hasattr(result, "status")

    def test_transcribe_file_not_found(self, client: SonioxClient) -> None:
        """Test transcription with non-existent file."""
        with pytest.raises(FileNotFoundError):
            client.transcribe_file("/path/to/nonexistent.wav")


class TestSyncGetTranscriptionJob:
    """Tests for getting transcription job."""

    def test_get_transcription_job_success(
        self,
        client: SonioxClient,
        mock_transcription_job_response: dict,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test successful get transcription job."""
        job_id = "550e8400-e29b-41d4-a716-446655440000"
        httpx_mock.add_response(
            url=f"{client.base_url}/v1/transcriptions/{job_id}",
            method="GET",
            json=mock_transcription_job_response,
            status_code=200,
        )

        result = client.get_transcription_job(job_id)

        assert result.id == job_id
        assert hasattr(result, "status")
        assert result.status == "completed"

    def test_get_transcription_job_not_found(
        self,
        client: SonioxClient,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test get transcription job with non-existent ID."""
        job_id = "550e8400-e29b-41d4-a716-446655440000"
        httpx_mock.add_response(
            url=f"{client.base_url}/v1/transcriptions/{job_id}",
            method="GET",
            json={"error": "Job not found"},
            status_code=404,
        )

        with pytest.raises((SonioxAPIError, Exception)) as exc_info:
            client.get_transcription_job(job_id)

        assert hasattr(exc_info.value, "status_code") or hasattr(
            exc_info.value,
            "response",
        )


class TestSyncGetTranscriptionResult:
    """Tests for getting transcription result."""

    def test_get_transcription_result_success(
        self,
        client: SonioxClient,
        mock_transcription_result_response: dict,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test successful get transcription result."""
        job_id = "550e8400-e29b-41d4-a716-446655440000"
        httpx_mock.add_response(
            url=f"{client.base_url}/v1/transcriptions/{job_id}/transcript",
            method="GET",
            json=mock_transcription_result_response,
            status_code=200,
        )

        result = client.get_transcription_result(job_id)

        assert result.id == job_id
        assert result.text == "Hello world"
        assert len(result.tokens) == 2
        assert hasattr(result, "tokens")

    def test_get_transcription_result_not_found(
        self,
        client: SonioxClient,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test get transcription result with non-existent ID."""
        job_id = "550e8400-e29b-41d4-a716-446655440000"
        httpx_mock.add_response(
            url=f"{client.base_url}/v1/transcriptions/{job_id}/transcript",
            method="GET",
            json={"error": "Transcript not found"},
            status_code=404,
        )

        with pytest.raises((SonioxAPIError, Exception)) as exc_info:
            client.get_transcription_result(job_id)

        assert hasattr(exc_info.value, "status_code") or hasattr(
            exc_info.value,
            "response",
        )


class TestSyncErrorHandling:
    """Tests for error handling in sync methods."""

    def test_handle_response_success(
        self,
        client: SonioxClient,
        httpx_mock: HTTPXMock,
    ) -> None:
        """Test _handle_response with success status."""
        httpx_mock.add_response(
            url=f"{client.base_url}/test",
            method="GET",
            json={"result": "success"},
            status_code=200,
        )

        with client._get_client() as http_client:
            response = http_client.get("/test")
            result = client._handle_response(response)

        assert result["result"] == "success"
