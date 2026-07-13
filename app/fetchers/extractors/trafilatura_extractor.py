"""Full-article extraction from a URL using trafilatura.

This module downloads a web page and extracts the main article content,
stripping ads, navigation, comments, and other boilerplate.
Trafilatura is the primary extractor; returns None on failure.
"""

from __future__ import annotations

import logging
import ipaddress
import socket
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx
import trafilatura

logger = logging.getLogger(__name__)

# Shared HTTP client settings
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

_ALLOWED_SCHEMES = {"http", "https"}
_MAX_REDIRECTS = 3


def _is_public_hostname(hostname: str) -> bool:
    """Reject localhost, private, and otherwise non-public destinations."""
    try:
        # Literal IP address
        ip_obj = ipaddress.ip_address(hostname)
        return not (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_multicast
            or ip_obj.is_reserved
            or ip_obj.is_unspecified
        )
    except ValueError:
        pass

    try:
        infos = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror:
        return False

    resolved_ips = set()
    for info in infos:
        sockaddr = info[4]
        ip_text = sockaddr[0]
        try:
            ip_obj = ipaddress.ip_address(ip_text)
        except ValueError:
            return False
        resolved_ips.add(ip_obj)

    if not resolved_ips:
        return False

    for ip_obj in resolved_ips:
        if (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_multicast
            or ip_obj.is_reserved
            or ip_obj.is_unspecified
        ):
            return False

    return True


def _is_safe_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in _ALLOWED_SCHEMES:
        return False
    if not parsed.hostname:
        return False
    if parsed.username or parsed.password:
        return False
    return _is_public_hostname(parsed.hostname)


async def _download_html(url: str, timeout: float) -> str:
    current_url = url

    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=False,
        headers=_HEADERS,
    ) as client:
        for _ in range(_MAX_REDIRECTS + 1):
            if not _is_safe_url(current_url):
                raise ValueError(f"Unsafe URL blocked: {current_url}")

            response = await client.get(current_url)

            if response.status_code in {301, 302, 303, 307, 308}:
                location = response.headers.get("Location")
                if not location:
                    raise ValueError("Redirect without a Location header")
                current_url = urljoin(current_url, location)
                continue

            response.raise_for_status()
            return response.text

    raise ValueError(f"Too many redirects while fetching {url}")


async def extract_article(
    url: str,
    timeout: float = 20.0,
) -> Optional[str]:
    """Download a URL and extract the main article text.

    Args:
        url: The article URL to extract.
        timeout: HTTP request timeout in seconds.

    Returns:
        The extracted article text, or None if extraction fails.
    """
    try:
        html = await _download_html(url, timeout)

        # Extract main content using trafilatura
        text = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            no_fallback=False,  # Allow fallback extraction methods
            favor_recall=True,  # Prefer getting more text over precision
        )

        if text and len(text.strip()) > 100:
            return text.strip()

        logger.debug("Extraction returned too little text for %s", url)
        return None

    except httpx.HTTPError as e:
        logger.debug("HTTP error extracting %s: %s", url, e)
        return None
    except Exception as e:
        logger.debug("Extraction error for %s: %s", url, e)
        return None
