class DiscardWatchEvent(Exception):
    """Marks a permanently invalid event that must be acknowledged without retry."""
