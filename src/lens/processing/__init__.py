"""Content processing: LLM-powered summarization via Anthropic API."""

from lens.processing.summarizer import summarize_article, summarize_batch, SummaryResult

__all__ = ["summarize_article", "summarize_batch", "SummaryResult"]
