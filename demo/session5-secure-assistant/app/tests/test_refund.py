import time

from refund_confirm import handler


class FakeTable:
    def __init__(self, item=None):
        self.item = item
        self.updated = False

    def get_item(self, Key):
        if self.item and self.item["confirmationToken"] == Key["confirmationToken"]:
            return {"Item": dict(self.item)}
        return {}

    def update_item(self, Key, **kwargs):
        self.updated = True
        if self.item:
            self.item["status"] = "CONFIRMED"


VALID_TOKEN = "f47ac10b-58cc-4372-a567-0e02b2c3d479"


def _pending(ttl_offset=600):
    return {
        "confirmationToken": VALID_TOKEN,
        "status": "PENDING_CONFIRMATION",
        "ttl": int(time.time()) + ttl_offset,
    }


def test_confirm_bad_token_format():
    assert handler.confirm_refund(FakeTable(), "nope")["status"] == 400


def test_confirm_unknown_token():
    assert handler.confirm_refund(FakeTable(), VALID_TOKEN)["status"] == 404


def test_confirm_happy_path_executes_once():
    table = FakeTable(_pending())
    result = handler.confirm_refund(table, VALID_TOKEN)
    assert result["status"] == 200
    assert result["body"]["status"] == "CONFIRMED"
    assert table.updated is True


def test_confirm_idempotent_on_already_confirmed():
    item = _pending()
    item["status"] = "CONFIRMED"
    table = FakeTable(item)
    result = handler.confirm_refund(table, VALID_TOKEN)
    assert result["status"] == 200
    assert result["body"].get("idempotent") is True
    # No second update on an already-confirmed refund.
    assert table.updated is False


def test_confirm_expired():
    table = FakeTable(_pending(ttl_offset=-10))
    result = handler.confirm_refund(table, VALID_TOKEN)
    assert result["status"] == 410
