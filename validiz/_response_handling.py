import json
from typing import Dict, Any

import requests
import aiohttp

from validiz._exceptions import (
    ValidizError,
    ValidizAuthError,
    ValidizRateLimitError,
    ValidizValidationError,
    ValidizNotFoundError
)


def handle_sync_response(response: requests.Response) -> Dict[str, Any]:
    """
    Handle synchronous API response and raise appropriate exceptions for errors.
    
    Args:
        response: Response object from requests
        
    Returns:
        Dict containing the response data
    
    Raises:
        ValidizAuthError: When authentication fails
        ValidizRateLimitError: When rate limits are exceeded
        ValidizValidationError: When validation fails
        ValidizNotFoundError: When resource is not found
        ValidizError: For other API errors
    """
    if 200 <= response.status_code < 300:
        # Check content type to determine how to parse response
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            return response.json()
        else:
            return {"content": response.content, "content_type": content_type}
    
    # Handle error responses
    try:
        error_data = response.json()
    except (json.JSONDecodeError, ValueError):
        error_message = response.text or f"HTTP Error {response.status_code}"
        error_data = {"error": error_message}
    
    error_message = (
        error_data.get("error", {}).get("message") 
        if isinstance(error_data.get("error"), dict) 
        else error_data.get("error", f"HTTP Error {response.status_code}")
    )
    
    error_code = error_data.get("error", {}).get("code") if isinstance(error_data.get("error"), dict) else None
    error_details = error_data.get("error", {}).get("details") if isinstance(error_data.get("error"), dict) else None
    
    if response.status_code == 401:
        raise ValidizAuthError(error_message, response.status_code, error_code, error_details)
    elif response.status_code == 429:
        raise ValidizRateLimitError(error_message, response.status_code, error_code, error_details)
    elif response.status_code == 422 or response.status_code == 400:
        raise ValidizValidationError(error_message, response.status_code, error_code, error_details)
    elif response.status_code == 404:
        raise ValidizNotFoundError(error_message, response.status_code, error_code, error_details)
    else:
        raise ValidizError(error_message, response.status_code, error_code, error_details)


async def handle_async_response(response: aiohttp.ClientResponse) -> Dict[str, Any]:
    """
    Handle asynchronous API response and raise appropriate exceptions for errors.
    
    Args:
        response: Response object from aiohttp
        
    Returns:
        Dict containing the response data
    
    Raises:
        ValidizAuthError: When authentication fails
        ValidizRateLimitError: When rate limits are exceeded
        ValidizValidationError: When validation fails
        ValidizNotFoundError: When resource is not found
        ValidizError: For other API errors
    """
    if 200 <= response.status < 300:
        # Check content type to determine how to parse response
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            return await response.json()
        else:
            content = await response.read()
            return {"content": content, "content_type": content_type}
    
    # Handle error responses
    try:
        error_data = await response.json()
    except (json.JSONDecodeError, ValueError, aiohttp.ContentTypeError):
        error_message = await response.text() or f"HTTP Error {response.status}"
        error_data = {"error": error_message}
    
    error_message = (
        error_data.get("error", {}).get("message") 
        if isinstance(error_data.get("error"), dict) 
        else error_data.get("error", f"HTTP Error {response.status}")
    )
    
    error_code = error_data.get("error", {}).get("code") if isinstance(error_data.get("error"), dict) else None
    error_details = error_data.get("error", {}).get("details") if isinstance(error_data.get("error"), dict) else None
    
    if response.status == 401:
        raise ValidizAuthError(error_message, response.status, error_code, error_details)
    elif response.status == 429:
        raise ValidizRateLimitError(error_message, response.status, error_code, error_details)
    elif response.status == 422 or response.status == 400:
        raise ValidizValidationError(error_message, response.status, error_code, error_details)
    elif response.status == 404:
        raise ValidizNotFoundError(error_message, response.status, error_code, error_details)
    else:
        raise ValidizError(error_message, response.status, error_code, error_details) 