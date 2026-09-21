import socket
import ssl

from src.models.tls import TLSEvidence

CONNECT_TIMEOUT_SECONDS = 5.0


def _format_dn(name_tuples) -> str | None:
    """Flattens an ssl cert 'subject'/'issuer' tuple structure into a
    readable string, e.g. 'CN=example.com,O=Example Inc'."""
    if not name_tuples:
        return None
    parts = []
    for rdn in name_tuples:
        for key, value in rdn:
            parts.append(f"{key}={value}")
    return ",".join(parts) if parts else None


def _inspect_verified(hostname: str) -> TLSEvidence:
    context = ssl.create_default_context()
    with socket.create_connection((hostname, 443), timeout=CONNECT_TIMEOUT_SECONDS) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
            return TLSEvidence(
                hostname=hostname,
                connection_successful=True,
                certificate_valid=True,
                issuer=_format_dn(cert.get("issuer")),
                subject=_format_dn(cert.get("subject")),
                not_before=cert.get("notBefore"),
                not_after=cert.get("notAfter"),
                is_self_signed=False,
            )


def _inspect_unverified(hostname: str, original_error: str) -> TLSEvidence:
    """
    Used only when verified inspection fails due to a certificate
    problem. Connects without verifying the certificate chain, purely
    to extract the certificate's raw fields as evidence. Does not
    treat the resulting certificate as trustworthy.
    """
    context = ssl._create_unverified_context()
    try:
        with socket.create_connection((hostname, 443), timeout=CONNECT_TIMEOUT_SECONDS) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert_bin = ssock.getpeercert(binary_form=True)
                cert = ssock.getpeercert()

                issuer = _format_dn(cert.get("issuer")) if cert else None
                subject = _format_dn(cert.get("subject")) if cert else None

                is_self_signed = (
                    issuer is not None and subject is not None and issuer == subject
                )

                return TLSEvidence(
                    hostname=hostname,
                    connection_successful=True,
                    certificate_valid=False,
                    issuer=issuer,
                    subject=subject,
                    not_before=cert.get("notBefore") if cert else None,
                    not_after=cert.get("notAfter") if cert else None,
                    is_self_signed=is_self_signed,
                    error_message=original_error,
                )
    except (ssl.SSLError, socket.error, OSError) as e:
        return TLSEvidence(
            hostname=hostname,
            connection_successful=False,
            error_message=f"{original_error}; unverified retry also failed: {str(e)}",
        )


def inspect_tls(hostname: str) -> TLSEvidence:
    """
    Connects to hostname:443 and inspects the TLS certificate.

    Does not fetch page content. Does not assign a risk verdict.
    A certificate validation failure is captured as evidence, not
    treated as a reason to abandon the lookup.
    """
    try:
        return _inspect_verified(hostname)
    except ssl.SSLCertVerificationError as e:
        return _inspect_unverified(hostname, f"Certificate verification failed: {str(e)}")
    except (socket.timeout, TimeoutError):
        return TLSEvidence(
            hostname=hostname,
            connection_successful=False,
            error_message="Connection timed out",
        )
    except (socket.gaierror, ConnectionRefusedError, OSError) as e:
        return TLSEvidence(
            hostname=hostname,
            connection_successful=False,
            error_message=f"Connection failed: {str(e)}",
        )
