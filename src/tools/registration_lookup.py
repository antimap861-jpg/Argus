import httpx

from src.models.registration import RegistrationEvidence

IANA_BOOTSTRAP_URL = "https://data.iana.org/rdap/dns.json"


def _extract_tld(hostname: str) -> str:
    """
    Returns the rightmost label of a hostname (naive TLD extraction).

    LIMITATION: This does not use a public suffix list, so multi-part
    TLDs like "co.uk" are not handled correctly. Known, accepted
    limitation for this stage.
    """
    return hostname.rstrip(".").split(".")[-1].lower()


def _find_rdap_base_url(tld: str, client: httpx.Client) -> str | None:
    response = client.get(IANA_BOOTSTRAP_URL, timeout=10.0)
    response.raise_for_status()
    data = response.json()

    for entry in data.get("services", []):
        tlds, urls = entry[0], entry[1]
        if tld in [t.lower() for t in tlds]:
            return urls[0].rstrip("/")
    return None


def _parse_rdap_response(hostname: str, data: dict) -> RegistrationEvidence:
    registrar = None
    for entity in data.get("entities", []):
        if "registrar" in entity.get("roles", []):
            vcard = entity.get("vcardArray")
            if vcard and len(vcard) > 1:
                for field in vcard[1]:
                    if field[0] == "fn":
                        registrar = field[3]
                        break
            break

    creation_date = None
    expiration_date = None
    for event in data.get("events", []):
        if event.get("eventAction") == "registration":
            creation_date = event.get("eventDate")
        elif event.get("eventAction") == "expiration":
            expiration_date = event.get("eventDate")

    nameservers = [
        ns.get("ldhName")
        for ns in data.get("nameservers", [])
        if ns.get("ldhName")
    ]

    return RegistrationEvidence(
        hostname=hostname,
        lookup_successful=True,
        registrar=registrar,
        creation_date=creation_date,
        expiration_date=expiration_date,
        nameservers=nameservers,
    )


def lookup_registration(hostname: str) -> RegistrationEvidence:
    """
    Looks up domain registration evidence via RDAP.

    Does not compute domain age. Does not assign a risk verdict.
    """
    tld = _extract_tld(hostname)

    try:
        with httpx.Client() as client:
            base_url = _find_rdap_base_url(tld, client)
            if base_url is None:
                return RegistrationEvidence(
                    hostname=hostname,
                    lookup_successful=False,
                    error_message=f"No RDAP server found for TLD: {tld}",
                )

            rdap_url = f"{base_url}/domain/{hostname}"
            response = client.get(rdap_url, timeout=10.0)

            if response.status_code == 404:
                return RegistrationEvidence(
                    hostname=hostname,
                    lookup_successful=False,
                    error_message="Domain not found in RDAP registry",
                )

            response.raise_for_status()
            return _parse_rdap_response(hostname, response.json())

    except httpx.RequestError as e:
        return RegistrationEvidence(
            hostname=hostname,
            lookup_successful=False,
            error_message=f"Network error during RDAP lookup: {str(e)}",
        )
    except httpx.HTTPStatusError as e:
        return RegistrationEvidence(
            hostname=hostname,
            lookup_successful=False,
            error_message=f"RDAP server returned error: {str(e)}",
        )
