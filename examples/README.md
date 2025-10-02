# Soniox SDK Examples

This directory contains examples demonstrating various features of the Soniox Python SDK.

## Setup

Before running the examples, make sure you have:

1. Installed the Soniox SDK:
   ```bash
   pip install soniox
   ```

2. Set your API key as an environment variable:
   ```bash
   export SONIOX_API_KEY="your-api-key-here"
   ```

   Or modify the examples to pass the API key directly:
   ```python
   client = SonioxClient(api_key="your-api-key-here")
   ```

## Examples

### 1. Basic Usage (`basic_usage.py`)

Demonstrates synchronous operations:
- Transcribing local audio files
- Transcribing audio from URLs
- Speaker diarization
- Translation

```bash
python examples/basic_usage.py
```

### 2. Async Usage (`async_usage.py`)

Demonstrates asynchronous operations:
- Async file transcription
- Async URL transcription
- Concurrent transcription of multiple files

```bash
python examples/async_usage.py
```

### 3. Streaming Transcription (`streaming_transcription.py`)

Demonstrates real-time streaming:
- Streaming from audio files
- Streaming with speaker diarization
- Basic streaming test

```bash
python examples/streaming_transcription.py
```

## Audio File Formats

The SDK supports various audio formats. For best results:
- Sample rate: 16000 Hz (16 kHz) or higher
- Format: WAV, MP3, FLAC, OGG, etc.
- Channels: Mono or Stereo

## Common Use Cases

### Transcribe a single file

```python
from soniox import SonioxClient

client = SonioxClient()
response = client.transcribe_file("audio.wav")
print(response.result.text)
```

### Transcribe multiple files concurrently

```python
import asyncio
from soniox import SonioxClient

async def transcribe_many(files):
    client = SonioxClient()
    tasks = [client.transcribe_file_async(f) for f in files]
    return await asyncio.gather(*tasks)

files = ["file1.wav", "file2.wav", "file3.wav"]
responses = asyncio.run(transcribe_many(files))
```

### Real-time streaming

```python
import asyncio
from soniox import SonioxClient

async def stream_audio():
    client = SonioxClient()
    async for chunk in client.stream_transcribe(
        audio_stream=your_audio_generator(),
        model="en_v2",
        sample_rate=16000,
    ):
        print(f"Partial: {chunk.text}")
        if chunk.is_final:
            print(f"Final: {chunk.text}")
            break

asyncio.run(stream_audio())
```

## Error Handling

```python
from soniox import SonioxClient, SonioxAPIError, SonioxRateLimitError

client = SonioxClient()

try:
    response = client.transcribe_file("audio.wav")
except SonioxRateLimitError as e:
    print(f"Rate limit exceeded: {e}")
    print(f"Status code: {e.status_code}")
except SonioxAPIError as e:
    print(f"API error: {e}")
except FileNotFoundError:
    print("Audio file not found")
```

## Need Help?

- Check the [main README](../README.md) for detailed documentation
- Visit [Soniox Documentation](https://soniox.com/docs/)
- Open an issue on [GitHub](https://github.com/mahdikiani/soniox/issues)

