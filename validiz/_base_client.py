from typing import Dict, Optional


class BaseClient:
    """Base client class with shared functionality for Validiz API clients."""

    def __init__(
        self,
        api_key: str,
        api_base_url: str = "https://api.validiz.com/v1",
    ):
        """
        Initialize the base client.

        Args:
            api_key: API key for API endpoints
            api_base_url: Base URL for API endpoints
        """
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("API key is required for API endpoints")

        self.api_base_url = api_base_url

    def _get_headers(self) -> Dict[str, str]:
        """
        Get headers for API requests.

        Returns:
            Dict containing the X-API-Key header
        """
        return {"X-API-Key": self.api_key}

    def _wait_interval(self, interval: int):
        """
        Wait for the specified interval. This is a placeholder method
        that should be overridden by subclasses.

        Args:
            interval: The number of seconds to wait

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("This method must be implemented by subclasses")

    def get_file_status(self, file_id: str):
        """
        Check the status of a file validation job.
        This is a placeholder method that should be overridden by subclasses.

        Args:
            file_id: ID of the file upload

        Returns:
            Dict containing file status information

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("This method must be implemented by subclasses")

    def download_file(self, file_id: str, output_path: Optional[str] = None):
        """
        Download the results of a completed file validation job.
        This is a placeholder method that should be overridden by subclasses.

        Args:
            file_id: ID of the file upload
            output_path: Path to save the downloaded file

        Returns:
            Path to the downloaded file

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("This method must be implemented by subclasses")

    def get_file_content(self, file_id: str):
        """
        Get the content of a completed file validation job as bytes.
        This is a placeholder method that should be overridden by subclasses.

        Args:
            file_id: ID of the file upload

        Returns:
            File content as bytes

        Raises:
            NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("This method must be implemented by subclasses")
