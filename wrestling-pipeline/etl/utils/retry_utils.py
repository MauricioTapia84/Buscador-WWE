import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


def requests_get_with_retry(url, **kwargs):
    """Perform a GET request with retries for transient network errors."""
    headers = dict(kwargs.pop("headers", {}) or {})
    headers.setdefault(
        "User-Agent",
        "WrestlingPipeline/1.0 (educational project; contact: local-dev)"
    )
    kwargs["headers"] = headers
    resp = requests.get(url, **kwargs)
    resp.raise_for_status()
    return resp


def retry_on_exception(func=None, *, attempts: int = 3):
    def decorator(f):
        @retry(stop=stop_after_attempt(attempts), wait=wait_exponential(multiplier=1, min=1, max=10),
               retry=retry_if_exception_type(Exception))
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)
        return wrapper

    if func is None:
        return decorator
    return decorator(func)
