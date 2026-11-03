"""URL canonicalization and link normalization utilities."""

from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse


def normalize_canonical_url(url: str, base_url: str = "https://routica.com") -> str:
    """Normalizes URL by removing tracking query parameters, anchors, and trailing slashes."""
    if not url:
        return ""

    # Join relative URLs with base URL
    full_url = urljoin(base_url, url.strip())
    parsed = urlparse(full_url)

    # Force lowercase scheme and hostname
    scheme = parsed.scheme.lower() or "https"
    hostname = (parsed.hostname or "").lower()

    # Normalize path: collapse duplicate slashes and strip trailing slash (except root)
    path = parsed.path
    while "//" in path:
        path = path.replace("//", "/")
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    # Strip marketing/tracking query params (utm_*, fbclid, gclid, etc.)
    query_params = parse_qs(parsed.query, keep_blank_values=False)
    filtered_params = {
        k: v for k, v in query_params.items() if not k.lower().startswith("utm_") and k.lower() not in ("fbclid", "gclid", "ref")
    }
    cleaned_query = urlencode(filtered_params, doseq=True)

    # Reconstruct without fragment
    return urlunparse((scheme, hostname, path, "", cleaned_query, ""))

