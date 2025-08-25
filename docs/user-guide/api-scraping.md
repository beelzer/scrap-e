# API Scraping Guide

Comprehensive guide to scraping APIs using Scrap-E's HTTP scraper with API-specific patterns.

## Overview

API scraping involves programmatically accessing REST APIs, GraphQL endpoints, and WebSocket connections to extract structured data. Scrap-E's `HttpScraper` provides excellent support for API interactions.

## REST API Scraping

### Basic API Requests

```python
import asyncio
from scrap_e.scrapers.web import HttpScraper

async def basic_api_scraping():
    scraper = HttpScraper()

    # GET request
    result = await scraper.scrape(
        "https://jsonplaceholder.typicode.com/posts/1",
        headers={"Accept": "application/json"}
    )

    if result.success:
        print(f"Status: {result.data.status_code}")
        print(f"Data: {result.data.content}")

asyncio.run(basic_api_scraping())
```

### Authentication Methods

#### API Key Authentication

```python
async def api_key_auth():
    scraper = HttpScraper()

    headers = {
        "Authorization": "Bearer your-api-key-here",
        "Accept": "application/json"
    }

    result = await scraper.scrape(
        "https://api.example.com/v1/data",
        headers=headers
    )

    if result.success:
        print("Authenticated request successful")

asyncio.run(api_key_auth())
```

#### OAuth 2.0 Token Flow

```python
async def oauth_flow():
    scraper = HttpScraper()

    # Step 1: Get access token
    token_result = await scraper.scrape(
        "https://oauth.example.com/token",
        method="POST",
        data={
            "grant_type": "client_credentials",
            "client_id": "your_client_id",
            "client_secret": "your_client_secret"
        }
    )

    if token_result.success:
        import json
        token_data = json.loads(token_result.data.content)
        access_token = token_data["access_token"]

        # Step 2: Use access token for API calls
        headers = {"Authorization": f"Bearer {access_token}"}

        api_result = await scraper.scrape(
            "https://api.example.com/v1/protected",
            headers=headers
        )

asyncio.run(oauth_flow())
```

### Pagination Handling

#### Offset-based Pagination

```python
async def paginated_api_scraping():
    scraper = HttpScraper()

    all_data = []
    offset = 0
    limit = 100

    while True:
        result = await scraper.scrape(
            f"https://api.example.com/v1/items?offset={offset}&limit={limit}"
        )

        if result.success:
            import json
            data = json.loads(result.data.content)
            items = data.get("items", [])

            if not items:
                break

            all_data.extend(items)
            offset += limit

            print(f"Collected {len(items)} items (total: {len(all_data)})")
        else:
            break

    print(f"Final total: {len(all_data)} items")

asyncio.run(paginated_api_scraping())
```

#### Cursor-based Pagination

```python
async def cursor_pagination():
    scraper = HttpScraper()

    all_data = []
    next_cursor = None

    while True:
        url = "https://api.example.com/v1/items"
        if next_cursor:
            url += f"?cursor={next_cursor}"

        result = await scraper.scrape(url)

        if result.success:
            import json
            data = json.loads(result.data.content)
            items = data.get("items", [])

            if not items:
                break

            all_data.extend(items)
            next_cursor = data.get("next_cursor")

            if not next_cursor:
                break
        else:
            break

    print(f"Total items: {len(all_data)}")

asyncio.run(cursor_pagination())
```

### Rate Limiting and Error Handling

```python
from scrap_e.core.config import WebScraperConfig
from scrap_e.core.models import RateLimitConfig, RetryConfig

async def resilient_api_scraping():
    config = WebScraperConfig(
        rate_limit=RateLimitConfig(
            enabled=True,
            requests_per_second=10.0,  # Respect API limits
            retry_after_header="Retry-After"
        ),
        retry=RetryConfig(
            enabled=True,
            max_attempts=3,
            retry_on_status_codes=[429, 500, 502, 503, 504]
        )
    )

    scraper = HttpScraper(config)

    urls = [f"https://api.example.com/v1/item/{i}" for i in range(100)]

    results = await scraper.scrape_multiple(urls)

    successful = [r for r in results if r.success]
    rate_limited = [r for r in results if not r.success and "429" in str(r.error)]

    print(f"Successful: {len(successful)}")
    print(f"Rate limited: {len(rate_limited)}")

asyncio.run(resilient_api_scraping())
```

## GraphQL API Scraping

### Basic GraphQL Queries

```python
async def graphql_scraping():
    scraper = HttpScraper()

    query = """
    query {
        users(first: 10) {
            edges {
                node {
                    id
                    name
                    email
                    posts {
                        title
                        publishedAt
                    }
                }
            }
        }
    }
    """

    result = await scraper.scrape(
        "https://api.example.com/graphql",
        method="POST",
        json={"query": query},
        headers={"Content-Type": "application/json"}
    )

    if result.success:
        import json
        data = json.loads(result.data.content)
        users = data["data"]["users"]["edges"]
        print(f"Found {len(users)} users")

asyncio.run(graphql_scraping())
```

### GraphQL with Variables

```python
async def graphql_with_variables():
    scraper = HttpScraper()

    query = """
    query GetUserPosts($userId: ID!, $first: Int!) {
        user(id: $userId) {
            name
            posts(first: $first) {
                edges {
                    node {
                        title
                        content
                        publishedAt
                    }
                }
            }
        }
    }
    """

    variables = {
        "userId": "123",
        "first": 5
    }

    result = await scraper.scrape(
        "https://api.example.com/graphql",
        method="POST",
        json={
            "query": query,
            "variables": variables
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer your-token"
        }
    )

    if result.success:
        import json
        data = json.loads(result.data.content)
        user = data["data"]["user"]
        print(f"User: {user['name']}")
        print(f"Posts: {len(user['posts']['edges'])}")

asyncio.run(graphql_with_variables())
```

## Advanced API Patterns

### Concurrent API Requests

```python
async def concurrent_api_requests():
    scraper = HttpScraper()

    # Create multiple API endpoints
    base_url = "https://jsonplaceholder.typicode.com"
    endpoints = [
        f"{base_url}/posts",
        f"{base_url}/comments",
        f"{base_url}/albums",
        f"{base_url}/photos",
        f"{base_url}/todos",
        f"{base_url}/users"
    ]

    # Fetch all endpoints concurrently
    results = await scraper.scrape_multiple(endpoints, max_concurrent=3)

    for endpoint, result in zip(endpoints, results):
        if result.success:
            import json
            data = json.loads(result.data.content)
            print(f"{endpoint}: {len(data)} items")
        else:
            print(f"{endpoint}: Failed - {result.error}")

asyncio.run(concurrent_api_requests())
```

### API Response Caching

```python
from scrap_e.core.models import CacheConfig

async def cached_api_requests():
    config = WebScraperConfig(
        cache=CacheConfig(
            enabled=True,
            backend="memory",
            ttl_seconds=600,  # Cache for 10 minutes
            max_size_mb=50
        )
    )

    scraper = HttpScraper(config)

    # First request - fetched from API
    result1 = await scraper.scrape("https://api.example.com/v1/expensive-data")
    print(f"First request: {result1.metadata.duration_seconds:.2f}s")

    # Second request - served from cache
    result2 = await scraper.scrape("https://api.example.com/v1/expensive-data")
    print(f"Cached request: {result2.metadata.duration_seconds:.2f}s")

asyncio.run(cached_api_requests())
```

### Data Transformation and Validation

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Post(BaseModel):
    id: int
    title: str
    content: str = Field(alias="body")
    user_id: int = Field(alias="userId")
    created_at: Optional[datetime] = None

async def validated_api_scraping():
    scraper = HttpScraper()

    result = await scraper.scrape("https://jsonplaceholder.typicode.com/posts")

    if result.success:
        import json
        raw_data = json.loads(result.data.content)

        # Validate and transform data
        posts = []
        for item in raw_data[:5]:  # First 5 posts
            try:
                post = Post(**item)
                posts.append(post)
            except Exception as e:
                print(f"Validation error for item {item.get('id')}: {e}")

        print(f"Successfully validated {len(posts)} posts")
        for post in posts:
            print(f"Post {post.id}: {post.title[:50]}...")

asyncio.run(validated_api_scraping())
```

## WebSocket API Integration

### Basic WebSocket Connection

```python
import websockets
import json

async def websocket_scraping():
    uri = "wss://api.example.com/v1/live"

    try:
        async with websockets.connect(uri) as websocket:
            # Send subscription message
            subscribe_msg = {
                "type": "subscribe",
                "channel": "updates",
                "auth_token": "your-token"
            }

            await websocket.send(json.dumps(subscribe_msg))

            # Listen for messages
            for i in range(10):  # Collect 10 messages
                message = await websocket.recv()
                data = json.loads(message)
                print(f"Received: {data}")

    except Exception as e:
        print(f"WebSocket error: {e}")

# asyncio.run(websocket_scraping())  # Uncomment to run
```

## API-Specific Extraction Rules

### JSON Path Extraction

```python
from scrap_e.core.models import ExtractionRule

async def json_path_extraction():
    scraper = HttpScraper()

    scraper.add_extraction_rule(ExtractionRule(
        name="user_names",
        json_path="$.users[*].name",
        multiple=True
    ))

    scraper.add_extraction_rule(ExtractionRule(
        name="post_count",
        json_path="$.meta.total_posts"
    ))

    result = await scraper.scrape("https://api.example.com/v1/users")

    if result.success and result.data.extracted_data:
        data = result.data.extracted_data
        print(f"Users: {data['user_names']}")
        print(f"Total posts: {data['post_count']}")

asyncio.run(json_path_extraction())
```

## Best Practices for API Scraping

### 1. Respect Rate Limits

```python
# Always configure appropriate rate limiting
config = WebScraperConfig(
    rate_limit=RateLimitConfig(
        enabled=True,
        requests_per_second=5.0,  # Conservative rate
        burst_size=10
    )
)
```

### 2. Handle API Errors Properly

```python
async def robust_api_handling():
    scraper = HttpScraper()

    result = await scraper.scrape("https://api.example.com/v1/data")

    if result.success:
        if result.data.status_code == 200:
            # Success
            process_data(result.data.content)
        elif result.data.status_code == 429:
            # Rate limited
            print("Rate limited - wait and retry")
        elif result.data.status_code == 401:
            # Unauthorized
            print("Authentication failed")
        else:
            print(f"API error: {result.data.status_code}")
    else:
        print(f"Request failed: {result.error}")

def process_data(content):
    pass  # Process your API response
```

### 3. Use Appropriate Authentication

```python
# Store credentials securely
import os

api_key = os.getenv("API_KEY")
headers = {"Authorization": f"Bearer {api_key}"}
```

### 4. Monitor API Usage

```python
async def monitor_api_usage():
    scraper = HttpScraper()

    # Make several API calls
    urls = [f"https://api.example.com/v1/item/{i}" for i in range(10)]
    await scraper.scrape_multiple(urls)

    # Check statistics
    stats = scraper.get_stats()
    print(f"API calls made: {stats.total_requests}")
    print(f"Success rate: {stats.successful_requests/stats.total_requests*100:.1f}%")
    print(f"Average response time: {stats.average_response_time:.2f}s")

    if stats.rate_limited > 0:
        print(f"Rate limited: {stats.rate_limited} times")

asyncio.run(monitor_api_usage())
```

## Common API Patterns

### REST CRUD Operations

```python
async def crud_operations():
    scraper = HttpScraper()
    base_url = "https://api.example.com/v1/posts"

    # CREATE
    new_post = {
        "title": "My New Post",
        "content": "This is the content"
    }

    create_result = await scraper.scrape(
        base_url,
        method="POST",
        json=new_post
    )

    if create_result.success:
        import json
        created_post = json.loads(create_result.data.content)
        post_id = created_post["id"]

        # READ
        read_result = await scraper.scrape(f"{base_url}/{post_id}")

        # UPDATE
        update_data = {"title": "Updated Title"}
        update_result = await scraper.scrape(
            f"{base_url}/{post_id}",
            method="PATCH",
            json=update_data
        )

        # DELETE
        delete_result = await scraper.scrape(
            f"{base_url}/{post_id}",
            method="DELETE"
        )

        print(f"CRUD operations completed for post {post_id}")

asyncio.run(crud_operations())
```

### Bulk Data Processing

```python
async def bulk_data_processing():
    scraper = HttpScraper()

    # Get list of all items
    list_result = await scraper.scrape("https://api.example.com/v1/items")

    if list_result.success:
        import json
        items = json.loads(list_result.data.content)

        # Process items in batches
        batch_size = 50
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]

            # Create URLs for batch processing
            urls = [f"https://api.example.com/v1/item/{item['id']}/details"
                   for item in batch]

            # Process batch concurrently
            results = await scraper.scrape_multiple(urls, max_concurrent=10)

            print(f"Processed batch {i//batch_size + 1}: {len(results)} items")

asyncio.run(bulk_data_processing())
```

## Next Steps

- Learn about [database scraping](database-scraping.md) for direct database access
- Explore [web scraping](web-scraping.md) for HTML content extraction
- Review [configuration options](../getting-started/configuration.md) for API-specific settings
- Check out [performance optimization](performance.md) for high-volume API scraping
