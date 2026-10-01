"""coffee-ship container HTTP service.

The image source the ECS/Fargate service runs. A tiny stdlib-only HTTP server
(no external dependencies) exposing:

* ``GET /``       -> health check, returns ``{"status": "ok"}``.
* ``GET /order``  -> echoes a sample order with computed loyalty points.
* ``POST /order`` -> echoes the posted order with computed loyalty points.

Loyalty points mirror the Lambda path: points = floor(total) * POINTS_PER_DOLLAR
(default 10, overridable via env). The service listens on ``PORT`` (default 8080),
matching the ECS taskdef / ALB container port.
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Points awarded per whole dollar of order total. Overridable via env; the
# default matches the Lambda handler and the SSM loyalty config.
POINTS_PER_DOLLAR = int(os.environ.get("POINTS_PER_DOLLAR", "10"))

# Service port, kept configurable but defaulting to the taskdef container port.
PORT = int(os.environ.get("PORT", "8080"))


def compute_points(order):
    """Return loyalty points for an order dict.

    Points = floor(total) * POINTS_PER_DOLLAR. A missing or non-numeric total
    raises ValueError so callers can map it to a 400.
    """
    try:
        total = float(order["total"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("order is missing a numeric 'total'") from exc
    if total < 0:
        raise ValueError("order 'total' must not be negative")
    return int(total) * POINTS_PER_DOLLAR


class OrderHandler(BaseHTTPRequestHandler):
    """Routes GET / (health) and GET|POST /order (loyalty echo)."""

    def _send_json(self, status_code, body):
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/" or self.path == "/health":
            self._send_json(200, {"status": "ok"})
            return
        if self.path.startswith("/order"):
            # Sample order so the demo endpoint is browsable without a body.
            order = {"orderId": "sample-order", "total": 12.50}
            self._send_json(
                200, {"orderId": order["orderId"], "points": compute_points(order)}
            )
            return
        self._send_json(404, {"error": "not found"})

    def do_POST(self):
        if not self.path.startswith("/order"):
            self._send_json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length) if length else b""
        try:
            order = json.loads(raw_body or b"{}")
            if not isinstance(order, dict):
                raise ValueError("order payload must be a JSON object")
            points = compute_points(order)
        except (ValueError, json.JSONDecodeError) as exc:
            self._send_json(400, {"error": str(exc)})
            return
        self._send_json(200, {"orderId": order.get("orderId"), "points": points})

    def log_message(self, fmt, *args):
        # Log to stdout so ECS/awslogs captures request lines.
        print("%s - %s" % (self.address_string(), fmt % args))


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), OrderHandler)
    print("coffee-ship container listening on port %d" % PORT)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
