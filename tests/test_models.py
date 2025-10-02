"""Tests for Soniox models."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.soniox.languages import Language
from src.soniox.types import (
    AudioFormat,
    FileUploadResponse,
    StreamingChunk,
    Token,
    TranscriptionConfig,
    TranscriptionConfigRealTime,
    TranscriptionJob,
    TranscriptionJobStatus,
    TranscriptionResult,
    TranslationConfig,
)


class TestFileUploadResponse:
    """Tests for FileUploadResponse model."""

    def test_file_upload_response_valid(self) -> None:
        """Test FileUploadResponse with valid data."""
        data = {
            "id": "file_123",
            "filename": "test.wav",
            "size": 1024,
            "created_at": "2024-01-01T00:00:00Z",
        }
        response = FileUploadResponse(**data)
        assert response.id == "file_123"
        assert response.filename == "test.wav"
        assert response.size == 1024
        assert response.client_reference_id is None

    def test_file_upload_response_with_reference_id(self) -> None:
        """Test FileUploadResponse with client_reference_id."""
        data = {
            "id": "file_123",
            "filename": "test.wav",
            "size": 1024,
            "created_at": "2024-01-01T00:00:00Z",
            "client_reference_id": "ref_123",
        }
        response = FileUploadResponse(**data)
        assert response.client_reference_id == "ref_123"


class TestTranscriptionConfig:
    """Tests for TranscriptionConfig model."""

    def test_default_config(self) -> None:
        """Test TranscriptionConfig with default values."""
        config = TranscriptionConfig()
        assert config.model == "stt-async-preview"
        assert config.language_hints is None
        assert config.enable_language_identification is False
        assert config.enable_speaker_diarization is False
        assert config.context is None
        assert config.webhook_url is None

    def test_config_with_language_hints(self) -> None:
        """Test TranscriptionConfig with language hints."""
        config = TranscriptionConfig(
            language_hints=[Language.ENGLISH, Language.SPANISH],
        )
        assert config.language_hints == [Language.ENGLISH, Language.SPANISH]

    def test_config_with_language_string(self) -> None:
        """Test TranscriptionConfig with language as string."""
        config = TranscriptionConfig(language_hints=["en"])
        assert config.language_hints == [Language.ENGLISH]

    def test_config_with_speaker_diarization(self) -> None:
        """Test TranscriptionConfig with speaker diarization."""
        config = TranscriptionConfig(enable_speaker_diarization=True)
        assert config.enable_speaker_diarization is True

    def test_config_with_context(self) -> None:
        """Test TranscriptionConfig with context."""
        config = TranscriptionConfig(context="Medical transcription context")
        assert config.context == "Medical transcription context"

    def test_config_with_webhook(self) -> None:
        """Test TranscriptionConfig with webhook settings."""
        config = TranscriptionConfig(
            webhook_url="https://example.com/webhook",
            webhook_auth_header_name="X-Auth-Token",
            webhook_auth_header_value="secret",
        )
        assert config.webhook_url == "https://example.com/webhook"
        assert config.webhook_auth_header_name == "X-Auth-Token"
        assert config.webhook_auth_header_value == "secret"

    def test_config_serialization(self) -> None:
        """Test TranscriptionConfig serialization."""
        config = TranscriptionConfig(
            model="stt-async-v2",
            language_hints=[Language.ENGLISH],
            enable_speaker_diarization=True,
        )
        data = config.model_dump()
        assert data["model"] == "stt-async-v2"
        assert data["language_hints"] == [Language.ENGLISH]
        assert data["enable_speaker_diarization"] is True


class TestTranscriptionConfigRealTime:
    """Tests for TranscriptionConfigRealTime model."""

    def test_default_realtime_config(self) -> None:
        """Test TranscriptionConfigRealTime with default values."""
        config = TranscriptionConfigRealTime()
        assert config.model == "stt-rt-preview"
        assert config.audio_format == AudioFormat.auto
        assert config.enable_endpoint_detection is False
        assert config.translation is None

    def test_realtime_config_with_endpoint_detection(self) -> None:
        """Test TranscriptionConfigRealTime with endpoint detection."""
        config = TranscriptionConfigRealTime(enable_endpoint_detection=True)
        assert config.enable_endpoint_detection is True

    def test_realtime_config_with_translation(self) -> None:
        """Test TranscriptionConfigRealTime with translation."""
        translation = TranslationConfig(
            type="one_way",
            target_language=Language.ENGLISH,
        )
        config = TranscriptionConfigRealTime(translation=translation)
        assert config.translation is not None
        assert config.translation.type == "one_way"
        assert config.translation.target_language == Language.ENGLISH


class TestTranslationConfig:
    """Tests for TranslationConfig model."""

    def test_one_way_translation_valid(self) -> None:
        """Test one-way translation with valid config."""
        config = TranslationConfig(
            type="one_way",
            target_language=Language.ENGLISH,
        )
        assert config.type == "one_way"
        assert config.target_language == Language.ENGLISH

    def test_two_way_translation_valid(self) -> None:
        """Test two-way translation with valid config."""
        config = TranslationConfig(
            type="two_way",
            language_a=Language.ENGLISH,
            language_b=Language.SPANISH,
        )
        assert config.type == "two_way"
        assert config.language_a == Language.ENGLISH
        assert config.language_b == Language.SPANISH

    def test_one_way_translation_invalid(self) -> None:
        """Test one-way translation with invalid config."""
        with pytest.raises(ValidationError):
            TranslationConfig(
                type="one_way",
                language_a=Language.ENGLISH,
                language_b=Language.SPANISH,
            )

    def test_two_way_translation_invalid(self) -> None:
        """Test two-way translation with invalid config."""
        with pytest.raises(ValidationError):
            TranslationConfig(
                type="two_way",
                target_language=Language.ENGLISH,
            )


class TestToken:
    """Tests for Token model."""

    def test_token_without_speaker(self) -> None:
        """Test Token without speaker information."""
        token = Token(
            text="Hello",
            start_ms=0,
            end_ms=500,
            confidence=0.99,
        )
        assert token.text == "Hello"
        assert token.start_ms == 0
        assert token.end_ms == 500
        assert token.confidence == 0.99
        assert token.speaker is None

    def test_token_with_speaker(self) -> None:
        """Test Token with speaker information."""
        token = Token(
            text="Hello",
            start_ms=0,
            end_ms=500,
            confidence=0.99,
            speaker="speaker_1",
        )
        assert token.speaker == "speaker_1"


class TestTranscriptionJob:
    """Tests for TranscriptionJob model."""

    def test_transcription_job_valid(self) -> None:
        """Test TranscriptionJob with valid UUID."""
        job = TranscriptionJob(
            id="550e8400-e29b-41d4-a716-446655440000",
            status=TranscriptionJobStatus.COMPLETED,
            created_at=datetime.now(UTC),
            file_id="file_123",
            filename="test.wav",
        )
        assert job.id == "550e8400-e29b-41d4-a716-446655440000"
        assert job.status == TranscriptionJobStatus.COMPLETED
        assert job.filename == "test.wav"
        assert job.uid == job.id

    def test_transcription_job_invalid_uuid(self) -> None:
        """Test TranscriptionJob with invalid UUID."""
        with pytest.raises(ValidationError, match="id must be a valid UUID"):
            TranscriptionJob(
                id="invalid-uuid",
                status=TranscriptionJobStatus.COMPLETED,
                created_at=datetime.now(UTC),
                file_id="file_123",
                filename="test.wav",
            )

    def test_transcription_job_with_error(self) -> None:
        """Test TranscriptionJob with error status."""
        job = TranscriptionJob(
            id="550e8400-e29b-41d4-a716-446655440000",
            status=TranscriptionJobStatus.ERROR,
            created_at=datetime.now(UTC),
            file_id="file_123",
            filename="test.wav",
            error_message="Transcription failed",
        )
        assert job.status == TranscriptionJobStatus.ERROR
        assert job.error_message == "Transcription failed"


class TestTranscriptionResult:
    """Tests for TranscriptionResult model."""

    def test_transcription_result_basic(self) -> None:
        """Test TranscriptionResult with basic data."""
        result = TranscriptionResult(
            id="550e8400-e29b-41d4-a716-446655440000",
            text="Hello world",
        )
        assert result.id == "550e8400-e29b-41d4-a716-446655440000"
        assert result.text == "Hello world"
        assert result.tokens == []

    def test_transcription_result_with_tokens(self) -> None:
        """Test TranscriptionResult with tokens."""
        tokens = [
            Token(text="Hello", start_ms=0, end_ms=500, confidence=0.99),
            Token(text="world", start_ms=500, end_ms=1000, confidence=0.98),
        ]
        result = TranscriptionResult(
            id="550e8400-e29b-41d4-a716-446655440000",
            text="Hello world",
            tokens=tokens,
        )
        assert len(result.tokens) == 2
        assert result.tokens[0].text == "Hello"
        assert result.tokens[1].text == "world"


class TestStreamingChunk:
    """Tests for StreamingChunk model."""

    def test_streaming_chunk_partial(self) -> None:
        """Test StreamingChunk with partial result."""
        chunk = StreamingChunk(text="Hello", is_final=False)
        assert chunk.text == "Hello"
        assert chunk.is_final is False
        assert chunk.confidence is None
        assert chunk.words == []

    def test_streaming_chunk_final(self) -> None:
        """Test StreamingChunk with final result."""
        words = [
            Token(text="Hello", start_ms=0, end_ms=500, confidence=0.99),
        ]
        chunk = StreamingChunk(
            text="Hello",
            is_final=True,
            confidence=0.99,
            words=words,
        )
        assert chunk.text == "Hello"
        assert chunk.is_final is True
        assert chunk.confidence == 0.99
        assert len(chunk.words) == 1


class TestAudioFormat:
    """Tests for AudioFormat enum."""

    def test_audio_format_values(self) -> None:
        """Test AudioFormat enum values."""
        assert AudioFormat.auto == "auto"

    def test_audio_format_membership(self) -> None:
        """Test AudioFormat enum membership."""
        assert "auto" in [fmt.value for fmt in AudioFormat]


class TestTranscriptionJobStatus:
    """Tests for TranscriptionJobStatus enum."""

    def test_status_values(self) -> None:
        """Test TranscriptionJobStatus enum values."""
        assert TranscriptionJobStatus.QUEUED == "queued"
        assert TranscriptionJobStatus.PROCESSING == "processing"
        assert TranscriptionJobStatus.COMPLETED == "completed"
        assert TranscriptionJobStatus.ERROR == "error"

    def test_status_membership(self) -> None:
        """Test TranscriptionJobStatus enum membership."""
        statuses = [status.value for status in TranscriptionJobStatus]
        assert "queued" in statuses
        assert "processing" in statuses
        assert "completed" in statuses
        assert "error" in statuses
