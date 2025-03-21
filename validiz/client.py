import os
import time
from typing import Any, Dict, List, Optional, Union

import requests

from validiz._base_client import BaseClient
from validiz._exceptions import ValidizConnectionError
from validiz._response_handling import handle_sync_response


class Validiz(BaseClient):
    """
    Synchronous client for the Validiz API.

    Provides methods to interact with the Validiz API using synchronous requests.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base_url: str = "https://api.validiz.com/v1",
        timeout: int = 30,
    ):
        """
        Initialize the synchronous client.

        Args:
            api_key: API key for authentication
            api_base_url: Base URL for API endpoints
            timeout: Request timeout in seconds
        """
        super().__init__(api_key, api_base_url)
        self.timeout = timeout

    def _wait_interval(self, interval: int):
        """
        Wait for the specified interval.

        Args:
            interval: The number of seconds to wait
        """
        time.sleep(interval)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request and handle the response.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Optional query parameters
            json_data: Optional JSON body
            files: Optional files to upload

        Returns:
            Dict containing the response data
        """
        url = f"{self.api_base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                files=files,
                timeout=self.timeout,
            )
            return handle_sync_response(response)
        except requests.RequestException as e:
            raise ValidizConnectionError(f"Connection error: {str(e)}")

    def validate_email(self, emails: Union[str, List[str]]) -> List[Dict[str, Any]]:
        """
        Validate one or more email addresses.

        Args:
            emails: Email address or list of email addresses to validate

        Returns:
            List of dicts containing validation results
        """
        if isinstance(emails, str):
            emails = [emails]

        data = {"emails": emails}

        response = self._make_request(
            method="POST", endpoint="validate/email", json_data=data
        )

        # The response could be a single dict or a list of dicts
        if isinstance(response, dict):
            return [response]
        return response

    def upload_file(self, file_path: str) -> Dict[str, Any]:
        """
        Upload a file containing email addresses for validation.

        Args:
            file_path: Path to the file containing email addresses

        Returns:
            Dict containing file upload information
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_name = os.path.basename(file_path)
        files = {"file": (file_name, open(file_path, "rb"))}

        try:
            response = self._make_request(
                method="POST", endpoint="validate/file", files=files
            )
            return response
        finally:
            # Ensure the file is closed
            files["file"][1].close()

    def get_file_status(self, file_id: str) -> Dict[str, Any]:
        """
        Check the status of a file validation job.

        Args:
            file_id: ID of the file upload

        Returns:
            Dict containing file status information
        """
        return self._make_request(
            method="GET", endpoint=f"validate/file/{file_id}/status"
        )

    def download_file(self, file_id: str, output_path: Optional[str] = None) -> str:
        """
        Download the results of a completed file validation job and save to disk.

        Args:
            file_id: ID of the file upload
            output_path: Path to save the downloaded file, if None, a temp file is used

        Returns:
            Path to the downloaded file
        """
        response = self._make_request(
            method="GET", endpoint=f"validate/file/{file_id}/download"
        )

        # Handle file download
        if output_path is None:
            output_path = f"validiz_results_{file_id}.csv"

        with open(output_path, "wb") as f:
            f.write(response.get("content"))

        return output_path

    def get_file_content(self, file_id: str) -> bytes:
        """
        Get the content of a completed file validation job without saving to disk.

        Args:
            file_id: ID of the file upload

        Returns:
            File content as bytes
        """
        response = self._make_request(
            method="GET", endpoint=f"validate/file/{file_id}/download"
        )

        return response.get("content")
