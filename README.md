# Validiz Python Library

A Python client library for the Validiz Email Validation API. This library provides both synchronous and asynchronous clients for interacting with the API endpoints.

## Installation

```bash
pip install validiz
```

## Features

- Both synchronous and asynchronous clients
- Email validation API
- File upload and processing
- Health check endpoints
- Comprehensive error handling
- Type annotations for IDE completion

## Quick Start

### Synchronous Client

```python
from validiz import ValidizClient, ValidizError

# Create a client with API key
client = ValidizClient(api_key="your_api_key_here")

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
from validiz import AsyncValidizClient, ValidizError

async def validate_email():
    # Create a client with API key
    async with AsyncValidizClient(api_key="your_api_key_here") as client:
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

Both client classes provide the same methods, with the async client providing asynchronous versions.

### Initialization

```python
# Synchronous client
from validiz import ValidizClient

client = ValidizClient(
    api_key="your_api_key",  # Required
    api_base_url="https://api.validiz.com/v1",  # Optional
    timeout=30  # Optional (seconds)
)

# Asynchronous client
from validiz import AsyncValidizClient

client = AsyncValidizClient(
    api_key="your_api_key",  # Required
    api_base_url="https://api.validiz.com/v1",  # Optional
    timeout=30.0,  # Optional (seconds)
    session=None  # Optional aiohttp ClientSession
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

# Asynchronous
# Upload a file
upload_result = await client.upload_file("emails.csv")
file_id = upload_result["file_id"]

# Check status
status = await client.get_file_status(file_id)

# Download results when complete
if status["status"] == "completed":
    output_file = await client.download_file(file_id, "results.csv")
```

#### Health Check

```python
# Synchronous
health = client.check_health()

# Asynchronous
health = await client.check_health()
```

### Batch Processing with Async Client

One of the major advantages of the async client is the ability to process multiple requests in parallel:

```python
import asyncio
from validiz import AsyncValidizClient

async def batch_validate():
    emails = [
        "user1@example.com",
        "user2@example.com",
        "user3@example.com",
        "user4@example.com",
    ]
    
    async with AsyncValidizClient(api_key="your_api_key") as client:
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

## Error Handling

The library provides several exception classes for different types of errors:

```python
from validiz import (
    ValidizError,  # Base exception
    ValidizAuthError,  # Authentication errors
    ValidizRateLimitError,  # Rate limit exceeded
    ValidizValidationError,  # Validation errors
    ValidizNotFoundError,  # Resource not found
    ValidizConnectionError  # Connection errors
)

try:
    # Make API call
    results = client.validate_email("user@example.com")
except ValidizAuthError as e:
    print(f"Authentication error: {e.message}")
except ValidizRateLimitError as e:
    print(f"Rate limit exceeded: {e.message}")
except ValidizConnectionError as e:
    print(f"Connection error: {e.message}")
except ValidizError as e:
    print(f"API error (status {e.status_code}): {e.message}")
```

## Examples

Check the `examples` directory for more detailed examples:

- `sync_example.py` - Examples for the synchronous client
- `async_example.py` - Examples for the asynchronous client

## License

This library is released under the MIT License. See the LICENSE file for more details. 