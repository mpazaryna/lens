"""HTML to clean text extraction using BeautifulSoup.

Extracts article content by:
1. Isolating <body> content
2. Removing non-content elements (script, style, nav, footer, etc.)
3. Extracting text with structure preserved
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from bs4 import BeautifulSoup, Tag

# Tags to remove entirely (element + children)
REMOVE_TAGS = frozenset({
    "script",
    "style",
    "noscript",
    "svg",
    "nav",
    "header",
    "footer",
    "iframe",
    "form",
    "button",
    "select",
    "textarea",
    "input",
    "aside",
})

# Roles that indicate non-content
REMOVE_ROLES = frozenset({
    "banner",
    "navigation",
    "complementary",
    "contentinfo",
})

# Classes that indicate non-content
REMOVE_CLASS_PATTERNS = frozenset({
    "cookie",
    "modal",
    "popup",
    "sidebar",
    "skip",
    "social-share",
    "newsletter",
    "advertisement",
})


@dataclass(frozen=True)
class ExtractionResult:
    """Result of extracting content from HTML."""

    text: str
    title: str | None
    word_count: int
    urls: list[str]


def extract_article(html: str) -> ExtractionResult:
    """Extract clean article text from HTML.

    Args:
        html: Raw HTML content.

    Returns:
        ExtractionResult with clean text and metadata.
    """
    soup = BeautifulSoup(html, "lxml")

    # Extract title before we modify the tree
    title = _extract_title(soup)

    # Extract URLs before cleanup
    urls = _extract_urls(soup)

    # Isolate body
    body = soup.body or soup

    # Remove non-content elements
    _remove_noise(body)

    # Extract text with structure
    text = _extract_text(body)

    # Word count
    words = text.split()
    word_count = len(words)

    return ExtractionResult(
        text=text,
        title=title,
        word_count=word_count,
        urls=urls,
    )


def extract_articles(
    html_dir: Path,
    output_dir: Path,
    overwrite: bool = False,
) -> list[tuple[Path, ExtractionResult | Exception]]:
    """Extract all HTML files in a directory to clean markdown.

    Args:
        html_dir: Directory containing HTML files.
        output_dir: Directory to write extracted markdown files.
        overwrite: Whether to overwrite existing files.

    Returns:
        List of (output_path, result | error) tuples.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    results: list[tuple[Path, ExtractionResult | Exception]] = []

    html_files = sorted(html_dir.glob("*.html")) + sorted(html_dir.glob("*.htm"))

    for html_path in html_files:
        out_path = output_dir / f"{html_path.stem}.md"

        if out_path.exists() and not overwrite:
            # Read existing to return metadata
            try:
                text = out_path.read_text(encoding="utf-8")
                title_line = text.split("\n")[0].lstrip("# ").strip() if text else None
                word_count = len(text.split())
                result = ExtractionResult(
                    text=text, title=title_line, word_count=word_count, urls=[]
                )
                results.append((out_path, result))
            except Exception as e:
                results.append((out_path, e))
            continue

        try:
            html = html_path.read_text(encoding="utf-8")
            result = extract_article(html)

            # Write as markdown
            md = _format_markdown(result, html_path.name)
            out_path.write_text(md, encoding="utf-8")
            results.append((out_path, result))
        except Exception as e:
            results.append((out_path, e))

    return results


def _extract_title(soup: BeautifulSoup) -> str | None:
    """Extract document title."""
    # Try <title> tag
    if soup.title and soup.title.string:
        return soup.title.string.strip()

    # Try og:title
    og = soup.find("meta", property="og:title")
    if og and isinstance(og, Tag):
        content = og.get("content", "")
        if content:
            return str(content).strip()

    # Try first h1
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)

    return None


def _extract_urls(soup: BeautifulSoup) -> list[str]:
    """Extract HTTP URLs from anchor tags."""
    urls = []
    for a in soup.find_all("a", href=True):
        href = str(a["href"])
        if href.startswith("http"):
            urls.append(href)
    return urls


def _remove_noise(element: Tag) -> None:
    """Remove non-content elements from the DOM tree."""
    to_remove: list[Tag] = []

    # Collect by tag name
    for tag_name in REMOVE_TAGS:
        to_remove.extend(element.find_all(tag_name))

    # Collect by role attribute
    for role in REMOVE_ROLES:
        to_remove.extend(element.find_all(attrs={"role": role}))

    # Collect hidden elements
    to_remove.extend(element.find_all(attrs={"aria-hidden": "true"}))
    to_remove.extend(
        element.find_all(style=lambda s: s and "display:none" in s.replace(" ", ""))
    )

    # Collect by class patterns
    for tag in element.find_all(True):
        if tag.attrs is None:
            continue
        classes = " ".join(tag.get("class", []))
        if any(pattern in classes.lower() for pattern in REMOVE_CLASS_PATTERNS):
            to_remove.append(tag)

    # Decompose all collected elements
    for tag in to_remove:
        if tag.parent is not None:
            tag.decompose()


def _extract_text(element: Tag) -> str:
    """Extract text from cleaned HTML, preserving basic structure."""
    lines: list[str] = []

    for child in element.descendants:
        if isinstance(child, str):
            text = child.strip()
            if text:
                lines.append(text)
        elif isinstance(child, Tag):
            if child.name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                level = int(child.name[1])
                heading_text = child.get_text(strip=True)
                if heading_text:
                    lines.append("")
                    lines.append(f"{'#' * level} {heading_text}")
                    lines.append("")
            elif child.name in ("p", "div", "section", "article", "blockquote"):
                lines.append("")
            elif child.name == "br":
                lines.append("")
            elif child.name == "li":
                lines.append("")

    # Join and clean up
    text = "\n".join(lines)

    # Collapse multiple blank lines
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")

    return text.strip()


def _format_markdown(result: ExtractionResult, source_filename: str) -> str:
    """Format extraction result as markdown."""
    lines = [f"# {result.title or 'Untitled'}", ""]
    lines.append(result.text)
    lines.append("")

    if result.urls:
        lines.append("## Links")
        lines.append("")
        for url in result.urls:
            lines.append(f"- {url}")
        lines.append("")

    lines.append("---")
    lines.append(f"*Extracted from: {source_filename}*")
    lines.append("")

    return "\n".join(lines)
