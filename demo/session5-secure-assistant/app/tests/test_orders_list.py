"""Unit tests for the orders_list Lambda — strands-free and boto3-free.

A _StubTable records the query kwargs (tolerant of a boto3 KeyConditionExpression
object OR a raw string) and returns canned Items; a raising variant drives the
handler's 500 path. list_recent_orders must query the byCreatedAt GSI
newest-first with Limit 10, never scan, coerce total to float, derive status,
skip malformed items, and return {"orders": []} for an empty result.
"""
import orders_list.handler as handler
from assistant import tools


class _StubTable:
    """Records query kwargs and returns canned Items. Fails if scan is called."""

    def __init__(self, items):
        self._items = items
        self.query_kwargs = None

    def query(self, **kwargs):
        self.query_kwargs = kwargs
        return {"Items": list(self._items)}

    def scan(self, **kwargs):  # pragma: no cover - must never be called
        raise AssertionError("list_recent_orders must never call scan")


class _RaisingTable:
    def query(self, **kwargs):
        raise RuntimeError("boom — simulated DynamoDB failure")

    def scan(self, **kwargs):  # pragma: no cover
        raise AssertionError("must never scan")


def _gsi_pk_value(cond):
    """Extract the gsiPk equality value from either a boto3 condition object or
    the raw-string fallback, so the test needs no boto3."""
    # boto3 KeyConditionExpression object exposes its values via get_expression.
    if hasattr(cond, "get_expression"):
        expr = cond.get_expression()
        return expr["values"][1]
    # Raw-string fallback: "gsiPk = ORDER".
    return str(cond).split("=")[-1].strip()


def test_list_recent_orders_queries_gsi_newest_first():
    now = 1_000_000
    table = _StubTable(
        [
            {"orderId": "ORD-000456", "summary": "2x Latte", "total": "9.50", "createdAt": now - 30},
            {"orderId": "ORD-000123", "summary": "1x Flat White, 1x Croissant", "total": "7.50", "createdAt": now - 90},
        ]
    )
    result = handler.list_recent_orders(table, "byCreatedAt", now)

    # Query targets the GSI, single-partition "ORDER", newest-first, Limit 10.
    assert table.query_kwargs["IndexName"] == "byCreatedAt"
    assert _gsi_pk_value(table.query_kwargs["KeyConditionExpression"]) == "ORDER"
    assert table.query_kwargs["ScanIndexForward"] is False
    assert table.query_kwargs["Limit"] == 10

    orders = result["orders"]
    assert len(orders) == 2
    # Newest-first is preserved from the query (ORD-000456 is more recent).
    assert orders[0]["orderId"] == "ORD-000456"
    assert orders[1]["orderId"] == "ORD-000123"
    # total coerced to float; status derived from age.
    assert orders[0]["total"] == 9.50 and isinstance(orders[0]["total"], float)
    assert orders[0]["status"] == "PREPARING"   # 30s old -> [20,60)
    assert orders[1]["status"] == "READY"       # 90s old -> [60, inf)
    assert orders[0]["createdAt"] == now - 30 and isinstance(orders[0]["createdAt"], int)


def test_list_recent_orders_default_limit_is_ten():
    table = _StubTable([])
    handler.list_recent_orders(table, "byCreatedAt", 0)
    assert table.query_kwargs["Limit"] == 10


def test_list_recent_orders_skips_malformed_items():
    now = 1_000_000
    table = _StubTable(
        [
            {"orderId": "ORD-000456", "summary": "2x Latte", "total": "9.50", "createdAt": now - 30},
            {"summary": "no id", "total": "1.00", "createdAt": now},        # missing orderId
            {"orderId": "ORD-000789", "summary": "no createdAt", "total": "1.00"},  # missing createdAt
        ]
    )
    orders = handler.list_recent_orders(table, "byCreatedAt", now)["orders"]
    assert len(orders) == 1
    assert orders[0]["orderId"] == "ORD-000456"


def test_list_recent_orders_empty_items():
    table = _StubTable([])
    assert handler.list_recent_orders(table, "byCreatedAt", 123) == {"orders": []}


def test_list_recent_orders_total_coerced_from_number():
    now = 1_000_000
    table = _StubTable([{"orderId": "ORD-000001", "summary": "x", "total": 4.5, "createdAt": now}])
    orders = handler.list_recent_orders(table, "byCreatedAt", now)["orders"]
    assert orders[0]["total"] == 4.5 and isinstance(orders[0]["total"], float)


def test_handler_maps_query_failure_to_500(monkeypatch):
    # Drive the handler's except branch without live AWS by stubbing boto3 to a
    # fake resource whose Table() returns a raising stub.
    class _FakeDdb:
        def Table(self, _name):
            return _RaisingTable()

    class _FakeBoto3:
        def resource(self, _svc):
            return _FakeDdb()

    monkeypatch.setattr(handler, "boto3", _FakeBoto3())
    monkeypatch.setenv("ORDERS_TABLE", "orders-table")
    monkeypatch.setenv("ORDERS_GSI_NAME", "byCreatedAt")

    resp = handler.handler({}, None)
    assert resp["statusCode"] == 500
    import json

    assert json.loads(resp["body"]) == {"error": "could not list orders"}


def test_handler_success_returns_200(monkeypatch):
    class _FakeDdb:
        def Table(self, _name):
            return _StubTable([])

    class _FakeBoto3:
        def resource(self, _svc):
            return _FakeDdb()

    monkeypatch.setattr(handler, "boto3", _FakeBoto3())
    monkeypatch.setenv("ORDERS_TABLE", "orders-table")
    monkeypatch.setenv("ORDERS_GSI_NAME", "byCreatedAt")

    resp = handler.handler({}, None)
    assert resp["statusCode"] == 200
    import json

    assert json.loads(resp["body"]) == {"orders": []}


def test_derive_status_copies_agree_across_ages():
    """Cross-check: the mirrored derive_status in orders_list.handler and the
    canonical copy in assistant.tools MUST have identical constants and outputs."""
    assert handler.PREPARING_AFTER == tools.PREPARING_AFTER == 20
    assert handler.READY_AFTER == tools.READY_AFTER == 60
    created_at = 1_000_000
    for age in (0, 19, 20, 59, 60, 120):
        now = created_at + age
        assert handler.derive_status(created_at, now) == tools.derive_status(created_at, now)
