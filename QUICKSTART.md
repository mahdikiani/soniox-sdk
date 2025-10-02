# Soniox SDK - Quick Start Guide

Welcome! This guide will help you get started with the Soniox Python SDK in minutes.

## Installation

```bash
pip install soniox
```

## Authentication

Set your API key as an environment variable:

```bash
export SONIOX_API_KEY="your-api-key-here"
```

## Your First Transcription

### 1. Transcribe an Audio File

```python
from soniox import SonioxClient

# Initialize client (reads SONIOX_API_KEY from environment)
client = SonioxClient()

# Transcribe
response = client.transcribe_file("audio.wav")
print(response.result.text)
```

### 2. Transcribe from URL

```python
response = client.transcribe_url("https://example.com/audio.mp3")
print(response.result.text)
```

### 3. Async Transcription

```python
import asyncio

async def transcribe():
    client = SonioxClient()
    response = await client.transcribe_file_async("audio.wav")
    print(response.result.text)

asyncio.run(transcribe())
```

### 4. Real-time Streaming

```python
import asyncio

async def stream():
    client = SonioxClient()
    
    async for chunk in client.stream_transcribe(
        model="en_v2",
        sample_rate=16000
    ):
        print(f"Partial: {chunk.text}")
        if chunk.is_final:
            print(f"Final: {chunk.text}")
            break

asyncio.run(stream())
```

## Advanced Features

### Speaker Diarization

```python
response = client.transcribe_file(
    "conversation.wav",
    enable_speaker_diarization=True
)

for word in response.result.words:
    print(f"{word.speaker}: {word.text}")
```

### Translation

```python
response = client.transcribe_url(
    "https://example.com/spanish.mp3",
    enable_translation=True
)

print(f"Original: {response.result.language}")
print(f"Translated: {response.result.text}")
```

### Custom Models

```python
response = client.transcribe_file(
    "audio.wav",
    model="es_v2",  # Spanish model
    language="es"
)
```

## Error Handling

```python
from soniox import SonioxClient, SonioxAPIError

client = SonioxClient()

try:
    response = client.transcribe_file("audio.wav")
except FileNotFoundError:
    print("File not found!")
except SonioxAPIError as e:
    print(f"API Error: {e.status_code} - {e}")
```

## Configuration Options

```python
client = SonioxClient(
    api_key="your-key",              # API key (or use env var)
    base_url="https://api.soniox.com",  # Custom endpoint
    timeout=60.0                     # Request timeout in seconds
)
```

## Logging

Enable debug logging to see SDK internals:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("soniox")
```

## Next Steps

- Check out the [examples](examples/) directory for more detailed examples
- Read the full [README](README.md) for complete API documentation
- Visit [Soniox Documentation](https://soniox.com/docs/) for API details

## Common Issues

### "API key must be provided"
Set the `SONIOX_API_KEY` environment variable or pass it to the client:
```python
client = SonioxClient(api_key="your-key")
```

### "File not found"
Ensure the audio file path is correct and the file exists.

### Import errors
Make sure the package is installed:
```bash
pip install soniox
```

## Support

- 📧 Email: mahdikiany@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/mahdikiani/soniox/issues)
- 📖 Docs: [Soniox Documentation](https://soniox.com/docs/)

Happy transcribing! 🎙️

