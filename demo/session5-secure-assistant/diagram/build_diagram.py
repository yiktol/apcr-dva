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


# Anchor points on a node's bounding box by side.
def anchor(key, side):
    cx, cy = NODE[key]
    h = ICON // 2 + 4  # include the white padding rect
    if side == "r":
        return cx + h, cy
    if side == "l":
        return cx - h, cy
    if side == "t":
        return cx, cy - h
    if side == "b":
        return cx, cy + h
    return cx, cy


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

    `mid` optionally forces the x (for vertical-first) or y (for horizontal-
    first) of the elbow. The label is centred at (lx, ly) if given, else on the
    connector's longest leg.
    """
    ax, ay = anchor(a, sa)
    bx, by = anchor(b, sb)
    d = ' stroke-dasharray="6 5"' if dash else ""

    # Decide routing: if exit side is horizontal (l/r) go horizontal-first;
    # if vertical (t/b) go vertical-first.
    pts = [(ax, ay)]
    if sa in ("l", "r"):
        midx = mid if mid is not None else (ax + bx) / 2
        pts += [(midx, ay), (midx, by), (bx, by)]
    else:
        midy = mid if mid is not None else (ay + by) / 2
        pts += [(ax, midy), (bx, midy), (bx, by)]
    # Drop zero-length duplicate points.
    clean = [pts[0]]
    for pt in pts[1:]:
        if pt != clean[-1]:
            clean.append(pt)
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
# TOP request path (horizontal spine).
p.append(orth("viewer", "r", "cloudfront", "l", "https", BLUE, num=1))
p.append(orth("cloudfront", "t", "spa", "b", "SPA (OAC)", BLUE, num=2))
p.append(orth("cloudfront", "r", "waf", "b", "/api/*", ORANGE, num=3, mid=COL["api"]))
p.append(orth("waf", "b", "apigw", "t", "allow / count", ORANGE, num=4))
p.append(orth("apigw", "r", "assistant", "l", "invoke", ORANGE, num=5))
# API GW -> Orders list: up into the satellite row, elbow at a dedicated x so it
# does not sit on top of the invoke/place labels.
p.append(orth("apigw", "t", "orderslist", "l", "GET /api/orders", ORANGE, num=11,
              mid=COL["api"], lx=(COL["api"] + COL["compute"]) / 2, ly=ROW["sat"]))

# Assistant -> PrivateLink -> Bedrock. Horizontal-first: leave Assistant on the
# RIGHT, run along a clear lane, then drop into PrivateLink's column.
p.append(orth("assistant", "r", "privatelink", "t", "InvokeModel", PURPLE, num=6,
              mid=COL["ai"]))
p.append(orth("privatelink", "r", "bedrock", "l", "Nova + Guardrail", PURPLE, num=7))

# Compute -> data plane (downward connectors into the data band).
p.append(orth("assistant", "b", "dynamodb", "t", "place / look-up", BLUE, num=8,
              lx=COL["compute"], ly=ROW["top"] + 95))
p.append(orth("secrets", "t", "assistant", "b", "payment key", BLUE, dash=True, num=9,
              mid=COL["api"], lx=(COL["api"] + COL["compute"]) / 2, ly=ROW["top"] + 150))
p.append(orth("ssm", "t", "assistant", "b", "config", BLUE, dash=True, num=10,
              mid=COL["edge"], lx=COL["api"] - 40, ly=ROW["top"] - 60))
# Orders list -> DynamoDB: own column gutter to the left of the assistant spine.
p.append(orth("orderslist", "b", "dynamodb", "l", "query GSI", BLUE, num=12,
              mid=COL["compute"] - 110,
              lx=COL["compute"] - 110, ly=ROW["top"] + 40))
p.append(orth("refund", "l", "dynamodb", "r", "confirm (human)", ORANGE, num=13))

# Presign -> receipts -> KMS (store band).
p.append(orth("presign", "b", "receipts", "t", "presigned GET", BLUE, num=14, mid=COL["api"]))
p.append(orth("receipts", "l", "kms", "r", "SSE-KMS", BLUE, dash=True, num=15))

# Observability (own right-hand lane; never crosses the request spine).
p.append(orth("bedrock", "b", "cloudwatch", "t", "invocation logs", GREEN, dash=True, num=16))
# X-Ray -> Assistant trace: drop straight down X-Ray's column, then left into the
# assistant's TOP along the satellite/ spine gutter.
p.append(orth("xray", "l", "assistant", "t", "trace", GREEN, dash=True, num=17,
              lx=(COL["compute"] + COL["ai"]) / 2, ly=ROW["sat"] + 40))

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

with open(OUT, "w") as f:
    f.write("\n".join(p))
print("wrote", OUT, os.path.getsize(OUT), "bytes")
