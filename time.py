from datetime import datetime, timezone


def utc_now():
    """Return timezone-aware current UTC datetime."""
    return datetime.now(timezone.utc)


def utc_today():
    """Return current UTC date."""
    return utc_now().date()


def ensure_utc(dt):
    """Normalize datetime to timezone-aware UTC."""
    if dt is None:
        return None

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)
