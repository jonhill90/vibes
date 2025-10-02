# API Documentation

Complete API reference for [Project Name].

## Base URL

```
Production: https://api.example.com/v1
Staging:    https://staging-api.example.com/v1
Local:      http://localhost:8000/v1
```

## Authentication

All API endpoints require authentication using Bearer tokens.

### Getting an API Key

1. Sign up at [dashboard.example.com](https://dashboard.example.com)
2. Navigate to **Settings** → **API Keys**
3. Click **Create New Key**
4. Copy your API key immediately (shown only once)

### Using Your API Key

Include your API key in the `Authorization` header:

```bash
Authorization: Bearer YOUR_API_KEY
```

**Example:**
```bash
curl -X GET https://api.example.com/v1/users \
  -H "Authorization: Bearer sk_live_abc123..."
```

## Rate Limiting

API requests are rate limited to prevent abuse.

| Tier       | Requests/Minute | Requests/Hour |
|------------|----------------|---------------|
| Free       | 60             | 1,000         |
| Pro        | 600            | 10,000        |
| Enterprise | Unlimited      | Unlimited     |

### Rate Limit Headers

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1640995200
```

### Handling Rate Limits

When rate limited, you'll receive a `429 Too Many Requests` response:

```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Try again in 45 seconds.",
    "retry_after": 45
  }
}
```

Implement exponential backoff when you receive a 429 response.

## Response Format

All responses follow a consistent JSON structure.

### Success Response

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "validation_error",
    "message": "Invalid email address",
    "details": {
      "field": "email",
      "value": "invalid@"
    }
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `invalid_request` | 400 | Request validation failed |
| `unauthorized` | 401 | Invalid or missing API key |
| `forbidden` | 403 | Insufficient permissions |
| `not_found` | 404 | Resource not found |
| `rate_limit_exceeded` | 429 | Too many requests |
| `server_error` | 500 | Internal server error |
| `service_unavailable` | 503 | Service temporarily unavailable |

---

## Endpoints

### Users

#### List Users

Get a paginated list of users.

**Endpoint:** `GET /users`

**Query Parameters:**

| Parameter | Type    | Required | Default | Description |
|-----------|---------|----------|---------|-------------|
| `page`    | integer | No       | 1       | Page number |
| `limit`   | integer | No       | 20      | Items per page (max: 100) |
| `sort`    | string  | No       | created_at | Sort field |
| `order`   | string  | No       | desc    | Sort order (asc/desc) |
| `search`  | string  | No       | -       | Search term |

**Request Example:**

```bash
curl -X GET "https://api.example.com/v1/users?page=1&limit=10&sort=created_at&order=desc" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response Example (200 OK):**

```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": "usr_abc123",
        "email": "user@example.com",
        "name": "John Doe",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 100,
      "total_pages": 10
    }
  }
}
```

**Error Responses:**

- `401 Unauthorized`: Invalid API key
- `429 Too Many Requests`: Rate limit exceeded

---

#### Get User

Retrieve a single user by ID.

**Endpoint:** `GET /users/{user_id}`

**Path Parameters:**

| Parameter | Type   | Required | Description |
|-----------|--------|----------|-------------|
| `user_id` | string | Yes      | User ID     |

**Request Example:**

```bash
curl -X GET "https://api.example.com/v1/users/usr_abc123" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response Example (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": "usr_abc123",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "metadata": {
      "plan": "pro",
      "credits": 100
    }
  }
}
```

**Error Responses:**

- `404 Not Found`: User does not exist

---

#### Create User

Create a new user.

**Endpoint:** `POST /users`

**Request Body:**

| Field      | Type    | Required | Description |
|------------|---------|----------|-------------|
| `email`    | string  | Yes      | Valid email address |
| `name`     | string  | Yes      | Full name (2-100 chars) |
| `password` | string  | Yes      | Password (min 8 chars) |
| `metadata` | object  | No       | Custom metadata |

**Request Example:**

```bash
curl -X POST "https://api.example.com/v1/users" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "name": "Jane Doe",
    "password": "SecurePassword123!",
    "metadata": {
      "referral": "friend"
    }
  }'
```

**Response Example (201 Created):**

```json
{
  "success": true,
  "data": {
    "id": "usr_xyz789",
    "email": "newuser@example.com",
    "name": "Jane Doe",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

**Error Responses:**

- `400 Bad Request`: Validation failed (email invalid, password too short, etc.)
- `409 Conflict`: User with this email already exists

---

#### Update User

Update an existing user.

**Endpoint:** `PUT /users/{user_id}`

**Path Parameters:**

| Parameter | Type   | Required | Description |
|-----------|--------|----------|-------------|
| `user_id` | string | Yes      | User ID     |

**Request Body:**

| Field      | Type   | Required | Description |
|------------|--------|----------|-------------|
| `name`     | string | No       | Updated name |
| `email`    | string | No       | Updated email |
| `metadata` | object | No       | Updated metadata |

**Request Example:**

```bash
curl -X PUT "https://api.example.com/v1/users/usr_abc123" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Smith"
  }'
```

**Response Example (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": "usr_abc123",
    "email": "user@example.com",
    "name": "John Smith",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-16T14:25:00Z"
  }
}
```

**Error Responses:**

- `404 Not Found`: User does not exist
- `400 Bad Request`: Validation failed

---

#### Delete User

Delete a user (soft delete - can be recovered).

**Endpoint:** `DELETE /users/{user_id}`

**Path Parameters:**

| Parameter | Type   | Required | Description |
|-----------|--------|----------|-------------|
| `user_id` | string | Yes      | User ID     |

**Request Example:**

```bash
curl -X DELETE "https://api.example.com/v1/users/usr_abc123" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Response Example (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": "usr_abc123",
    "deleted": true,
    "deleted_at": "2024-01-16T15:00:00Z"
  }
}
```

**Error Responses:**

- `404 Not Found`: User does not exist

---

### Items

*(Repeat similar structure for other resources)*

---

## Pagination

All list endpoints support pagination.

**Query Parameters:**

- `page` (integer): Page number (default: 1)
- `limit` (integer): Items per page (default: 20, max: 100)

**Response Structure:**

```json
{
  "data": { ... },
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

**Pagination Links:**

```http
Link: <https://api.example.com/v1/users?page=2>; rel="next",
      <https://api.example.com/v1/users?page=8>; rel="last"
```

---

## Filtering

List endpoints support filtering by various fields.

**Examples:**

```bash
# Filter by date range
GET /users?created_after=2024-01-01&created_before=2024-12-31

# Filter by status
GET /items?status=active

# Combine filters
GET /users?plan=pro&created_after=2024-01-01
```

---

## Sorting

Customize result ordering with sort parameters.

**Examples:**

```bash
# Sort by created date (descending)
GET /users?sort=created_at&order=desc

# Sort by name (ascending)
GET /users?sort=name&order=asc

# Multiple sort fields
GET /users?sort=status,-created_at  # status asc, created_at desc
```

---

## Searching

Full-text search available on applicable endpoints.

**Examples:**

```bash
# Search users by name or email
GET /users?search=john

# Search items by title or description
GET /items?search=tutorial
```

---

## Webhooks

Subscribe to real-time events via webhooks.

### Supported Events

- `user.created` - New user created
- `user.updated` - User updated
- `user.deleted` - User deleted
- `item.created` - New item created

### Webhook Payload

```json
{
  "event": "user.created",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "id": "usr_abc123",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

### Signature Verification

Verify webhook signatures using HMAC-SHA256:

```python
import hmac
import hashlib

def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)
```

---

## Code Examples

### Python

```python
import requests

API_KEY = "your_api_key"
BASE_URL = "https://api.example.com/v1"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# List users
response = requests.get(f"{BASE_URL}/users", headers=headers)
users = response.json()

# Create user
data = {
    "email": "new@example.com",
    "name": "New User",
    "password": "SecurePass123!"
}
response = requests.post(f"{BASE_URL}/users", json=data, headers=headers)
new_user = response.json()
```

### JavaScript

```javascript
const API_KEY = 'your_api_key';
const BASE_URL = 'https://api.example.com/v1';

const headers = {
  'Authorization': `Bearer ${API_KEY}`,
  'Content-Type': 'application/json'
};

// List users
const response = await fetch(`${BASE_URL}/users`, { headers });
const users = await response.json();

// Create user
const data = {
  email: 'new@example.com',
  name: 'New User',
  password: 'SecurePass123!'
};
const createResponse = await fetch(`${BASE_URL}/users`, {
  method: 'POST',
  headers,
  body: JSON.stringify(data)
});
const newUser = await createResponse.json();
```

---

## SDKs

Official SDKs available for:

- **Python**: `pip install example-api-client`
- **JavaScript/TypeScript**: `npm install @example/api-client`
- **Ruby**: `gem install example-api`
- **Go**: `go get github.com/example/go-client`

---

## Support

- 📧 API Support: api-support@example.com
- 📚 API Status: [status.example.com](https://status.example.com)
- 💬 Community: [Discord](https://discord.gg/example)
- 🐛 Report Issues: [GitHub](https://github.com/example/api-issues)

---

Last updated: 2024-01-15
