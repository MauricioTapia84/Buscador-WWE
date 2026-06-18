from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10),
       retry=retry_if_exception_type((requests.exceptions.RequestException,)))
def requests_get_with_retry(url, **kwargs):
    """Perform a GET request with retries for transient network errors."""
    resp = requests.get(url, **kwargs)
    resp.raise_for_status()
    return resp


from tenacity import retry as ten_retry


def retry_on_exception(func=None, *, attempts: int = 3):
       """Generic decorator to retry a function on any Exception (configurable attempts)."""
       def decorator(f):
              @ten_retry(stop=stop_after_attempt(attempts), wait=wait_exponential(multiplier=1, min=1, max=10),
                               retry=retry_if_exception_type(Exception))
              def wrapper(*args, **kwargs):
                     return f(*args, **kwargs)
              return wrapper

       if func is None:
              return decorator
       return decorator(func)
