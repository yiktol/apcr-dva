from assistant import pii


def test_mask_account_keeps_last_four():
    assert pii.mask_account("123456789012") == "********9012"
    assert pii.mask_account("12") == "****"


def test_mask_ssn():
    assert pii.mask_ssn("123-45-6789") == "***-**-6789"
    assert pii.mask_ssn("bad") == "***-**-****"


def test_mask_email():
    assert pii.mask_email("mary.major@example.com") == "m***@example.com"
    assert pii.mask_email("notanemail") == "***"


def test_mask_pii_free_text():
    text = "acct 123456789012 ssn 123-45-6789 mail a@b.com"
    masked = pii.mask_pii(text)
    assert "123456789012" not in masked
    assert "123-45-6789" not in masked
    assert "a@b.com" not in masked
    assert "9012" in masked  # last-4 retained


def test_validators():
    assert pii.validate_order_id("ORD-000123")
    assert not pii.validate_order_id("ORD-12")
    assert pii.validate_uuid4("f47ac10b-58cc-4372-a567-0e02b2c3d479")
    assert not pii.validate_uuid4("not-a-uuid")
    assert pii.validate_amount(10, 50)
    assert not pii.validate_amount(0, 50)
    assert not pii.validate_amount(100, 50)
    assert not pii.validate_amount("x", 50)
