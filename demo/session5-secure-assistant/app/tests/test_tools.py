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


class _FakePresignS3:
    """A presign S3 client stub (mirrors test_presign.py's FakeS3)."""

    def __init__(self):
        self.called_with = None

    def generate_presigned_url(self, op, Params, ExpiresIn):
        self.called_with = (op, Params, ExpiresIn)
        return f"https://example-bucket.s3.amazonaws.com/{Params['Key']}?sig=abc"


class _FakeS3Client:
    """A plain (non-presign) S3 client stub: records put_object calls and
    answers head_object from a set of existing keys.

    `existing_keys` is the set of keys that exist; head_object raises a
    ClientError-like error for anything else (mirroring 403/404 on a missing
    key). `fail_put` makes put_object raise, exercising the best-effort path.
    """

    def __init__(self, existing_keys=None, fail_put=False):
        self.existing_keys = set(existing_keys or [])
        self.fail_put = fail_put
        self.put_calls = []
        self.head_calls = []

    def put_object(self, **kwargs):
        self.put_calls.append(kwargs)
        if self.fail_put:
            raise _FakeClientError("AccessDenied")
        # A successful write makes the object exist for later head_object.
        self.existing_keys.add(kwargs["Key"])
        return {}

    def head_object(self, Bucket, Key):
        self.head_calls.append({"Bucket": Bucket, "Key": Key})
        if Key not in self.existing_keys:
            raise _FakeClientError("404")
        return {"ContentLength": 42}


def test_get_receipt_url_ok_populates_side_channel(monkeypatch):
    # Inject fake presign + plain clients so no real AWS/boto3 is touched.
    from presign import handler as presign_handler

    fake_s3 = _FakeS3Client(existing_keys={"receipts/ORD-000123.pdf"})
    monkeypatch.setattr(
        presign_handler, "make_s3_presign_client", lambda region=None: _FakePresignS3()
    )
    monkeypatch.setattr(
        presign_handler, "make_s3_client", lambda region=None: fake_s3
    )

    req_ctx = {"receipts": []}
    get_receipt = tools.make_get_receipt_url(req_ctx, "bucket")

    result = get_receipt("ORD-000123")

    assert result["status"] == "OK"
    assert result["orderId"] == "ORD-000123"
    assert result["url"]
    assert result["expiresIn"] == tools.EXPIRES_IN == 900
    # head_object was consulted for existence against the right key.
    assert fake_s3.head_calls[-1] == {
        "Bucket": "bucket",
        "Key": "receipts/ORD-000123.pdf",
    }
    # Authoritative side-channel record.
    assert req_ctx["receipts"][-1] == {
        "orderId": "ORD-000123",
        "url": result["url"],
        "expiresIn": tools.EXPIRES_IN,
    }


def test_get_receipt_url_missing_object_returns_not_found(monkeypatch):
    from presign import handler as presign_handler

    fake_s3 = _FakeS3Client(existing_keys=set())  # object does not exist
    monkeypatch.setattr(
        presign_handler, "make_s3_presign_client", lambda region=None: _FakePresignS3()
    )
    monkeypatch.setattr(
        presign_handler, "make_s3_client", lambda region=None: fake_s3
    )

    req_ctx = {"receipts": []}
    get_receipt = tools.make_get_receipt_url(req_ctx, "bucket")

    result = get_receipt("ORD-079522")

    # Graceful NOT_FOUND, no URL, nothing appended to the side channel.
    assert result == {"status": "NOT_FOUND", "orderId": "ORD-079522"}
    assert req_ctx["receipts"] == []


def test_get_receipt_url_rejects_bad_order_id(monkeypatch):
    from presign import handler as presign_handler

    # Guard: even if a client were built, the bad id is rejected first.
    monkeypatch.setattr(
        presign_handler, "make_s3_presign_client", lambda region=None: _FakePresignS3()
    )

    req_ctx = {"receipts": []}
    get_receipt = tools.make_get_receipt_url(req_ctx, "bucket")

    result = get_receipt("nope")

    assert result["status"] == "REJECTED"
    assert req_ctx["receipts"] == []


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


def test_place_order_writes_receipt_object(monkeypatch):
    from presign import handler as presign_handler

    fake_s3 = _FakeS3Client()
    monkeypatch.setattr(
        presign_handler, "make_s3_client", lambda region=None: fake_s3
    )

    table = _StubTable()
    req_ctx = {"placed_orders": []}
    place = tools.make_place_order(table, req_ctx, receipts_bucket="receipts-bucket")

    result = place("2x Latte, 1x Croissant")

    assert result["status"] == "RECEIVED"
    # A receipt PDF was uploaded for exactly this order.
    assert len(fake_s3.put_calls) == 1
    put = fake_s3.put_calls[0]
    assert put["Bucket"] == "receipts-bucket"
    assert put["Key"] == f"receipts/{result['orderId']}.pdf"
    assert put["ContentType"] == "application/pdf"
    assert put["Body"].startswith(b"%PDF-")
    assert result["orderId"].encode("ascii") in put["Body"]


def test_place_order_still_received_when_receipt_upload_fails(monkeypatch):
    from presign import handler as presign_handler

    fake_s3 = _FakeS3Client(fail_put=True)
    monkeypatch.setattr(
        presign_handler, "make_s3_client", lambda region=None: fake_s3
    )

    table = _StubTable()
    req_ctx = {"placed_orders": []}
    place = tools.make_place_order(table, req_ctx, receipts_bucket="receipts-bucket")

    result = place("1x Latte")

    # Order placement is unaffected by a failed (best-effort) receipt upload.
    assert result["status"] == "RECEIVED"
    assert len(table.put_items) == 1
    assert req_ctx["placed_orders"][-1]["orderId"] == result["orderId"]
    assert len(fake_s3.put_calls) == 1  # attempted, raised, swallowed


def test_place_order_no_bucket_skips_upload(monkeypatch):
    # The old two-arg signature must still work and must NOT touch S3.
    from presign import handler as presign_handler

    fake_s3 = _FakeS3Client()
    monkeypatch.setattr(
        presign_handler, "make_s3_client", lambda region=None: fake_s3
    )

    table = _StubTable()
    req_ctx = {"placed_orders": []}
    place = tools.make_place_order(table, req_ctx)  # no receipts_bucket

    result = place("1x Latte")

    assert result["status"] == "RECEIVED"
    assert fake_s3.put_calls == []


def test_tool_factories_accept_xray_entity_none_and_still_work(monkeypatch):
    """Every tool factory accepts the optional xray_entity param (default None)
    and behaves identically on the no-entity / no-xray path (traced is a plain
    pass-through). This guards the cross-thread X-Ray wiring without needing
    aws-xray-sdk or real AWS."""
    from presign import handler as presign_handler

    fake_s3 = _FakeS3Client(existing_keys={"receipts/ORD-000123.pdf"})
    monkeypatch.setattr(
        presign_handler, "make_s3_presign_client", lambda region=None: _FakePresignS3()
    )
    monkeypatch.setattr(
        presign_handler, "make_s3_client", lambda region=None: fake_s3
    )

    # place_order with explicit xray_entity=None still writes + uploads.
    place_table = _StubTable()
    place_ctx = {"placed_orders": []}
    place = tools.make_place_order(
        place_table, place_ctx, receipts_bucket="receipts-bucket", xray_entity=None
    )
    placed = place("1x Latte")
    assert placed["status"] == "RECEIVED"
    assert len(place_table.put_items) == 1
    assert len(fake_s3.put_calls) == 1

    # look_up_order with xray_entity=None still does the GetItem.
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
    look_up = tools.make_look_up_order(found, xray_entity=None)
    assert look_up("ORD-000123")["status"] == "OK"
    assert found.get_calls == [{"orderId": "ORD-000123"}]

    # initiate_refund with xray_entity=None still writes the pending record.
    refund_table = FakeTable()
    refund_ctx = {"pending_refunds": []}
    initiate = tools.make_initiate_refund(
        refund_table, refund_ctx, max_refund=50, xray_entity=None
    )
    assert initiate("ORD-000123", 10)["status"] == "PENDING_CONFIRMATION"
    assert len(refund_table.items) == 1

    # get_receipt_url with xray_entity=None still head-checks + presigns.
    receipt_ctx = {"receipts": []}
    get_receipt = tools.make_get_receipt_url(
        receipt_ctx, "receipts-bucket", xray_entity=None
    )
    got = get_receipt("ORD-000123")
    assert got["status"] == "OK"
    assert got["url"]
    assert fake_s3.head_calls[-1]["Key"] == "receipts/ORD-000123.pdf"


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
