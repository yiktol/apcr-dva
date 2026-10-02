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


def test_strip_reasoning_removes_paired_block():
    text = "<thinking>internal plan here</thinking>\nYour order is placed."
    assert pii.strip_reasoning(text) == "Your order is placed."


def test_strip_reasoning_removes_block_mid_text():
    text = "Sure. <thinking>let me check the menu</thinking> Done!"
    assert "thinking" not in pii.strip_reasoning(text)
    assert "Sure." in pii.strip_reasoning(text)
    assert "Done!" in pii.strip_reasoning(text)


def test_strip_reasoning_handles_dangling_open_tag():
    # A truncated reasoning block (no close) must not leak to the user.
    text = "Here is your answer.\n<thinking>I was about to reason but got cut"
    out = pii.strip_reasoning(text)
    assert out == "Here is your answer."
    assert "thinking" not in out


def test_strip_reasoning_handles_stray_close_tag():
    text = "The order total is $12.50.</thinking>"
    assert pii.strip_reasoning(text) == "The order total is $12.50."


def test_strip_reasoning_passthrough_and_empty():
    assert pii.strip_reasoning("A normal reply.") == "A normal reply."
    assert pii.strip_reasoning("") == ""
    assert pii.strip_reasoning(None) is None


def test_strip_reasoning_is_case_insensitive():
    text = "<Thinking>plan</Thinking>Hello"
    assert pii.strip_reasoning(text) == "Hello"
