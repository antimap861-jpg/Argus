import ipaddress
import socket
from html.parser import HTMLParser
from urllib.parse import urlparse, urljoin

import httpx

from src.models.website import WebsiteEvidence

CONNECT_TIMEOUT_SECONDS = 10.0
MAX_REDIRECTS = 5
MAX_CONTENT_BYTES = 2 * 1024 * 1024  # 2 MB
REDIRECT_STATUS_CODES = (301, 302, 303, 307, 308)


class _PageInspector(HTMLParser):
    """Extracts a page title and detects login-related form fields.
    Does not execute any scripts; pure text/structure parsing."""

    def __init__(self):
        super().__init__()
        self.title: str | None = None
        self.has_password_field: bool = False
        self.has_login_form: bool = False
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "input" and attrs_dict.get("type", "").lower() == "password":
            self.has_password_field = True
        elif tag == "form":
            self.has_login_form = True

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title and self.title is None:
            stripped = data.strip()
            if stripped:
                self.title = stripped


def _is_public_ip(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False
    return not (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def _resolve_ips(hostname: str) -> set[str] | None:
    """Returns the set of resolved IPs, or None if DNS resolution failed."""
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return None
    return {info[4][0] for info in infos}


def fetch_website(url: str) -> WebsiteEvidence:
    """
    Fetches a webpage's static HTML content, refusing to connect to any
    private/internal address at any hop of a redirect chain (SSRF
    protection). Does not execute JavaScript. Does not assign a risk
    verdict.
    """
    current_url = url
    redirect_count = 0

    with httpx.Client(follow_redirects=False, timeout=CONNECT_TIMEOUT_SECONDS) as client:
        while True:
            parsed = urlparse(current_url)

            if parsed.scheme not in ("http", "https"):
                return WebsiteEvidence(
                    requested_url=url,
                    fetch_successful=False,
                    redirect_count=redirect_count,
                    blocked_reason=f"Unsupported URL scheme: {parsed.scheme!r}",
                )

            hostname = parsed.hostname
            if not hostname:
                return WebsiteEvidence(
                    requested_url=url,
                    fetch_successful=False,
                    redirect_count=redirect_count,
                    error_message="Could not parse a hostname from the URL",
                )

            ips = _resolve_ips(hostname)
            if ips is None:
                return WebsiteEvidence(
                    requested_url=url,
                    fetch_successful=False,
                    final_url=current_url,
                    redirect_count=redirect_count,
                    error_message=f"DNS resolution failed for hostname: {hostname}",
                )
            if not all(_is_public_ip(ip) for ip in ips):
                return WebsiteEvidence(
                    requested_url=url,
                    fetch_successful=False,
                    final_url=current_url,
                    redirect_count=redirect_count,
                    blocked_reason=f"Refused: '{hostname}' resolves to a private or internal address",
                )

            try:
                with client.stream("GET", current_url) as response:
                    if response.status_code in REDIRECT_STATUS_CODES and "location" in response.headers:
                        redirect_count += 1
                        if redirect_count > MAX_REDIRECTS:
                            return WebsiteEvidence(
                                requested_url=url,
                                fetch_successful=False,
                                final_url=current_url,
                                redirect_count=redirect_count,
                                error_message="Too many redirects",
                            )
                        current_url = urljoin(current_url, response.headers["location"])
                        continue

                    content_bytes = b""
                    for chunk in response.iter_bytes():
                        content_bytes += chunk
                        if len(content_bytes) >= MAX_CONTENT_BYTES:
                            break

                    content_type = response.headers.get("content-type", "")
                    title = None
                    has_password_field = None
                    has_login_form = None

                    if "text/html" in content_type.lower():
                        text = content_bytes.decode(
                            response.encoding or "utf-8", errors="replace"
                        )
                        inspector = _PageInspector()
                        inspector.feed(text)
                        title = inspector.title
                        has_password_field = inspector.has_password_field
                        has_login_form = inspector.has_login_form

                    return WebsiteEvidence(
                        requested_url=url,
                        fetch_successful=True,
                        final_url=current_url,
                        redirect_count=redirect_count,
                        status_code=response.status_code,
                        title=title,
                        has_password_field=has_password_field,
                        has_login_form=has_login_form,
                    )
            except httpx.RequestError as e:
                return WebsiteEvidence(
                    requested_url=url,
                    fetch_successful=False,
                    final_url=current_url,
                    redirect_count=redirect_count,
                    error_message=f"Request failed: {str(e)}",
                )
