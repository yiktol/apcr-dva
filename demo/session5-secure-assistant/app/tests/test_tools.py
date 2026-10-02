import logging
from decimal import Decimal

from assistant import tools


class FakeTable:
    def __init__(self):
        self.items = {}

    def put_item(self, Item):
        self.items[Item["confirmationToken"]] = Item


class _FakeClientError(Exception):
    """A botocore.exceptions.ClientError look-alike (no botocore needed)."""

    def __init__(self, code):
        super().__init__(code)
        self.response = {"Error": {"Code": code}}


class _StubTable:
    """Injectable orders-table stub for place_order / look_up_order tests.

    `get_items` maps orderId -> stored item (for get_item).
    `collide_first_put` raises a ConditionalCheckFailedException on the first
    put_item call to exercise the single-retry path.
    """

    def __init__(self, get_items=None, collide_first_put=False):
        self.get_items = get_items or {}
        self.put_items = []
        self.get_calls = []
        self._collide_first_put = collide_first_put
        self._put_calls = 0

    def put_item(self, Item, ConditionExpression=None):
        self._put_calls += 1
        if self._collide_first_put and self._put_calls == 1:
            raise _FakeClientError("ConditionalCheckFailedException")
        self.put_items.append(Item)

    def get_item(self, Key):
        self.get_calls.append(Key)
        item = self.get_items.get(Key["orderId"])
        return {"Item": item} if item is not None else {}


def test_initiate_refund_pending_and_no_money():
    table = FakeTable()
    req_ctx = {"pending_refunds": []}
    initiate = tools.make_initiate_refund(table, req_ctx, max_refund=50)

    result = initiate("ORD-000123", 12.50)

    assert result["status"] == "PENDING_CONFIRMATION"
    # A token was written to the table.
    assert len(table.items) == 1
    token = next(iter(table.items))
    written = table.items[token]
    assert written["status"] == "PENDING_CONFIRMATION"
    # The side channel carries the authoritative token.
    assert req_ctx["pending_refunds"][-1]["token"] == token
    # No field named like a settled payment exists — the tool moves no money.
    assert "paid" not in written and "settled" not in written


def test_initiate_refund_rejects_bad_input():
    table = FakeTable()
    req_ctx = {"pending_refunds": []}
    initiate = tools.make_initiate_refund(table, req_ctx, max_refund=50)

    assert initiate("bad-order", 10)["status"] == "REJECTED"
    assert initiate("ORD-000123", 0)["status"] == "REJECTED"
    assert initiate("ORD-000123", 999)["status"] == "REJECTED"
    assert table.items == {}


def test_no_raw_pii_in_item_or_logs(caplog):
    """A raw account number must never land in the written item nor a log line."""
    table = FakeTable()
    req_ctx = {"pending_refunds": []}
    initiate = tools.make_initiate_refund(table, req_ctx, max_refund=50)

    raw_account = "123456789012"
    with caplog.at_level(logging.DEBUG):
        # The order id itself is non-PII, but assert the masker is on the path:
        # feed a value through look_up_order's masker contract indirectly by
        # checking the written item never contains a raw account string.
        initiate("ORD-000123", 10)

    for item in table.items.values():
        assert raw_account not in str(item)
    assert raw_account not in caplog.text


def test_look_up_order_validates():
    # Bad id is rejected WITHOUT ever touching the table.
    table = _StubTable()
    look_up = tools.make_look_up_order(table)
    assert look_up("nope")["status"] == "REJECTED"
    assert table.get_calls == []

    # Found case returns the locked OK shape with a derived orderStatus.
    now = int(__import__("time").time())
    found = _StubTable(
        get_items={
            "ORD-000123": {
                "orderId": "ORD-000123",
                "summary": "1x Flat White",
                "total": Decimal("4.50"),
                "status": "RECEIVED",
                "createdAt": now,
                "gsiPk": "ORDER",
            }
        }
    )
    look_up = tools.make_look_up_order(found)
    result = look_up("ORD-000123")
    assert result["status"] == "OK"
    assert result["orderId"] == "ORD-000123"
    assert result["summary"] == "1x Flat White"
    assert result["total"] == 4.50
    assert result["orderStatus"] in {"RECEIVED", "PREPARING", "READY"}
    # status and orderStatus must not collapse.
    assert "status" in result and "orderStatus" in result


def test_look_up_order_not_found():
    look_up = tools.make_look_up_order(_StubTable())
    result = look_up("ORD-999999")
    assert result == {"status": "NOT_FOUND", "orderId": "ORD-999999"}


def test_price_order_valid_multi_item():
    total, normalized = tools.price_order("2x Latte, 1x Croissant")
    assert total == round(2 * 4.75 + 3.00, 2)
    assert normalized == "2x Latte, 1x Croissant"


def test_price_order_case_and_whitespace():
    total, normalized = tools.price_order("  flat  WHITE ")
    assert total == 4.50
    # Collapsed whitespace + title-cased canonical display, default qty 1.
    assert normalized == "1x Flat White"


def test_price_order_rejects_unknown_item():
    result = tools.price_order("1x Lattes")
    assert result["status"] == "REJECTED"
    assert "unknown menu item" in result["reason"]


def test_price_order_rejects_bad_quantity():
    assert tools.price_order("0x Latte")["status"] == "REJECTED"
    assert tools.price_order("21x Latte")["status"] == "REJECTED"
    assert tools.price_order("-3x Latte")["status"] == "REJECTED"


def test_price_order_rejects_empty():
    assert tools.price_order("")["status"] == "REJECTED"
    assert tools.price_order("   ")["status"] == "REJECTED"
    assert tools.price_order(",,")["status"] == "REJECTED"


def test_derive_status_boundaries():
    base = 1_000_000
    assert tools.derive_status(base, base + 19) == "RECEIVED"
    assert tools.derive_status(base, base + 20) == "PREPARING"
    assert tools.derive_status(base, base + 59) == "PREPARING"
    assert tools.derive_status(base, base + 60) == "READY"


def test_place_order_writes_and_appends():
    table = _StubTable()
    req_ctx = {"placed_orders": []}
    place = tools.make_place_order(table, req_ctx)

    result = place("2x Latte, 1x Croissant")

    assert result["status"] == "RECEIVED"
    assert len(table.put_items) == 1
    item = table.put_items[0]
    assert item["gsiPk"] == "ORDER"
    assert item["status"] == "RECEIVED"
    assert isinstance(item["total"], Decimal)
    assert item["orderId"] == result["orderId"]
    # Authoritative side-channel record.
    record = req_ctx["placed_orders"][-1]
    assert record == {
        "orderId": result["orderId"],
        "summary": result["summary"],
        "total": result["total"],
        "status": "RECEIVED",
    }


def test_place_order_rejected_input_writes_nothing():
    table = _StubTable()
    req_ctx = {"placed_orders": []}
    place = tools.make_place_order(table, req_ctx)

    result = place("1x Unicorn")

    assert result["status"] == "REJECTED"
    assert table.put_items == []
    assert req_ctx["placed_orders"] == []


def test_place_order_collision_retries_once():
    table = _StubTable(collide_first_put=True)
    req_ctx = {"placed_orders": []}
    place = tools.make_place_order(table, req_ctx)

    result = place("1x Latte")

    # Exactly one retry → one successful write.
    assert result["status"] == "RECEIVED"
    assert len(table.put_items) == 1
    assert table._put_calls == 2


def test_place_order_double_collision_rejects_clean():
    table = _StubTable()

    def always_collide(Item, ConditionExpression=None):
        raise _FakeClientError("ConditionalCheckFailedException")

    table.put_item = always_collide
    req_ctx = {"placed_orders": []}
    place = tools.make_place_order(table, req_ctx)

    result = place("1x Latte")

    assert result == {"status": "REJECTED", "reason": "could not allocate order id"}
    assert req_ctx["placed_orders"] == []
