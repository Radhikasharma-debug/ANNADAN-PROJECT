from flask import request


def get_json_data(required=False):
    """Safely parse JSON request body as dict."""
    data = request.get_json(silent=True)

    if data is None:
        if required:
            raise ValueError('Request body must be valid JSON')
        return {}

    if not isinstance(data, dict):
        raise ValueError('Request body must be a JSON object')

    return data


def parse_pagination(default_limit=20, max_limit=100):
    """Parse and clamp pagination params from query string."""
    skip = request.args.get('skip', 0, type=int)
    limit = request.args.get('limit', default_limit, type=int)

    if skip is None or skip < 0:
        skip = 0

    if limit is None:
        limit = default_limit

    limit = max(1, min(int(limit), max_limit))

    return skip, limit
