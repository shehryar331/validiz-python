"""Integration tests for synchronous Validiz client.

These tests require a valid API key set in the environment variable VALIDIZ_API_KEY.
They will be skipped if the environment variable is not set.
"""

import os
import unittest
from typing import ClassVar, Optional, cast

import pytest
from pandas import DataFrame

from tests.utils import create_temp_csv_file
from validiz import Validiz, ValidizPaymentRequiredError


@pytest.mark.integration
class TestValidizSyncIntegration(unittest.TestCase):
    """Integration tests for the synchronous Validiz client."""

    # Class variables with type annotations
    api_key: ClassVar[Optional[str]] = None
    client: ClassVar[Optional[Validiz]] = None
    test_file_path: ClassVar[Optional[str]] = None

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before running tests."""
        cls.api_key = os.environ.get("VALIDIZ_API_KEY")
        if not cls.api_key:
            pytest.skip("VALIDIZ_API_KEY environment variable not set")

        cls.client = Validiz(api_key=cls.api_key)
        cls.test_file_path = create_temp_csv_file()

    @classmethod
    def tearDownClass(cls):
        """Tear down test fixtures after running tests."""
        if cls.test_file_path and os.path.exists(cls.test_file_path):
            os.remove(cls.test_file_path)

    def test_validate_email(self):
        """Test validating an email against the real API."""
        # Ensure client is available
        assert self.client is not None, "Client should be initialized"

        try:
            # Use a known valid email for testing
            results = self.client.validate_email("user@example.com")

            # Check that we got a valid response
            self.assertIsNotNone(results)
            self.assertGreaterEqual(len(results), 1)
            self.assertEqual(results[0].email, "user@example.com")

            # We don't know if the API will consider this valid or not,
            # so we just check that the is_valid field exists
            self.assertIsNotNone(results[0].is_valid)
        except ValidizPaymentRequiredError:
            # Skip test if there are insufficient credits
            pytest.skip("Insufficient credits to run this test")

    def test_validate_multiple_emails(self):
        """Test validating multiple emails against the real API."""
        # Ensure client is available
        assert self.client is not None, "Client should be initialized"

        try:
            test_emails = ["user1@example.com", "user2@example.com"]
            results = self.client.validate_email(test_emails)

            # Check that we got valid responses
            self.assertIsNotNone(results)
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0].email, "user1@example.com")
            self.assertEqual(results[1].email, "user2@example.com")
        except ValidizPaymentRequiredError:
            # Skip test if there are insufficient credits
            pytest.skip("Insufficient credits to run this test")

    @pytest.mark.skip(reason="This test makes real API calls and uploads files")
    def test_file_upload_workflow(self):
        """
        Test the complete file upload workflow.

        This test is skipped by default since it makes multiple API calls
        and may take some time to complete.
        """
        # Ensure client and test_file_path are available
        assert self.client is not None, "Client should be initialized"
        assert self.test_file_path is not None, "Test file path should be initialized"

        try:
            # Upload a file
            upload_result = self.client.upload_file(self.test_file_path)
            self.assertIsNotNone(upload_result)
            self.assertIn("file_id", upload_result)

            file_id = upload_result["file_id"]

            # Check status
            status = self.client.get_file_status(file_id)
            self.assertIsNotNone(status)
            self.assertIn("status", status)

            # Poll until complete
            try:
                # Set smaller values for testing
                result = self.client.poll_file_until_complete(
                    file_id=file_id, interval=2, max_retries=10, return_dataframe=True
                )

                # Check if result is a DataFrame
                df = cast(DataFrame, result)

                # Check the DataFrame
                self.assertIsNotNone(df)
                self.assertTrue(hasattr(df, "shape"))
                self.assertGreaterEqual(df.shape[0], 1)  # At least one row

            except Exception as e:
                self.fail(f"poll_file_until_complete failed: {str(e)}")
        except ValidizPaymentRequiredError:
            # Skip test if there are insufficient credits
            pytest.skip("Insufficient credits to run this test")


if __name__ == "__main__":
    unittest.main()
