from src.tools.dns_resolver import resolve_hostname

def test_resolve_hostname_success():
    evidence = resolve_hostname("google.com")
    assert evidence.resolved is True
    assert evidence.hostname == "google.com"
    assert len(evidence.ip_addresses) > 0
    assert evidence.error_message is None
    print("test_resolve_hostname_success passed")

def test_resolve_hostname_failure():
    # An intentionally non-existent domain
    evidence = resolve_hostname("this-domain-should-definitely-not-exist.test")
    assert evidence.resolved is False
    assert evidence.hostname == "this-domain-should-definitely-not-exist.test"
    assert len(evidence.ip_addresses) == 0
    assert evidence.error_message is not None
    # We should get a gaierror message string
    assert "name or service not known" in evidence.error_message.lower() or "nodename nor servname" in evidence.error_message.lower()
    print("test_resolve_hostname_failure passed")

def test_resolve_hostname_invalid_encoding():
    # Test something that might fail IDNA encoding depending on socket implementation
    # A string that exceeds 63 characters per label
    long_label = "a" * 100 + ".com"
    evidence = resolve_hostname(long_label)
    assert evidence.resolved is False
    assert evidence.error_message is not None
    print("test_resolve_hostname_invalid_encoding passed")

if __name__ == "__main__":
    test_resolve_hostname_success()
    test_resolve_hostname_failure()
    test_resolve_hostname_invalid_encoding()
    print("All tests passed.")
