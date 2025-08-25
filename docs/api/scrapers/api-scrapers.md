# API Scrapers

Scrap-E provides specialized scrapers for consuming APIs and web services. These scrapers handle authentication, rate limiting, and data transformation for various API types.

!!! note "Development Status"
    API scrapers are currently in development. This documentation describes the planned interface and features.

## Overview

API scrapers in Scrap-E support:

- **REST APIs** - HTTP-based RESTful services
- **GraphQL APIs** - Query-based GraphQL endpoints  
- **WebSocket APIs** - Real-time WebSocket connections
- **Authentication** - OAuth 1.0/2.0, API keys, JWT tokens
- **Rate Limiting** - Built-in request throttling
- **Pagination** - Automatic page traversal
- **Response Validation** - Schema validation for API responses

## Planned Architecture

### REST API Scraper

```python
from scrap_e.scrapers.api.rest_scraper import RestScraper
from scrap_e.core.config import APIScraperConfig
from scrap_e.core.models import AuthType

# Configuration for REST API
config = APIScraperConfig(
    api_base_url="https://api.example.com",
    api_auth_type=AuthType.BEARER,
    api_key="your-api-token",
    default_timeout=30.0,
    rate_limit_calls=100,
    rate_limit_period=60
)

# Create REST scraper
scraper = RestScraper(config)

# Simple GET request
result = await scraper.scrape("/users", method="GET")

# POST request with data
result = await scraper.scrape(
    "/users",
    method="POST",
    json_data={"name": "John Doe", "email": "john@example.com"}
)

# Query parameters
result = await scraper.scrape(
    "/users",
    params={"page": 1, "limit": 50}
)
```

### GraphQL API Scraper

```python
from scrap_e.scrapers.api.graphql_scraper import GraphQLScraper

# GraphQL configuration
config = APIScraperConfig(
    graphql_endpoint="https://api.example.com/graphql",
    api_auth_type=AuthType.BEARER,
    api_key="your-token"
)

scraper = GraphQLScraper(config)

# GraphQL query
query = """
    query GetUsers($first: Int!) {
        users(first: $first) {
            edges {
                node {
                    id
                    name
                    email
                }
            }
        }
    }
"""

result = await scraper.scrape(
    query=query,
    variables={"first": 10}
)

# GraphQL mutation
mutation = """
    mutation CreateUser($input: UserInput!) {
        createUser(input: $input) {
            id
            name
            email
        }
    }
"""

result = await scraper.scrape(
    query=mutation,
    variables={"input": {"name": "Jane Doe", "email": "jane@example.com"}}
)
```

### WebSocket API Scraper

```python
from scrap_e.scrapers.api.websocket_scraper import WebSocketScraper

# WebSocket configuration
config = APIScraperConfig(
    ws_endpoint="wss://api.example.com/ws",
    ws_ping_interval=30.0,
    ws_pong_timeout=10.0
)

scraper = WebSocketScraper(config)

# Connect and listen for messages
async with scraper.session() as ws:
    # Send subscription message
    await ws.send_json({
        "type": "subscribe",
        "channel": "updates"
    })

    # Listen for messages
    async for message in ws.listen():
        print(f"Received: {message}")

        # Process message
        if message.get("type") == "update":
            await process_update(message["data"])
```

## Authentication Methods

### API Key Authentication

```python
# Header-based API key
config = APIScraperConfig(
    api_auth_type=AuthType.API_KEY,
    api_key="your-api-key",
    auth_header="X-API-Key"  # Custom header name
)

# Query parameter API key
config = APIScraperConfig(
    api_auth_type=AuthType.API_KEY,
    api_key="your-api-key",
    auth_query_param="api_key"
)
```

### Bearer Token Authentication

```python
config = APIScraperConfig(
    api_auth_type=AuthType.BEARER,
    api_key="your-bearer-token"
)

# Results in: Authorization: Bearer your-bearer-token
```

### OAuth 2.0 Authentication

```python
# OAuth 2.0 client credentials flow
config = APIScraperConfig(
    api_auth_type=AuthType.OAUTH2,
    oauth_client_id="your-client-id",
    oauth_client_secret="your-client-secret",
    oauth_token_url="https://api.example.com/oauth/token",
    oauth_scope=["read", "write"]
)

scraper = RestScraper(config)

# Token is automatically obtained and refreshed
result = await scraper.scrape("/protected-resource")
```

### JWT Token Authentication

```python
config = APIScraperConfig(
    api_auth_type=AuthType.JWT,
    jwt_secret="your-jwt-secret",
    jwt_algorithm="HS256",
    jwt_payload={"user_id": 123, "role": "admin"}
)
```

## Rate Limiting

### Built-in Rate Limiting

```python
config = APIScraperConfig(
    rate_limit_calls=100,      # 100 requests
    rate_limit_period=60,      # Per 60 seconds
    rate_limit_burst=10        # Allow bursts of 10
)

scraper = RestScraper(config)

# Rate limiting is automatically applied
urls = [f"/users/{i}" for i in range(200)]
results = await scraper.scrape_multiple(urls)  # Respects rate limits
```

### Adaptive Rate Limiting

```python
# Responds to HTTP 429 (Too Many Requests)
config = APIScraperConfig(
    adaptive_rate_limit=True,
    rate_limit_backoff_factor=2.0,  # Exponential backoff
    rate_limit_max_delay=300        # Max 5 minute delay
)

scraper = RestScraper(config)

# Automatically slows down when rate limited
result = await scraper.scrape("/rate-limited-endpoint")
```

## Pagination Support

### Automatic Pagination

```python
from scrap_e.core.models import PaginationConfig

# Offset-based pagination
pagination_config = PaginationConfig(
    enabled=True,
    pagination_type="offset",
    page_param="offset",
    page_size_param="limit",
    page_size=50,
    max_pages=100
)

config = APIScraperConfig(pagination=pagination_config)
scraper = RestScraper(config)

# Scrape all pages automatically
all_data = await scraper.scrape_all_pages("/users")
```

### Cursor-based Pagination

```python
pagination_config = PaginationConfig(
    enabled=True,
    pagination_type="cursor",
    cursor_param="cursor",
    page_size_param="limit",
    page_size=25
)

# Automatically follows cursor pagination
all_data = await scraper.scrape_all_pages("/timeline")
```

### Link Header Pagination

```python
pagination_config = PaginationConfig(
    enabled=True,
    pagination_type="link_header",
    max_pages=50
)

# Follows RFC 5988 Link headers (GitHub style)
all_data = await scraper.scrape_all_pages("/repositories")
```

## Response Processing

### Automatic JSON Parsing

```python
config = APIScraperConfig(
    parse_json_automatically=True,
    validate_response_schema=True
)

scraper = RestScraper(config)

# Automatic JSON parsing and validation
result = await scraper.scrape("/api/data")
data = result.data.json_data  # Parsed JSON object
```

### Schema Validation

```python
from pydantic import BaseModel
from typing import List

class UserModel(BaseModel):
    id: int
    name: str
    email: str

class UsersResponse(BaseModel):
    users: List[UserModel]
    total: int

# Configure response validation
config = APIScraperConfig(
    response_model=UsersResponse,
    validate_response_schema=True
)

scraper = RestScraper(config)

result = await scraper.scrape("/users")
validated_data = result.data.validated_response  # UsersResponse instance
```

### Custom Response Processing

```python
def process_api_response(response_data: dict) -> dict:
    """Custom response processor."""
    # Extract nested data
    if "data" in response_data:
        response_data = response_data["data"]

    # Normalize field names
    for item in response_data.get("items", []):
        if "created_at" in item:
            item["created_date"] = item.pop("created_at")

    return response_data

config = APIScraperConfig(
    response_processor=process_api_response
)
```

## Error Handling

### API-Specific Errors

```python
from scrap_e.core.exceptions import (
    APIError,
    AuthenticationError,
    RateLimitError,
    ValidationError
)

try:
    result = await scraper.scrape("/protected-endpoint")
except AuthenticationError as e:
    print(f"Auth failed: {e}")
    # Refresh token or re-authenticate

except RateLimitError as e:
    print(f"Rate limited: {e}")
    print(f"Retry after: {e.retry_after} seconds")

except APIError as e:
    print(f"API error: {e}")
    print(f"Status code: {e.status_code}")
    print(f"Error response: {e.response_data}")
```

### Retry Logic for APIs

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((RateLimitError, APIError))
)
async def resilient_api_call(endpoint: str):
    return await scraper.scrape(endpoint)

# Usage
result = await resilient_api_call("/flaky-endpoint")
```

## Streaming and Real-time Data

### Server-Sent Events (SSE)

```python
from scrap_e.scrapers.api.sse_scraper import SSEScraper

config = APIScraperConfig(
    sse_endpoint="https://api.example.com/events",
    api_auth_type=AuthType.BEARER,
    api_key="your-token"
)

scraper = SSEScraper(config)

# Stream events
async for event in scraper.stream("/live-updates"):
    print(f"Event: {event.event}")
    print(f"Data: {event.data}")

    if event.event == "user_update":
        await process_user_update(event.data)
```

### WebSocket Streaming

```python
async def stream_websocket_data():
    scraper = WebSocketScraper(config)

    async with scraper.session() as ws:
        # Send subscription
        await ws.send_json({
            "action": "subscribe",
            "channels": ["trades", "orders"]
        })

        # Process streaming data
        async for message in ws.listen():
            if message["channel"] == "trades":
                await process_trade(message["data"])
            elif message["channel"] == "orders":
                await process_order(message["data"])
```

## Configuration Examples

### Production API Configuration

```yaml
# api_config.yaml
api:
  base_url: "https://api.production.com/v1"
  auth_type: oauth2
  client_id: "${OAUTH_CLIENT_ID}"
  client_secret: "${OAUTH_CLIENT_SECRET}"
  token_url: "https://auth.production.com/oauth/token"

rate_limit:
  calls: 1000
  period: 3600  # 1 hour
  burst: 50
  adaptive: true

retry:
  max_attempts: 5
  initial_delay: 1.0
  max_delay: 60.0

pagination:
  enabled: true
  type: "offset"
  page_size: 100
  max_pages: 500

cache:
  enabled: true
  ttl: 300  # 5 minutes
```

### Development API Configuration

```yaml
# dev_config.yaml
api:
  base_url: "https://api.dev.com/v1"
  auth_type: api_key
  api_key: "${DEV_API_KEY}"

rate_limit:
  calls: 100
  period: 60

debug: true
log_requests: true
log_responses: true
```

## Testing API Scrapers

### Unit Tests

```python
import pytest
from unittest.mock import AsyncMock, patch
from scrap_e.scrapers.api.rest_scraper import RestScraper

@pytest.mark.asyncio
async def test_rest_scraper_get():
    config = APIScraperConfig(api_base_url="https://api.example.com")
    scraper = RestScraper(config)

    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = AsyncMock()
        mock_response.json.return_value = {"users": [{"id": 1, "name": "John"}]}
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = await scraper.scrape("/users")

        assert result.success
        assert result.data.json_data["users"][0]["name"] == "John"

@pytest.mark.asyncio
async def test_rest_scraper_authentication():
    config = APIScraperConfig(
        api_base_url="https://api.example.com",
        api_auth_type=AuthType.BEARER,
        api_key="test-token"
    )
    scraper = RestScraper(config)

    with patch('httpx.AsyncClient.get') as mock_get:
        await scraper.scrape("/protected")

        # Verify Authorization header was set
        call_kwargs = mock_get.call_args[1]
        headers = call_kwargs.get("headers", {})
        assert headers.get("Authorization") == "Bearer test-token"
```

### Integration Tests

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_api_integration():
    """Test against real API (with test credentials)."""
    config = APIScraperConfig(
        api_base_url="https://jsonplaceholder.typicode.com",
        default_timeout=10.0
    )

    scraper = RestScraper(config)

    # Test GET
    result = await scraper.scrape("/users")
    assert result.success
    assert len(result.data.json_data) > 0

    # Test pagination
    users_page_1 = await scraper.scrape("/users?_page=1&_limit=5")
    users_page_2 = await scraper.scrape("/users?_page=2&_limit=5")

    assert len(users_page_1.data.json_data) == 5
    assert len(users_page_2.data.json_data) == 5
    assert users_page_1.data.json_data[0]["id"] != users_page_2.data.json_data[0]["id"]
```

## Performance Optimization

### Connection Pooling

```python
config = APIScraperConfig(
    connection_pool_size=20,
    connection_pool_max_size=100,
    connection_keep_alive=30.0
)

# Reuse connections across multiple requests
scraper = RestScraper(config)
```

### Caching

```python
from scrap_e.core.models import CacheConfig

cache_config = CacheConfig(
    enabled=True,
    backend="redis",  # or "memory", "disk"
    ttl_seconds=300,
    cache_key_prefix="api_cache"
)

config = APIScraperConfig(cache=cache_config)
scraper = RestScraper(config)

# Responses are automatically cached
result1 = await scraper.scrape("/slow-endpoint")  # Cache miss
result2 = await scraper.scrape("/slow-endpoint")  # Cache hit
```

### Batch Operations

```python
# Batch multiple API calls
endpoints = [f"/users/{i}" for i in range(1, 101)]

# Process in batches to respect rate limits
batch_size = 10
results = []

for i in range(0, len(endpoints), batch_size):
    batch = endpoints[i:i + batch_size]
    batch_results = await scraper.scrape_multiple(batch)
    results.extend(batch_results)

    # Optional delay between batches
    if i + batch_size < len(endpoints):
        await asyncio.sleep(1.0)
```

This comprehensive API scraper documentation covers the planned features and architecture for handling various types of APIs and web services within the Scrap-E framework.
