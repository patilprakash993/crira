from utils import redact_pii


def test_redact_email_and_phone():
    text = "Contact me at john.doe@example.com or +1 (555) 123-4567."
    redacted, found = redact_pii(text)
    assert "[PII_EMAIL]" in redacted
    assert "[PII_PHONE]" in redacted
    assert "PII_EMAIL" in found and "PII_PHONE" in found


def test_redact_name_and_order():
    text = "Sarah Smith ordered Order12345 and lives at 12 Elm Street, Anytown."
    redacted, found = redact_pii(text)
    assert "[PII_NAME]" in redacted
    assert "[PII_ADDRESS]" in redacted
    assert "[PII_ORDER]" in redacted
    assert isinstance(found, list)
    assert "PII_NAME" in found
    assert "PII_ADDRESS" in found
    assert "PII_ORDER" in found
