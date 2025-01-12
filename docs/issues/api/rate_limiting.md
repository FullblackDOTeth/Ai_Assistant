# Rate Limiting Issues

## Problem
You're receiving "429 Too Many Requests" errors when making API calls.

## Diagnosis

### Check Your Current Usage
1. Monitor your API usage in the dashboard
2. Review your rate limits based on your plan
3. Check for any automated scripts making excessive calls

### Common Causes
1. Inefficient API usage patterns
2. Missing request caching
3. Parallel requests exceeding limits
4. Shared API key across multiple services

## Solution

### Implement Request Caching
```python
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def cached_api_call(params):
    return api.make_request(params)
```

### Use Rate Limiting Decorator
```python
import time
from functools import wraps

def rate_limit(calls_per_second):
    min_interval = 1.0 / calls_per_second
    last_call = 0.0
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal last_call
            now = time.time()
            elapsed = now - last_call
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_call = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(calls_per_second=2)
def make_api_call():
    return api.request()
```

### Implement Retry Logic
```python
import time
from tenacity import retry, wait_exponential

@retry(wait=wait_exponential(multiplier=1, min=4, max=10))
def api_call_with_retry():
    try:
        return api.make_request()
    except RateLimitError:
        time.sleep(30)
        raise
```

### Batch Requests
```python
def batch_api_calls(items, batch_size=10):
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        results = api.batch_request(batch)
        time.sleep(1)  # Rate limiting
        yield results
```

## Prevention

### Best Practices
1. Implement proper caching
2. Use batch operations when possible
3. Monitor API usage
4. Set up alerts for rate limit warnings

### Monitoring Setup
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('api_monitor')

def monitor_rate_limits(response):
    remaining = response.headers.get('X-RateLimit-Remaining')
    if remaining and int(remaining) < 100:
        logger.warning(f'Rate limit warning: {remaining} requests remaining')
```

### Rate Limit Headers
Monitor these headers in API responses:
- `X-RateLimit-Limit`: Total requests allowed
- `X-RateLimit-Remaining`: Requests remaining
- `X-RateLimit-Reset`: Time until limit resets

## Additional Resources
1. [API Documentation](#api-reference)
2. [Rate Limiting Guide](#rate-limiting)
3. [Best Practices](#best-practices)
