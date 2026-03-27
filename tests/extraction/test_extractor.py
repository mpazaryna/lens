"""Tests for HTML content extractor."""

from pathlib import Path

import pytest

from lens.extraction.extractor import extract_article, extract_articles


class TestExtractArticle:
    """Tests for extract_article function."""

    def test_extracts_title_from_title_tag(self, sample_html: str) -> None:
        result = extract_article(sample_html)
        assert result.title == "AI Advances in 2026 | Tech News"

    def test_extracts_article_text(self, sample_html: str) -> None:
        result = extract_article(sample_html)
        assert "AI models are becoming increasingly capable" in result.text
        assert "complex reasoning tasks" in result.text

    def test_preserves_headings(self, sample_html: str) -> None:
        result = extract_article(sample_html)
        assert "# AI Advances in 2026" in result.text
        assert "## Key Developments" in result.text
        assert "### Safety Considerations" in result.text

    def test_removes_scripts(self, sample_html: str) -> None:
        result = extract_article(sample_html)
        assert "analytics" not in result.text
        assert "tracking" not in result.text

    def test_removes_styles(self, sample_html: str) -> None:
        result = extract_article(sample_html)
        assert "font-family" not in result.text

    def test_removes_nav(self, sample_html: str) -> None:
        result = extract_article(sample_html)
        # Nav links should be removed
        assert "Home" not in result.text or "About" not in result.text

    def test_removes_footer(self, sample_html: str) -> None:
        result = extract_article(sample_html)
        assert "Copyright 2026" not in result.text
        assert "Privacy" not in result.text

    def test_removes_sidebar(self, sample_html: str) -> None:
        result = extract_article(sample_html)
        assert "Related Articles" not in result.text

    def test_removes_cookie_banner(self, sample_html: str) -> None:
        result = extract_article(sample_html)
        assert "cookie" not in result.text.lower()

    def test_extracts_http_urls(self, sample_html: str) -> None:
        result = extract_article(sample_html)
        assert "https://example.com/benchmarks" in result.urls
        assert "https://example.com/safety" in result.urls

    def test_word_count_is_reasonable(self, sample_html: str) -> None:
        result = extract_article(sample_html)
        # Should have article content but not nav/footer/script text
        assert 30 < result.word_count < 300

    def test_preserves_blockquote_text(self, sample_html: str) -> None:
        result = extract_article(sample_html)
        assert "pace of progress" in result.text

    def test_extracts_insurance_mention(self, sample_html: str) -> None:
        result = extract_article(sample_html)
        assert "insurance" in result.text.lower()

    def test_minimal_html(self) -> None:
        html = "<html><body><p>Hello world</p></body></html>"
        result = extract_article(html)
        assert "Hello world" in result.text
        assert result.word_count == 2

    def test_no_body_tag(self) -> None:
        html = "<p>Just a paragraph</p>"
        result = extract_article(html)
        assert "Just a paragraph" in result.text

    def test_empty_html(self) -> None:
        result = extract_article("")
        assert result.word_count == 0

    def test_result_is_frozen(self, sample_html: str) -> None:
        result = extract_article(sample_html)
        with pytest.raises(AttributeError):
            result.text = "modified"  # type: ignore[misc]


class TestExtractArticles:
    """Tests for batch extraction."""

    def test_extracts_all_html_files(self, tmp_path: Path) -> None:
        html_dir = tmp_path / "fetched"
        out_dir = tmp_path / "extracted"
        html_dir.mkdir()

        for i in range(3):
            (html_dir / f"article-{i}.html").write_text(
                f"<html><body><h1>Article {i}</h1><p>Content {i}</p></body></html>"
            )

        results = extract_articles(html_dir, out_dir)
        assert len(results) == 3
        assert all(not isinstance(r, Exception) for _, r in results)

    def test_writes_markdown_files(self, tmp_path: Path) -> None:
        html_dir = tmp_path / "fetched"
        out_dir = tmp_path / "extracted"
        html_dir.mkdir()

        (html_dir / "test.html").write_text(
            "<html><body><h1>Test</h1><p>Content here</p></body></html>"
        )

        extract_articles(html_dir, out_dir)
        md_file = out_dir / "test.md"
        assert md_file.exists()
        content = md_file.read_text()
        assert "# Test" in content
        assert "Content here" in content

    def test_skips_existing_without_overwrite(self, tmp_path: Path) -> None:
        html_dir = tmp_path / "fetched"
        out_dir = tmp_path / "extracted"
        html_dir.mkdir()
        out_dir.mkdir()

        (html_dir / "test.html").write_text("<html><body><p>New</p></body></html>")
        (out_dir / "test.md").write_text("# Old content")

        extract_articles(html_dir, out_dir, overwrite=False)
        assert "Old content" in (out_dir / "test.md").read_text()

    def test_overwrites_with_flag(self, tmp_path: Path) -> None:
        html_dir = tmp_path / "fetched"
        out_dir = tmp_path / "extracted"
        html_dir.mkdir()
        out_dir.mkdir()

        (html_dir / "test.html").write_text(
            "<html><body><h1>New</h1><p>Updated</p></body></html>"
        )
        (out_dir / "test.md").write_text("# Old content")

        extract_articles(html_dir, out_dir, overwrite=True)
        content = (out_dir / "test.md").read_text()
        assert "New" in content

    def test_empty_directory(self, tmp_path: Path) -> None:
        html_dir = tmp_path / "fetched"
        out_dir = tmp_path / "extracted"
        html_dir.mkdir()

        results = extract_articles(html_dir, out_dir)
        assert results == []

    def test_creates_output_dir(self, tmp_path: Path) -> None:
        html_dir = tmp_path / "fetched"
        out_dir = tmp_path / "extracted"
        html_dir.mkdir()

        (html_dir / "test.html").write_text("<html><body><p>Test</p></body></html>")
        extract_articles(html_dir, out_dir)
        assert out_dir.exists()
