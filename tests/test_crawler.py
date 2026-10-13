import pytest
from backend.services.crawler import (
    validate_url,
    clean_html,
    extract_links,
    crawl_page,
    crawl_multiple_pages,
    PageCrawlResult,
    is_internal_link,
)


def test_validate_url_valid():
    assert validate_url("https://example.com") == "https://example.com"
    assert validate_url("http://test.org/about") == "http://test.org/about"
    assert validate_url("example.com") == "https://example.com"


def test_validate_url_ssrf_blocked():
    with pytest.raises(ValueError, match="Private or local"):
        validate_url("http://localhost:8000")
    with pytest.raises(ValueError, match="Private or local"):
        validate_url("http://127.0.0.1:3000")
    with pytest.raises(ValueError, match="Private or local"):
        validate_url("http://192.168.1.1")
    with pytest.raises(ValueError, match="Private or local"):
        validate_url("http://10.0.0.1")
    with pytest.raises(ValueError, match="Private or local"):
        validate_url("http://169.254.169.254")


def test_validate_url_invalid_scheme():
    with pytest.raises(ValueError, match="Invalid URL scheme"):
        validate_url("ftp://example.com")
    with pytest.raises(ValueError, match="Invalid URL scheme"):
        validate_url("javascript:alert(1)")


def test_clean_html_strips_scripts_and_extracts_title():
    html = """
    <!DOCTYPE html>
    <html>
      <head>
        <title> Acme Corp | Innovations </title>
        <script>console.log("noisy tracking script");</script>
        <style>body { color: red; }</style>
      </head>
      <body>
        <nav><a href="/home">Home</a></nav>
        <main>
          <h1>Welcome to Acme Corp</h1>
          <p>We build cutting-edge intelligent software solutions.</p>
          <script>alert("another script");</script>
        </main>
        <footer>
          <p>© 2026 Acme Corp</p>
        </footer>
      </body>
    </html>
    """
    title, text = clean_html(html, max_chars=1000)
    assert title == "Acme Corp | Innovations"
    assert "Welcome to Acme Corp" in text
    assert "cutting-edge intelligent software solutions" in text
    assert "noisy tracking script" not in text
    assert "color: red" not in text


def test_clean_html_respects_max_chars():
    html = "<html><head><title>Long</title></head><body>" + "<p>Test paragraph content. </p>" * 100 + "</body></html>"
    title, text = clean_html(html, max_chars=150)
    assert len(text) <= 153  # account for potential ellipsis
    assert title == "Long"


def test_extract_links_relative_to_absolute_and_filtering():
    base_url = "https://example.com/company/"
    html = """
    <html>
      <body>
        <a href="/about">About Us</a>
        <a href="careers">Careers</a>
        <a href="https://example.com/pricing">Pricing</a>
        <a href="https://twitter.com/example">Twitter</a>
        <a href="mailto:contact@example.com">Email Us</a>
        <a href="tel:+1234567890">Call Us</a>
        <a href="#section-contact">Jump to Section</a>
        <a href="javascript:void(0)">Do nothing</a>
        <a>No href</a>
      </body>
    </html>
    """
    links = extract_links(base_url, html)
    assert "https://example.com/about" in links
    assert "https://example.com/company/careers" in links
    assert "https://example.com/pricing" in links
    # Mailto, tel, javascript and fragment anchors should be omitted
    for link in links:
        assert not link.startswith(("mailto:", "tel:", "javascript:"))
        assert "#" not in link


def test_is_internal_link():
    assert is_internal_link("https://example.com", "https://example.com/about") is True
    assert is_internal_link("https://example.com", "https://blog.example.com/post") is True
    assert is_internal_link("https://example.com", "https://google.com") is False


@pytest.mark.asyncio
async def test_crawl_page_success():
    import respx
    import httpx

    test_url = "https://mockcompany.org"
    mock_html = """
    <html>
      <head><title>Mock Company</title></head>
      <body>
        <h1>Hello World</h1>
        <p>This is mock content for testing crawler.</p>
        <a href="/about">About Us</a>
      </body>
    </html>
    """

    with respx.mock(base_url=test_url) as respx_mock:
        respx_mock.get("/").respond(200, text=mock_html, headers={"Content-Type": "text/html"})
        result: PageCrawlResult = await crawl_page(test_url)

        assert result.success is True
        assert result.title == "Mock Company"
        assert "This is mock content for testing crawler" in result.text
        assert "https://mockcompany.org/about" in result.links
        assert result.error is None


@pytest.mark.asyncio
async def test_crawl_page_failure_graceful():
    import respx

    test_url = "https://mockcompany.org/missing"
    with respx.mock(base_url="https://mockcompany.org") as respx_mock:
        respx_mock.get("/missing").respond(404)
        result: PageCrawlResult = await crawl_page(test_url)

        assert result.success is False
        assert result.error is not None
        assert "404" in result.error


@pytest.mark.asyncio
async def test_crawl_multiple_pages():
    import respx

    urls = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3",
    ]

    with respx.mock(base_url="https://example.com") as respx_mock:
        respx_mock.get("/page1").respond(200, text="<html><head><title>Page 1</title></head><body>Content 1</body></html>")
        respx_mock.get("/page2").respond(200, text="<html><head><title>Page 2</title></head><body>Content 2</body></html>")
        respx_mock.get("/page3").respond(500)

        results = await crawl_multiple_pages(urls, max_concurrent=2)

        assert len(results) == 3
        assert results[0].success is True
        assert results[0].title == "Page 1"
        assert results[1].success is True
        assert results[1].title == "Page 2"
        # Page 3 failed but didn't crash the other fetches
        assert results[2].success is False
        assert "500" in results[2].error
