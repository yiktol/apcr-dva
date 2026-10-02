"""Pure PII validation + masking helpers for the assistant tool layer.

GUARDRAIL TOOL-CALL BLIND SPOT (read this before changing anything):
    The Bedrock Guardrail inspects the model's PROMPT and COMPLETION text only.
    It does NOT see — and therefore does NOT mask — PII that flows through
    tool-call ARGUMENTS or tool RESULTS. If the model passes a raw account
    number as a tool argument, that raw value reaches the tool handler
    untouched by the guardrail.

    Therefore the tool/handler layer is the PRIMARY, in-our-control defense for
    PII at rest and in logs: every tool handler masks + validates its own
    arguments with these functions BEFORE persisting anything to DynamoDB or
    writing any log line. Never rely on the guardrail (or on log redaction) to
    keep raw PII out of our data.

These functions are pure (no AWS, no I/O) so they are unit-testable without any
dependency installed.
"""
import re

# Validation patterns.
ORDER_ID_RE = re.compile(r"^ORD-[0-9]{6}$")
UUID4_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

# Detection patterns for masking free text.
_ACCOUNT_RE = re.compile(r"\b\d{10,12}\b")  # US bank account: 10-12 digits
_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_EMAIL_RE = re.compile(r"\b[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}\b")


def mask_account(value: str) -> str:
    """Mask all but the last 4 digits of an account-like number."""
    digits = re.sub(r"\D", "", value or "")
    if len(digits) < 4:
        return "****"
    return "*" * (len(digits) - 4) + digits[-4:]


def mask_ssn(value: str) -> str:
    """Mask an SSN, keeping only the last 4 digits."""
    digits = re.sub(r"\D", "", value or "")
    if len(digits) != 9:
        return "***-**-****"
    return "***-**-" + digits[-4:]


def mask_email(value: str) -> str:
    """Mask the local part of an email, keeping the domain."""
    value = value or ""
    if "@" not in value:
        return "***"
    local, _, domain = value.partition("@")
    keep = local[:1] if local else ""
    return f"{keep}***@{domain}"


def mask_pii(text: str) -> str:
    """Mask any account numbers, SSNs, or emails found in free text.

    Order matters: mask SSNs before bare account digits so an SSN's digit run is
    not partially consumed by the account matcher.
    """
    if not text:
        return text
    text = _SSN_RE.sub(lambda m: mask_ssn(m.group(0)), text)
    text = _EMAIL_RE.sub(lambda m: mask_email(m.group(0)), text)
    text = _ACCOUNT_RE.sub(lambda m: mask_account(m.group(0)), text)
    return text


def validate_order_id(order_id: str) -> bool:
    """True if order_id matches ^ORD-[0-9]{6}$."""
    return bool(order_id and ORDER_ID_RE.match(order_id))


def validate_uuid4(token: str) -> bool:
    """True if token is a uuid4-formatted string."""
    return bool(token and UUID4_RE.match(token))


def validate_amount(amount, max_amount: float) -> bool:
    """True if amount is a positive number not exceeding max_amount."""
    try:
        value = float(amount)
    except (TypeError, ValueError):
        return False
    return 0 < value <= float(max_amount)
