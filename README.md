# Validiz Python Library

[![PyPI version](https://img.shields.io/pypi/v/validiz.svg)](https://pypi.org/project/validiz/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/validiz.svg)](https://pypi.org/project/validiz/)
[![PyPI - Status](https://img.shields.io/pypi/status/validiz.svg)](https://pypi.org/project/validiz/)
[![PyPI - License](https://img.shields.io/pypi/l/validiz.svg)](https://pypi.org/project/validiz/)

A Python client library for the Validiz Email Validation API. This library provides both synchronous and asynchronous clients for interacting with the API endpoints.

## Installation

```bash
pip install validiz
```

## Requirements

Python 3.9 or higher is required. All dependencies will be installed automatically when installing the package.

Alternatively, you can install the dependencies directly from the requirements.txt file:

```bash
pip install -r requirements.txt
```

## Features

- Both synchronous and asynchronous clients
- Email validation API
- File upload and processing
- Comprehensive error handling
- Type annotations for IDE completion

## Quick Start

### Synchronous Client

```python
from validiz import Validiz, ValidizError

# Create a client with API key
client = Validiz(api_key="your_api_key_here")

# Validate an email
try:
    results = client.validate_email("user@example.com")
    for result in results:
        print(f"Email: {result['email']}")
        print(f"Is valid: {result['is_valid']}")
        print(f"Status: {result['status']}")
except ValidizError as e:
    print(f"API error: {e.message}")
```

### Asynchronous Client

```python
import asyncio
from validiz import AsyncValidiz, ValidizError

async def validate_email():
    # Create a client with API key
    async with AsyncValidiz(api_key="your_api_key_here") as client:
        # Validate an email
        try:
            results = await client.validate_email("user@example.com")
            for result in results:
                print(f"Email: {result['email']}")
                print(f"Is valid: {result['is_valid']}")
                print(f"Status: {result['status']}")
        except ValidizError as e:
            print(f"API error: {e.message}")

# Run the async function
asyncio.run(validate_email())
```

## API Reference

### Client Architecture

The library uses a Template Method pattern for shared functionality:

- `BaseClient` implements common methods like `poll_file_until_complete`
- Synchronous and asynchronous clients inherit from `BaseClient` and implement client-specific operations
- This architecture ensures code reuse while handling the differences between synchronous and asynchronous operations

### Initialization

```python
# Synchronous client
from validiz import Validiz

client = Validiz(
    api_key="your_api_key",  # Required
    api_base_url="https://api.validiz.com/v1",  # Optional
    timeout=30  # Optional (seconds)
)

# Asynchronous client
from validiz import AsyncValidiz

client = AsyncValidiz(
    api_key="your_api_key",  # Required
    api_base_url="https://api.validiz.com/v1",  # Optional
    timeout=30  # Optional (seconds)
)
```

### Validation Methods

#### Email Validation

```python
# Synchronous
results = client.validate_email("user@example.com")
# or
results = client.validate_email(["user1@example.com", "user2@example.com"])

# Asynchronous
results = await client.validate_email("user@example.com")
# or
results = await client.validate_email(["user1@example.com", "user2@example.com"])
```

#### File Operations

```python
# Synchronous
# Upload a file
upload_result = client.upload_file("emails.csv")
file_id = upload_result["file_id"]

# Check status
status = client.get_file_status(file_id)

# Download results when complete
if status["status"] == "completed":
    output_file = client.download_file(file_id, "results.csv")

# Or use the polling method to wait for completion and get results as DataFrame
import pandas as pd

# Get results as DataFrame without saving to disk
df = client.poll_file_until_complete(
    file_id=file_id, 
    interval=5, 
    max_retries=60,
    output_path=None,  # No file will be saved
    return_dataframe=True
)

# Or save the file and get the DataFrame
df = client.poll_file_until_complete(
    file_id=file_id, 
    interval=5, 
    max_retries=60,
    output_path="results.csv",  # File will be saved here
    return_dataframe=True
)

# Or get the file path
file_path = client.poll_file_until_complete(
    file_id=file_id, 
    interval=5, 
    max_retries=60,
    output_path="results.csv",
    return_dataframe=False
)

# Or get the raw content as bytes
content = client.poll_file_until_complete(
    file_id=file_id, 
    interval=5, 
    max_retries=60,
    output_path=None,
    return_dataframe=False
)

# Process results
print(f"Number of validated emails: {len(df)}")
print(df.head())

# Asynchronous
# Upload a file
upload_result = await client.upload_file("emails.csv")
file_id = upload_result["file_id"]

# Check status
status = await client.get_file_status(file_id)

# Download results when complete
if status["status"] == "completed":
    output_file = await client.download_file(file_id, "results.csv")

# Or use the polling method to wait for completion and get results as DataFrame
import pandas as pd

# Get results as DataFrame without saving to disk
df = await client.poll_file_until_complete(
    file_id=file_id, 
    interval=5, 
    max_retries=60,
    output_path=None,  # No file will be saved
    return_dataframe=True
)

# Process results
print(f"Number of validated emails: {len(df)}")
print(df.head())
```

### Batch Processing with Async Client

One of the major advantages of the async client is the ability to process multiple requests in parallel:

```python
import asyncio
from validiz import AsyncValidiz

async def batch_validate():
    emails = [
        "user1@example.com",
        "user2@example.com",
        "user3@example.com",
        "user4@example.com",
    ]
    
    async with AsyncValidiz(api_key="your_api_key") as client:
        # Create tasks for each email
        tasks = [client.validate_email(email) for email in emails]
        
        # Process all emails in parallel
        results = await asyncio.gather(*tasks)
        
        # Process results
        for i, result in enumerate(results):
            print(f"Results for {emails[i]}:")
            print(result)

# Run the async function
asyncio.run(batch_validate())
```

### Batch File Processing with Polling

Process multiple files in parallel and wait for them to complete:

```python
import asyncio
import pandas as pd
from validiz import AsyncValidiz

async def process_multiple_files():
    files = ["file1.csv", "file2.csv", "file3.csv"]
    
    async with AsyncValidiz(api_key="your_api_key") as client:
        # Upload all files
        upload_tasks = [client.upload_file(file) for file in files]
        upload_results = await asyncio.gather(*upload_tasks)
        
        # Get file IDs
        file_ids = [result["file_id"] for result in upload_results]
        
        # Poll for completion and get results without saving to disk
        poll_tasks = [client.poll_file_until_complete(file_id, output_path=None) for file_id in file_ids]
        dataframes = await asyncio.gather(*poll_tasks)
        
        # Process results
        for i, df in enumerate(dataframes):
            print(f"Results for {files[i]}:")
            print(f"Number of emails: {len(df)}")
            print(f"Valid emails: {df[df['is_valid'] == True].shape[0]}")
            print(f"Invalid emails: {df[df['is_valid'] == False].shape[0]}")

# Run the async function
asyncio.run(process_multiple_files())
```

## Error Handling

The library provides a comprehensive set of exception classes for different types of errors:

```python
from validiz import (
    ValidizError,              # Base exception for all errors
    ValidizAuthError,          # Authentication errors (HTTP 401)
    ValidizRateLimitError,     # Rate limit exceeded errors (HTTP 429)
    ValidizValidationError,    # Validation errors (HTTP 400, 422)
    ValidizNotFoundError,      # Resource not found errors (HTTP 404)
    ValidizConnectionError,    # Connection errors (network issues)
    ValidizPaymentRequiredError, # Payment required errors (HTTP 402/403)
    ValidizServerError,        # Server-side errors (HTTP 500, 502, 503, 504)
    ValidizTimeoutError        # Request timeout errors
)

try:
    # Make API call
    results = client.validate_email("user@example.com")
except ValidizAuthError as e:
    print(f"Authentication error: {e}")  # Improved error messages
except ValidizRateLimitError as e:
    print(f"Rate limit exceeded: {e}")  # Includes advice about waiting
except ValidizPaymentRequiredError as e:
    print(f"Payment required: {e}")  # Includes advice about adding credits
except ValidizConnectionError as e:
    print(f"Connection error: {e}")
except ValidizServerError as e:
    print(f"Server error: {e}")  # Includes advice about retrying or contacting support
except ValidizError as e:
    print(f"API error (status {e.status_code}): {e}")
```

### Error Details

All exceptions include:
- `message`: Human-readable error message
- `status_code`: HTTP status code (if applicable)
- `error_code`: API-specific error code (if available)
- `details`: Additional error details (if available)

For example:
```python
except ValidizError as e:
    print(f"Error: {e.message}")
    print(f"Status Code: {e.status_code}")
    print(f"Error Code: {e.error_code}")
    print(f"Details: {e.details}")
```

### Logging

The library uses Python's standard logging module. You can configure it to see what's happening:

```python
import logging

# Configure logging to see API errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("validiz")
logger.setLevel(logging.DEBUG)
```

## Examples

Check the `examples` directory for more detailed examples:

- `sync_example.py` - Examples for the synchronous client
- `async_example.py` - Examples for the asynchronous client

## License

This library is released under the MIT License. See the LICENSE file for more details. 