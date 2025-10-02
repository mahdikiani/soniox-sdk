# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.1] - 2025-10-02

### Added
- Initial release of Soniox Python SDK
- HTTP-based transcription support via `httpx`
  - Synchronous file transcription (`transcribe_file`)
  - Asynchronous file transcription (`transcribe_file_async`)
  - Synchronous URL transcription (`transcribe_url`)
  - Asynchronous URL transcription (`transcribe_url_async`)
- WebSocket-based real-time streaming transcription (`stream_transcribe`)
- Pydantic models for type-safe API interactions
  - `TranscriptionRequest`
  - `TranscriptionResponse`
  - `TranscriptionResult`
  - `Word`
  - `StreamingChunk`
- Comprehensive error handling
  - `SonioxError` (base exception)
  - `SonioxAuthenticationError`
  - `SonioxAPIError`
  - `SonioxRateLimitError`
- Built-in logging with `soniox` logger
- Support for authentication via API key parameter or `SONIOX_API_KEY` environment variable
- Advanced features support
  - Speaker diarization
  - Language detection
  - Translation to English
  - Custom models
  - Word-level timestamps
- Full test coverage (>90%) with pytest
- Comprehensive documentation and README
- Type hints throughout the codebase

### Features
- 🎯 Complete API coverage for both REST and WebSocket
- ⚡ Full async/sync support
- 🔒 Type-safe with Pydantic v2
- 📝 Structured logging
- 🎤 Real-time streaming transcription
- 🌍 60+ languages support
- 🎭 Speaker diarization

[0.0.1]: https://github.com/mahdikiani/soniox/releases/tag/v0.0.1

