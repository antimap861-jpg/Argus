import socket
from src.models.dns import DNSEvidence

def resolve_hostname(hostname: str) -> DNSEvidence:
    """
    Resolves a hostname to its IP addresses.
    
    Args:
        hostname: The domain name to resolve.
        
    Returns:
        DNSEvidence: The evidence containing resolved IPs or error details.
    """
    try:
        # getaddrinfo returns a list of 5-tuples: (family, type, proto, canonname, sockaddr)
        # sockaddr is a tuple where the first element is the IP address string
        addr_info = socket.getaddrinfo(hostname, None)
        
        # Extract IPs and remove duplicates
        ips = list(set(info[4][0] for info in addr_info))
        
        return DNSEvidence(
            hostname=hostname,
            resolved=True,
            ip_addresses=ips
        )
    except socket.gaierror as e:
        return DNSEvidence(
            hostname=hostname,
            resolved=False,
            error_message=str(e)
        )
    except UnicodeError as e:
        # Handles cases where hostname cannot be encoded via IDNA
        return DNSEvidence(
            hostname=hostname,
            resolved=False,
            error_message=f"Invalid hostname encoding: {str(e)}"
        )
