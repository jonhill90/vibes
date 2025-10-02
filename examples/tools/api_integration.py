"""
Example: External API Integration Pattern

This module demonstrates best practices for integrating external REST APIs in Vibes.

Key Patterns Demonstrated:
- Async HTTP client with httpx
- Configuration management with environment variables
- Error handling and retry logic with tenacity
- Rate limiting to respect API limits
- Request/response validation with Pydantic
- Proper resource cleanup with context managers

Adapt this pattern for any external API integration (Stripe, OpenAI, etc.)
"""

import os
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

import httpx
from pydantic import BaseModel, Field, validator
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)


# ==============================================================================
# Configuration
# ==============================================================================

class APIConfig:
    """API configuration from environment variables"""

    def __init__(self):
        self.API_KEY = os.getenv("EXTERNAL_API_KEY")
        if not self.API_KEY:
            raise ValueError("EXTERNAL_API_KEY environment variable required")

        self.BASE_URL = os.getenv("EXTERNAL_API_BASE_URL", "https://api.example.com")
        self.TIMEOUT = int(os.getenv("EXTERNAL_API_TIMEOUT", "30"))
        self.MAX_RETRIES = int(os.getenv("EXTERNAL_API_MAX_RETRIES", "3"))
        self.RATE_LIMIT_PER_MINUTE = int(os.getenv("EXTERNAL_API_RATE_LIMIT", "60"))


# ==============================================================================
# Data Models (Pydantic for validation)
# ==============================================================================

class ResponseStatus(str, Enum):
    """API response status enum"""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"


class APIRequest(BaseModel):
    """Base API request model"""
    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(10, ge=1, le=100)
    include_metadata: bool = Field(False)

    @validator("query")
    def query_must_not_be_empty(cls, v):
        """Ensure query is not just whitespace"""
        if not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class APIResponse(BaseModel):
    """Base API response model"""
    status: ResponseStatus
    data: List[Dict[str, Any]]
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None


# ==============================================================================
# Custom Exceptions
# ==============================================================================

class APIError(Exception):
    """Base API error"""
    pass


class RateLimitError(APIError):
    """Rate limit exceeded"""
    pass


class AuthenticationError(APIError):
    """Authentication failed"""
    pass


class ValidationError(APIError):
    """Request validation failed"""
    pass


# ==============================================================================
# Rate Limiter
# ==============================================================================

class RateLimiter:
    """
    Simple token bucket rate limiter.

    Ensures we don't exceed API rate limits.
    """

    def __init__(self, max_calls: int, period: int = 60):
        """
        Args:
            max_calls: Maximum calls allowed
            period: Time period in seconds (default: 60)
        """
        self.max_calls = max_calls
        self.period = period
        self.calls: List[float] = []

    async def acquire(self):
        """Wait if necessary to respect rate limit"""
        now = asyncio.get_event_loop().time()

        # Remove calls outside the time window
        self.calls = [call for call in self.calls if now - call < self.period]

        # If at limit, wait until oldest call expires
        if len(self.calls) >= self.max_calls:
            sleep_time = self.period - (now - self.calls[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)

        # Record this call
        self.calls.append(asyncio.get_event_loop().time())


# ==============================================================================
# API Client
# ==============================================================================

class ExternalAPIClient:
    """
    Async API client with error handling, retries, and rate limiting.

    Usage:
        async with ExternalAPIClient(api_key="xxx") as client:
            result = await client.search("query")
    """

    def __init__(self, api_key: Optional[str] = None, config: Optional[APIConfig] = None):
        """
        Initialize API client.

        Args:
            api_key: API key (optional, reads from config if not provided)
            config: APIConfig instance (optional, creates default if not provided)
        """
        self.config = config or APIConfig()
        self.api_key = api_key or self.config.API_KEY

        # Create HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.config.BASE_URL,
            timeout=self.config.TIMEOUT,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": "Vibes-API-Client/1.0"
            }
        )

        # Rate limiter
        self.rate_limiter = RateLimiter(
            max_calls=self.config.RATE_LIMIT_PER_MINUTE
        )

    async def __aenter__(self):
        """Context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup"""
        await self.client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, RateLimitError))
    )
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> httpx.Response:
        """
        Make HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for httpx request

        Returns:
            httpx.Response object

        Raises:
            RateLimitError: Rate limit exceeded
            AuthenticationError: Invalid API key
            APIError: Other API errors
        """
        # CRITICAL: Respect rate limits
        await self.rate_limiter.acquire()

        try:
            response = await self.client.request(method, endpoint, **kwargs)

            # Handle specific status codes
            if response.status_code == 429:
                # Rate limit exceeded - will trigger retry
                raise RateLimitError("Rate limit exceeded, retrying...")

            elif response.status_code == 401:
                # Authentication failed - don't retry
                raise AuthenticationError("Invalid API key")

            elif response.status_code == 400:
                # Validation error - don't retry
                error_detail = response.json().get("detail", "Unknown error")
                raise ValidationError(f"Request validation failed: {error_detail}")

            elif response.status_code >= 500:
                # Server error - will trigger retry
                raise APIError(f"Server error: {response.status_code}")

            # Raise for other 4xx errors (won't retry)
            elif response.status_code >= 400:
                raise APIError(f"API error: {response.status_code}")

            return response

        except httpx.HTTPError as e:
            # Network errors - will trigger retry
            raise APIError(f"HTTP error: {str(e)}")

    async def search(
        self,
        query: str,
        limit: int = 10,
        include_metadata: bool = False
    ) -> APIResponse:
        """
        Search API endpoint.

        Args:
            query: Search query
            limit: Maximum results
            include_metadata: Include metadata in response

        Returns:
            APIResponse with results

        Raises:
            ValidationError: Invalid request parameters
            APIError: API request failed
        """
        # Validate request with Pydantic
        request_data = APIRequest(
            query=query,
            limit=limit,
            include_metadata=include_metadata
        )

        # Make API request
        response = await self._make_request(
            "POST",
            "/search",
            json=request_data.dict()
        )

        # Parse and validate response
        response_data = response.json()
        return APIResponse(**response_data)

    async def get_item(self, item_id: str) -> Dict[str, Any]:
        """
        Get single item by ID.

        Args:
            item_id: Item identifier

        Returns:
            Item data dict

        Raises:
            APIError: Item not found or request failed
        """
        response = await self._make_request("GET", f"/items/{item_id}")
        return response.json()

    async def create_item(self, item_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new item.

        Args:
            item_data: Item data

        Returns:
            Created item data

        Raises:
            ValidationError: Invalid item data
            APIError: Creation failed
        """
        response = await self._make_request(
            "POST",
            "/items",
            json=item_data
        )
        return response.json()

    async def health_check(self) -> bool:
        """
        Check if API is healthy.

        Returns:
            True if API responsive, False otherwise
        """
        try:
            response = await self._make_request("GET", "/health")
            return response.status_code == 200
        except:
            return False


# ==============================================================================
# Example Usage
# ==============================================================================

async def example_usage():
    """
    Example of using the API client.

    This would typically be in a different file/module.
    """
    # Initialize client with context manager (ensures cleanup)
    async with ExternalAPIClient() as client:

        # Example 1: Search
        print("Searching...")
        results = await client.search(
            query="machine learning",
            limit=5,
            include_metadata=True
        )
        print(f"Found {len(results.data)} results")
        print(f"Status: {results.status}")

        # Example 2: Get specific item
        print("\nGetting item...")
        item = await client.get_item("item-123")
        print(f"Item: {item}")

        # Example 3: Create item
        print("\nCreating item...")
        new_item = await client.create_item({
            "name": "Test Item",
            "description": "Created via API"
        })
        print(f"Created: {new_item}")

        # Example 4: Health check
        print("\nHealth check...")
        is_healthy = await client.health_check()
        print(f"API healthy: {is_healthy}")


# ==============================================================================
# Testing Pattern
# ==============================================================================

async def test_with_mock():
    """
    Example of testing with mocked HTTP client.

    In actual tests, use pytest with pytest-asyncio and respx for mocking.
    """
    import respx
    from httpx import Response

    # Mock API responses
    with respx.mock:
        # Mock search endpoint
        respx.post("https://api.example.com/search").mock(
            return_value=Response(
                200,
                json={
                    "status": "success",
                    "data": [{"id": "1", "title": "Result 1"}],
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        )

        # Use client normally - requests will be mocked
        async with ExternalAPIClient(api_key="test-key") as client:
            results = await client.search("test query")
            assert results.status == ResponseStatus.SUCCESS
            assert len(results.data) == 1


if __name__ == "__main__":
    # Run example
    asyncio.run(example_usage())
