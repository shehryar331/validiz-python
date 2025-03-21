# Validiz Example Scripts

This directory contains example scripts that demonstrate how to use the Validiz package for email validation.

## Contents

- `sync_example.py` - Examples using the synchronous client
- `async_example.py` - Examples using the asynchronous client

## Prerequisites

Before running these examples, you need:

1. The Validiz package installed:
   ```
   pip install validiz
   ```

2. A valid API key from [Validiz](https://validiz.com)

## Running the Examples

### Option 1: Set your API key as an environment variable

```bash
# Set the API key (Linux/Mac)
export VALIDIZ_API_KEY="your_api_key_here"

# Set the API key (Windows)
set VALIDIZ_API_KEY=your_api_key_here
```

### Option 2: Edit the examples directly

Open the example files and replace `your_api_key_here` with your actual API key:

```python
API_KEY = os.environ.get("VALIDIZ_API_KEY", "your_api_key_here")
```

### Run the examples

```bash
# Run the synchronous examples
python sync_example.py

# Run the asynchronous examples
python async_example.py
```

## What These Examples Demonstrate

### Synchronous Client (`sync_example.py`)

1. **Validating a single email address**
   - Basic email validation with detailed results

2. **Validating multiple email addresses**
   - Batch validation in a single API call

3. **File processing**
   - Uploading CSV files with email addresses
   - Polling for completion
   - Downloading validation results
   - Converting results to pandas DataFrames

4. **Error handling**
   - Handling authentication errors
   - Handling connection errors
   - Handling validation errors

### Asynchronous Client (`async_example.py`)

1. **Validating a single email address asynchronously**
   - Using async/await syntax

2. **Validating multiple email addresses asynchronously**
   - Batch validation in a single asynchronous API call

3. **Parallel email validation**
   - Demonstrating how to use `asyncio.gather` to validate multiple emails concurrently
   - Performance comparison with sequential validation

4. **Asynchronous file processing**
   - Uploading and downloading files asynchronously
   - Polling for file status with async methods

5. **Parallel file processing**
   - Processing multiple files concurrently
   - Getting results as pandas DataFrames

6. **Error handling with asynchronous code**
   - Using try/except with async functions
   - Context managers for proper resource cleanup

## Notes

- The examples create dummy CSV files if they don't already exist
- The error handling examples intentionally use invalid credentials or URLs to demonstrate error cases
- The examples are designed to be self-contained and can be run without any additional setup (other than providing your API key) 