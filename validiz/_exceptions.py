class ValidizError(Exception):
    """Base exception for Validiz API errors."""

    def __init__(self, message, status_code=None, error_code=None, details=None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        super().__init__(message)

    def __str__(self):
        """Improved string representation for better error messages."""
        base_msg = self.message
        if self.status_code:
            base_msg += f" (HTTP {self.status_code})"
        if self.error_code:
            base_msg += f" [Error code: {self.error_code}]"
        return base_msg


class ValidizAuthError(ValidizError):
    """Exception raised for authentication errors (HTTP 401)."""

    pass


class ValidizPaymentRequiredError(ValidizError):
    """Exception raised when payment is required (HTTP 402) or insufficient credits."""

    def __str__(self):
        """Improved string representation with helpful message."""
        if "insufficient" in self.message.lower() or "credits" in self.message.lower():
            return f"{self.message} - Please add credits to your account at https://validiz.com/"
        return super().__str__()


class ValidizRateLimitError(ValidizError):
    """Exception raised when API rate limits are exceeded (HTTP 429)."""

    def __str__(self):
        """Improved string representation with helpful message."""
        base_msg = super().__str__()
        return f"{base_msg} - Please wait before making more requests or consider upgrading your plan."


class ValidizValidationError(ValidizError):
    """Exception raised for validation errors (HTTP 400, 422)."""

    pass


class ValidizNotFoundError(ValidizError):
    """Exception raised when a resource is not found (HTTP 404)."""

    pass


class ValidizConnectionError(ValidizError):
    """Exception raised for connection errors."""

    pass


class ValidizServerError(ValidizError):
    """Exception raised for server-side errors (HTTP 500, 502, 503, 504)."""

    def __str__(self):
        """Improved string representation with helpful message."""
        base_msg = super().__str__()
        return f"{base_msg} - This is a server-side error. Please try again later or contact support if it persists."


class ValidizTimeoutError(ValidizError):
    """Exception raised for request timeouts."""

    def __init__(self, message="Request timed out", timeout=None, **kwargs):
        self.timeout = timeout
        message += f" (after {timeout}s)" if timeout else ""
        super().__init__(message, **kwargs)
