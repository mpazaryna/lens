"""Tests for OPML parser."""

from pathlib import Path

import pytest

from lens.collect.opml import OpmlFeed, parse_opml


class TestParseOpml:
    """Tests for parse_opml function."""

    def test_parses_all_feeds(self, sample_opml: Path) -> None:
        feeds = parse_opml(sample_opml)
        assert len(feeds) == 2

    def test_extracts_feed_attributes(self, sample_opml: Path) -> None:
        feeds = parse_opml(sample_opml)
        anthropic = next(f for f in feeds if "Anthropic" in f.title)

        assert anthropic.title == "Anthropic News"
        assert anthropic.xml_url == "https://www.anthropic.com/rss.xml"
        assert anthropic.html_url == "https://www.anthropic.com/news"

    def test_extracts_category(self, sample_opml: Path) -> None:
        feeds = parse_opml(sample_opml)
        anthropic = next(f for f in feeds if "Anthropic" in f.title)
        nasa = next(f for f in feeds if "NASA" in f.title)

        assert anthropic.category == "Technology"
        assert nasa.category == "Science"

    def test_filters_by_category(self, sample_opml: Path) -> None:
        feeds = parse_opml(sample_opml, category_filter="Technology")
        assert len(feeds) == 1
        assert feeds[0].title == "Anthropic News"

    def test_category_filter_case_insensitive(self, sample_opml: Path) -> None:
        feeds = parse_opml(sample_opml, category_filter="technology")
        assert len(feeds) == 1

    def test_category_filter_no_match(self, sample_opml: Path) -> None:
        feeds = parse_opml(sample_opml, category_filter="Sports")
        assert len(feeds) == 0

    def test_returns_frozen_dataclass(self, sample_opml: Path) -> None:
        feeds = parse_opml(sample_opml)
        with pytest.raises(AttributeError):
            feeds[0].title = "modified"  # type: ignore[misc]

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            parse_opml(tmp_path / "nonexistent.opml")

    def test_empty_opml(self, tmp_path: Path) -> None:
        opml_path = tmp_path / "empty.opml"
        opml_path.write_text(
            '<?xml version="1.0"?><opml version="2.0">'
            "<head><title>Empty</title></head>"
            "<body></body></opml>"
        )
        feeds = parse_opml(opml_path)
        assert feeds == []
