import io
import os
import time
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import requests

from validiz._base_client import BaseClient
from validiz._exceptions import (
    ValidizConnectionError,
    ValidizError,
    ValidizTimeoutError,
)
from validiz._response_handling import handle_sync_response
from validiz._schema import EmailResponse


class Validiz(BaseClient):
    """
    Synchronous client for the Validiz API.

    Provides methods to interact with the Validiz API using synchronous requests.
    """

    def __init__(
        self,
        api_key: str,
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
        except requests.Timeout:
            raise ValidizTimeoutError(timeout=self.timeout)
        except requests.RequestException as e:
            raise ValidizConnectionError(f"Connection error: {str(e)}")

    def validate_email(self, emails: Union[str, List[str]]) -> List[EmailResponse]:
        """
        Validate one or more email addresses.

        Args:
            emails: Email address or list of email addresses to validate

        Returns:
            List of EmailResponse instances containing validation results
        """

        data = {"emails": emails}

        response = self._make_request(
            method="POST", endpoint="validate/email", json_data=data
        )
        if not isinstance(response, list):
            raise ValueError("Expected a list response from validate_email API call")
        for res in response:
            if not isinstance(res, dict):
                raise ValueError(f"Expected dict in response, got {type(res)}")

        return [EmailResponse(**res) for res in response]

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
            content_type = response.get("content_type", "").lower()
            ext = ".csv"
            if "spreadsheetml.sheet" in content_type:
                ext = ".xlsx"
            elif "excel" in content_type:
                ext = ".xls"
            output_path = f"validiz_results_{file_id}{ext}"

        with open(output_path, "wb") as f:
            content = response.get("content")
            if not isinstance(content, bytes):
                raise ValueError("Downloaded content is not of type bytes")
            f.write(content)

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

        content = response.get("content")
        if not isinstance(content, bytes):
            raise ValueError("Downloaded content is not of type bytes")
        return content

    def poll_file_until_complete(
        self,
        file_id: str,
        interval: int = 5,
        max_retries: int = 60,
        output_path: Optional[str] = None,
        return_dataframe: bool = True,
    ) -> Union[pd.DataFrame, str, bytes]:
        """
        Poll the status of a file until it is complete, then download and return the results.

        Args:
            file_id: ID of the file upload
            interval: Polling interval in seconds
            max_retries: Maximum number of polling attempts
            output_path: Path to save the downloaded file. If None, the file will not be saved locally.
            return_dataframe: Whether to return the results as a pandas DataFrame

        Returns:
            If return_dataframe is True, returns a pandas DataFrame with the validation results.
            If return_dataframe is False and output_path is provided, returns the path to the downloaded file.
            If return_dataframe is False and output_path is None, returns the file content as bytes.

        Raises:
            TimeoutError: If the file processing takes longer than interval * max_retries seconds
            ValidizError: If there's an error with the API call
        """
        for attempt in range(max_retries):
            status = self.get_file_status(file_id)

            if status["status"] == "completed":
                # If output_path is provided, download the file to disk
                if output_path is not None:
                    file_path = self.download_file(file_id, output_path)

                    if return_dataframe:
                        # Try to determine the file format and read it
                        try:
                            if file_path.endswith(".csv"):
                                return pd.read_csv(file_path)
                            elif file_path.endswith(".xlsx") or file_path.endswith(
                                ".xls"
                            ):
                                return pd.read_excel(file_path)
                            else:
                                # Default to CSV
                                return pd.read_csv(file_path)
                        except Exception as e:
                            raise ValidizError(f"Error parsing result file: {str(e)}")
                    else:
                        return file_path
                # If output_path is None, get the content in memory
                else:
                    content = self.get_file_content(file_id)

                    if return_dataframe:
                        try:
                            # Attempt to parse as CSV by default
                            return pd.read_csv(io.BytesIO(content))
                        except Exception as e:
                            try:
                                # If CSV fails, try Excel
                                return pd.read_excel(io.BytesIO(content))
                            except Exception:
                                raise ValidizError(
                                    f"Error parsing file content: {str(e)}"
                                )
                    else:
                        return content

            elif status["status"] == "failed":
                error_message = status.get("error_message", "File processing failed")
                raise ValidizError(error_message)

            # Wait for the next polling interval
            self._wait_interval(interval)

        raise TimeoutError(
            f"File processing timed out after {interval * max_retries} seconds"
        )
