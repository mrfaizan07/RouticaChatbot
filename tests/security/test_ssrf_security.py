"""Security tests for SSRF protections and domain allowlists."""

import pytest
from app.core.exceptions import ScrapingSSRFError
from app.utils.validators import is_private_ip, validate_crawl_url


def test_private_ip_detection():
    assert is_private_ip("127.0.0.1") is True
    assert is_private_ip("10.0.0.1") is True
    assert is_private_ip("192.168.1.100") is True
    assert is_private_ip("172.16.0.5") is True
    assert is_private_ip("169.254.169.254") is True  # Cloud metadata
    assert is_private_ip("::1") is True  # IPv6 loopback
    assert is_private_ip("8.8.8.8") is False  # Public IP


def test_validate_crawl_url_rejects_unallowed_domains():
    with pytest.raises(ScrapingSSRFError):
        validate_crawl_url("https://evil-attacker.com/malicious")

    with pytest.raises(ScrapingSSRFError):
        validate_crawl_url("https://google.com")


def test_validate_crawl_url_rejects_invalid_schemes():
    with pytest.raises(ScrapingSSRFError):
        validate_crawl_url("file:///etc/passwd")

    with pytest.raises(ScrapingSSRFError):
        validate_crawl_url("ftp://routica.com/file.txt")


def test_validate_crawl_url_allows_routica_domains(monkeypatch):
    # Mock DNS resolution to public IP for offline testing
    import socket

    def mock_getaddrinfo(host, port, *args, **kwargs):
        return [(2, 1, 0, "", ("104.21.45.10", 80))]

    monkeypatch.setattr(socket, "getaddrinfo", mock_getaddrinfo)

    url = validate_crawl_url("https://routica.com/products", allow_custom_domains=["routica.com"])
    assert url == "https://routica.com/products"