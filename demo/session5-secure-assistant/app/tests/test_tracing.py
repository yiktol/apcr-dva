"""Tests for the X-Ray cross-thread tracing helper.

These run WITHOUT aws-xray-sdk installed (the test env), so they exercise the
no-xray degrade path: `capture_entity()` returns None and `traced()` is a plain
pass-through that just calls the wrapped function. They also confirm `traced`
is a pass-through when a parent_entity is None even if the SDK were present.
"""
from assistant import tracing


def test_capture_entity_returns_none_without_xray():
    # aws-xray-sdk is not installed in the test env, so there is no entity to
    # capture and capture_entity must degrade to None (never raise).
    assert tracing.capture_entity() is None


def test_traced_calls_fn_and_returns_result_when_no_entity():
    calls = []

    def fn(a, b, c=0):
        calls.append((a, b, c))
        return a + b + c

    # parent_entity is None → traced must be a plain pass-through.
    result = tracing.traced("ddb-get_item", None, fn, 1, 2, c=3)

    assert result == 6
    assert calls == [(1, 2, 3)]


def test_traced_propagates_fn_exception_when_no_entity():
    def boom():
        raise ValueError("kaboom")

    try:
        tracing.traced("ddb-put_item", None, boom)
    except ValueError as e:
        assert str(e) == "kaboom"
    else:  # pragma: no cover - should not reach
        raise AssertionError("expected ValueError to propagate")


def test_traced_passes_through_when_xray_unavailable_even_with_entity():
    # Even if a non-None "entity" is supplied, with the SDK unavailable traced
    # must still just call fn (no attribute access on a fake entity).
    sentinel = object()
    assert tracing._XRAY_AVAILABLE is False
    out = tracing.traced("name", sentinel, lambda: "ok")
    assert out == "ok"
