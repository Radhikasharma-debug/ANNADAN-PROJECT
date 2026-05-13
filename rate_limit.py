from collections import deque
from functools import wraps
from threading import Lock
import time

from flask import jsonify, request


# In-memory fixed-window limiter per process.
_RATE_LIMIT_STORE = {}
_RATE_LIMIT_LOCK = Lock()


def rate_limit(max_requests, window_seconds, key_func=None):
    """Simple in-memory rate limiter decorator."""

    if max_requests <= 0 or window_seconds <= 0:
        raise ValueError('max_requests and window_seconds must be positive')

    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            now = time.time()
            endpoint = request.endpoint or func.__name__
            identifier = key_func() if key_func else _default_identifier()
            bucket_key = f"{endpoint}:{identifier}"

            with _RATE_LIMIT_LOCK:
                bucket = _RATE_LIMIT_STORE.setdefault(bucket_key, deque())
                cutoff = now - window_seconds

                while bucket and bucket[0] <= cutoff:
                    bucket.popleft()

                if len(bucket) >= max_requests:
                    retry_after = int(max(1, window_seconds - (now - bucket[0])))
                    response = jsonify(
                        {
                            'error': 'Rate limit exceeded',
                            'retry_after_seconds': retry_after,
                            'limit': max_requests,
                            'window_seconds': window_seconds,
                        }
                    )
                    response.status_code = 429
                    response.headers['Retry-After'] = str(retry_after)
                    return response

                bucket.append(now)

            return func(*args, **kwargs)

        return wrapped

    return decorator


def _default_identifier():
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.remote_addr or 'unknown'
