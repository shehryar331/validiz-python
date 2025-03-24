import json
import logging
from typing import Any, Dict, Optional

import aiohttp
import requests

from validiz._exceptions import (
    ValidizAuthError,
    ValidizError,
    ValidizNotFoundError,
    ValidizPaymentRequiredError,
    ValidizRateLimitError,
    ValidizServerError,
    ValidizValidationError,
)

# Set up logging
logger = logging.getLogger("validiz")


def _extract_error_message(error_data: Dict[str, Any]) -> str:
    """
    Extract error message from API response in a robust way.
    Handles various error response formats.

    Args:
        error_data: Error data dictionary from API response

    Returns:
        Extracted error message as string
    """
    # Check for detail field (common in FastAPI/Starlette errors)
    if "detail" in error_data:
        if isinstance(error_data["detail"], str):
            return error_data["detail"]
        elif (
            isinstance(error_data["detail"], dict) and "message" in error_data["detail"]
        ):
            return error_data["detail"]["message"]
        elif isinstance(error_data["detail"], list) and error_data["detail"]:
            # For validation errors that return a list of errors
            return "; ".join(
                str(item.get("msg", str(item))) for item in error_data["detail"]
            )

    # Check for error.message pattern
    if isinstance(error_data.get("error"), dict):
        if "message" in error_data["error"]:
            return error_data["error"]["message"]

    # Check for message field directly
    if "message" in error_data:
        return error_data["message"]

    # Check for error field as string
    if "error" in error_data and isinstance(error_data["error"], str):
        return error_data["error"]

    # Check for error_description field (common in OAuth errors)
    if "error_description" in error_data:
        return error_data["error_description"]

    # Fallback: return the whole error data as string
    return str(error_data)


def _extract_error_code(error_data: Dict[str, Any]) -> Optional[str]:
    """
    Extract error code from API response.

    Args:
        error_data: Error data dictionary from API response

    Returns:
        Extracted error code or None if not found
    """
    # Various possible locations for error codes
    if isinstance(error_data.get("error"), dict) and "code" in error_data["error"]:
        return error_data["error"]["code"]

    if "code" in error_data:
        return error_data["code"]

    if "error_code" in error_data:
        return error_data["error_code"]

    if isinstance(error_data.get("detail"), dict) and "code" in error_data["detail"]:
        return error_data["detail"]["code"]

    return None


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
        ValidizServerError: When a server error occurs
        ValidizPaymentRequiredError: When payment is required
        ValidizError: For other API errors
    """
    if 200 <= response.status_code < 300:
        # Check content type to determine how to parse response
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            try:
                return response.json()
            except json.JSONDecodeError:
                logger.warning(
                    "Response indicated JSON but could not parse JSON content"
                )
                return {"content": response.content, "content_type": content_type}
        else:
            return {"content": response.content, "content_type": content_type}

    # Log the error response
    logger.error(f"API Error: HTTP {response.status_code}, URL: {response.url}")

    # Handle error responses
    try:
        error_data = response.json()
        logger.debug(f"Error response: {error_data}")
    except (json.JSONDecodeError, ValueError):
        error_message = response.text or f"HTTP Error {response.status_code}"
        error_data = {"error": error_message}
        logger.debug(f"Non-JSON error response: {error_message}")

    # Extract error details
    error_message = _extract_error_message(error_data)
    error_code = _extract_error_code(error_data)

    # Extract more detailed error information
    if isinstance(error_data.get("error"), dict):
        error_details = error_data["error"].get("details")
    elif isinstance(error_data.get("detail"), dict):
        error_details = error_data["detail"].get("details")
    else:
        error_details = error_data.get("details")

    # Raise appropriate exception based on status code
    if response.status_code == 401:
        raise ValidizAuthError(
            error_message, response.status_code, error_code, error_details
        )
    elif response.status_code == 429:
        raise ValidizRateLimitError(
            error_message, response.status_code, error_code, error_details
        )
    elif response.status_code == 402 or (
        response.status_code == 403 and "insufficient credits" in error_message.lower()
    ):
        raise ValidizPaymentRequiredError(
            error_message, response.status_code, error_code, error_details
        )
    elif response.status_code == 422 or response.status_code == 400:
        raise ValidizValidationError(
            error_message, response.status_code, error_code, error_details
        )
    elif response.status_code == 404:
        raise ValidizNotFoundError(
            error_message, response.status_code, error_code, error_details
        )
    elif 500 <= response.status_code < 600:
        raise ValidizServerError(
            error_message, response.status_code, error_code, error_details
        )
    else:
        raise ValidizError(
            error_message, response.status_code, error_code, error_details
        )


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
        ValidizServerError: When a server error occurs
        ValidizPaymentRequiredError: When payment is required
        ValidizError: For other API errors
    """
    if 200 <= response.status < 300:
        # Check content type to determine how to parse response
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            try:
                return await response.json()
            except (json.JSONDecodeError, aiohttp.ContentTypeError):
                logger.warning(
                    "Response indicated JSON but could not parse JSON content"
                )
                content = await response.read()
                return {"content": content, "content_type": content_type}
        else:
            content = await response.read()
            return {"content": content, "content_type": content_type}

    # Log the error response
    logger.error(f"API Error: HTTP {response.status}, URL: {response.url}")

    # Handle error responses
    try:
        error_data = await response.json()
        logger.debug(f"Error response: {error_data}")
    except (json.JSONDecodeError, ValueError, aiohttp.ContentTypeError):
        error_message = await response.text() or f"HTTP Error {response.status}"
        error_data = {"error": error_message}
        logger.debug(f"Non-JSON error response: {error_message}")

    # Extract error details
    error_message = _extract_error_message(error_data)
    error_code = _extract_error_code(error_data)

    # Extract more detailed error information
    if isinstance(error_data.get("error"), dict):
        error_details = error_data["error"].get("details")
    elif isinstance(error_data.get("detail"), dict):
        error_details = error_data["detail"].get("details")
    else:
        error_details = error_data.get("details")

    # Raise appropriate exception based on status code
    if response.status == 401:
        raise ValidizAuthError(
            error_message, response.status, error_code, error_details
        )
    elif response.status == 429:
        raise ValidizRateLimitError(
            error_message, response.status, error_code, error_details
        )
    elif response.status == 402 or (
        response.status == 403 and "insufficient credits" in error_message.lower()
    ):
        raise ValidizPaymentRequiredError(
            error_message, response.status, error_code, error_details
        )
    elif response.status == 422 or response.status == 400:
        raise ValidizValidationError(
            error_message, response.status, error_code, error_details
        )
    elif response.status == 404:
        raise ValidizNotFoundError(
            error_message, response.status, error_code, error_details
        )
    elif 500 <= response.status < 600:
        raise ValidizServerError(
            error_message, response.status, error_code, error_details
        )
    else:
        raise ValidizError(error_message, response.status, error_code, error_details)
