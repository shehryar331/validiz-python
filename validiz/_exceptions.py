class ValidizError(Exception):
    """Base exception for Validiz API errors."""
    
    def __init__(self, message, status_code=None, error_code=None, details=None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        super().__init__(message)


class ValidizAuthError(ValidizError):
    """Exception raised for authentication errors."""
    pass


class ValidizRateLimitError(ValidizError):
    """Exception raised when API rate limits are exceeded."""
    pass


class ValidizValidationError(ValidizError):
    """Exception raised for validation errors."""
    pass


class ValidizNotFoundError(ValidizError):
    """Exception raised when a resource is not found."""
    pass


class ValidizConnectionError(ValidizError):
    """Exception raised for connection errors."""
    pass 