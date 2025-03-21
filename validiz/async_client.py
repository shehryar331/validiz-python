import os
import asyncio
from typing import Dict, Any, List, Optional, Union

import aiofiles
import aiohttp
import pandas as pd

from validiz._base_client import BaseClient
from validiz._exceptions import ValidizConnectionError, ValidizError
from validiz._response_handling import handle_async_response


class AsyncValidiz(BaseClient):
    """
    Asynchronous client for the Validiz API.
    
    Provides methods to interact with the Validiz API using asynchronous requests.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base_url: str = "https://api.validiz.com/v1",
        timeout: int = 30
    ):
        """
        Initialize the asynchronous client.
        
        Args:
            api_key: API key for authentication
            api_base_url: Base URL for API endpoints
            timeout: Request timeout in seconds
        """
        super().__init__(api_key, api_base_url)
        self.timeout = timeout
        self._session = None
    
    async def _wait_interval(self, interval: int):
        """
        Wait for the specified interval.
        
        Args:
            interval: The number of seconds to wait
        """
        await asyncio.sleep(interval)
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Get or create an aiohttp ClientSession.
        
        Returns:
            An aiohttp ClientSession
        """
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an asynchronous HTTP request and handle the response.
        
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
        session = await self._get_session()
        
        try:
            if files:
                # Handle file uploads
                form_data = aiohttp.FormData()
                for key, (file_name, file_obj) in files.items():
                    form_data.add_field(key, file_obj, filename=file_name)
                
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    data=form_data,
                    timeout=self.timeout
                ) as response:
                    return await handle_async_response(response)
            else:
                # Standard request with JSON data
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    timeout=self.timeout
                ) as response:
                    return await handle_async_response(response)
        except aiohttp.ClientError as e:
            raise ValidizConnectionError(f"Connection error: {str(e)}")
    
    async def validate_email(self, emails: Union[str, List[str]]) -> List[Dict[str, Any]]:
        """
        Validate one or more email addresses asynchronously.
        
        Args:
            emails: Email address or list of email addresses to validate
            
        Returns:
            List of dicts containing validation results
        """
        if isinstance(emails, str):
            emails = [emails]
        
        data = {"emails": emails}
        
        response = await self._make_request(
            method="POST",
            endpoint="validate/email",
            json_data=data
        )
        
        # The response could be a single dict or a list of dicts
        if isinstance(response, dict):
            return [response]
        return response
    
    async def upload_file(self, file_path: str) -> Dict[str, Any]:
        """
        Upload a file containing email addresses for validation asynchronously.
        
        Args:
            file_path: Path to the file containing email addresses
            
        Returns:
            Dict containing file upload information
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_name = os.path.basename(file_path)
        file_content = None
        
        try:
            async with aiofiles.open(file_path, mode="rb") as f:
                file_content = await f.read()
            
            files = {"file": (file_name, file_content)}
            
            response = await self._make_request(
                method="POST",
                endpoint="validate/file",
                files=files
            )
            return response
        except Exception as e:
            if isinstance(e, ValidizConnectionError) or isinstance(e, ValidizError):
                raise
            raise ValidizError(f"Error uploading file: {str(e)}")
    
    async def get_file_status(self, file_id: str) -> Dict[str, Any]:
        """
        Check the status of a file validation job asynchronously.
        
        Args:
            file_id: ID of the file upload
            
        Returns:
            Dict containing file status information
        """
        return await self._make_request(
            method="GET",
            endpoint=f"validate/file/{file_id}/status"
        )
    
    async def download_file(self, file_id: str, output_path: Optional[str] = None) -> str:
        """
        Download the results of a completed file validation job asynchronously and save to disk.
        
        Args:
            file_id: ID of the file upload
            output_path: Path to save the downloaded file, if None, a temp file is used
            
        Returns:
            Path to the downloaded file
        """
        response = await self._make_request(
            method="GET",
            endpoint=f"validate/file/{file_id}/download"
        )
        
        # Handle file download
        if output_path is None:
            output_path = f"validiz_results_{file_id}.csv"
        
        async with aiofiles.open(output_path, mode="wb") as f:
            await f.write(response.get("content"))
        
        return output_path
    
    async def get_file_content(self, file_id: str) -> bytes:
        """
        Get the content of a completed file validation job asynchronously without saving to disk.
        
        Args:
            file_id: ID of the file upload
            
        Returns:
            File content as bytes
        """
        response = await self._make_request(
            method="GET",
            endpoint=f"validate/file/{file_id}/download"
        )
        
        return response.get("content")
    
    async def close(self):
        """
        Close the aiohttp session to free up resources.
        """
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None 