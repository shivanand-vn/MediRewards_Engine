from datetime import datetime, timezone

def ensure_utc_naive(dt: datetime) -> datetime:
    """
    Normalizes a datetime object to UTC naive representation for consistent DB storage and comparisons.
    """
    if dt is None:
        return None
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt
