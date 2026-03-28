"""Custom exception hierarchy for the lens pipeline."""

from __future__ import annotations


class LensError(Exception):
    """Base exception for all lens pipeline errors."""


class FeedParseError(LensError):
    """Raised when RSS/Atom feed parsing fails."""


class FeedFetchError(LensError):
    """Raised when fetching a feed over the network fails."""


class ArticleFetchError(LensError):
    """Raised when downloading article HTML fails."""


class ExtractionError(LensError):
    """Raised when HTML-to-text extraction fails."""


class LLMProviderError(LensError):
    """Raised when an LLM provider call fails."""


class ConfigError(LensError):
    """Raised when configuration is invalid or incomplete."""
