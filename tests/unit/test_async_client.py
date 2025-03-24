"""Unit tests for asynchronous Validiz client."""

import asyncio
import unittest
from unittest.mock import MagicMock, patch

import aiohttp
import pandas as pd
import pytest

from tests.config import (
    MOCK_EMAIL_RESPONSE,
    MOCK_FILE_CONTENT,
    MOCK_FILE_STATUS_FAILED_RESPONSE,
    MOCK_FILE_STATUS_PROCESSING_RESPONSE,
    MOCK_FILE_STATUS_RESPONSE,
    MOCK_FILE_UPLOAD_RESPONSE,
    TEST_API_KEY,
)
from tests.utils import create_temp_csv_file
from validiz import (
    AsyncValidiz,
    ValidizAuthError,
    ValidizConnectionError,
    ValidizError,
    ValidizRateLimitError,
)


# Mock ClientResponse
class MockClientResponse:
    """Mock aiohttp.ClientResponse for testing."""

    def __init__(self, status, headers, data, content=None):
        self.status = status
        self.headers = headers
        self._data = data
        self._content = content if content is not None else b""
        self.url = "https://api.validiz.com/v1/mock-endpoint"  # Add url attribute

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def json(self):
        return self._data

    async def read(self):
        return self._content

    async def text(self):
        return (
            self._content.decode()
            if isinstance(self._content, bytes)
            else str(self._content)
        )


@pytest.mark.unit
class TestValidizAsyncClient(unittest.TestCase):
    """Test cases for the asynchronous Validiz client."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = AsyncValidiz(api_key=TEST_API_KEY)
        self.test_file_path = create_temp_csv_file()
        # Create event loop
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        """Tear down test fixtures."""
        import os

        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

        # Close the event loop
        self.loop.close()

    def run_async(self, coro):
        """Run an async coroutine in the test loop."""
        return self.loop.run_until_complete(coro)

    @patch("aiohttp.ClientSession.request")
    def test_validate_email_single(self, mock_request):
        """Test validating a single email."""
        # Mock the response
        mock_response = MockClientResponse(
            status=200,
            headers={"Content-Type": "application/json"},
            data=MOCK_EMAIL_RESPONSE,
        )
        mock_request.return_value = mock_response

        # Call the method
        results = self.run_async(self.client.validate_email("valid@example.com"))

        # Assertions
        mock_request.assert_called_once()
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].email, "valid@example.com")
        self.assertTrue(results[0].is_valid)
        self.assertEqual(results[1].email, "invalid@example.com")
        self.assertFalse(results[1].is_valid)

    @patch("aiohttp.ClientSession.request")
    def test_validate_email_multiple(self, mock_request):
        """Test validating multiple emails."""
        # Mock the response
        mock_response = MockClientResponse(
            status=200,
            headers={"Content-Type": "application/json"},
            data=MOCK_EMAIL_RESPONSE,
        )
        mock_request.return_value = mock_response

        # Call the method
        results = self.run_async(
            self.client.validate_email(["valid@example.com", "invalid@example.com"])
        )

        # Assertions
        mock_request.assert_called_once()
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].email, "valid@example.com")
        self.assertTrue(results[0].is_valid)
        self.assertEqual(results[1].email, "invalid@example.com")
        self.assertFalse(results[1].is_valid)

    @patch("aiohttp.ClientSession.request")
    @patch("aiofiles.open")
    def test_upload_file(self, mock_aiofiles, mock_request):
        """Test uploading a file."""
        # Mock aiofiles
        mock_file = MagicMock()
        mock_file.read.return_value = asyncio.Future()
        mock_file.read.return_value.set_result(b"email\ntest@example.com")
        mock_aiofiles_ctx = MagicMock()
        mock_aiofiles_ctx.__aenter__.return_value = mock_file
        mock_aiofiles.return_value = mock_aiofiles_ctx

        # Mock the response
        mock_response = MockClientResponse(
            status=200,
            headers={"Content-Type": "application/json"},
            data=MOCK_FILE_UPLOAD_RESPONSE,
        )
        mock_request.return_value = mock_response

        # Call the method
        result = self.run_async(self.client.upload_file(self.test_file_path))

        # Assertions
        mock_request.assert_called_once()
        mock_aiofiles.assert_called_once()
        self.assertEqual(result["file_id"], "file_12345")
        self.assertEqual(result["status"], "processing")

    @patch("aiohttp.ClientSession.request")
    def test_get_file_status(self, mock_request):
        """Test getting file status."""
        # Mock the response
        mock_response = MockClientResponse(
            status=200,
            headers={"Content-Type": "application/json"},
            data=MOCK_FILE_STATUS_RESPONSE,
        )
        mock_request.return_value = mock_response

        # Call the method
        result = self.run_async(self.client.get_file_status("file_12345"))

        # Assertions
        mock_request.assert_called_once()
        self.assertEqual(result["file_id"], "file_12345")
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["valid_emails"], 80)
        self.assertEqual(result["invalid_emails"], 20)

    @patch("aiohttp.ClientSession.request")
    @patch("aiofiles.open")
    def test_download_file(self, mock_aiofiles, mock_request):
        """Test downloading a file."""
        # Mock aiofiles
        mock_file = MagicMock()
        mock_file.write = MagicMock()
        mock_file.write.return_value = asyncio.Future()
        mock_file.write.return_value.set_result(None)
        mock_aiofiles_ctx = MagicMock()
        mock_aiofiles_ctx.__aenter__.return_value = mock_file
        mock_aiofiles.return_value = mock_aiofiles_ctx

        # Mock the response
        mock_response = MockClientResponse(
            status=200,
            headers={"Content-Type": "text/csv"},
            data={},
            content=MOCK_FILE_CONTENT,
        )
        mock_request.return_value = mock_response

        with patch("validiz._response_handling.handle_async_response") as mock_handler:
            mock_handler.return_value = asyncio.Future()
            mock_handler.return_value.set_result(
                {
                    "content": MOCK_FILE_CONTENT,
                    "content_type": "text/csv",
                }
            )

            # Call the method with a custom output path
            output_path = "test_output.csv"
            result = self.run_async(
                self.client.download_file("file_12345", output_path)
            )

            # Assertions
            mock_request.assert_called_once()
            mock_aiofiles.assert_called_once_with(output_path, mode="wb")
            mock_file.write.assert_called_once_with(MOCK_FILE_CONTENT)
            self.assertEqual(result, output_path)

    @patch("aiohttp.ClientSession.request")
    def test_get_file_content(self, mock_request):
        """Test getting file content."""
        # Mock the response
        mock_response = MockClientResponse(
            status=200,
            headers={"Content-Type": "text/csv"},
            data={},
            content=MOCK_FILE_CONTENT,
        )
        mock_request.return_value = mock_response

        with patch("validiz._response_handling.handle_async_response") as mock_handler:
            mock_handler.return_value = asyncio.Future()
            mock_handler.return_value.set_result(
                {
                    "content": MOCK_FILE_CONTENT,
                    "content_type": "text/csv",
                }
            )

            # Call the method
            content = self.run_async(self.client.get_file_content("file_12345"))

            # Assertions
            mock_request.assert_called_once()
            self.assertEqual(content, MOCK_FILE_CONTENT)

    def test_poll_file_until_complete(self):
        """Test polling a file until complete."""

        # Initialize call_count before the function definition
        call_count = 0

        # Instead of patching with autospec=True, we'll directly patch the method
        # and have it return the values we want
        async def mock_get_status_side_effect(self, file_id):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return MOCK_FILE_STATUS_PROCESSING_RESPONSE
            else:
                return MOCK_FILE_STATUS_RESPONSE

        async def mock_get_content(self, file_id):
            return MOCK_FILE_CONTENT

        async def mock_wait_interval(self, seconds):
            pass

        with (
            patch.object(AsyncValidiz, "get_file_status", mock_get_status_side_effect),
            patch.object(AsyncValidiz, "get_file_content", mock_get_content),
            patch.object(AsyncValidiz, "_wait_interval", mock_wait_interval),
        ):
            # Mock pandas read_csv
            with patch("pandas.read_csv") as mock_read_csv:
                mock_df = pd.DataFrame(
                    {
                        "email": ["valid@example.com", "invalid@example.com"],
                        "is_valid": [True, False],
                        "status": ["valid", "invalid"],
                    }
                )
                mock_read_csv.return_value = mock_df

                # Call the method
                result = self.run_async(
                    self.client.poll_file_until_complete(
                        "file_12345", interval=1, max_retries=2
                    )
                )

                # Assertions
                self.assertEqual(
                    call_count, 2
                )  # Verify get_file_status was called twice
                self.assertTrue(isinstance(result, pd.DataFrame))
                self.assertEqual(len(result), 2)

    def test_poll_file_failed(self):
        """Test polling a file that failed."""

        # Instead of patching with autospec=True, we'll directly patch the method
        # to return the failed status
        async def mock_get_failed_status(self, file_id):
            return MOCK_FILE_STATUS_FAILED_RESPONSE

        with patch.object(AsyncValidiz, "get_file_status", mock_get_failed_status):
            # Call the method and check for exception
            with self.assertRaises(ValidizError) as context:
                self.run_async(
                    self.client.poll_file_until_complete(
                        "file_12345", interval=1, max_retries=2
                    )
                )

            self.assertEqual(str(context.exception), "Invalid file format")

    @patch("aiohttp.ClientSession.request")
    def test_auth_error(self, mock_request):
        """Test authentication error handling."""
        # Mock the response
        mock_response = MockClientResponse(
            status=401,
            headers={"Content-Type": "application/json"},
            data={"error": {"message": "Invalid API key", "code": "auth_error"}},
        )
        mock_request.return_value = mock_response

        # Call the method and check for exception
        with self.assertRaises(ValidizAuthError) as context:
            self.run_async(self.client.validate_email("valid@example.com"))

        self.assertEqual(
            str(context.exception),
            "Invalid API key (HTTP 401) [Error code: auth_error]",
        )
        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.error_code, "auth_error")

    @patch("aiohttp.ClientSession.request")
    def test_rate_limit_error(self, mock_request):
        """Test rate limit error handling."""
        # Mock the response
        mock_response = MockClientResponse(
            status=429,
            headers={"Content-Type": "application/json"},
            data={
                "error": {
                    "message": "Rate limit exceeded",
                    "code": "rate_limit_exceeded",
                }
            },
        )
        mock_request.return_value = mock_response

        # Call the method and check for exception
        with self.assertRaises(ValidizRateLimitError) as context:
            self.run_async(self.client.validate_email("valid@example.com"))

        self.assertEqual(
            str(context.exception),
            "Rate limit exceeded (HTTP 429) [Error code: rate_limit_exceeded] - Please wait before making more requests or consider upgrading your plan.",
        )
        self.assertEqual(context.exception.status_code, 429)
        self.assertEqual(context.exception.error_code, "rate_limit_exceeded")

    @patch("aiohttp.ClientSession.request")
    def test_connection_error(self, mock_request):
        """Test connection error handling."""
        # Mock the response
        mock_request.side_effect = aiohttp.ClientError("Connection error")

        # Call the method and check for exception
        with self.assertRaises(ValidizConnectionError) as context:
            self.run_async(self.client.validate_email("valid@example.com"))

        self.assertEqual(str(context.exception), "Connection error: Connection error")

    def test_async_context_manager(self):
        """Test using the async client as a context manager."""

        async def run_test():
            # Mock the response
            with patch("aiohttp.ClientSession.request") as mock_request:
                mock_response = MockClientResponse(
                    status=200,
                    headers={"Content-Type": "application/json"},
                    data=MOCK_EMAIL_RESPONSE,
                )
                mock_request.return_value = mock_response

                # Use as context manager
                async with AsyncValidiz(api_key=TEST_API_KEY) as client:
                    results = await client.validate_email("valid@example.com")

                    # Assertions
                    self.assertEqual(len(results), 2)
                    self.assertEqual(results[0].email, "valid@example.com")
                    self.assertTrue(results[0].is_valid)

        self.run_async(run_test())


if __name__ == "__main__":
    unittest.main()
