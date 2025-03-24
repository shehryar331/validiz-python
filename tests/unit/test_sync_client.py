"""Unit tests for synchronous Validiz client."""

import unittest
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import requests

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
    Validiz,
    ValidizAuthError,
    ValidizConnectionError,
    ValidizError,
    ValidizRateLimitError,
)


@pytest.mark.unit
class TestValidizSyncClient(unittest.TestCase):
    """Test cases for the synchronous Validiz client."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = Validiz(api_key=TEST_API_KEY)
        self.test_file_path = create_temp_csv_file()

    def tearDown(self):
        """Tear down test fixtures."""
        import os

        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    @patch("validiz.client.requests.request")
    def test_validate_email_single(self, mock_request):
        """Test validating a single email."""
        # Mock the response
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = MOCK_EMAIL_RESPONSE
        mock_request.return_value = mock_response

        # Call the method
        results = self.client.validate_email("valid@example.com")

        # Assertions
        mock_request.assert_called_once()
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].email, "valid@example.com")
        self.assertTrue(results[0].is_valid)
        self.assertEqual(results[1].email, "invalid@example.com")
        self.assertFalse(results[1].is_valid)

    @patch("validiz.client.requests.request")
    def test_validate_email_multiple(self, mock_request):
        """Test validating multiple emails."""
        # Mock the response
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = MOCK_EMAIL_RESPONSE
        mock_request.return_value = mock_response

        # Call the method
        results = self.client.validate_email(
            ["valid@example.com", "invalid@example.com"]
        )

        # Assertions
        mock_request.assert_called_once()
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].email, "valid@example.com")
        self.assertTrue(results[0].is_valid)
        self.assertEqual(results[1].email, "invalid@example.com")
        self.assertFalse(results[1].is_valid)

    @patch("validiz.client.requests.request")
    def test_upload_file(self, mock_request):
        """Test uploading a file."""
        # Mock the response
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = MOCK_FILE_UPLOAD_RESPONSE
        mock_request.return_value = mock_response

        # Call the method
        result = self.client.upload_file(self.test_file_path)

        # Assertions
        mock_request.assert_called_once()
        self.assertEqual(result["file_id"], "file_12345")
        self.assertEqual(result["status"], "processing")

    @patch("validiz.client.requests.request")
    def test_get_file_status(self, mock_request):
        """Test getting file status."""
        # Mock the response
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "application/json"}
        mock_response.json.return_value = MOCK_FILE_STATUS_RESPONSE
        mock_request.return_value = mock_response

        # Call the method
        result = self.client.get_file_status("file_12345")

        # Assertions
        mock_request.assert_called_once()
        self.assertEqual(result["file_id"], "file_12345")
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["valid_emails"], 80)
        self.assertEqual(result["invalid_emails"], 20)

    @patch("validiz.client.requests.request")
    def test_download_file(self, mock_request):
        """Test downloading a file."""
        # Mock the response
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/csv"}
        mock_response.content = MOCK_FILE_CONTENT
        mock_request.return_value = mock_response

        with patch("validiz._response_handling.handle_sync_response") as mock_handler:
            mock_handler.return_value = {
                "content": MOCK_FILE_CONTENT,
                "content_type": "text/csv",
            }

            # Call the method with a custom output path
            output_path = "test_output.csv"
            result = self.client.download_file("file_12345", output_path)

            # Assertions
            mock_request.assert_called_once()
            self.assertEqual(result, output_path)

            # Clean up
            import os

            if os.path.exists(output_path):
                os.remove(output_path)

    @patch("validiz.client.requests.request")
    def test_get_file_content(self, mock_request):
        """Test getting file content."""
        # Mock the response
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.headers = {"Content-Type": "text/csv"}
        mock_response.content = MOCK_FILE_CONTENT
        mock_request.return_value = mock_response

        with patch("validiz._response_handling.handle_sync_response") as mock_handler:
            mock_handler.return_value = {
                "content": MOCK_FILE_CONTENT,
                "content_type": "text/csv",
            }

            # Call the method
            content = self.client.get_file_content("file_12345")

            # Assertions
            mock_request.assert_called_once()
            self.assertEqual(content, MOCK_FILE_CONTENT)

    @patch("validiz.client.Validiz.get_file_status")
    @patch("validiz.client.Validiz.get_file_content")
    @patch("validiz.client.Validiz._wait_interval")
    def test_poll_file_until_complete(self, mock_wait, mock_get_content, mock_status):
        """Test polling a file until complete."""
        # Mock the status response - first processing, then completed
        mock_status.side_effect = [
            MOCK_FILE_STATUS_PROCESSING_RESPONSE,
            MOCK_FILE_STATUS_RESPONSE,
        ]

        # Mock the content response
        mock_get_content.return_value = MOCK_FILE_CONTENT

        # Mock the DataFrame creation
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
            result = self.client.poll_file_until_complete(
                "file_12345", interval=1, max_retries=2
            )

            # Assertions
            self.assertEqual(mock_status.call_count, 2)
            mock_get_content.assert_called_once()
            mock_wait.assert_called_once_with(1)
            self.assertTrue(isinstance(result, pd.DataFrame))
            self.assertEqual(len(result), 2)

    @patch("validiz.client.Validiz.get_file_status")
    def test_poll_file_failed(self, mock_status):
        """Test polling a file that failed."""
        # Mock the status response
        mock_status.return_value = MOCK_FILE_STATUS_FAILED_RESPONSE

        # Call the method and check for exception
        with self.assertRaises(ValidizError) as context:
            self.client.poll_file_until_complete(
                "file_12345", interval=1, max_retries=2
            )

        self.assertEqual(str(context.exception), "Invalid file format")

    @patch("validiz.client.requests.request")
    def test_auth_error(self, mock_request):
        """Test authentication error handling."""
        # Mock the response
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "error": {"message": "Invalid API key", "code": "auth_error"}
        }
        mock_response.url = "https://api.validiz.com/v1/mock-endpoint"
        mock_request.return_value = mock_response

        # Call the method and check for exception
        with self.assertRaises(ValidizAuthError) as context:
            self.client.validate_email("valid@example.com")

        self.assertEqual(
            str(context.exception),
            "Invalid API key (HTTP 401) [Error code: auth_error]",
        )
        self.assertEqual(context.exception.status_code, 401)
        self.assertEqual(context.exception.error_code, "auth_error")

    @patch("validiz.client.requests.request")
    def test_rate_limit_error(self, mock_request):
        """Test rate limit error handling."""
        # Mock the response
        mock_response = MagicMock(spec=requests.Response)
        mock_response.status_code = 429
        mock_response.json.return_value = {
            "error": {"message": "Rate limit exceeded", "code": "rate_limit_exceeded"}
        }
        mock_response.url = "https://api.validiz.com/v1/mock-endpoint"
        mock_request.return_value = mock_response

        # Call the method and check for exception
        with self.assertRaises(ValidizRateLimitError) as context:
            self.client.validate_email("valid@example.com")

        self.assertEqual(
            str(context.exception),
            "Rate limit exceeded (HTTP 429) [Error code: rate_limit_exceeded] - Please wait before making more requests or consider upgrading your plan.",
        )
        self.assertEqual(context.exception.status_code, 429)
        self.assertEqual(context.exception.error_code, "rate_limit_exceeded")

    @patch("validiz.client.requests.request")
    def test_connection_error(self, mock_request):
        """Test connection error handling."""
        # Mock the response
        mock_request.side_effect = requests.RequestException("Connection error")

        # Call the method and check for exception
        with self.assertRaises(ValidizConnectionError) as context:
            self.client.validate_email("valid@example.com")

        self.assertEqual(str(context.exception), "Connection error: Connection error")


if __name__ == "__main__":
    unittest.main()
