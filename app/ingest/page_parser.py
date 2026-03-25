"""Helpers for extracting readable text and links from raw page HTML."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from app.ingest.cleaner import clean_text
from app.shared.utils import normalize_text


@dataclass
class ParsedLink:
    title: str
    url: str
    snippet: str


@dataclass
class ParsedPage:
    title: str
    text_blocks: list[str]
    links: list[ParsedLink]


def parse_page_html(
    page_url: str,
    page_html: str,
    *,
    max_text_chars: int = 12000,
    max_blocks: int = 5,
    max_links: int = 30,
) -> ParsedPage:
    """Parse raw HTML into readable text blocks and deduplicated absolute links."""
    soup = BeautifulSoup(page_html, "html.parser")

    for tag_name in ("script", "style", "noscript", "nav", "header", "footer", "aside"):
        for tag in soup.find_all(tag_name):
            tag.decompose()

    page_title = (soup.title.string.strip() if soup.title and soup.title.string else page_url) or "Current page"

    text_blocks: list[str] = []
    consumed = 0
    for tag in soup.find_all(["main", "article", "section", "p", "li", "h1", "h2", "h3"]):
        text = normalize_text(clean_text(tag.get_text(" ", strip=True)))
        if not text:
            continue
        if len(text) < 40 and tag.name not in {"h1", "h2", "h3"}:
            continue
        remaining = max_text_chars - consumed
        if remaining <= 0:
            break
        clipped = text[:remaining]
        text_blocks.append(clipped)
        consumed += len(clipped)
        if len(text_blocks) >= max_blocks:
            break

    if not text_blocks:
        fallback_text = normalize_text(clean_text(soup.get_text("\n", strip=True)))
        if fallback_text:
            text_blocks = [fallback_text[:max_text_chars]]

    page_host = urlparse(page_url).netloc
    links: list[ParsedLink] = []
    seen_urls: set[str] = set()
    for anchor in soup.find_all("a", href=True):
        href = str(anchor.get("href", "")).strip()
        if not href or href.startswith("#") or href.lower().startswith("javascript:"):
            continue
        absolute = urljoin(page_url, href)
        if absolute in seen_urls:
            continue
        if not absolute.startswith(("http://", "https://")):
            continue
        seen_urls.add(absolute)

        label = normalize_text(anchor.get_text(" ", strip=True)) or absolute
        parsed = urlparse(absolute)
        is_same_site = bool(page_host and parsed.netloc == page_host)
        snippet = f"Same-site link: {label}" if is_same_site else f"External link: {label}"
        links.append(ParsedLink(title=label[:120], url=absolute, snippet=snippet[:220]))
        if len(links) >= max_links:
            break

    links.sort(key=lambda item: 0 if urlparse(item.url).netloc == page_host else 1)
    return ParsedPage(title=page_title, text_blocks=text_blocks, links=links)
