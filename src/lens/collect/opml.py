"""OPML parser: extract feed URLs from OPML files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree


@dataclass(frozen=True)
class OpmlFeed:
    """A feed source parsed from an OPML file."""

    title: str
    xml_url: str
    html_url: str
    category: str


def parse_opml(path: Path, category_filter: str | None = None) -> list[OpmlFeed]:
    """Parse an OPML file and return feed sources.

    Args:
        path: Path to the OPML file.
        category_filter: Optional category name to filter by.

    Returns:
        List of feed sources found in the OPML file.
    """
    tree = ElementTree.parse(path)  # noqa: S314
    root = tree.getroot()
    feeds: list[OpmlFeed] = []

    for outline in root.iter("outline"):
        xml_url = outline.get("xmlUrl", "")
        if not xml_url:
            continue

        title = outline.get("title", outline.get("text", "Untitled"))
        html_url = outline.get("htmlUrl", "")

        # Walk up to find category
        category = _find_category(root, outline)

        if category_filter and category.lower() != category_filter.lower():
            continue

        feeds.append(
            OpmlFeed(
                title=title,
                xml_url=xml_url,
                html_url=html_url,
                category=category,
            )
        )

    return feeds


def _find_category(root: ElementTree.Element, target: ElementTree.Element) -> str:
    """Find the category (parent outline title) for a feed outline."""
    for parent in root.iter("outline"):
        for child in parent:
            if child is target:
                return parent.get("title", parent.get("text", ""))
    return ""
