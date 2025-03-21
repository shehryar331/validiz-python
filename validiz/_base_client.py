import os
from typing import Dict, Any, List, Optional, Union, TypeVar, Generic, Protocol

import pandas as pd

from validiz._exceptions import ValidizError


class BaseClient:
    """Base client class with shared functionality for Validiz API clients."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base_url: str = "https://api.validiz.com/v1"
    ):
        """
        Initialize the base client.
        
        Args:
            api_key: API key for API endpoints
            api_base_url: Base URL for API endpoints
        """
        self.api_key = api_key or os.environ.get("VALIDIZ_API_KEY")
        if self.api_key is None:
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
    
    def get_file_status(self, file_id: str) -> Dict[str, Any]:
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
    
    def download_file(self, file_id: str, output_path: Optional[str] = None) -> str:
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
    
    def poll_file_until_complete(
        self, 
        file_id: str, 
        interval: int = 5, 
        max_retries: int = 60,
        output_path: Optional[str] = None,
        return_dataframe: bool = True
    ) -> Union[pd.DataFrame, str]:
        """
        Poll the status of a file until it is complete, then download and return the results.
        This is a template method that uses abstract methods implemented by subclasses.
        
        Args:
            file_id: ID of the file upload
            interval: Polling interval in seconds
            max_retries: Maximum number of polling attempts
            output_path: Path to save the downloaded file, if None, a temp file is used
            return_dataframe: Whether to return the results as a pandas DataFrame
            
        Returns:
            If return_dataframe is True, returns a pandas DataFrame with the validation results.
            Otherwise, returns the path to the downloaded file.
            
        Raises:
            TimeoutError: If the file processing takes longer than interval * max_retries seconds
            ValidizError: If there's an error with the API call
        """
        for attempt in range(max_retries):
            status = self.get_file_status(file_id)
            
            if status["status"] == "completed":
                # Download the file
                file_path = self.download_file(file_id, output_path)
                
                if return_dataframe:
                    # Try to determine the file format and read it
                    try:
                        if file_path.endswith(".csv"):
                            return pd.read_csv(file_path)
                        elif file_path.endswith(".xlsx") or file_path.endswith(".xls"):
                            return pd.read_excel(file_path)
                        else:
                            # Default to CSV
                            return pd.read_csv(file_path)
                    except Exception as e:
                        raise ValidizError(f"Error parsing result file: {str(e)}")
                else:
                    return file_path
            
            elif status["status"] == "failed":
                error_message = status.get("error_message", "File processing failed")
                raise ValidizError(error_message)
            
            # Wait for the next polling interval
            self._wait_interval(interval)
        
        raise TimeoutError(f"File processing timed out after {interval * max_retries} seconds") 