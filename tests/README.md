# Soniox SDK Tests

Comprehensive test suite for the Soniox Python SDK.

## Test Coverage

The test suite includes:

### 1. **Models Tests** (`test_models.py`)
- FileUploadResponse validation
- TranscriptionConfig and TranscriptionConfigRealTime
- TranslationConfig (one-way and two-way)
- Token, TranscriptionJob, TranscriptionResult
- StreamingChunk
- Enum types (AudioFormat, TranscriptionJobStatus)

### 2. **Exceptions Tests** (`test_exceptions.py`)
- SonioxError base class
- SonioxAuthenticationError
- SonioxAPIError
- SonioxRateLimitError
- Error inheritance and propagation

### 3. **Client Base Tests** (`test_client_base.py`)
- Client initialization (with API key, env var, custom settings)
- Authentication error handling
- Headers generation
- Configuration methods
- Context managers (sync and async)

### 4. **Sync Client Tests** (`test_client_sync.py`)
- File upload (success and error cases)
- File transcription (with config and kwargs)
- Get transcription job
- Get transcription result
- Error handling (rate limits, API errors)

### 5. **Async Client Tests** (`test_client_async.py`)
- Async file upload
- Async file transcription
- Async get transcription job
- Async get transcription result
- Async error handling

## Running Tests

### Prerequisites

Install test dependencies:

```bash
pip install -e ".[test]"
```

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_models.py
pytest tests/test_client_sync.py
pytest tests/test_client_async.py
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html --cov-report=term-missing
```

The coverage report will be generated in `htmlcov/index.html`.

### Run Specific Test Class or Method

```bash
# Run a specific test class
pytest tests/test_models.py::TestTranscriptionConfig

# Run a specific test method
pytest tests/test_models.py::TestTranscriptionConfig::test_default_config
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Only Failed Tests

```bash
pytest --lf
```

## Test Fixtures

Common fixtures are defined in `conftest.py`:

- `api_key`: Test API key
- `mock_env_api_key`: Sets SONIOX_API_KEY environment variable
- `client`: Initialized SonioxClient instance
- `mock_file_upload_response`: Mock file upload response
- `mock_transcription_job_response`: Mock transcription job response
- `mock_transcription_result_response`: Mock transcription result response
- `audio_file`: Temporary test audio file

## Mocking

Tests use `pytest-httpx` for mocking HTTP requests, avoiding real API calls during testing.

Example:
```python
def test_example(client, httpx_mock):
    httpx_mock.add_response(
        url=f"{client.base_url}/v1/endpoint",
        method="POST",
        json={"result": "success"},
        status_code=200,
    )
    # Test code here
```

## Test Structure

Each test file follows this structure:
- Tests are organized in classes by feature
- Each test method has a descriptive docstring
- Tests cover both success and error cases
- Edge cases and input validation are tested
- Type hints are used throughout

## Continuous Integration

Tests are designed to run in CI/CD environments without requiring actual API credentials or making real API calls.

