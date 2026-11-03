"""Security validators: SSRF prevention, safe DNS resolution, and filename sanitization."""

import ipaddress
import re
import socket
from urllib.parse import urlparse

from app.config import get_settings
from app.core.constants import ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES
from app.core.exceptions import ScrapingSSRFError, ValidationException

settings = get_settings()


def is_private_ip(ip_str: str) -> bool:
    """Checks whether an IP address belongs to private, loopback, link-local, or cloud metadata ranges."""
    try:
        ip = ipaddress.ip_address(ip_str)
        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
            # Explicit AWS/GCP/Azure link-local metadata protection
            or str(ip).startswith("169.254.")
        )
    except ValueError:
        return True


def validate_crawl_url(url: str, allow_custom_domains: list[str] | None = None) -> str:
    """Strict SSRF validator: ensures URL has http(s) scheme, allowed domain, and resolves to public IP."""
    if not url or not isinstance(url, str):
        raise ScrapingSSRFError("Invalid URL provided")

    url = url.strip()
    parsed = urlparse(url)

    if parsed.scheme.lower() not in ("http", "https"):
        raise ScrapingSSRFError(f"Disallowed URL scheme: '{parsed.scheme}'. Only http and https are allowed.")

    hostname = (parsed.hostname or "").lower().strip()
    if not hostname:
        raise ScrapingSSRFError("URL must contain a valid hostname")

    allowed_domains = allow_custom_domains or settings.scrape_allowed_domains_list
    if hostname not in allowed_domains:
        raise ScrapingSSRFError(f"Domain '{hostname}' is not in the allowed crawling list: {allowed_domains}")

    # DNS Resolution Check to prevent internal IP / DNS rebinding attacks
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        for _, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            if is_private_ip(ip_str):
                raise ScrapingSSRFError(f"Domain '{hostname}' resolved to private or restricted IP: {ip_str}")
    except socket.gaierror as exc:
        raise ScrapingSSRFError(f"DNS resolution failed for hostname '{hostname}': {exc}")

    return url


def sanitize_filename(filename: str) -> str:
    """Sanitizes filename against path traversal (../, ..\\) and invalid characters."""
    if not filename:
        return "unnamed_document"
    # Remove path components
    cleaned = filename.replace("\\", "/").split("/")[-1].strip()
    # Remove non-alphanumeric chars except safe ones
    cleaned = re.sub(r"[^\w\s\.-]", "_", cleaned)
    # Avoid hidden files
    cleaned = cleaned.lstrip(".")
    return cleaned[:100] if cleaned else "document"


def validate_file_upload(filename: str, content_type: str, file_size_bytes: int) -> str:
    """Validates uploaded file extension, size limits, and ensures only Excel and JSON files are accepted."""
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size_bytes > max_bytes:
        raise ValidationException(f"File size exceeds maximum allowed limit of {settings.MAX_UPLOAD_SIZE_MB} MB")

    clean_name = sanitize_filename(filename)
    extension = "." + clean_name.split(".")[-1].lower() if "." in clean_name else ""

    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationException(f"Unsupported file extension '{extension}'. Only Excel (.xlsx, .xls) and JSON (.json) files are permitted.")

    return clean_name

