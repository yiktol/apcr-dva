"""Unit tests for the pure ``status_for`` thresholds.

``app`` imports cleanly without boto3 (the import is guarded there), so these
tests run with no AWS. Runs under pytest (``python3 -m pytest -q test_app.py``)
and also standalone (``python3 test_app.py``), exiting nonzero on failure.
"""

import app


def test_status_for_received():
    now = 1_000_000
    # ~5s elapsed -> RECEIVED (< 10s).
    assert app.status_for(now - 5, now) == "RECEIVED"
    # Exactly 0s elapsed is still RECEIVED.
    assert app.status_for(now, now) == "RECEIVED"


def test_status_for_brewing():
    now = 1_000_000
    # ~15s elapsed -> BREWING (10s <= elapsed < 25s).
    assert app.status_for(now - 15, now) == "BREWING"
    # Boundary: exactly 10s elapsed is BREWING.
    assert app.status_for(now - 10, now) == "BREWING"


def test_status_for_ready():
    now = 1_000_000
    # ~30s elapsed -> READY (>= 25s).
    assert app.status_for(now - 30, now) == "READY"
    # Boundary: exactly 25s elapsed is READY.
    assert app.status_for(now - 25, now) == "READY"


def test_compute_points():
    # floor(total) * rate.
    assert app.compute_points(12.50, 10) == 120
    assert app.compute_points(0, 10) == 0
    assert app.compute_points(9.99, 5) == 45


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print("ok   %s" % name)
            except AssertionError as exc:
                failures += 1
                print("FAIL %s: %s" % (name, exc))
    if failures:
        raise SystemExit("%d test(s) failed" % failures)
    print("all tests passed")
