"""Tests for feed utility functions.

Derived from gherkin.md Step 0 scenarios:
- Feed name sanitization for filesystem safety
"""

from __future__ import annotations

from lens.collect.feed_utils import sanitize_feed_name


class TestSanitizeFeedName:
    """Feature: Feed name sanitization."""

    def test_simple_name(self) -> None:
        assert sanitize_feed_name("Hacker News") == "hacker-news"

    def test_special_characters_removed(self) -> None:
        result = sanitize_feed_name("Tech & Science (2026)")
        assert all(c.isalnum() or c in "-_" for c in result)

    def test_lowercased(self) -> None:
        assert sanitize_feed_name("BBC Top Stories") == "bbc-top-stories"

    def test_multiple_spaces_collapsed(self) -> None:
        result = sanitize_feed_name("Some   Feed   Name")
        assert "--" not in result

    def test_empty_string(self) -> None:
        assert sanitize_feed_name("") == "unknown"

    def test_only_special_chars(self) -> None:
        assert sanitize_feed_name("!@#$%") == "unknown"
