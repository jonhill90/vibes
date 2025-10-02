name: "Tool Integration Template - For APIs and External Tools"
description: |

## Purpose
Template for integrating external tools, APIs, and services into Vibes. Use this when adding third-party integrations, MCP servers, or external API connections.

## Core Principles
1. **Context is King**: Include ALL API documentation and authentication details
2. **Validation Loops**: Test with both mocked and live API calls
3. **Error Handling**: Handle rate limits, timeouts, and API failures gracefully
4. **Security First**: Never hardcode credentials, use environment variables

---

## Goal
[Specific tool or API to integrate]

Example: "Integrate Stripe payment API for subscription management with webhook support"

## Why
- **Business Value**: [What capabilities does this unlock?]
- **User Impact**: [How will users benefit?]
- **Integration Value**: [How does this complement existing features?]

## What
[Detailed description of the integration including key endpoints and operations]

### Success Criteria
- [ ] [Specific integration milestone 1]
- [ ] [Specific integration milestone 2]
- [ ] [Authentication working correctly]
- [ ] [Error handling implemented]
- [ ] [Rate limiting respected]

## Context

### API Documentation
```yaml
# MUST READ - Critical API resources
- url: [Official API documentation URL]
  sections:
    - Authentication: [Link to auth section]
    - Endpoints: [Link to endpoint reference]
    - Rate Limits: [Link to rate limit docs]
    - Error Codes: [Link to error documentation]

- url: [API SDK/client library documentation]
  why: [Official client usage patterns]

- url: [Code examples repository]
  why: [Reference implementations]
```

### Authentication Setup
```yaml
AUTH_TYPE: [API Key | OAuth2 | JWT | Basic Auth]

REQUIRED_CREDENTIALS:
  - ENV_VAR: API_KEY
    description: [Where to obtain, how to generate]
    example: sk_live_xxx...

  - ENV_VAR: API_SECRET (if needed)
    description: [Secret key details]

OAUTH_FLOW (if applicable):
  - authorization_url: [URL]
  - token_url: [URL]
  - scopes: [Required scopes]
```

### Current Structure
```bash
# Relevant current codebase
project/
├── tools/
│   └── existing_tool.py
└── config/
    └── settings.py
```

### Desired Structure
```bash
# What will be added
project/
├── tools/
│   ├── existing_tool.py
│   ├── new_api_client.py      # NEW: API client wrapper
│   └── new_api_models.py      # NEW: Pydantic models for validation
├── config/
│   └── settings.py            # MODIFIED: API configuration
├── tests/
│   └── test_new_api.py        # NEW: Tests with mocked API
└── .env.example               # MODIFIED: Add API credentials template
```

### Known Gotchas
```python
# CRITICAL: API-specific quirks and limitations
# Example: This API has rate limit of 100 req/minute
# Example: OAuth tokens expire after 1 hour - implement refresh
# Example: API uses cursor-based pagination, not offset/limit
# Example: Webhook signatures must be verified with HMAC-SHA256

# PATTERN: How similar tools are integrated
# See tools/existing_api.py for async HTTP client pattern
# See tools/webhook_handler.py for signature verification
```

## Implementation

### Task List
```yaml
Task 1: Set up configuration and environment
ACTION: Add API credentials to settings
FILES:
  - config/settings.py: Add API configuration
  - .env.example: Document required environment variables

Task 2: Create API client wrapper
ACTION: Build async API client with error handling
FILES:
  - tools/new_api_client.py: Main client class
PATTERN: Mirror tools/existing_api.py structure

Task 3: Create data models
ACTION: Define Pydantic models for request/response validation
FILES:
  - tools/new_api_models.py: Request and response models

Task 4: Implement authentication
ACTION: Set up authentication flow (API key/OAuth)
FILES:
  - tools/new_api_client.py: Add auth methods
PATTERN: Follow OAuth pattern in tools/auth_handler.py (if exists)

Task 5: Add error handling
ACTION: Handle rate limits, timeouts, API errors
FILES:
  - tools/new_api_client.py: Add retry logic and error handling

Task 6: Create tests
ACTION: Write unit tests with mocked API responses
FILES:
  - tests/test_new_api.py: Comprehensive test suite
```

### API Client Implementation
```python
# Pseudocode for async API client

import httpx
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential

class APIClient:
    def __init__(self, api_key: str, base_url: str = "https://api.example.com"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> dict:
        """Make API request with retry logic"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # CRITICAL: Add rate limiting
        await self._rate_limit_check()

        response = await self.client.request(
            method=method,
            url=f"{self.base_url}/{endpoint}",
            headers=headers,
            **kwargs
        )

        # PATTERN: Structured error handling
        if response.status_code == 429:
            raise RateLimitError("Rate limit exceeded")
        elif response.status_code >= 400:
            raise APIError(f"API error: {response.status_code}")

        return response.json()

    async def _rate_limit_check(self):
        """Implement rate limiting logic"""
        # Example: Token bucket or sliding window
        pass
```

### Integration Points
```yaml
CONFIGURATION:
  - file: config/settings.py
  - add: |
      API_KEY = os.getenv('API_KEY')
      API_BASE_URL = os.getenv('API_BASE_URL', 'https://api.example.com')
      API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))

ENVIRONMENT:
  - file: .env.example
  - add: |
      # API Integration
      API_KEY=your_api_key_here
      API_BASE_URL=https://api.example.com
      API_TIMEOUT=30

DEPENDENCIES:
  - Add to requirements.txt:
    - httpx>=0.24.0
    - tenacity>=8.2.0
    - pydantic>=2.0.0

WEBHOOKS (if applicable):
  - Create endpoint: /webhooks/api_name
  - Verify signatures: Use HMAC-SHA256
  - Handle async processing
```

## Validation

### Level 1: Syntax & Type Checking
```bash
# Lint and type check
ruff check tools/new_api_client.py --fix
mypy tools/new_api_client.py

# Expected: No errors
```

### Level 2: Unit Tests (Mocked API)
```python
# tests/test_new_api.py

import pytest
from unittest.mock import AsyncMock, patch
from tools.new_api_client import APIClient

@pytest.mark.asyncio
async def test_successful_request():
    """Test successful API request"""
    async with APIClient(api_key="test_key") as client:
        with patch.object(client.client, 'request') as mock_request:
            mock_request.return_value.status_code = 200
            mock_request.return_value.json.return_value = {"status": "success"}

            result = await client.make_request("GET", "endpoint")
            assert result["status"] == "success"

@pytest.mark.asyncio
async def test_rate_limit_error():
    """Test rate limit handling"""
    async with APIClient(api_key="test_key") as client:
        with patch.object(client.client, 'request') as mock_request:
            mock_request.return_value.status_code = 429

            with pytest.raises(RateLimitError):
                await client.make_request("GET", "endpoint")

@pytest.mark.asyncio
async def test_retry_logic():
    """Test automatic retries on transient failures"""
    # Mock failing twice, then succeeding
    async with APIClient(api_key="test_key") as client:
        # Test implementation
        pass
```

```bash
# Run mocked tests
pytest tests/test_new_api.py -v

# Expected: All tests pass
```

### Level 3: Integration Test (Live API - Optional)
```bash
# Test with real API (use test/sandbox environment)
# IMPORTANT: Use test credentials, not production

# Set test environment variables
export API_KEY=test_sk_xxx
export API_BASE_URL=https://sandbox.api.example.com

# Run integration test
pytest tests/test_new_api_integration.py -v --integration

# Expected: Live API calls succeed in sandbox
```

### Level 4: Error Handling Validation
```bash
# Test error scenarios
# 1. Invalid API key
# 2. Rate limit exceeded
# 3. Network timeout
# 4. Malformed response

# Each should fail gracefully with appropriate error messages
```

## Final Checklist
- [ ] API client implemented with async support
- [ ] Authentication working (API key/OAuth)
- [ ] Rate limiting implemented
- [ ] Retry logic for transient failures
- [ ] All error cases handled gracefully
- [ ] Pydantic models validate all responses
- [ ] Unit tests pass with mocked API
- [ ] Integration tests pass (if applicable)
- [ ] No credentials committed to repo
- [ ] .env.example updated with all required variables
- [ ] Documentation includes setup instructions

---

## Anti-Patterns to Avoid
- ❌ Don't hardcode API keys or secrets
- ❌ Don't skip rate limiting - you'll get banned
- ❌ Don't ignore retry logic for transient failures
- ❌ Don't use sync HTTP clients in async code
- ❌ Don't skip webhook signature verification
- ❌ Don't test against production API - use sandbox
- ❌ Don't commit .env files with real credentials
- ❌ Don't assume API responses are always valid - validate with Pydantic

## Common API Patterns

### Pagination
```python
async def get_all_items(self):
    """Handle cursor/offset pagination"""
    all_items = []
    cursor = None

    while True:
        response = await self.make_request(
            "GET",
            "items",
            params={"cursor": cursor} if cursor else {}
        )
        all_items.extend(response["items"])

        if not response.get("has_more"):
            break
        cursor = response.get("next_cursor")

    return all_items
```

### Webhook Verification
```python
import hmac
import hashlib

def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify webhook signature"""
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)
```
