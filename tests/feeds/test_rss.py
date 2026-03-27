"""Tests for RSS feed parser."""

import pytest

from lens_py.feeds.rss import Feed, FeedItem, parse_feed


SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <link>https://example.com</link>
    <description>A test feed</description>
    <item>
      <title>First Article</title>
      <link>https://example.com/article-1</link>
      <description>Description of first article</description>
      <pubDate>Mon, 27 Mar 2026 12:00:00 GMT</pubDate>
      <guid>https://example.com/article-1</guid>
    </item>
    <item>
      <title>Second Article</title>
      <link>https://example.com/article-2</link>
      <description>Description of second article</description>
      <pubDate>Mon, 27 Mar 2026 13:00:00 GMT</pubDate>
      <guid>https://example.com/article-2</guid>
    </item>
  </channel>
</rss>"""

SAMPLE_ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>Atom Feed</title>
  <link href="https://example.com" rel="alternate"/>
  <entry>
    <title>Atom Entry</title>
    <link href="https://example.com/entry-1"/>
    <id>urn:uuid:entry-1</id>
    <published>2026-03-27T12:00:00Z</published>
    <summary>An atom entry summary</summary>
  </entry>
</feed>"""


class TestParseFeed:
    """Tests for parse_feed function."""

    def test_parses_rss_feed_metadata(self) -> None:
        feed = parse_feed(SAMPLE_RSS)
        assert feed.title == "Test Feed"
        assert feed.link == "https://example.com"
        assert feed.description == "A test feed"

    def test_parses_rss_items(self) -> None:
        feed = parse_feed(SAMPLE_RSS)
        assert len(feed.items) == 2

    def test_parses_rss_item_fields(self) -> None:
        feed = parse_feed(SAMPLE_RSS)
        item = feed.items[0]
        assert item.title == "First Article"
        assert item.link == "https://example.com/article-1"
        assert item.description == "Description of first article"
        assert item.guid == "https://example.com/article-1"
        assert "Mar 2026" in item.pub_date

    def test_parses_atom_feed(self) -> None:
        feed = parse_feed(SAMPLE_ATOM)
        assert feed.title == "Atom Feed"
        assert len(feed.items) == 1

    def test_parses_atom_item_fields(self) -> None:
        feed = parse_feed(SAMPLE_ATOM)
        item = feed.items[0]
        assert item.title == "Atom Entry"
        assert item.link == "https://example.com/entry-1"
        assert item.guid == "urn:uuid:entry-1"

    def test_feed_is_frozen(self) -> None:
        feed = parse_feed(SAMPLE_RSS)
        with pytest.raises(AttributeError):
            feed.title = "modified"  # type: ignore[misc]

    def test_item_is_frozen(self) -> None:
        feed = parse_feed(SAMPLE_RSS)
        with pytest.raises(AttributeError):
            feed.items[0].title = "modified"  # type: ignore[misc]

    def test_invalid_xml_raises(self) -> None:
        with pytest.raises(ValueError, match="Failed to parse"):
            parse_feed("this is not xml at all")

    def test_empty_feed(self) -> None:
        xml = (
            '<?xml version="1.0"?><rss version="2.0">'
            "<channel><title>Empty</title><link>https://example.com</link>"
            "<description></description></channel></rss>"
        )
        feed = parse_feed(xml)
        assert feed.title == "Empty"
        assert feed.items == []
