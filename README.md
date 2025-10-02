# Soniox Python SDK

[![Python Version](https://img.shields.io/pypi/pyversions/soniox.svg)](https://pypi.org/project/soniox/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Official Python SDK for [Soniox](https://soniox.com) Speech-to-Text API. Built with `httpx` for both synchronous and asynchronous support.

## Features

- 🎯 **Complete API Coverage**: Full support for Soniox REST API
- ⚡ **Async & Sync**: Full support for both synchronous and asynchronous operations
- 🔒 **Type Safe**: Built with Pydantic v2 for robust type checking and validation
- 📝 **Comprehensive Logging**: Built-in logging with the `soniox` logger
- 🌍 **60+ Languages**: Transcribe speech in multiple languages with language hints
- 🎭 **Speaker Diarization**: Identify different speakers in audio
- 🔍 **Language Identification**: Automatic language detection
- 📊 **Word-Level Timestamps**: Get precise timing for each word
- 🎯 **Context Support**: Improve accuracy with domain-specific context

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
import time
from soniox import SonioxClient

client = SonioxClient()

# Submit transcription job
job = client.transcribe_file("path/to/audio.wav")
print(f"Job ID: {job.id}")
print(f"Status: {job.status}")

# Poll for completion
while True:
    job = client.get_transcription_job(job.id)
    if job.status == "completed":
        break
    time.sleep(1)

# Get the transcript
result = client.get_transcription_result(job.id)
print(f"Transcript: {result.text}")
print(f"Tokens: {len(result.tokens)}")
```

**Asynchronous:**

```python
import asyncio
from soniox import SonioxClient

async def transcribe():
    client = SonioxClient()
    
    # Submit transcription job
    job = await client.transcribe_file_async("path/to/audio.wav")
    print(f"Job ID: {job.id}")
    
    # Poll for completion
    while True:
        job = await client.get_transcription_job_async(job.id)
        if job.status == "completed":
            break
        await asyncio.sleep(1)
    
    # Get the transcript
    result = await client.get_transcription_result_async(job.id)
    print(f"Transcript: {result.text}")

asyncio.run(transcribe())
```

#### Transcribe with Custom Configuration

You can pass configuration options either as a `TranscriptionConfig` object or as keyword arguments:

```python
from soniox import SonioxClient
from soniox.languages import Language
from soniox.types import TranscriptionConfig

client = SonioxClient()

# Using TranscriptionConfig
config = TranscriptionConfig(
    model="stt-async-preview",
    language_hints=[Language.en],
    enable_speaker_diarization=True,
    context="Medical terminology context"
)
job = client.transcribe_file("audio.wav", config=config)

# Or using kwargs
job = client.transcribe_file(
    "audio.wav",
    model="stt-async-preview",
    enable_speaker_diarization=True
)
```

## Advanced Features

### Speaker Diarization

Identify different speakers in your audio:

```python
import time
from soniox import SonioxClient

client = SonioxClient()

# Submit job with speaker diarization
job = client.transcribe_file(
    "path/to/audio.wav",
    enable_speaker_diarization=True
)

# Wait for completion
while True:
    job = client.get_transcription_job(job.id)
    if job.status == "completed":
        break
    time.sleep(1)

# Get results with speaker information
result = client.get_transcription_result(job.id)
for token in result.tokens:
    if token.speaker:
        print(f"Speaker {token.speaker}: {token.text}")
```

### Language Identification

Automatically identify the language being spoken:

```python
from soniox import SonioxClient
from soniox.languages import Language

client = SonioxClient()

job = client.transcribe_file(
    "multilingual_audio.wav",
    language_hints=[Language.en, Language.es, Language.fr],
    enable_language_identification=True
)
```

### Context for Improved Accuracy

Provide context to improve recognition of domain-specific terms:

```python
from soniox import SonioxClient

client = SonioxClient()

job = client.transcribe_file(
    "medical_audio.wav",
    context="Medical terminology: hypertension, cardiovascular, stethoscope"
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

##### `transcribe_file(file_path, config=None, **kwargs)` → `TranscriptionJob`

Submit an audio file for transcription.

**Parameters:**
- `file_path` (str): Path to audio file
- `config` (TranscriptionConfig, optional): Configuration object
- `**kwargs`: Configuration options (used if config is None)
  - `model` (str): Model to use (default: "stt-async-preview")
  - `language_hints` (list[Language]): Language hints for better accuracy
  - `enable_speaker_diarization` (bool): Enable speaker diarization
  - `enable_language_identification` (bool): Enable language identification
  - `context` (str): Context for improved accuracy
  - `webhook_url` (str): Webhook URL for completion notification
  - `client_reference_id` (str): Your reference ID

**Returns:** `TranscriptionJob` - Job object with status information

**Raises:**
- `FileNotFoundError`: If file doesn't exist
- `SonioxAPIError`: If API returns an error

##### `get_transcription_job(job_id)` → `TranscriptionJob`

Get the status of a transcription job.

**Parameters:**
- `job_id` (str): Job ID from `transcribe_file()`

**Returns:** `TranscriptionJob` - Updated job status

##### `get_transcription_result(job_id)` → `TranscriptionResult`

Get the transcript once the job is completed.

**Parameters:**
- `job_id` (str): Job ID from completed transcription

**Returns:** `TranscriptionResult` - Transcript with tokens

**Raises:**
- `SonioxAPIError`: If job is not completed or not found

##### `transcribe_file_async(file_path, config=None, **kwargs)` → `TranscriptionJob`

Async version of `transcribe_file()`.

##### `get_transcription_job_async(job_id)` → `TranscriptionJob`

Async version of `get_transcription_job()`.

##### `get_transcription_result_async(job_id)` → `TranscriptionResult`

Async version of `get_transcription_result()`.

### Models

#### TranscriptionJob

Transcription job status and metadata.

**Fields:**
- `id` (str): Job ID (UUID)
- `status` (TranscriptionJobStatus): Job status ("queued", "processing", "completed", "error")
- `created_at` (datetime): Job creation timestamp
- `filename` (str): Original filename
- `file_id` (str | None): Uploaded file ID
- `audio_url` (str | None): Audio URL if provided
- `audio_duration_ms` (int | None): Audio duration in milliseconds
- `error_message` (str | None): Error message if failed
- All configuration fields from `TranscriptionConfig`

#### TranscriptionResult

Transcription result with full transcript.

**Fields:**
- `id` (str): Transcript ID (matches job ID)
- `text` (str): Full transcribed text
- `tokens` (list[Token]): Word-level tokens with timing

#### Token

Word-level transcription token.

**Fields:**
- `text` (str): Token text
- `start_ms` (int): Start time in milliseconds
- `end_ms` (int): End time in milliseconds
- `confidence` (float): Confidence score (0-1)
- `speaker` (str | None): Speaker ID if diarization enabled

#### TranscriptionConfig

Configuration for transcription jobs.

**Fields:**
- `model` (str): Model to use (default: "stt-async-preview")
- `language_hints` (list[Language] | None): Language hints
- `enable_language_identification` (bool): Enable language detection
- `enable_speaker_diarization` (bool): Enable speaker diarization
- `context` (str | None): Context for improved accuracy
- `client_reference_id` (str | None): Your reference ID
- `webhook_url` (str | None): Webhook URL
- `webhook_auth_header_name` (str | None): Webhook auth header name
- `webhook_auth_header_value` (str | None): Webhook auth header value

#### FileUploadResponse

Response from file upload.

**Fields:**
- `id` (str): File ID
- `filename` (str): Original filename
- `size` (int): File size in bytes
- `created_at` (datetime): Upload timestamp
- `client_reference_id` (str | None): Your reference ID

### Exceptions

- `SonioxError`: Base exception for all Soniox errors
- `SonioxAuthenticationError`: Raised when authentication fails
- `SonioxAPIError`: Raised when API returns an error response
- `SonioxRateLimitError`: Raised when rate limit is exceeded

## Error Handling

```python
import time
from soniox import SonioxClient
from soniox.exceptions import (
    SonioxAPIError,
    SonioxAuthenticationError,
    SonioxRateLimitError,
)

client = SonioxClient()

try:
    # Submit transcription
    job = client.transcribe_file("audio.wav")
    
    # Wait for completion
    while True:
        job = client.get_transcription_job(job.id)
        if job.status == "completed":
            break
        elif job.status == "error":
            print(f"Transcription failed: {job.error_message}")
            break
        time.sleep(1)
    
    # Get result
    if job.status == "completed":
        result = client.get_transcription_result(job.id)
        print(result.text)

except FileNotFoundError:
    print("Audio file not found")
except SonioxAuthenticationError as e:
    print(f"Authentication failed: {e}")
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

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v
```

See [tests/README.md](tests/README.md) for more details on the test suite.

## Development

```bash
# Clone the repository
git clone https://github.com/mahdikiani/soniox-sdk.git
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
- [GitHub Repository](https://github.com/mahdikiani-sdk/soniox-sdk)
- [Issue Tracker](https://github.com/mahdikiani/soniox-sdk/issues)

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

## Support

- 📧 Email: mahdikiany@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/mahdikiani/soniox-sdk/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/mahdikiani/soniox-sdk/discussions)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

---

Made with ❤️ by [Mahdi Kiani](https://github.com/mahdikiani)


