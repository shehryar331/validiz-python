"""Integration tests for asynchronous Validiz client.

These tests require a valid API key set in the environment variable VALIDIZ_API_KEY.
They will be skipped if the environment variable is not set.
"""
import asyncio
import os
import unittest

import pytest

from tests.utils import create_temp_csv_file
from validiz import AsyncValidiz


@pytest.mark.integration
class TestValidizAsyncIntegration(unittest.TestCase):
    """Integration tests for the asynchronous Validiz client."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before running tests."""
        cls.api_key = os.environ.get("VALIDIZ_API_KEY")
        if not cls.api_key:
            pytest.skip("VALIDIZ_API_KEY environment variable not set")
        
        cls.test_file_path = create_temp_csv_file()
        cls.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(cls.loop)

    @classmethod
    def tearDownClass(cls):
        """Tear down test fixtures after running tests."""
        if hasattr(cls, "test_file_path") and os.path.exists(cls.test_file_path):
            os.remove(cls.test_file_path)
        
        if hasattr(cls, "loop") and not cls.loop.is_closed():
            cls.loop.close()

    def run_async(self, coro):
        """Run an async coroutine in the test loop."""
        return self.loop.run_until_complete(coro)

    async def async_setup(self):
        """Async setup for tests."""
        self.client = AsyncValidiz(api_key=self.api_key)
        return self.client

    async def async_teardown(self):
        """Async teardown for tests."""
        if hasattr(self, "client"):
            await self.client.close()

    def test_validate_email(self):
        """Test validating an email against the real API."""
        async def run_test():
            client = await self.async_setup()
            try:
                # Use a known valid email for testing
                results = await client.validate_email("user@example.com")
                
                # Check that we got a valid response
                self.assertIsNotNone(results)
                self.assertGreaterEqual(len(results), 1)
                self.assertEqual(results[0].email, "user@example.com")
                
                # We don't know if the API will consider this valid or not,
                # so we just check that the is_valid field exists
                self.assertIsNotNone(results[0].is_valid)
            finally:
                await self.async_teardown()
                
        self.run_async(run_test())

    def test_validate_multiple_emails(self):
        """Test validating multiple emails against the real API."""
        async def run_test():
            client = await self.async_setup()
            try:
                test_emails = ["user1@example.com", "user2@example.com"]
                results = await client.validate_email(test_emails)
                
                # Check that we got valid responses
                self.assertIsNotNone(results)
                self.assertEqual(len(results), 2)
                self.assertEqual(results[0].email, "user1@example.com")
                self.assertEqual(results[1].email, "user2@example.com")
            finally:
                await self.async_teardown()
                
        self.run_async(run_test())

    def test_context_manager(self):
        """Test using the client as a context manager."""
        async def run_test():
            async with AsyncValidiz(api_key=self.api_key) as client:
                # Use a known valid email for testing
                results = await client.validate_email("user@example.com")
                
                # Check that we got a valid response
                self.assertIsNotNone(results)
                self.assertGreaterEqual(len(results), 1)
                self.assertEqual(results[0].email, "user@example.com")
                
        self.run_async(run_test())

    @pytest.mark.skip(reason="This test makes real API calls and uploads files")
    def test_file_upload_workflow(self):
        """
        Test the complete file upload workflow.
        
        This test is skipped by default since it makes multiple API calls
        and may take some time to complete.
        """
        async def run_test():
            async with AsyncValidiz(api_key=self.api_key) as client:
                # Upload a file
                upload_result = await client.upload_file(self.test_file_path)
                self.assertIsNotNone(upload_result)
                self.assertIn("file_id", upload_result)
                
                file_id = upload_result["file_id"]
                
                # Check status
                status = await client.get_file_status(file_id)
                self.assertIsNotNone(status)
                self.assertIn("status", status)
                
                # Poll until complete
                try:
                    # Set smaller values for testing
                    df = await client.poll_file_until_complete(
                        file_id=file_id,
                        interval=2,
                        max_retries=10,
                        return_dataframe=True
                    )
                    
                    # Check the DataFrame
                    self.assertIsNotNone(df)
                    self.assertTrue(hasattr(df, "shape"))
                    self.assertGreaterEqual(df.shape[0], 1)  # At least one row
                    
                except Exception as e:
                    self.fail(f"poll_file_until_complete failed: {str(e)}")
                
        self.run_async(run_test())


if __name__ == "__main__":
    unittest.main()
