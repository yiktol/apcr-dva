"""Unit tests for the coffee-ship loyalty Lambda handler."""

import json
import os

import app


def _load_event(name):
    events_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "events"
    )
    with open(os.path.join(events_dir, name), encoding="utf-8") as fh:
        return json.load(fh)


def test_happy_path_returns_200_with_points():
    event = _load_event("apigw-happy.json")
    # The API Gateway proxy body must be a JSON string.
    assert isinstance(event["body"], str)

    result = app.handler(event, None)

    assert result["statusCode"] == 200
    body = json.loads(result["body"])
    assert body["orderId"] == "order-1001"
    # total 42.50 -> floor(42) * 10 points-per-dollar = 420
    assert body["points"] == 420


def test_malformed_body_returns_400():
    event = _load_event("apigw-malformed.json")
    assert isinstance(event["body"], str)

    result = app.handler(event, None)

    assert result["statusCode"] == 400
    assert "error" in json.loads(result["body"])


def test_compute_points_floors_total():
    assert app.compute_points({"total": 9.99}) == 90


def test_compute_points_rejects_missing_total():
    import pytest

    with pytest.raises(ValueError):
        app.compute_points({"orderId": "x"})


def test_sqs_event_processes_records():
    event = {
        "Records": [
            {"body": json.dumps({"orderId": "order-1", "total": 10})},
            {"body": json.dumps({"orderId": "order-2", "total": 25})},
        ]
    }

    result = app.handler(event, None)

    assert result["processed"] == 2
    assert result["results"][0]["points"] == 100
    assert result["results"][1]["points"] == 250
