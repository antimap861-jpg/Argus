from urllib.parse import urlparse

from src.models.indicators import URLIndicators


def analyze_url(url: str) -> URLIndicators:
    """
    Analyzes a URL string and extracts its components.
    
    Args:
        url: The URL string to parse.
        
    Returns:
        URLIndicators: The parsed structured URL information.
    """
    try:
        parsed = urlparse(url)
        # Attempt to access port, as this is where urlparse might raise ValueError for invalid ports
        _ = parsed.port
    except ValueError as e:
        # urlparse raises ValueError on things like invalid ports. 
        # For our purposes, we can fall back to returning the original URL with empty components if parsing completely fails.
        return URLIndicators(original_url=url, parsing_error=str(e))

    return URLIndicators(
        original_url=url,
        scheme=parsed.scheme if parsed.scheme else None,
        hostname=parsed.hostname,
        port=parsed.port,
        path=parsed.path if parsed.path else None,
        query=parsed.query if parsed.query else None,
        fragment=parsed.fragment if parsed.fragment else None,
    )
