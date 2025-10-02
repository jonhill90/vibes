name: "Example: Simple Feature PRP - User Authentication Endpoint"
description: |

## Purpose
This is a complete example of a simple, single-component feature PRP. Use this as a reference when creating PRPs for straightforward features that don't require multi-agent systems or complex integrations.

---

## Goal
Add a user authentication endpoint to the API that validates JWT tokens and returns user information.

## Why
- **Business Value**: Enables secure user authentication for all API endpoints
- **Integration**: Foundation for role-based access control (RBAC) in future
- **Problems Solved**: Currently no standardized authentication - each endpoint does it differently

## What
A FastAPI endpoint at `/auth/verify` that:
- Accepts JWT token in Authorization header
- Validates token signature and expiration
- Returns user information if valid
- Returns 401 error if invalid/expired

### Success Criteria
- [ ] `/auth/verify` endpoint returns 200 with user info for valid tokens
- [ ] Endpoint returns 401 for invalid tokens
- [ ] Endpoint returns 401 for expired tokens
- [ ] All unit tests pass
- [ ] Integration test with live JWT token succeeds

## Context

### Documentation & References
```yaml
# MUST READ - Include these in your context window
- url: https://fastapi.tiangolo.com/advanced/security/http-basic-auth/
  why: FastAPI authentication patterns

- url: https://pyjwt.readthedocs.io/en/stable/
  why: PyJWT token validation methods

- file: api/auth/middleware.py
  why: Existing JWT secret configuration and middleware patterns

- file: api/routes/users.py
  why: Pattern for user data retrieval from database
```

### Current Structure
```bash
api/
├── auth/
│   ├── __init__.py
│   └── middleware.py       # JWT middleware exists
├── routes/
│   ├── __init__.py
│   └── users.py           # User routes
├── models/
│   └── user.py            # User Pydantic model
└── main.py                # FastAPI app
```

### Desired Structure
```bash
api/
├── auth/
│   ├── __init__.py
│   ├── middleware.py      # Existing JWT middleware
│   └── verify.py          # NEW: Token verification logic
├── routes/
│   ├── __init__.py
│   ├── users.py
│   └── auth.py            # NEW: Auth endpoints
├── models/
│   └── user.py
└── main.py                # MODIFIED: Register auth router
```

### Known Gotchas
```python
# CRITICAL: JWT secret is loaded from environment variable
# See api/auth/middleware.py - uses JWT_SECRET from .env

# PATTERN: All API responses use StandardResponse model
# See api/models/responses.py for structure

# GOTCHA: User IDs in JWT are stored as strings, not integers
# Must convert to int before database query
```

## Implementation

### Task List
```yaml
Task 1: Create token verification logic
ACTION: Build JWT token validation function
FILES: api/auth/verify.py
PATTERN: Mirror middleware.py JWT decoding logic

Task 2: Create auth endpoint
ACTION: Build FastAPI endpoint for token verification
FILES: api/routes/auth.py
PATTERN: Follow users.py router structure

Task 3: Register router
ACTION: Add auth router to main FastAPI app
FILES: api/main.py
PATTERN: Same pattern as user router registration

Task 4: Add tests
ACTION: Create unit and integration tests
FILES: tests/test_auth_verify.py
PATTERN: Follow tests/test_users.py structure
```

### Key Implementation Details
```python
# api/auth/verify.py

import jwt
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class TokenData(BaseModel):
    user_id: int
    email: str
    exp: datetime

async def verify_jwt_token(token: str, secret: str) -> Optional[TokenData]:
    """
    Verify JWT token and extract user data.

    Args:
        token: JWT token string
        secret: JWT secret for verification

    Returns:
        TokenData if valid, None if invalid
    """
    try:
        # PATTERN: Use same algorithm as middleware
        payload = jwt.decode(token, secret, algorithms=["HS256"])

        # GOTCHA: user_id stored as string in token
        user_id = int(payload.get("sub"))
        email = payload.get("email")

        # Validate required fields present
        if not user_id or not email:
            return None

        return TokenData(
            user_id=user_id,
            email=email,
            exp=datetime.fromtimestamp(payload.get("exp"))
        )
    except jwt.ExpiredSignatureError:
        # Token expired
        return None
    except jwt.InvalidTokenError:
        # Invalid token
        return None

# api/routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from api.auth.verify import verify_jwt_token
from api.config import get_settings

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

@router.get("/verify")
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Verify JWT token and return user information.

    Returns:
        User information if token valid

    Raises:
        401: If token invalid or expired
    """
    settings = get_settings()
    token = credentials.credentials

    # Verify token
    token_data = await verify_jwt_token(token, settings.JWT_SECRET)

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    # PATTERN: Return standardized response
    return {
        "user_id": token_data.user_id,
        "email": token_data.email,
        "expires_at": token_data.exp.isoformat()
    }
```

### Integration Points
```yaml
CONFIGURATION:
  - file: api/config.py
  - already_has: JWT_SECRET from environment
  - no_changes_needed: true

ROUTES:
  - file: api/main.py
  - add: app.include_router(auth_router)

DEPENDENCIES:
  - Already in requirements.txt: pyjwt>=2.0.0
```

## Validation

### Level 1: Syntax & Style
```bash
# Lint and type check
ruff check api/auth/verify.py api/routes/auth.py --fix
mypy api/auth/verify.py api/routes/auth.py

# Expected: No errors
```

### Level 2: Unit Tests
```python
# tests/test_auth_verify.py

import pytest
from datetime import datetime, timedelta
import jwt
from api.auth.verify import verify_jwt_token

# Test secret
TEST_SECRET = "test-secret-key"

def create_test_token(user_id: int, email: str, exp_delta: timedelta):
    """Helper to create test JWT tokens"""
    payload = {
        "sub": str(user_id),  # Store as string
        "email": email,
        "exp": datetime.utcnow() + exp_delta
    }
    return jwt.encode(payload, TEST_SECRET, algorithm="HS256")

@pytest.mark.asyncio
async def test_verify_valid_token():
    """Test verification of valid token"""
    token = create_test_token(
        user_id=123,
        email="test@example.com",
        exp_delta=timedelta(hours=1)
    )

    result = await verify_jwt_token(token, TEST_SECRET)

    assert result is not None
    assert result.user_id == 123
    assert result.email == "test@example.com"

@pytest.mark.asyncio
async def test_verify_expired_token():
    """Test verification of expired token"""
    token = create_test_token(
        user_id=123,
        email="test@example.com",
        exp_delta=timedelta(hours=-1)  # Expired
    )

    result = await verify_jwt_token(token, TEST_SECRET)

    assert result is None

@pytest.mark.asyncio
async def test_verify_invalid_token():
    """Test verification of malformed token"""
    result = await verify_jwt_token("invalid.token.here", TEST_SECRET)

    assert result is None

@pytest.mark.asyncio
async def test_verify_wrong_secret():
    """Test verification with wrong secret"""
    token = create_test_token(
        user_id=123,
        email="test@example.com",
        exp_delta=timedelta(hours=1)
    )

    result = await verify_jwt_token(token, "wrong-secret")

    assert result is None
```

```bash
# Run tests
pytest tests/test_auth_verify.py -v

# Expected: All 4 tests pass
```

### Level 3: Integration Test
```bash
# Start the API server
uvicorn api.main:app --reload

# In another terminal, test the endpoint
# First, get a valid token (from your auth system)
export TEST_TOKEN="your.jwt.token.here"

# Test with valid token
curl -X GET http://localhost:8000/auth/verify \
  -H "Authorization: Bearer $TEST_TOKEN"

# Expected response:
# {
#   "user_id": 123,
#   "email": "test@example.com",
#   "expires_at": "2024-01-20T15:30:00"
# }

# Test with invalid token
curl -X GET http://localhost:8000/auth/verify \
  -H "Authorization: Bearer invalid.token"

# Expected: 401 Unauthorized
```

## Final Checklist
- [ ] All unit tests pass (4/4)
- [ ] No linting errors
- [ ] No type errors
- [ ] Integration test with valid token returns user info
- [ ] Integration test with invalid token returns 401
- [ ] Integration test with expired token returns 401
- [ ] Code follows FastAPI patterns in codebase
- [ ] Error messages are clear and helpful

---

## Anti-Patterns to Avoid
- ❌ Don't log JWT tokens - they're sensitive
- ❌ Don't skip expiration validation
- ❌ Don't return detailed error messages (security risk)
- ❌ Don't hardcode JWT secret
- ❌ Don't use different algorithm than middleware

## Notes

This example demonstrates:
- Simple, focused feature scope
- Clear task breakdown
- Validation at multiple levels
- Following existing patterns
- Comprehensive testing
- Security considerations

**Key Takeaway**: Even simple features benefit from comprehensive PRPs. The time spent planning prevents bugs and rework.
