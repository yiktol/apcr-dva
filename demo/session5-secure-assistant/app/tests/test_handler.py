from assistant import handler


def test_build_response_placed_order_from_side_channel():
    req_ctx = {
        "pending_refunds": [],
        "placed_orders": [
            {
                "orderId": "ORD-000123",
                "summary": "2x Latte",
                "total": 9.50,
                "status": "RECEIVED",
            }
        ],
    }
    # reply_text names a DIFFERENT fake order id; the envelope must ignore it
    # and use ONLY the side-channel record.
    body = handler.build_response("Your order ORD-999999 is placed.", req_ctx)

    assert "placedOrder" in body
    assert body["placedOrder"] == {
        "orderId": "ORD-000123",
        "summary": "2x Latte",
        "total": 9.50,
        "status": "RECEIVED",
    }
    # Side-channel id wins over any id in the model text.
    assert body["placedOrder"]["orderId"] == "ORD-000123"


def test_build_response_both_blocks():
    req_ctx = {
        "pending_refunds": [
            {
                "token": "tok-1",
                "amountMasked": "12.50",
                "orderMasked": "ORD-000123",
            }
        ],
        "placed_orders": [
            {
                "orderId": "ORD-000456",
                "summary": "1x Flat White",
                "total": 4.50,
                "status": "RECEIVED",
            }
        ],
    }
    body = handler.build_response("done", req_ctx)
    assert "pendingRefund" in body
    assert "placedOrder" in body


def test_build_response_no_placed_order():
    body = handler.build_response("hi", {"pending_refunds": [], "placed_orders": []})
    assert "placedOrder" not in body


def test_handler_module_imports_without_strands_or_boto3():
    # The module imported above (handler) proves import-safety under the test
    # env where strands/boto3 are absent; _build_agent is NOT run at import.
    # build_response works on a plain dict with no agent constructed.
    body = handler.build_response("ok", {})
    assert body == {"reply": "ok"}
