"""Pydantic models for Soniox API requests and responses."""

from datetime import datetime
from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, Field, field_validator, model_validator

from soniox.languages import Language


class FileUploadResponse(BaseModel):
    """File upload response."""

    id: str = Field(..., description="File ID")
    filename: str = Field(..., description="Filename")
    size: int = Field(..., description="File size")
    created_at: datetime = Field(..., description="Created at")
    client_reference_id: str | None = Field(
        None,
        description="Client reference ID",
    )


class BaseTranscriptionConfig(BaseModel):
    """Base transcription configuration."""

    language_hints: list[Language] | None = Field(
        None,
        description=(
            "language hints when possible "
            "to significantly improve accuracy (e.g., 'en', 'es')\n"
            "See: soniox.com/docs/stt/concepts/language-hints"
        ),
    )
    enable_language_identification: bool = Field(
        False,
        description=(
            "Enable language identification. Each token will include a "
            '"language" field.\n'
            "See: soniox.com/docs/stt/concepts/language-identification"
        ),
    )
    enable_speaker_diarization: bool = Field(
        False,
        description=(
            "Enable speaker diarization. Each token will include a "
            '"speaker" field.\n'
            "See: soniox.com/docs/stt/concepts/speaker-diarization"
        ),
    )
    context: str | None = Field(
        None,
        description=(
            "Set context to improve recognition of difficult and rare words. "
            "Context is a string and can include words, phrases, sentences, "
            "or summaries (limit: 10K chars).\n"
            "See: soniox.com/docs/stt/concepts/context"
        ),
    )
    client_reference_id: str | None = Field(
        None,
        description=(
            "Optional identifier to track this request (client-defined).\n"
            "See: https://soniox.com/docs/stt/api-reference/transcriptions/create_transcription#request"
        ),
    )

    @field_validator("language_hints")
    @classmethod
    def validate_language(
        cls,
        v: list[Language] | None,
    ) -> list[Language] | None:
        if v is None:
            return None
        if isinstance(v, Language):
            return [v]
        if isinstance(v, str):
            return [Language(v)]
        if isinstance(v, list):
            return [Language(item) for item in v]
        return v


class TranscriptionConfig(BaseTranscriptionConfig):
    """Transcription configuration."""

    model: str = Field(
        "stt-async-preview",
        description="Model to use, See: soniox.com/docs/stt/models",
    )

    webhook_url: str | None = Field(
        None,
        description=(
            "Webhook URL to receive transcription events.\n"
            "See: https://soniox.com/docs/stt/api-reference/transcriptions/create_transcription#request"
        ),
    )
    webhook_auth_header_name: str | None = Field(
        None,
        description=(
            "Webhook authentication header name\n"
            "See: https://soniox.com/docs/stt/api-reference/transcriptions/create_transcription#request"
        ),
    )
    webhook_auth_header_value: str | None = Field(
        None,
        description=(
            "Webhook authentication header value\n"
            "See: https://soniox.com/docs/stt/api-reference/transcriptions/create_transcription#request"
        ),
    )


class AudioFormat(StrEnum):
    """Audio format."""

    auto = "auto"

    # aac = "aac"
    # aiff = "aiff"
    # amr = "amr"
    # asf = "asf"
    # flac = "flac"
    # mp3 = "mp3"
    # ogg = "ogg"
    # wav = "wav"
    # webm = "webm"


class TranslationConfig(BaseModel):
    """Translation configuration."""

    type: Literal["one_way", "two_way"] = Field(
        "one_way",
        description="Translation type",
    )
    target_language: Language | None = Field(
        None,
        description="Language to translate to",
    )
    language_a: Language | None = Field(
        None,
        description="Language to translate from",
    )
    language_b: Language | None = Field(
        None,
        description="Language to translate to",
    )

    @model_validator(mode="after")
    def validate_translation_config(self) -> Self:
        if (
            self.type == "one_way"
            and self.target_language is not None
            and self.language_a is None
            and self.language_b is None
        ):
            return self
        if (
            self.type == "two_way"
            and self.target_language is None
            and self.language_a is not None
            and self.language_b is not None
        ):
            return self

        raise ValueError("Invalid translation configuration")


class TranscriptionConfigRealTime(BaseTranscriptionConfig):
    """Transcription configuration."""

    model: str = Field(
        "stt-rt-preview",
        description="Model to use, See: soniox.com/docs/stt/models",
    )
    audio_format: AudioFormat = Field(
        "auto",
        description="Audio format",
    )
    # num_channels: Literal[1, 2] | None = Field(
    #     None,
    #     description="Number of channels",
    # )
    # sample_rate: int | None = Field(
    #     None,
    #     description="Sample rate",
    # )
    enable_endpoint_detection: bool = Field(
        False,
        description=(
            "Use endpointing to detect when the speaker stops.\n"
            "It finalizes all non-final tokens right away, "
            "minimizing latency.\n"
            "See: soniox.com/docs/stt/rt/endpoint-detection"
        ),
    )
    translation: TranslationConfig | None = Field(
        None,
        description="Translation configuration",
    )


class TranscriptionRequest(BaseModel):
    """Request model for transcription."""

    audio: str = Field(
        description="Audio file path or URL.",
    )
    config: TranscriptionConfig = Field(
        TranscriptionConfig(),
        description="Transcription configuration",
    )


class Token(BaseModel):
    """Word-level transcription result."""

    text: str = Field(..., description="Transcribed word")
    start_ms: int = Field(..., description="Start time in milliseconds")
    end_ms: int = Field(..., description="End time in milliseconds")
    confidence: float = Field(..., description="Confidence score 0-1")
    speaker: str | None = Field(
        default=None,
        description="Speaker ID if diarization enabled",
    )


class TranscriptionJobStatus(StrEnum):
    """Transcription job status."""

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class TranscriptionJob(TranscriptionConfig):
    """Transcription job."""

    id: str = Field(..., description="Job ID")
    status: TranscriptionJobStatus = Field(..., description="Job status")
    created_at: datetime = Field(..., description="Created at")

    audio_url: str | None = Field(None, description="Audio URL")
    file_id: str | None = Field(None, description="File ID")
    filename: str = Field(..., description="Filename")

    audio_duration_ms: int | None = Field(
        None,
        description="Audio duration in milliseconds",
    )
    error_message: str | None = Field(None, description="Error message")
    webhook_status_code: int | None = Field(
        None,
        description="Webhook status code",
    )

    @property
    def uid(self) -> str:
        return self.id

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        import uuid

        try:
            uuid.UUID(v)
        except (ValueError, AttributeError, TypeError) as e:
            raise ValueError("id must be a valid UUID string") from e
        return v


class TranscriptionWebhook(BaseModel):
    """Transcript."""

    id: str = Field(..., description="Transcript ID")
    status: TranscriptionJobStatus = Field(..., description="Job status")


class TranscriptionResult(BaseModel):
    """Transcript."""

    id: str = Field(..., description="Transcript ID")
    text: str = Field(..., description="Transcript text")
    tokens: list[Token] = Field(
        default_factory=list,
        description="Tokens",
    )


class StreamingChunk(BaseModel):
    """Streaming transcription chunk."""

    text: str = Field(..., description="Partial transcription text")
    is_final: bool = Field(
        default=False,
        description="Whether this is the final result",
    )
    confidence: float | None = Field(
        default=None,
        description="Confidence score",
    )
    words: list[Token] = Field(
        default_factory=list,
        description="Word-level results",
    )
