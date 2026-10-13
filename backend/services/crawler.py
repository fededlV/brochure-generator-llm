import asyncio
import ipaddress
import re
from typing import List, Optional, Tuple
from urllib.parse import urljoin, urlparse, urldefrag
from bs4 import BeautifulSoup
import httpx
from pydantic import BaseModel, Field

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 (BrochureGenerator/1.0)"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

BLOCKED_HOSTNAMES = {"localhost", "0.0.0.0", "127.0.0.1", "::1", "localhost.localdomain"}


class PageCrawlResult(BaseModel):
    url: str
    title: str = ""
    text: str = ""
    links: List[str] = Field(default_factory=list)
    success: bool = True
    error: Optional[str] = None


def validate_url(url: str) -> str:
    """
    Validate, sanitize, and normalize target URLs.
    Guards against SSRF attacks targeting internal or loopback IP ranges.
    """
    cleaned_url = url.strip()
    if not cleaned_url:
        raise ValueError("URL cannot be empty.")

    # Check scheme first
    parsed_initial = urlparse(cleaned_url)
    if not parsed_initial.scheme:
        cleaned_url = f"https://{cleaned_url}"
        parsed = urlparse(cleaned_url)
    elif parsed_initial.scheme.lower() not in {"http", "https"}:
        raise ValueError(f"Invalid URL scheme '{parsed_initial.scheme}'. Only HTTP and HTTPS are supported.")
    else:
        parsed = parsed_initial

    hostname = (parsed.hostname or "").lower()
    if not hostname:
        raise ValueError("Invalid URL: missing hostname.")

    if hostname in BLOCKED_HOSTNAMES:
        raise ValueError("Private or local network destinations are not allowed.")

    # Check for direct IP address SSRF
    ip_obj = None
    try:
        ip_obj = ipaddress.ip_address(hostname)
    except ValueError:
        pass

    if ip_obj is not None and (
        ip_obj.is_private
        or ip_obj.is_loopback
        or ip_obj.is_link_local
        or ip_obj.is_reserved
        or ip_obj.is_multicast
    ):
        raise ValueError("Private or local network destinations are not allowed.")

    return cleaned_url


def is_internal_link(base_url: str, candidate_url: str) -> bool:
    """
    Determine if a candidate link belongs to the same domain (including subdomains).
    """
    base_host = (urlparse(base_url).hostname or "").lower()
    cand_host = (urlparse(candidate_url).hostname or "").lower()

    if not base_host or not cand_host:
        return False

    return cand_host == base_host or cand_host.endswith(f".{base_host}") or base_host.endswith(f".{cand_host}")


def clean_html(html_content: str, max_chars: int = 4000) -> Tuple[str, str]:
    """
    Parse HTML, extract the title, strip decorative/noisy elements,
    and return clean text truncated to max_chars.
    """
    try:
        soup = BeautifulSoup(html_content, "lxml")
    except Exception:
        soup = BeautifulSoup(html_content, "html.parser")

    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    # Decompose script, style, and media noise
    for tag in soup(["script", "style", "noscript", "svg", "iframe", "canvas", "form", "button", "input"]):
        tag.decompose()

    # Extract clean text
    body = soup.body if soup.body else soup
    raw_text = body.get_text(separator="\n", strip=True)

    # Normalize multiple newlines and spaces
    cleaned_lines = [re.sub(r"[ \t]+", " ", line).strip() for line in raw_text.splitlines() if line.strip()]
    full_text = "\n".join(cleaned_lines)

    if len(full_text) > max_chars:
        full_text = full_text[:max_chars].rstrip() + "..."

    return title, full_text


def extract_links(base_url: str, html_content: str, max_links: int = 60) -> List[str]:
    """
    Extract, resolve, and normalize hyperlinks from HTML content.
    Filters out non-HTTP schemes, fragments, and media files.
    """
    try:
        soup = BeautifulSoup(html_content, "lxml")
    except Exception:
        soup = BeautifulSoup(html_content, "html.parser")

    seen = set()
    links: List[str] = []

    # File extensions to ignore for brochure context
    ignored_extensions = (
        ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp",
        ".pdf", ".zip", ".tar", ".gz", ".mp4", ".mp3",
        ".css", ".js", ".json", ".xml"
    )

    for anchor in soup.find_all("a", href=True):
        raw_href = anchor.get("href", "").strip()
        if not raw_href or raw_href.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
            continue

        absolute_url = urljoin(base_url, raw_href)
        # Strip URL fragment (#section)
        clean_url, _ = urldefrag(absolute_url)
        parsed = urlparse(clean_url)

        if parsed.scheme.lower() not in {"http", "https"}:
            continue

        if any(parsed.path.lower().endswith(ext) for ext in ignored_extensions):
            continue

        if clean_url not in seen:
            seen.add(clean_url)
            links.append(clean_url)
            if len(links) >= max_links:
                break

    return links


async def crawl_page(
    url: str,
    timeout: float = 12.0,
    max_chars: int = 4000,
    client: Optional[httpx.AsyncClient] = None
) -> PageCrawlResult:
    """
    Asynchronously fetch and parse a single web page.
    """
    try:
        validated = validate_url(url)
    except ValueError as e:
        return PageCrawlResult(url=url, success=False, error=str(e))

    should_close_client = False
    if client is None:
        client = httpx.AsyncClient(
            headers=DEFAULT_HEADERS,
            follow_redirects=True,
            timeout=timeout,
            verify=True
        )
        should_close_client = True

    try:
        response = await client.get(validated)
        if response.status_code >= 400:
            return PageCrawlResult(
                url=validated,
                success=False,
                error=f"HTTP {response.status_code} {response.reason_phrase}"
            )

        html_text = response.text
        title, text = clean_html(html_text, max_chars=max_chars)
        links = extract_links(validated, html_text)

        return PageCrawlResult(
            url=validated,
            title=title,
            text=text,
            links=links,
            success=True
        )
    except httpx.TimeoutException:
        return PageCrawlResult(url=validated, success=False, error="Request timed out.")
    except Exception as exc:
        return PageCrawlResult(url=validated, success=False, error=str(exc))
    finally:
        if should_close_client:
            await client.aclose()


async def crawl_multiple_pages(
    urls: List[str],
    max_concurrent: int = 3,
    timeout: float = 12.0,
    max_chars: int = 3000
) -> List[PageCrawlResult]:
    """
    Concurrently crawl a list of URLs with concurrency control and resilient error handling.
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async with httpx.AsyncClient(
        headers=DEFAULT_HEADERS,
        follow_redirects=True,
        timeout=timeout
    ) as client:
        async def _fetch(u: str) -> PageCrawlResult:
            async with semaphore:
                return await crawl_page(u, timeout=timeout, max_chars=max_chars, client=client)

        tasks = [_fetch(url) for url in urls]
        return await asyncio.gather(*tasks)
