"""Feed utility functions."""

from __future__ import annotations

import re


def sanitize_feed_name(name: str) -> str:
    """Convert a feed name to a safe directory name.

    Lowercases, replaces non-alphanumeric characters with hyphens,
    collapses multiple hyphens, and strips leading/trailing hyphens.

    Returns 'unknown' for empty or all-special-character names.
    """
    safe = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return safe or "unknown"
