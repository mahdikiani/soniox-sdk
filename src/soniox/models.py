"""Pydantic models for Soniox API requests and responses."""

from typing import Any

from pydantic import BaseModel, Field


class TranscriptionRequest(BaseModel):
    """Request model for transcription."""

    audio: str | bytes = Field(
        ...,
        description="Audio file path, URL, or raw audio bytes",
    )
    model: str = Field(default="en_v2", description="Model to use")
    language: str | None = Field(
        default=None,
        description="Language code (e.g., 'en', 'es')",
    )
    enable_speaker_diarization: bool = Field(
        default=False,
        description="Enable speaker diarization",
    )
    enable_streaming: bool = Field(
        default=False,
        description="Enable streaming mode",
    )
    sample_rate: int = Field(
        default=16000,
        description="Audio sample rate in Hz",
    )
    enable_translation: bool = Field(
        default=False,
        description="Enable translation to English",
    )


class Word(BaseModel):
    """Word-level transcription result."""

    text: str = Field(..., description="Transcribed word")
    start_ms: int = Field(..., description="Start time in milliseconds")
    duration_ms: int = Field(..., description="Duration in milliseconds")
    confidence: float = Field(..., description="Confidence score 0-1")
    speaker: str | None = Field(
        default=None,
        description="Speaker ID if diarization enabled",
    )


class TranscriptionResult(BaseModel):
    """Transcription result."""

    text: str = Field(..., description="Full transcribed text")
    words: list[Word] = Field(
        default_factory=list,
        description="Word-level results",
    )
    language: str | None = Field(
        default=None,
        description="Detected language",
    )
    confidence: float = Field(..., description="Overall confidence score")
    audio_duration_ms: int | None = Field(
        default=None,
        description="Audio duration in milliseconds",
    )


class TranscriptionResponse(BaseModel):
    """Response model for transcription."""

    result: TranscriptionResult = Field(
        ..., description="Transcription result",
    )
    request_id: str | None = Field(
        default=None,
        description="Request ID for tracking",
    )
    processing_time_ms: int | None = Field(
        default=None,
        description="Processing time in milliseconds",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata",
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
    words: list[Word] = Field(
        default_factory=list,
        description="Word-level results",
    )
