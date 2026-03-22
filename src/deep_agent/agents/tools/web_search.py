"""Web tools: web_search and web_fetch with security hardening."""

import html
import ipaddress
import json
import re
from typing import Literal
from urllib.parse import urlparse

import httpx
from langchain_core.tools import tool

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7_2) AppleWebKit/537.36"
MAX_REDIRECTS = 5

PRIVATE_IP_RANGES = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]

BLOCKED_HOSTNAMES = {
    "localhost",
    "127.0.0.1",
    "::1",
    "169.254.169.254",
    "metadata.google.internal",
    "metadata.azure.com",
    "metadata.aws.internal",
    "kubernetes.default.svc",
}


def _strip_tags(text: str) -> str:
    """Remove HTML tags and decode entities."""
    text = re.sub(r"<script[\s\S]*?</script>", "", text, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", "", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).strip()


def _normalize(text: str) -> str:
    """Normalize whitespace."""
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _is_private_ip(ip: str) -> bool:
    """Check if IP address is in a private range."""
    try:
        ip_obj = ipaddress.ip_address(ip)
        for network in PRIVATE_IP_RANGES:
            if ip_obj in network:
                return True
        return False
    except ValueError:
        return False


def _validate_url(url: str) -> tuple[bool, str]:
    """Validate URL with SSRF protection."""
    try:
        p = urlparse(url)

        if p.scheme not in ("http", "https"):
            return False, f"Only http/https allowed, got '{p.scheme or 'none'}'"

        hostname = p.hostname.lower() if p.hostname else ""
        if not hostname:
            return False, "Missing domain"

        if hostname in BLOCKED_HOSTNAMES:
            return False, f"Blocked hostname: {hostname}"

        import socket

        try:
            ip = socket.gethostbyname(hostname)
            if _is_private_ip(ip):
                return False, f"Private IP blocked: {ip}"
        except socket.gaierror:
            return False, f"Could not resolve hostname: {hostname}"

        return True, ""
    except Exception as e:
        return False, str(e)


def _to_markdown(html: str) -> str:
    """Convert HTML to markdown."""
    text = re.sub(
        r'<a\s+[^>]*href=["\']([^"\']+)["\'][^>]*>([\s\S]*?)</a>',
        lambda m: f"[{_strip_tags(m[2])}]({m[1]})",
        html,
        flags=re.I,
    )
    text = re.sub(
        r"<h([1-6])[^>]*>([\s\S]*?)</h\1>",
        lambda m: f"\n{'#' * int(m[1])} {_strip_tags(m[2])}\n",
        text,
        flags=re.I,
    )
    text = re.sub(
        r"<li[^>]*>([\s\S]*?)</li>",
        lambda m: f"\n- {_strip_tags(m[1])}",
        text,
        flags=re.I,
    )
    text = re.sub(r"</(p|div|section|article)>", "\n\n", text, flags=re.I)
    text = re.sub(r"<(br|hr)\s*/?>", "\n", text, flags=re.I)
    return _normalize(_strip_tags(text))


@tool
async def web_search(query: str, count: int = 5) -> str:
    """Search the web using DuckDuckGo.

    Args:
        query: Search query
        count: Number of results (1-10, default: 5)

    Returns:
        Search results with titles, URLs, and snippets
    """
    from duckduckgo_search import DDGS

    try:
        n = min(max(count, 1), 10)
        results = []
        with DDGS() as ddgs:
            ddgs_gen = ddgs.text(query, max_results=n)
            for r in ddgs_gen:
                results.append(r)

        if not results:
            return f"No results for: {query}"

        lines = [f"Results for: {query}\n"]
        for i, item in enumerate(results, 1):
            lines.append(f"{i}. {item.get('title', '')}\n   {item.get('href', '')}")
            if body := item.get("body"):
                lines.append(f"   {body}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"


@tool
async def web_fetch(
    url: str,
    extract_mode: Literal["markdown", "text"] = "markdown",
    max_chars: int = 50000,
) -> str:
    """Fetch and extract content from a URL using Readability.

    Args:
        url: URL to fetch
        extract_mode: Output format - "markdown" (default) or "text"
        max_chars: Maximum characters to return (default: 50000)

    Returns:
        JSON string with extracted content, status, and metadata
    """
    from readability import Document

    is_valid, error_msg = _validate_url(url)
    if not is_valid:
        return json.dumps({"error": f"URL validation failed: {error_msg}", "url": url})

    try:
        async with httpx.AsyncClient(
            follow_redirects=True, max_redirects=MAX_REDIRECTS, timeout=30.0
        ) as client:
            r = await client.get(url, headers={"User-Agent": USER_AGENT})
            r.raise_for_status()

        ctype = r.headers.get("content-type", "")

        if "application/json" in ctype:
            text, extractor = json.dumps(r.json(), indent=2), "json"
        elif "text/html" in ctype or r.text[:256].lower().startswith(
            ("<!doctype", "<html")
        ):
            doc = Document(r.text)
            content = (
                _to_markdown(doc.summary())
                if extract_mode == "markdown"
                else _strip_tags(doc.summary())
            )
            text = f"# {doc.title()}\n\n{content}" if doc.title() else content
            extractor = "readability"
        else:
            text, extractor = r.text, "raw"

        truncated = len(text) > max_chars
        if truncated:
            text = text[:max_chars]

        return json.dumps(
            {
                "url": url,
                "finalUrl": str(r.url),
                "status": r.status_code,
                "extractor": extractor,
                "truncated": truncated,
                "length": len(text),
                "text": text,
            }
        )
    except Exception as e:
        return json.dumps({"error": str(e), "url": url})
