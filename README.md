# Soniox Python SDK

[![Python Version](https://img.shields.io/pypi/pyversions/soniox.svg)](https://pypi.org/project/soniox/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Official Python SDK for [Soniox](https://soniox.com) Speech-to-Text API. Built with `httpx` for both synchronous and asynchronous support.

## Features

- 🎯 **Complete API Coverage**: Support for both REST and WebSocket APIs
- ⚡ **Async & Sync**: Full support for both synchronous and asynchronous operations
- 🔒 **Type Safe**: Built with Pydantic for robust type checking
- 📝 **Comprehensive Logging**: Built-in logging with the `soniox` logger
- 🎤 **Real-time Streaming**: WebSocket support for live audio transcription
- 🌍 **60+ Languages**: Transcribe and translate speech in multiple languages
- 🎭 **Speaker Diarization**: Identify different speakers in audio

## Installation

```bash
pip install soniox
```

## Quick Start

### Authentication

Set your API key as an environment variable:

```bash
export SONIOX_API_KEY="your-api-key-here"
```

Or pass it directly when initializing the client:

```python
from soniox import SonioxClient

client = SonioxClient(api_key="your-api-key-here")
```

### Basic Usage

#### Transcribe an Audio File

**Synchronous:**

```python
from soniox import SonioxClient

client = SonioxClient()

# Transcribe a local audio file
response = client.transcribe_file("path/to/audio.wav")

print(response.result.text)
print(f"Confidence: {response.result.confidence}")
```

**Asynchronous:**

```python
import asyncio
from soniox import SonioxClient

async def transcribe():
    client = SonioxClient()
    response = await client.transcribe_file_async("path/to/audio.wav")
    print(response.result.text)

asyncio.run(transcribe())
```

#### Transcribe from URL

**Synchronous:**

```python
from soniox import SonioxClient

client = SonioxClient()

response = client.transcribe_url("https://example.com/audio.mp3")
print(response.result.text)
```

**Asynchronous:**

```python
import asyncio
from soniox import SonioxClient

async def transcribe_url():
    client = SonioxClient()
    response = await client.transcribe_url_async("https://example.com/audio.mp3")
    print(response.result.text)

asyncio.run(transcribe_url())
```

#### Real-time Streaming Transcription

```python
import asyncio
from soniox import SonioxClient

async def stream_transcription():
    client = SonioxClient()
    
    # Stream without sending audio (for testing)
    async for chunk in client.stream_transcribe():
        print(f"Partial: {chunk.text} (final: {chunk.is_final})")
        if chunk.is_final:
            break

asyncio.run(stream_transcription())
```

**With Audio Stream:**

```python
import asyncio
from soniox import SonioxClient

async def audio_generator():
    """Generate audio chunks from microphone or file"""
    # Your audio source here
    with open("audio.raw", "rb") as f:
        while chunk := f.read(4096):
            yield chunk

async def stream_with_audio():
    client = SonioxClient()
    
    async for chunk in client.stream_transcribe(
        audio_stream=audio_generator(),
        model="en_v2",
        sample_rate=16000
    ):
        print(f"Transcription: {chunk.text}")
        if chunk.is_final:
            print("Final result received")

asyncio.run(stream_with_audio())
```

## Advanced Features

### Speaker Diarization

Identify different speakers in your audio:

```python
from soniox import SonioxClient

client = SonioxClient()

response = client.transcribe_file(
    "path/to/audio.wav",
    enable_speaker_diarization=True
)

for word in response.result.words:
    print(f"{word.speaker}: {word.text}")
```

### Translation

Translate speech to English automatically:

```python
from soniox import SonioxClient

client = SonioxClient()

response = client.transcribe_url(
    "https://example.com/spanish_audio.mp3",
    enable_translation=True
)

print(f"Original language: {response.result.language}")
print(f"Translated text: {response.result.text}")
```

### Custom Models

Use specific models for different languages:

```python
from soniox import SonioxClient

client = SonioxClient()

# Use Spanish model
response = client.transcribe_file(
    "spanish_audio.wav",
    model="es_v2",
    language="es"
)
```

## Configuration

### Client Options

```python
from soniox import SonioxClient

client = SonioxClient(
    api_key="your-api-key",           # API key (or use SONIOX_API_KEY env var)
    base_url="https://api.soniox.com", # Custom base URL (optional)
    timeout=60.0                       # Request timeout in seconds
)
```

### Logging

The SDK uses Python's standard logging module with the logger name `soniox`:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("soniox")
logger.setLevel(logging.DEBUG)

# Or configure it your way
import logging

handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger("soniox")
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

## API Reference

### SonioxClient

Main client for interacting with Soniox API.

#### Methods

##### `transcribe_file(file_path, **options)` → `TranscriptionResponse`

Transcribe an audio file synchronously.

**Parameters:**
- `file_path` (str): Path to audio file
- `model` (str, optional): Model to use (default: "en_v2")
- `language` (str, optional): Language code (e.g., "en", "es")
- `enable_speaker_diarization` (bool, optional): Enable speaker diarization (default: False)
- `enable_translation` (bool, optional): Enable translation to English (default: False)

**Returns:** `TranscriptionResponse`

**Raises:**
- `FileNotFoundError`: If file doesn't exist
- `SonioxAPIError`: If API returns an error

##### `transcribe_file_async(file_path, **options)` → `TranscriptionResponse`

Asynchronous version of `transcribe_file()`.

##### `transcribe_url(audio_url, **options)` → `TranscriptionResponse`

Transcribe audio from a URL synchronously.

**Parameters:**
- `audio_url` (str): URL to audio file
- Other parameters same as `transcribe_file()`

**Returns:** `TranscriptionResponse`

##### `transcribe_url_async(audio_url, **options)` → `TranscriptionResponse`

Asynchronous version of `transcribe_url()`.

##### `stream_transcribe(audio_stream, **options)` → `AsyncIterator[StreamingChunk]`

Stream audio for real-time transcription.

**Parameters:**
- `audio_stream` (AsyncIterator[bytes], optional): Async iterator yielding audio chunks
- `model` (str, optional): Model to use (default: "en_v2")
- `sample_rate` (int, optional): Audio sample rate in Hz (default: 16000)
- `enable_speaker_diarization` (bool, optional): Enable speaker diarization (default: False)

**Yields:** `StreamingChunk` objects with partial transcription results

### Models

#### TranscriptionResponse

Response from transcription API.

**Fields:**
- `result` (TranscriptionResult): Transcription result
- `request_id` (str | None): Request ID for tracking
- `processing_time_ms` (int | None): Processing time in milliseconds
- `metadata` (dict): Additional metadata

#### TranscriptionResult

Transcription result data.

**Fields:**
- `text` (str): Full transcribed text
- `words` (list[Word]): Word-level results
- `language` (str | None): Detected language
- `confidence` (float): Overall confidence score (0-1)
- `audio_duration_ms` (int | None): Audio duration in milliseconds

#### Word

Word-level transcription result.

**Fields:**
- `text` (str): Transcribed word
- `start_ms` (int): Start time in milliseconds
- `duration_ms` (int): Duration in milliseconds
- `confidence` (float): Confidence score (0-1)
- `speaker` (str | None): Speaker ID if diarization enabled

#### StreamingChunk

Streaming transcription chunk.

**Fields:**
- `text` (str): Partial transcription text
- `is_final` (bool): Whether this is the final result
- `confidence` (float | None): Confidence score
- `words` (list[Word]): Word-level results

### Exceptions

- `SonioxError`: Base exception for all Soniox errors
- `SonioxAuthenticationError`: Raised when authentication fails
- `SonioxAPIError`: Raised when API returns an error response
- `SonioxRateLimitError`: Raised when rate limit is exceeded

## Error Handling

```python
from soniox import SonioxClient, SonioxAPIError, SonioxRateLimitError

client = SonioxClient()

try:
    response = client.transcribe_file("audio.wav")
except FileNotFoundError:
    print("Audio file not found")
except SonioxRateLimitError as e:
    print(f"Rate limit exceeded: {e}")
    print(f"Status code: {e.status_code}")
except SonioxAPIError as e:
    print(f"API error: {e}")
    print(f"Status code: {e.status_code}")
    print(f"Response: {e.response_body}")
```

## Testing

Run tests with pytest:

```bash
# Install development dependencies
pip install -e ".[dev,test]"

# Run tests
pytest

# Run with coverage
pytest --cov=soniox --cov-report=html
```

## Development

```bash
# Clone the repository
git clone https://github.com/mahdikiani/soniox.git
cd soniox

# Install in editable mode with dev dependencies
pip install -e ".[dev,test]"

# Run linter
ruff check src/

# Run type checker
mypy src/
```

## Resources

- [Soniox Documentation](https://soniox.com/docs/)
- [API Reference](https://soniox.com/docs/)
- [GitHub Repository](https://github.com/mahdikiani/soniox)
- [Issue Tracker](https://github.com/mahdikiani/soniox/issues)

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

## Support

- 📧 Email: mahdikiany@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/mahdikiani/soniox/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/mahdikiani/soniox/discussions)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

---

Made with ❤️ by [Mahdi Kiani](https://github.com/mahdikiani)


