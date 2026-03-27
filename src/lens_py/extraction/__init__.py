"""HTML extraction: strip HTML to clean article text. No LLM calls."""

from lens_py.extraction.extractor import extract_article, extract_articles, ExtractionResult

__all__ = ["extract_article", "extract_articles", "ExtractionResult"]
