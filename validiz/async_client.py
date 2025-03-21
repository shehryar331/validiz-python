import os
from typing import Dict, Any, List, Optional, Union

import aiohttp

from validiz.base_client import BaseClient
from validiz.exceptions import ValidizConnectionError
from validiz.response_handling import handle_async_response


class AsyncValidizClient(BaseClient):
    """
    Asynchronous client for the Validiz API.
    
    Provides methods to interact with the Validiz API using asynchronous requests.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base_url: str = "https://api.validiz.com/v1",
        timeout: float = 30.0,
        session: Optional[aiohttp.ClientSession] = None
    ):
        """
        Initialize the asynchronous client.
        
        Args:
            api_key: API key for authentication
            api_base_url: Base URL for API endpoints
            timeout: Request timeout in seconds
            session: Optional aiohttp ClientSession to use
        """
        super().__init__(api_key, api_base_url)
        self.timeout = timeout
        self._session = session
        self._owned_session = False
    
    async def __aenter__(self):
        """Create a session if one doesn't exist."""
        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._owned_session = True
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close the session if we created it."""
        if self._owned_session and self._session is not None:
            await self._session.close()
            self._session = None
            self._owned_session = False
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """
        Get or create a client session.
        
        Returns:
            aiohttp.ClientSession
        """
        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._owned_session = True
        return self._session
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request and handle the response.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Optional query parameters
            json_data: Optional JSON body
            data: Optional form data
            files: Optional files to upload
            
        Returns:
            Dict containing the response data
        """
        url = f"{self.api_base_url}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        session = await self._get_session()
        
        try:
            # Handle file uploads
            form_data = None
            if files:
                form_data = aiohttp.FormData()
                for key, (filename, file_obj) in files.items():
                    form_data.add_field(
                        key,
                        file_obj.read(),
                        filename=filename
                    )
            
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            
            async with session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                data=form_data or data,
                timeout=timeout
            ) as response:
                return await handle_async_response(response)
        except aiohttp.ClientError as e:
            raise ValidizConnectionError(f"Connection error: {str(e)}")
    
    async def validate_email(self, emails: Union[str, List[str]]) -> List[Dict[str, Any]]:
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
        Upload a file containing email addresses for validation.
        
        Args:
            file_path: Path to the file containing email addresses
            
        Returns:
            Dict containing file upload information
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_name = os.path.basename(file_path)
        with open(file_path, "rb") as f:
            files = {"file": (file_name, f)}
            response = await self._make_request(
                method="POST",
                endpoint="validate/file",
                files=files
            )
        
        return response
    
    async def get_file_status(self, file_id: str) -> Dict[str, Any]:
        """
        Check the status of a file validation job.
        
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
        Download the results of a completed file validation job.
        
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
        
        with open(output_path, "wb") as f:
            f.write(response.get("content"))
        
        return output_path
    
    async def check_health(self) -> Dict[str, Any]:
        """
        Check the health status of the API.
        
        Returns:
            Dict containing health status information
        """
        # Health endpoint is at the base URL without the /v1 prefix
        base_url = self.api_base_url.split("/v1")[0]
        url = f"{base_url}/health"
        
        session = await self._get_session()
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        try:
            async with session.get(url, timeout=timeout) as response:
                return await handle_async_response(response)
        except aiohttp.ClientError as e:
            raise ValidizConnectionError(f"Connection error: {str(e)}")
    
    async def close(self) -> None:
        """Close the client session."""
        if self._owned_session and self._session is not None:
            await self._session.close()
            self._session = None
            self._owned_session = False 