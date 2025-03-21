"""Unit tests for Validiz exceptions."""
import unittest

import pytest

from validiz import (
    ValidizAuthError,
    ValidizConnectionError,
    ValidizError,
    ValidizNotFoundError,
    ValidizRateLimitError,
    ValidizValidationError,
)


@pytest.mark.unit
class TestValidizExceptions(unittest.TestCase):
    """Test cases for Validiz exceptions."""

    def test_base_exception(self):
        """Test base ValidizError exception."""
        error = ValidizError("Test error")
        self.assertEqual(str(error), "Test error")
        self.assertEqual(error.message, "Test error")
        self.assertIsNone(error.status_code)
        self.assertIsNone(error.error_code)
        self.assertIsNone(error.details)

        # Test with additional parameters
        error = ValidizError(
            message="Test error with params",
            status_code=400,
            error_code="test_error",
            details={"field": "value"}
        )
        self.assertEqual(str(error), "Test error with params")
        self.assertEqual(error.message, "Test error with params")
        self.assertEqual(error.status_code, 400)
        self.assertEqual(error.error_code, "test_error")
        self.assertEqual(error.details, {"field": "value"})

    def test_auth_error(self):
        """Test ValidizAuthError exception."""
        error = ValidizAuthError("Invalid API key")
        self.assertEqual(str(error), "Invalid API key")
        self.assertTrue(isinstance(error, ValidizError))

        # Test with additional parameters
        error = ValidizAuthError(
            message="Invalid API key",
            status_code=401,
            error_code="auth_error",
            details={"hint": "Check your API key"}
        )
        self.assertEqual(error.message, "Invalid API key")
        self.assertEqual(error.status_code, 401)
        self.assertEqual(error.error_code, "auth_error")
        self.assertEqual(error.details, {"hint": "Check your API key"})

    def test_rate_limit_error(self):
        """Test ValidizRateLimitError exception."""
        error = ValidizRateLimitError("Rate limit exceeded")
        self.assertEqual(str(error), "Rate limit exceeded")
        self.assertTrue(isinstance(error, ValidizError))

        # Test with additional parameters
        error = ValidizRateLimitError(
            message="Rate limit exceeded",
            status_code=429,
            error_code="rate_limit_exceeded",
            details={"retry_after": 60}
        )
        self.assertEqual(error.message, "Rate limit exceeded")
        self.assertEqual(error.status_code, 429)
        self.assertEqual(error.error_code, "rate_limit_exceeded")
        self.assertEqual(error.details, {"retry_after": 60})

    def test_validation_error(self):
        """Test ValidizValidationError exception."""
        error = ValidizValidationError("Invalid email format")
        self.assertEqual(str(error), "Invalid email format")
        self.assertTrue(isinstance(error, ValidizError))

        # Test with additional parameters
        error = ValidizValidationError(
            message="Invalid email format",
            status_code=422,
            error_code="validation_error",
            details={"errors": ["Email is invalid"]}
        )
        self.assertEqual(error.message, "Invalid email format")
        self.assertEqual(error.status_code, 422)
        self.assertEqual(error.error_code, "validation_error")
        self.assertEqual(error.details, {"errors": ["Email is invalid"]})

    def test_not_found_error(self):
        """Test ValidizNotFoundError exception."""
        error = ValidizNotFoundError("File not found")
        self.assertEqual(str(error), "File not found")
        self.assertTrue(isinstance(error, ValidizError))

        # Test with additional parameters
        error = ValidizNotFoundError(
            message="File not found",
            status_code=404,
            error_code="not_found",
            details={"file_id": "file_12345"}
        )
        self.assertEqual(error.message, "File not found")
        self.assertEqual(error.status_code, 404)
        self.assertEqual(error.error_code, "not_found")
        self.assertEqual(error.details, {"file_id": "file_12345"})

    def test_connection_error(self):
        """Test ValidizConnectionError exception."""
        error = ValidizConnectionError("Connection timeout")
        self.assertEqual(str(error), "Connection timeout")
        self.assertTrue(isinstance(error, ValidizError))

        # Test with additional parameters
        error = ValidizConnectionError(
            message="Connection timeout",
            status_code=None,
            error_code="connection_error",
            details={"timeout": 30}
        )
        self.assertEqual(error.message, "Connection timeout")
        self.assertIsNone(error.status_code)
        self.assertEqual(error.error_code, "connection_error")
        self.assertEqual(error.details, {"timeout": 30})


if __name__ == "__main__":
    unittest.main()
