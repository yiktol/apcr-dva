#!/usr/bin/env python3
"""Generate a self-contained architecture SVG for the session5 secure assistant.

Each official AWS ``*_64.svg`` icon is inlined as ``data:image/svg+xml;base64``
so the SVG needs no external files.

LAYOUT MODEL (readability-first, rewritten to remove arrow overlap):
  Nodes live on a strict LEFT-TO-RIGHT COLUMN grid. Connectors are ORTHOGONAL
  elbows that leave a node from a named side (right/left/top/bottom) and enter
  the next from a named side, so lines run along column gutters and row bands
  instead of cutting diagonally across icons. Each edge carries a numbered,
  white-backed label placed on its longest straight segment. Flows are grouped
  into three horizontal bands:
    * TOP band    — the synchronous request path (Viewer -> edge -> API ->
                    compute -> Bedrock).
    * MIDDLE band — the shared data plane (DynamoDB / Secrets / SSM / receipts /
                    KMS), reached by downward connectors.
    * Observability (X-Ray / CloudWatch) sits on the right, kept on its own
      lane so it never crosses the request path.

Flows encoded (unchanged from the architecture):
  Viewer -> CloudFront; CloudFront -> S3 SPA (OAC); CloudFront -> WAF -> API GW
  API GW -> assistant Lambda (VPC); API GW -> orders-list Lambda (read-only)
  assistant -> PrivateLink -> Bedrock (Nova Micro + Guardrail)
  assistant -> DynamoDB (place/look-up) + Secrets + SSM
  orders-list -> DynamoDB byCreatedAt GSI (GET /api/orders)
  refund-confirm -> DynamoDB (human confirmation); presign -> receipts S3
  receipts -> KMS (SSE-KMS); Bedrock -> CloudWatch (invocation logs); X-Ray

Output: diagram/architecture.svg (next to this script).
"""
import base64
import os

ICON_BASE = "/Users/erictole/demo/apcr-dva/aws-icons/Architecture-Service-Icons_04302026"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "architecture.svg")

ICONS = {
    "cloudfront":  "Arch_Networking-Content-Delivery/64/Arch_Amazon-CloudFront_64.svg",
    "waf":         "Arch_Security-Identity/64/Arch_AWS-WAF_64.svg",
    "apigw":       "Arch_Networking-Content-Delivery/64/Arch_Amazon-API-Gateway_64.svg",
    "lambda":      "Arch_Compute/64/Arch_AWS-Lambda_64.svg",
    "bedrock":     "Arch_Artificial-Intelligence/64/Arch_Amazon-Bedrock_64.svg",
    "privatelink": "Arch_Networking-Content-Delivery/64/Arch_AWS-PrivateLink_64.svg",
    "vpc":         "Arch_Networking-Content-Delivery/64/Arch_Amazon-Virtual-Private-Cloud_64.svg",
    "dynamodb":    "Arch_Databases/64/Arch_Amazon-DynamoDB_64.svg",
    "s3":          "Arch_Storage/64/Arch_Amazon-Simple-Storage-Service_64.svg",
    "kms":         "Arch_Security-Identity/64/Arch_AWS-Key-Management-Service_64.svg",
    "secrets":     "Arch_Security-Identity/64/Arch_AWS-Secrets-Manager_64.svg",
    "iam":         "Arch_Security-Identity/64/Arch_AWS-Identity-and-Access-Management_64.svg",
    "ssm":         "Arch_Management-Tools/64/Arch_AWS-Systems-Manager_64.svg",
    "xray":        "Arch_Developer-Tools/64/Arch_AWS-X-Ray_64.svg",
    "cloudwatch":  "Arch_Management-Tools/64/Arch_Amazon-CloudWatch_64.svg",
}


def data_uri(rel):
    with open(os.path.join(ICON_BASE, rel), "rb") as f:
        return "data:image/svg+xml;base64," + base64.b64encode(f.read()).decode()


U = {k: data_uri(v) for k, v in ICONS.items()}

W, H = 1600, 1120
ICON = 56

# Act-color-coded zones (fill, stroke, title color).
ZONES = {
    "act1": ("#eaf0fb", "#4d72d6", "#2f52b0"),  # network/data security (blue)
    "act2": ("#fff2e6", "#ed7100", "#c25e00"),  # identity/access (orange)
    "act3": ("#f3eefc", "#8c4fff", "#6b2fd6"),  # Strands assistant (purple)
    "act4": ("#eafaf1", "#1f9d55", "#157a40"),  # observability (green)
}

BLUE, ORANGE, PURPLE, GREEN, GREY = (
    "#4d72d6", "#ed7100", "#8c4fff", "#1f9d55", "#5b7089",
)

# ---------------------------------------------------------------------------
# COLUMN / ROW GRID.  Columns are the x-centres of each layer; rows are the
# y-centres of each band. Every node is pinned to one (col, row) centre, so
# lines run in the clear gutters between columns and bands.
# ---------------------------------------------------------------------------
COL = {
    "viewer": 110,
    "edge":   330,   # CloudFront / WAF
    "api":    560,   # API Gateway
    "compute": 820,  # Lambdas (assistant / orders-list / refund / presign)
    "ai":     1090,  # PrivateLink -> Bedrock
    "sink":   1360,  # KMS / CloudWatch / receipts / data stores (right sinks)
}

ROW = {
    "sat":    230,   # satellite row above the spine (S3 SPA, WAF, orders, X-Ray)
    "top":    400,   # synchronous request path (the main spine)
    "mid":    610,   # Bedrock / PrivateLink lane
    "data":   820,   # shared data plane (DynamoDB / secrets / ssm / refund)
    "store":  1000,  # storage / crypto sinks (receipts / kms / presign)
}

# Node centre (cx, cy). Top of the icon is cy - ICON/2.
NODE = {
    "viewer":     (COL["viewer"],  ROW["top"]),
    "cloudfront": (COL["edge"],    ROW["top"]),
    "spa":        (COL["edge"],    ROW["sat"]),
    "waf":        (COL["api"],     ROW["sat"]),
    "apigw":      (COL["api"],     ROW["top"]),
    "assistant":  (COL["compute"], ROW["top"]),
    "orderslist": (COL["compute"], ROW["sat"]),
    "privatelink": (COL["ai"],     ROW["mid"]),
    "bedrock":    (COL["sink"],    ROW["mid"]),
    "dynamodb":   (COL["compute"], ROW["data"]),
    "secrets":    (COL["api"],     ROW["data"]),
    "ssm":        (COL["edge"],    ROW["data"]),
    "refund":     (COL["ai"],      ROW["data"]),
    "presign":    (COL["api"],     ROW["store"]),
    "receipts":   (COL["edge"],    ROW["store"]),
    "kms":        (COL["viewer"],  ROW["store"]),
    "cloudwatch": (COL["sink"],    ROW["data"]),
    "xray":       (COL["ai"],      ROW["sat"]),
}


def _top_left(cx, cy):
    return cx - ICON // 2, cy - ICON // 2


def icon(key_pos, icon_key, label, sub=""):
    cx, cy = NODE[key_pos]
    x, y = _top_left(cx, cy)
    s = f'<g filter="url(#soft)"><rect x="{x-4}" y="{y-4}" width="{ICON+8}" height="{ICON+8}" rx="12" fill="#ffffff"/></g>'
    s += f'<image x="{x}" y="{y}" width="{ICON}" height="{ICON}" href="{U[icon_key]}"/>'
    s += f'<text x="{cx}" y="{y + ICON + 15}" class="lbl">{label}</text>'
    if sub:
        s += f'<text x="{cx}" y="{y + ICON + 29}" class="sub">{sub}</text>'
    return s


def user_node(key_pos, label="Viewer", sub="browser"):
    cx, cy = NODE[key_pos]
    x, y = _top_left(cx, cy)
    s = f'<g filter="url(#soft)"><rect x="{x-4}" y="{y-4}" width="{ICON+8}" height="{ICON+8}" rx="12" fill="#ffffff"/></g>'
    s += f'<circle cx="{cx}" cy="{y+18}" r="10" fill="#48607c"/>'
    s += f'<path d="M {cx-16} {y+ICON-6} q 16 -22 32 0 z" fill="#48607c"/>'
    s += f'<text x="{cx}" y="{y + ICON + 15}" class="lbl">{label}</text>'
    s += f'<text x="{cx}" y="{y + ICON + 29}" class="sub">{sub}</text>'
    return s


def zone(x, y, w, h, title, kind):
    fill, stroke, tcol = ZONES[kind]
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill}" stroke="{stroke}" stroke-width="1.6" opacity="0.72"/>'
    s += f'<text x="{x+16}" y="{y+26}" class="ztitle" fill="{tcol}">{title}</text>'
    return s


# Half-extent of a node's clickable/padded box, plus clearance kept around it
# so connectors never graze an icon or its label.
BOX_HALF = ICON // 2 + 4          # white padding rect half-size
CLEAR = 20                        # keep lines this far from any icon box


def node_box(key):
    """Padded (x0, y0, x1, y1) obstacle box for a node. We guard the ICON box
    (plus a small clearance) only — the two-line label strip below the icon is
    intentionally NOT reserved, so horizontal lanes can still pass through the
    label gutter between rows without being pushed into other icons."""
    cx, cy = NODE[key]
    return (
        cx - BOX_HALF - CLEAR,
        cy - BOX_HALF - CLEAR,
        cx + BOX_HALF + CLEAR,
        cy + BOX_HALF + CLEAR,
    )


ALL_BOXES = None  # filled once all NODE entries are known (see build section)


# Anchor points on a node's bounding box by side.
def anchor(key, side):
    cx, cy = NODE[key]
    h = BOX_HALF
    if side == "r":
        return cx + h, cy
    if side == "l":
        return cx - h, cy
    if side == "t":
        return cx, cy - h
    if side == "b":
        return cx, cy + h
    return cx, cy


def _seg_hits_box(x1, y1, x2, y2, box, endpoints):
    """True if the axis-aligned segment crosses `box` (expanded) — ignoring the
    two endpoint nodes the edge legitimately touches."""
    bx0, by0, bx1, by1 = box
    if x1 == x2:  # vertical segment
        lo, hi = sorted((y1, y2))
        return bx0 < x1 < bx1 and not (hi < by0 or lo > by1)
    else:         # horizontal segment
        lo, hi = sorted((x1, x2))
        return by0 < y1 < by1 and not (hi < bx0 or lo > bx1)


LANE_STEP = 6  # lane search granularity (px)
ROUTED = []    # (exclude_set, [points]) per edge, for the no-crossing check


def _lane_is_clear(fixed_is_x, cand, lo, hi, exclude):
    for key, box in ALL_BOXES.items():
        if key in exclude:
            continue
        if fixed_is_x:
            if _seg_hits_box(cand, lo, cand, hi, box, exclude):
                return False
        else:
            if _seg_hits_box(lo, cand, hi, cand, box, exclude):
                return False
    return True


def _clear_lane(fixed_is_x, lane, lo, hi, exclude):
    """Nudge a candidate lane (x if fixed_is_x else y) outward from `lane` until
    the swept segment from lo..hi clears every node box except `exclude`."""
    shifts = [0]
    for k in range(1, 80):
        shifts.append(k * LANE_STEP)
        shifts.append(-k * LANE_STEP)
    for shift in shifts:
        cand = lane + shift
        if _lane_is_clear(fixed_is_x, cand, lo, hi, exclude):
            return cand
    return lane


def _label(x, y, text, color, num):
    w = len(text) * 6.6 + 14
    s = f'<rect x="{x - w/2}" y="{y - 11}" width="{w}" height="18" rx="9" fill="#ffffff" stroke="{color}" stroke-width="0.8" opacity="0.98"/>'
    s += f'<text x="{x}" y="{y + 2.5}" class="edge">{text}</text>'
    if num is not None:
        s += f'<circle cx="{x - w/2 + 2}" cy="{y - 2}" r="8" fill="{color}"/>'
        s += f'<text x="{x - w/2 + 2}" y="{y + 1.4}" class="enum">{num}</text>'
    return s


def orth(a, sa, b, sb, label="", color=GREY, dash=False, num=None,
         lx=None, ly=None, mid=None):
    """Orthogonal (elbow) connector from node `a` side `sa` to node `b` side `sb`.

    The shared middle leg is auto-routed into the nearest gutter that clears
    every OTHER node box (the two endpoints are excluded), so a connector never
    crosses an icon. `mid` seeds the preferred lane; the router nudges it clear.
    The label is centred at (lx, ly) if given, else on the longest leg.
    """
    ax, ay = anchor(a, sa)
    bx, by = anchor(b, sb)
    d = ' stroke-dasharray="6 5"' if dash else ""
    exclude = {a, b}

    # Decide routing: if exit side is horizontal (l/r) go horizontal-first (the
    # shared leg is a VERTICAL at x=midx); if vertical (t/b) go vertical-first
    # (the shared leg is a HORIZONTAL at y=midy).
    if sa in ("l", "r"):
        seed = mid if mid is not None else (ax + bx) / 2
        midx = _clear_lane(True, seed, ay, by, exclude)
        pts = [(ax, ay), (midx, ay), (midx, by), (bx, by)]
    else:
        seed = mid if mid is not None else (ay + by) / 2
        midy = _clear_lane(False, seed, ax, bx, exclude)
        pts = [(ax, ay), (ax, midy), (bx, midy), (bx, by)]
    # Drop zero-length duplicate points.
    clean = [pts[0]]
    for pt in pts[1:]:
        if pt != clean[-1]:
            clean.append(pt)
    # Record routed segments (for the no-crossing self-check at the end).
    ROUTED.append((exclude, clean))
    dpath = "M " + " L ".join(f"{x} {y}" for x, y in clean)
    s = f'<path d="{dpath}" fill="none" stroke="{color}" stroke-width="2.4" marker-end="url(#arw)"{d} opacity="0.92"/>'

    if label:
        if lx is None or ly is None:
            # Pick the longest segment midpoint for the label.
            best = None
            blen = -1
            for (x1, y1), (x2, y2) in zip(clean, clean[1:]):
                seglen = abs(x2 - x1) + abs(y2 - y1)
                if seglen > blen:
                    blen = seglen
                    best = ((x1 + x2) / 2, (y1 + y2) / 2)
            lx, ly = best
        s += _label(lx, ly, label, color, num)
    return s


p = []
p.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Segoe UI, Helvetica, Arial, sans-serif">
<defs>
  <marker id="arw" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0 0 L10 5 L0 10 z" fill="#5b7089"/>
  </marker>
  <filter id="soft" x="-30%" y="-30%" width="160%" height="160%">
    <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#16273f" flood-opacity="0.16"/>
  </filter>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#f5f8fc"/>
  </linearGradient>
</defs>
<style>
  .lbl {{ fill:#16273f; font-size:12.5px; font-weight:700; text-anchor:middle; }}
  .sub {{ fill:#7a8aa0; font-size:10px; text-anchor:middle; }}
  .ztitle {{ font-size:12.5px; font-weight:800; letter-spacing:.02em; }}
  .edge {{ fill:#3d5168; font-size:10.5px; font-weight:600; text-anchor:middle; }}
  .enum {{ fill:#fff; font-size:9px; font-weight:800; text-anchor:middle; }}
  .title {{ fill:#16273f; font-size:24px; font-weight:800; }}
  .cap {{ fill:#7a8aa0; font-size:13px; }}
  .lgd {{ fill:#48607c; font-size:11.5px; font-weight:600; }}
  .note {{ fill:#7a8aa0; font-size:10.5px; }}
</style>
<rect x="0" y="0" width="{W}" height="{H}" fill="url(#bg)"/>
<text x="34" y="44" class="title">Secure Coffee-Shop AI Assistant &#8212; Strands + Nova Micro</text>
<text x="34" y="66" class="cap">Left&#8594;right request path: Viewer &#8594; CloudFront+WAF+OAC &#8594; API &#8594; private-subnet Strands assistant &#8594; Bedrock (Nova Micro + Guardrail) via PrivateLink. Shared data plane below; observability on the right. Region ap-southeast-1.</text>
''')

# ---- Act zones (behind nodes), sized to the new grid ----------------------
# Act 1 wraps the edge column across the satellite (S3 SPA) + spine (CloudFront)
# rows. Each zone is sized from its members' centres +/- a padded icon box.
HALF = ICON // 2 + 18  # padded half-box used to frame members


def _zone_for(members, title, kind, pad_top=30, pad=14):
    xs = [NODE[m][0] for m in members]
    ys = [NODE[m][1] for m in members]
    x0 = min(xs) - HALF - pad
    y0 = min(ys) - HALF - pad_top
    x1 = max(xs) + HALF + pad
    y1 = max(ys) + HALF + pad + 18  # room for the 2-line labels under icons
    return zone(x0, y0, x1 - x0, y1 - y0, title, kind)


p.append(_zone_for(["spa", "cloudfront"], "Act 1 &#8212; edge: CloudFront + OAC", "act1"))
p.append(_zone_for(["waf"], "Act 2 &#8212; WAF", "act2"))
p.append(_zone_for(["orderslist", "assistant"], "Act 3 &#8212; Strands assistant (secured)", "act3"))
p.append(_zone_for(["xray"], "Act 4 &#8212; observability", "act4"))
p.append(_zone_for(
    ["ssm", "secrets", "dynamodb", "refund", "kms", "receipts", "presign"],
    "Shared data plane &#8212; CMK-encrypted (DynamoDB / receipts / secrets / config)",
    "act1",
))

# ---- Nodes ----------------------------------------------------------------
p.append(user_node("viewer"))
p.append(icon("cloudfront", "cloudfront", "CloudFront", "default domain + OAC"))
p.append(icon("spa", "s3", "S3 SPA", "private via OAC"))
p.append(icon("waf", "waf", "WAF", "REGIONAL, count mode"))
p.append(icon("apigw", "apigw", "API Gateway", "/api/* (X-Ray on)"))
p.append(icon("orderslist", "lambda", "Orders list", "read-only"))
p.append(icon("assistant", "lambda", "Assistant", "VPC private subnets"))
p.append(icon("privatelink", "privatelink", "PrivateLink", "bedrock-runtime EP"))
p.append(icon("bedrock", "bedrock", "Bedrock", "Nova Micro + Guardrail"))
p.append(icon("dynamodb", "dynamodb", "DynamoDB", "orders / pending-refunds"))
p.append(icon("secrets", "secrets", "Secrets Mgr", "payment key"))
p.append(icon("ssm", "ssm", "SSM Param", "assistant config"))
p.append(icon("refund", "lambda", "Refund confirm", "human-in-the-loop"))
p.append(icon("presign", "lambda", "Presign", "15-min GET URL"))
p.append(icon("receipts", "s3", "Receipts S3", "CMK, TLS-only DENY"))
p.append(icon("kms", "kms", "KMS CMK", "one key"))
p.append(icon("cloudwatch", "cloudwatch", "CloudWatch", "invocation logs (CMK)"))
p.append(icon("xray", "xray", "X-Ray", "traces"))

# ---- Edges (orthogonal, routed in gutters/bands) --------------------------
# All node boxes are now known: build the obstacle map the router avoids.
ALL_BOXES = {k: node_box(k) for k in NODE}

# TOP request path (the horizontal spine). Each hop is node-to-adjacent-node so
# no leg skips over a node that sits between the endpoints.
p.append(orth("viewer", "r", "cloudfront", "l", "https", BLUE, num=1))
p.append(orth("cloudfront", "t", "spa", "b", "SPA (OAC)", BLUE, num=2))
p.append(orth("cloudfront", "r", "waf", "b", "/api/*", ORANGE, num=3))
p.append(orth("waf", "b", "apigw", "t", "allow / count", ORANGE, num=4))
p.append(orth("apigw", "r", "assistant", "l", "invoke", ORANGE, num=5))
p.append(orth("apigw", "t", "orderslist", "b", "GET /api/orders", ORANGE, num=11))

# Assistant -> PrivateLink -> Bedrock.
p.append(orth("assistant", "r", "privatelink", "t", "InvokeModel", PURPLE, num=6))
p.append(orth("privatelink", "r", "bedrock", "l", "Nova + Guardrail", PURPLE, num=7))

# Compute -> data plane (downward connectors into the data band). The router
# auto-selects a clear vertical gutter for each.
p.append(orth("assistant", "b", "dynamodb", "t", "place / look-up", BLUE, num=8))
p.append(orth("assistant", "b", "secrets", "t", "payment key", BLUE, dash=True, num=9))
p.append(orth("assistant", "b", "ssm", "t", "config", BLUE, dash=True, num=10))
# Orders list and DynamoDB share the compute column with the Assistant sitting
# between them, so exit LEFT and let the router find a clear gutter down to
# DynamoDB's left side (avoids crossing the Assistant icon).
p.append(orth("orderslist", "l", "dynamodb", "l", "query GSI", BLUE, num=12))
p.append(orth("refund", "l", "dynamodb", "r", "confirm (human)", ORANGE, num=13))

# Presign -> receipts -> KMS (store band).
p.append(orth("presign", "b", "receipts", "t", "presigned GET", BLUE, num=14))
p.append(orth("receipts", "l", "kms", "r", "SSE-KMS", BLUE, dash=True, num=15))

# Observability (own right-hand lane; never crosses the request spine).
p.append(orth("bedrock", "b", "cloudwatch", "t", "invocation logs", GREEN, dash=True, num=16))
p.append(orth("xray", "b", "assistant", "t", "trace", GREEN, dash=True, num=17))

# ---- Legend ---------------------------------------------------------------
lg_x, lg_y = 1370, 470
p.append(f'<rect x="{lg_x-16}" y="{lg_y-26}" width="228" height="190" rx="12" fill="#ffffff" stroke="#d9e1ec" stroke-width="1"/>')
p.append(f'<text x="{lg_x}" y="{lg_y}" class="lgd" font-weight="800">Flow legend</text>')
legend = [(BLUE, "edge / data"),
          (ORANGE, "WAF / API / orders / refund"),
          (PURPLE, "Strands &#8594; Bedrock"),
          (GREEN, "observability")]
for i, (c, t) in enumerate(legend):
    yy = lg_y + 22 + i * 20
    p.append(f'<line x1="{lg_x}" y1="{yy-4}" x2="{lg_x+24}" y2="{yy-4}" stroke="{c}" stroke-width="3"/>')
    p.append(f'<text x="{lg_x+32}" y="{yy}" class="lgd">{t}</text>')
yy = lg_y + 22 + 4 * 20 + 6
p.append(f'<text x="{lg_x}" y="{yy}" class="note" fill="#9aa9bf">dashed = async / config / crypto</text>')
p.append(f'<text x="{lg_x}" y="{yy + 18}" class="note">Guardrail does NOT see tool-call</text>')
p.append(f'<text x="{lg_x}" y="{yy + 32}" class="note">args; handlers mask PII themselves.</text>')
p.append(f'<text x="{lg_x}" y="{yy + 46}" class="note">Refunds need human confirmation.</text>')

p.append('</svg>')

# ---- Self-check: no routed segment may cross a non-endpoint icon box -------
# This makes "arrows don't cross icons" a verified invariant rather than a
# visual hope: if a future edit moves a node into a line's path, the build
# fails loudly instead of silently producing an overlapping diagram.
crossings = []
for exclude, clean in ROUTED:
    for (x1, y1), (x2, y2) in zip(clean, clean[1:]):
        for key, box in ALL_BOXES.items():
            if key in exclude:
                continue
            if _seg_hits_box(x1, y1, x2, y2, box, exclude):
                crossings.append((key, (x1, y1, x2, y2)))
if crossings:
    for key, seg in crossings:
        print(f"  WARNING: a connector crosses the '{key}' icon box at {seg}")
    raise SystemExit(
        f"ERROR: {len(crossings)} connector/icon crossing(s) detected — "
        "adjust node placement or the edge's seed lane."
    )

with open(OUT, "w") as f:
    f.write("\n".join(p))
print("wrote", OUT, os.path.getsize(OUT), "bytes")
print(f"self-check OK: {len(ROUTED)} connectors, 0 icon crossings")
