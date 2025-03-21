from typing import Dict, Any, List, Optional, Union


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
        self.api_key = api_key
        self.api_base_url = api_base_url
    
    def _get_headers(self) -> Dict[str, str]:
        """
        Get headers for API requests.
        
        Returns:
            Dict containing the X-API-Key header
        """
        if not self.api_key:
            raise ValueError("API key is required for API endpoints")
        
        return {"X-API-Key": self.api_key} 