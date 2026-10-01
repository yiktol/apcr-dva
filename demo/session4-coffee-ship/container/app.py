"""coffee-shop container HTTP service — the REAL boto3 backend.

The image source the ECS/Fargate service runs. A stdlib ``http.server`` app that
serves both the baked React (Vite) SPA and a real JSON API backed by AWS:

* ``GET /``                -> serves the SPA ``index.html`` (``text/html`` 200).
                              This preserves the ALB health check which targets
                              ``GET /`` expecting HTTP 200.
* ``GET /health``          -> ``{"status": "ok", "version": APP_VERSION}``. Always
                              200, even if boto3/DynamoDB are unavailable.
* ``POST /order``          -> persist an order to DynamoDB and return it.
* ``GET /order/{id}``      -> fetch one order (also ``GET /order?id=...``).
* ``GET /orders``          -> the 10 most recent orders (Scan + sort desc).
* ``GET /architecture.svg``-> the baked architecture diagram (``image/svg+xml``).
* ``GET /assets/...`` etc. -> static files from the baked SPA, Content-Type via
                              ``mimetypes``.
* unknown asset-looking path (a dot in its last segment) -> 404.
* any other unknown non-API path -> SPA fallback: serves ``index.html`` 200 so
                              client-side routing works.

Data plane:
* Orders live in DynamoDB table ``ORDERS_TABLE_NAME`` (default
  ``coffee-shop-orders``), partitioned on ``orderId``. Only ``createdAt`` drives
  status, so order rows are immutable after the initial ``put_item``.
* The loyalty rate (points per whole dollar) is read from SSM parameter
  ``LOYALTY_PARAM_NAME`` (default ``/coffee-shop/loyalty/points-per-dollar``),
  cached ~60s in-process, falling back to ``10`` on any error / missing param.
* Order ``status`` is a PURE function of time via ``status_for(created_at, now)``:
  RECEIVED (< 10s), BREWING (10–25s), READY (>= 25s).

boto3 is imported under a try/except at module load and clients are created
lazily so ``python3 -m py_compile`` and ``GET /health`` work with no boto3 and no
AWS reachability. Static files are served from ``STATIC_DIR`` (default
``/app/static``, where the Dockerfile bakes ``frontend/dist`` + ``architecture.svg``).
The service listens on ``PORT`` (default 8080), matching the ECS taskdef / ALB
container port.
"""

import json
import mimetypes
import os
import time
import uuid
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# boto3 is guarded so py_compile and /health work without it installed. Clients
# are created lazily (see _dynamodb_table / _ssm_client) so import never does I/O.
try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:  # boto3 not installed (e.g. local py_compile / unit test)
    boto3 = None

    class ClientError(Exception):
        """Fallback so except-clauses are valid when boto3 is absent."""

    class BotoCoreError(Exception):
        """Fallback so except-clauses are valid when boto3 is absent."""


# Application version, surfaced by GET /health and shown by the SPA header. Bump
# this to see a real rolling deploy change in the browser.
APP_VERSION = "v3"

# AWS region — pinned to ap-southeast-1 everywhere.
AWS_REGION = (
    os.environ.get("AWS_DEFAULT_REGION")
    or os.environ.get("AWS_REGION")
    or "ap-southeast-1"
)

# DynamoDB orders table (partition key: orderId).
ORDERS_TABLE_NAME = os.environ.get("ORDERS_TABLE_NAME", "coffee-shop-orders")

# SSM parameter holding the loyalty rate (points per whole dollar).
LOYALTY_PARAM_NAME = os.environ.get(
    "LOYALTY_PARAM_NAME", "/coffee-shop/loyalty/points-per-dollar"
)

# Fallback loyalty rate when SSM is unavailable or the param is missing. Matches
# the SSM param default and the previous stdlib-only POINTS_PER_DOLLAR.
DEFAULT_LOYALTY_RATE = 10

# How long (seconds) to cache the SSM loyalty rate in-process.
LOYALTY_CACHE_TTL = 60

# Order status thresholds (seconds since createdAt). Pure, see status_for.
BREWING_AFTER = 10
READY_AFTER = 25

# Service port, kept configurable but defaulting to the taskdef container port.
PORT = int(os.environ.get("PORT", "8080"))

# Directory holding the baked SPA (frontend/dist) + architecture.svg. The
# multi-stage Dockerfile copies both into /app/static; overridable for local runs.
STATIC_DIR = os.environ.get("STATIC_DIR", "/app/static")

# Module-level lazy singletons / caches.
_dynamodb_table_cache = None
_ssm_client_cache = None
# (rate, fetched_at) tuple for the loyalty-rate TTL cache.
_loyalty_cache = (None, 0.0)


# --------------------------------------------------------------------------- #
# Pure helpers (no AWS / IO — unit-testable).
# --------------------------------------------------------------------------- #
def status_for(created_at, now):
    """Return the order status given its creation time and the current time.

    Pure function of elapsed seconds (``now - created_at``):

    * ``RECEIVED`` while elapsed < 10s,
    * ``BREWING``  while 10s <= elapsed < 25s,
    * ``READY``    once elapsed >= 25s.

    ``created_at`` and ``now`` are epoch seconds (int or float).
    """
    elapsed = float(now) - float(created_at)
    if elapsed < BREWING_AFTER:
        return "RECEIVED"
    if elapsed < READY_AFTER:
        return "BREWING"
    return "READY"


def compute_points(total, rate):
    """Loyalty points for an order: floor(total) * rate."""
    return int(float(total)) * int(rate)


# --------------------------------------------------------------------------- #
# Lazy AWS clients + loyalty rate.
# --------------------------------------------------------------------------- #
def _dynamodb_table():
    """Return the cached DynamoDB Table resource, creating it lazily.

    Raises RuntimeError if boto3 is not installed so callers map it to a 500.
    """
    global _dynamodb_table_cache
    if _dynamodb_table_cache is None:
        if boto3 is None:
            raise RuntimeError("boto3 is not installed")
        resource = boto3.resource("dynamodb", region_name=AWS_REGION)
        _dynamodb_table_cache = resource.Table(ORDERS_TABLE_NAME)
    return _dynamodb_table_cache


def _ssm_client():
    """Return the cached SSM client, creating it lazily."""
    global _ssm_client_cache
    if _ssm_client_cache is None:
        if boto3 is None:
            raise RuntimeError("boto3 is not installed")
        _ssm_client_cache = boto3.client("ssm", region_name=AWS_REGION)
    return _ssm_client_cache


def get_loyalty_rate():
    """Return the loyalty rate from SSM, cached ~60s, fallback 10.

    Any error (boto3 missing, ClientError, missing param, bad value) falls back
    to DEFAULT_LOYALTY_RATE and is logged — this never raises.
    """
    global _loyalty_cache
    cached_rate, fetched_at = _loyalty_cache
    now = time.time()
    if cached_rate is not None and (now - fetched_at) < LOYALTY_CACHE_TTL:
        return cached_rate
    try:
        resp = _ssm_client().get_parameter(Name=LOYALTY_PARAM_NAME)
        rate = int(float(resp["Parameter"]["Value"]))
    except (ClientError, BotoCoreError, RuntimeError, KeyError, ValueError) as exc:
        print("loyalty rate lookup failed, falling back to %d: %s"
              % (DEFAULT_LOYALTY_RATE, exc))
        rate = DEFAULT_LOYALTY_RATE
    _loyalty_cache = (rate, now)
    return rate


# --------------------------------------------------------------------------- #
# Order persistence.
# --------------------------------------------------------------------------- #
def _normalize_items(items):
    """Validate/normalize an optional items list into plain dicts.

    Returns a list of {id,name,qty,price} dicts, or raises ValueError.
    """
    if items is None:
        return None
    if not isinstance(items, list):
        raise ValueError("'items' must be a list")
    normalized = []
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("each item must be an object")
        normalized.append(
            {
                "id": str(item.get("id", "")),
                "name": str(item.get("name", "")),
                "qty": int(item.get("qty", 1)),
                "price": str(item.get("price", "0")),
            }
        )
    return normalized


def create_order(payload):
    """Persist a new order and return its public representation.

    Accepts ``{items:[{id,name,qty,price}], total}`` OR ``{orderId, total}``.
    Generates an orderId when absent. Raises ValueError on bad input.
    """
    if not isinstance(payload, dict):
        raise ValueError("order payload must be a JSON object")
    if "total" not in payload:
        raise ValueError("order is missing 'total'")
    try:
        total = float(payload["total"])
    except (TypeError, ValueError) as exc:
        raise ValueError("order 'total' must be numeric") from exc
    if total < 0:
        raise ValueError("order 'total' must not be negative")

    items = _normalize_items(payload.get("items"))
    rate = get_loyalty_rate()
    points = compute_points(total, rate)
    order_id = str(payload.get("orderId") or uuid.uuid4())
    created_at = int(time.time())

    # DynamoDB does not accept float; store total as a string for exactness.
    record = {
        "orderId": order_id,
        "createdAt": created_at,
        "total": str(total),
        "points": points,
        "status": "RECEIVED",
    }
    if items is not None:
        record["items"] = items

    _dynamodb_table().put_item(Item=record)

    return {
        "orderId": order_id,
        "status": status_for(created_at, time.time()),
        "points": points,
        "total": total,
        "createdAt": created_at,
    }


def _jsonable(value):
    """Recursively convert DynamoDB resource-API types to JSON-safe types.

    The DynamoDB resource API returns numbers as decimal.Decimal, which
    json.dumps cannot serialize. Convert Decimals to int when integral else
    float, and recurse into dicts/lists (e.g. the nested ``items`` list).
    """
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    return value


def _to_public_order(record):
    """Convert a stored DynamoDB record into the public order shape."""
    created_at = int(record.get("createdAt", 0))
    public = {
        "orderId": record.get("orderId"),
        "status": status_for(created_at, time.time()),
        "points": int(record.get("points", 0)),
        "total": float(record.get("total", 0)),
        "createdAt": created_at,
    }
    if "items" in record:
        # Convert any Decimal (e.g. item qty stored as a Number) to a JSON-safe
        # type so json.dumps does not raise and crash the request thread.
        public["items"] = _jsonable(record["items"])
    return public


def get_order(order_id):
    """Fetch one order by id. Returns the public order dict or None if missing."""
    resp = _dynamodb_table().get_item(Key={"orderId": order_id})
    item = resp.get("Item")
    if not item:
        return None
    return _to_public_order(item)


def list_recent_orders(limit=10):
    """Return the ``limit`` most recent orders, newest first.

    A Scan + in-memory sort is acceptable at this scale (tiny table, no
    GSI). The partition key is orderId, so there is no range key to query on.
    """
    resp = _dynamodb_table().scan()
    items = resp.get("Items", [])
    items.sort(key=lambda r: int(r.get("createdAt", 0)), reverse=True)
    return [_to_public_order(r) for r in items[:limit]]


class OrderHandler(BaseHTTPRequestHandler):
    """Serves the JSON API plus the baked SPA static files."""

    def _send_json(self, status_code, body):
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _resolve_static(self, rel_path):
        """Resolve ``rel_path`` under STATIC_DIR, guarding against traversal.

        Returns an absolute path inside STATIC_DIR, or None if the request
        escapes the static root (e.g. ``../etc/passwd``).
        """
        static_root = os.path.realpath(STATIC_DIR)
        candidate = os.path.realpath(os.path.join(static_root, rel_path.lstrip("/")))
        if candidate != static_root and not candidate.startswith(
            static_root + os.sep
        ):
            return None
        return candidate

    def _send_file(self, abs_path, content_type):
        """Send a file with the given Content-Type. Returns True if sent."""
        try:
            with open(abs_path, "rb") as fh:
                payload = fh.read()
        except (FileNotFoundError, IsADirectoryError, OSError):
            return False
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
        return True

    def _serve_index(self):
        """Serve the SPA index.html as text/html 200. Falls back to a tiny
        placeholder page if the SPA has not been baked (keeps '/' a 200 for the
        ALB health check even without a built dist)."""
        index_path = self._resolve_static("index.html")
        if index_path and self._send_file(index_path, "text/html; charset=utf-8"):
            return
        body = b"<!doctype html><title>coffee-shop</title><h1>coffee-shop</h1>"
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        raw_path = self.path
        path = raw_path.split("?", 1)[0].split("#", 1)[0]

        # --- JSON API ---
        if path == "/health":
            # Always 200, even if boto3/DynamoDB are unavailable.
            self._send_json(200, {"status": "ok", "version": APP_VERSION})
            return

        if path == "/orders":
            try:
                orders = list_recent_orders(10)
            except (ClientError, BotoCoreError, RuntimeError, TypeError, ValueError) as exc:
                print("GET /orders failed: %s" % exc)
                self._send_json(500, {"error": "could not list orders"})
                return
            self._send_json(200, {"orders": orders, "count": len(orders)})
            return

        if path == "/order" or path.startswith("/order/"):
            # Order id from path segment /order/{id} or query ?id=.
            order_id = None
            if path.startswith("/order/"):
                order_id = path[len("/order/"):].strip("/") or None
            if order_id is None:
                query = raw_path.split("?", 1)[1] if "?" in raw_path else ""
                for pair in query.split("&"):
                    if pair.startswith("id="):
                        order_id = pair[len("id="):] or None
                        break
            if order_id is None:
                # Browsable sample so GET /order (no id) is not an error.
                self._send_json(
                    200,
                    {
                        "orderId": "sample-order",
                        "status": "READY",
                        "points": compute_points(12.50, get_loyalty_rate()),
                        "total": 12.50,
                        "createdAt": 0,
                    },
                )
                return
            try:
                order = get_order(order_id)
            except (ClientError, BotoCoreError, RuntimeError, TypeError, ValueError) as exc:
                print("GET /order/%s failed: %s" % (order_id, exc))
                self._send_json(500, {"error": "could not fetch order"})
                return
            if order is None:
                self._send_json(404, {"error": "order not found"})
                return
            self._send_json(200, order)
            return

        # --- SPA + static assets ---
        if path == "/":
            self._serve_index()
            return

        if path == "/architecture.svg":
            svg_path = self._resolve_static("architecture.svg")
            if svg_path and self._send_file(svg_path, "image/svg+xml"):
                return
            self._send_json(404, {"error": "not found"})
            return

        resolved = self._resolve_static(path)
        if resolved and os.path.isfile(resolved):
            content_type = (
                mimetypes.guess_type(resolved)[0] or "application/octet-stream"
            )
            if self._send_file(resolved, content_type):
                return

        # Asset-looking path (a dot in the last segment) that was not found -> 404.
        last_segment = path.rsplit("/", 1)[-1]
        if "." in last_segment:
            self._send_json(404, {"error": "not found"})
            return

        # Any other unknown non-API path -> SPA client-side route fallback.
        self._serve_index()

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/order":
            self._send_json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length) if length else b""
        try:
            payload = json.loads(raw_body or b"{}")
        except json.JSONDecodeError as exc:
            self._send_json(400, {"error": "invalid JSON: %s" % exc})
            return
        try:
            order = create_order(payload)
        except ValueError as exc:
            self._send_json(400, {"error": str(exc)})
            return
        except (ClientError, BotoCoreError, RuntimeError) as exc:
            print("POST /order failed: %s" % exc)
            self._send_json(500, {"error": "could not create order"})
            return
        self._send_json(200, order)

    def log_message(self, fmt, *args):
        # Log to stdout so ECS/awslogs captures request lines.
        print("%s - %s" % (self.address_string(), fmt % args))


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), OrderHandler)
    print("coffee-shop container listening on port %d" % PORT)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
