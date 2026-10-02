#!/usr/bin/env python3
"""Generate a self-contained architecture SVG for the session5 secure assistant.

Reuses the session4 base64 icon-embed approach: each official AWS ``*_64.svg``
icon is inlined as ``data:image/svg+xml;base64`` so the SVG needs no external
files. Color-coded "act" zones, curved bezier flow arrows, numbered steps, a
legend, and a drop-shadow filter — same visual grammar as
``demo/session4-coffee-ship/container/build_diagram.py``.

Flow:
  Viewer -> CloudFront (default CloudFront domain)
    * default behavior  -> S3 + OAC SPA bucket
    * /api/* behavior   -> regional WAF -> API Gateway -> assistant Lambda
                           (VPC private subnets)
  assistant Lambda -> PrivateLink bedrock-runtime endpoint -> Bedrock
                      Nova Micro (inference profile + Guardrail)
  assistant Lambda -> DynamoDB orders/pending-refunds (CMK) + Secrets + SSM
  refund-confirm (human confirmation) -> executes the pending refund
  presign Lambda   -> receipts S3 (CMK, TLS-only)
  Bedrock invocation logs -> CMK CloudWatch
  X-Ray across API Gateway + Lambdas

Output: diagram/architecture.svg (next to this script).
"""
import base64
import os

ICON_BASE = "/Users/erictole/demo/apcr-dva/aws-icons/Architecture-Service-Icons_04302026"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "architecture.svg")

# Official *_64.svg icons for the services in this architecture (all verified
# present in the icon set).
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

W, H = 1480, 940
ICON = 56

# Act-color-coded zones (fill, stroke, title color).
ZONES = {
    "act1": ("#eaf0fb", "#4d72d6", "#2f52b0"),  # network/data security (blue)
    "act2": ("#fff2e6", "#ed7100", "#c25e00"),  # identity/access (orange)
    "act3": ("#f3eefc", "#8c4fff", "#6b2fd6"),  # Strands assistant (purple)
    "act4": ("#eafaf1", "#1f9d55", "#157a40"),  # observability (green)
}

# Node coordinates: (cx, top-of-icon-y).
N = {
    "cloudfront": (360, 150),
    "spa":        (580, 90),
    "waf":        (580, 250),
    "apigw":      (790, 250),
    "lambda":     (1010, 250),
    "privatelink": (1010, 440),
    "bedrock":    (1230, 440),
    "cloudwatch": (1230, 610),
    "dynamodb":   (790, 470),
    "secrets":    (640, 560),
    "ssm":        (790, 620),
    "refund":     (560, 440),
    "presign":    (360, 470),
    "receipts":   (360, 630),
    "kms":        (170, 630),
    "xray":       (1010, 90),
}

USER = (140, 250)


def icon(cx, y, key, label, sub=""):
    x = cx - ICON // 2
    s = f'<g filter="url(#soft)"><rect x="{x-4}" y="{y-4}" width="{ICON+8}" height="{ICON+8}" rx="12" fill="#ffffff"/></g>'
    s += f'<image x="{x}" y="{y}" width="{ICON}" height="{ICON}" href="{U[key]}"/>'
    s += f'<text x="{cx}" y="{y + ICON + 15}" class="lbl">{label}</text>'
    if sub:
        s += f'<text x="{cx}" y="{y + ICON + 29}" class="sub">{sub}</text>'
    return s


def user_node(cx, y, label="Viewer", sub="browser"):
    x = cx - ICON // 2
    s = f'<g filter="url(#soft)"><rect x="{x-4}" y="{y-4}" width="{ICON+8}" height="{ICON+8}" rx="12" fill="#ffffff"/></g>'
    s += f'<circle cx="{cx}" cy="{y+18}" r="10" fill="#48607c"/>'
    s += f'<path d="M {cx-16} {y+ICON-6} q 16 -22 32 0 z" fill="#48607c"/>'
    s += f'<text x="{cx}" y="{y + ICON + 15}" class="lbl">{label}</text>'
    s += f'<text x="{cx}" y="{y + ICON + 29}" class="sub">{sub}</text>'
    return s


def zone(x, y, w, h, title, kind):
    fill, stroke, tcol = ZONES[kind]
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill}" stroke="{stroke}" stroke-width="1.6" opacity="0.85"/>'
    s += f'<text x="{x+16}" y="{y+27}" class="ztitle" fill="{tcol}">{title}</text>'
    return s


def _center(key):
    if key == "user":
        return USER[0], USER[1] + ICON // 2
    return N[key][0], N[key][1] + ICON // 2


def edge(a, b, label="", dash=False, color="#5b7089", bend=40, num=None):
    ax, ay = _center(a)
    bx, by = _center(b)
    mx, my = (ax + bx) / 2, (ay + by) / 2
    if abs(bx - ax) >= abs(by - ay):
        cx, cy = mx, my - bend
    else:
        cx, cy = mx + bend, my
    d = ' stroke-dasharray="6 5"' if dash else ""
    s = f'<path d="M {ax} {ay} Q {cx} {cy} {bx} {by}" fill="none" stroke="{color}" stroke-width="2.4" marker-end="url(#arw)"{d} opacity="0.9"/>'
    if label:
        lx, ly = cx, cy - 2
        s += f'<rect x="{lx - len(label)*3.4 - 6}" y="{ly - 12}" width="{len(label)*6.8 + 12}" height="17" rx="8" fill="#ffffff" opacity="0.92"/>'
        s += f'<text x="{lx}" y="{ly}" class="edge">{label}</text>'
        if num is not None:
            s += f'<circle cx="{lx - len(label)*3.4 - 6}" cy="{ly - 3.5}" r="8" fill="{color}"/>'
            s += f'<text x="{lx - len(label)*3.4 - 6}" y="{ly - 0.5}" class="enum">{num}</text>'
    return s


p = []
p.append(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Segoe UI, Helvetica, Arial, sans-serif">
<defs>
  <marker id="arw" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7.5" markerHeight="7.5" orient="auto-start-reverse">
    <path d="M0 0 L10 5 L0 10 z" fill="#5b7089"/>
  </marker>
  <filter id="soft" x="-30%" y="-30%" width="160%" height="160%">
    <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#16273f" flood-opacity="0.18"/>
  </filter>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#f5f8fc"/>
  </linearGradient>
</defs>
<style>
  .lbl {{ fill:#16273f; font-size:12.5px; font-weight:700; text-anchor:middle; }}
  .sub {{ fill:#7a8aa0; font-size:10px; text-anchor:middle; }}
  .ztitle {{ font-size:13px; font-weight:800; letter-spacing:.02em; }}
  .edge {{ fill:#3d5168; font-size:10.5px; font-weight:600; text-anchor:middle; }}
  .enum {{ fill:#fff; font-size:9px; font-weight:800; text-anchor:middle; }}
  .title {{ fill:#16273f; font-size:24px; font-weight:800; }}
  .cap {{ fill:#7a8aa0; font-size:13px; }}
  .lgd {{ fill:#48607c; font-size:11.5px; font-weight:600; }}
  .note {{ fill:#7a8aa0; font-size:10.5px; }}
</style>
<rect x="0" y="0" width="{W}" height="{H}" fill="url(#bg)"/>
<text x="34" y="44" class="title">Secure Coffee-Shop AI Assistant &#8212; Strands + Nova Micro, four security acts</text>
<text x="34" y="66" class="cap">CloudFront+WAF+OAC &#8594; API &#8594; private-subnet Strands assistant &#8594; Bedrock (Nova Micro inference profile + Guardrail) via PrivateLink. Region ap-southeast-1.</text>
''')

# Act zones (behind nodes).
p.append(zone(300, 86, 360, 230, "Act 1 &#8212; network / data security", "act1"))
p.append(zone(520, 210, 400, 160, "Act 2 &#8212; identity &amp; access", "act2"))
p.append(zone(950, 210, 420, 300, "Act 3 &#8212; Strands assistant (secured)", "act3"))
p.append(zone(950, 575, 360, 130, "Act 4 &#8212; observability", "act4"))
p.append(zone(120, 410, 540, 300, "Data plane &#8212; CMK-encrypted (DynamoDB / receipts / secrets)", "act1"))

# Viewer glyph.
p.append(user_node(*USER))

# Nodes.
p.append(icon(*N["cloudfront"], "cloudfront", "CloudFront", "default domain + OAC"))
p.append(icon(*N["spa"], "s3", "S3 SPA", "private via OAC"))
p.append(icon(*N["waf"], "waf", "WAF (REGIONAL)", "common + rate (COUNT)"))
p.append(icon(*N["apigw"], "apigw", "API Gateway", "/api/* (X-Ray on)"))
p.append(icon(*N["lambda"], "lambda", "Assistant", "VPC private subnets"))
p.append(icon(*N["privatelink"], "privatelink", "PrivateLink", "bedrock-runtime EP"))
p.append(icon(*N["bedrock"], "bedrock", "Bedrock", "Nova Micro + Guardrail"))
p.append(icon(*N["cloudwatch"], "cloudwatch", "CloudWatch", "invocation logs (CMK)"))
p.append(icon(*N["dynamodb"], "dynamodb", "DynamoDB", "orders / pending-refunds"))
p.append(icon(*N["secrets"], "secrets", "Secrets Mgr", "payment key"))
p.append(icon(*N["ssm"], "ssm", "SSM Param", "assistant config"))
p.append(icon(*N["refund"], "lambda", "Refund confirm", "human-in-the-loop"))
p.append(icon(*N["presign"], "lambda", "Presign", "15-min GET URL"))
p.append(icon(*N["receipts"], "s3", "Receipts S3", "CMK, TLS-only DENY"))
p.append(icon(*N["kms"], "kms", "KMS CMK", "one key"))
p.append(icon(*N["xray"], "xray", "X-Ray", "API GW + Lambdas"))

BLUE, ORANGE, PURPLE, GREEN = "#4d72d6", "#ed7100", "#8c4fff", "#1f9d55"

# Edge flow (numbered).
p.append(edge("user", "cloudfront", "https", color=BLUE, bend=26, num=1))
p.append(edge("cloudfront", "spa", "SPA (OAC)", color=BLUE, bend=22, num=2))
p.append(edge("cloudfront", "waf", "/api/*", color=ORANGE, bend=22, num=3))
p.append(edge("waf", "apigw", "allow/count", color=ORANGE, bend=20, num=4))
p.append(edge("apigw", "lambda", "invoke", color=ORANGE, bend=20, num=5))
p.append(edge("lambda", "privatelink", "InvokeModel", color=PURPLE, bend=30, num=6))
p.append(edge("privatelink", "bedrock", "Nova + Guardrail", color=PURPLE, bend=20, num=7))
p.append(edge("lambda", "dynamodb", "orders / pending", color=BLUE, bend=40, num=8))
p.append(edge("lambda", "secrets", "payment key", dash=True, color=BLUE, bend=40, num=9))
p.append(edge("lambda", "ssm", "config", dash=True, color=BLUE, bend=60, num=10))
p.append(edge("refund", "dynamodb", "confirm (human)", color=ORANGE, bend=30, num=11))
p.append(edge("presign", "receipts", "presigned GET", color=BLUE, bend=24, num=12))
p.append(edge("receipts", "kms", "SSE-KMS", dash=True, color=BLUE, bend=20, num=13))
p.append(edge("bedrock", "cloudwatch", "invocation logs", dash=True, color=GREEN, bend=22, num=14))
p.append(edge("xray", "lambda", "trace", dash=True, color=GREEN, bend=30, num=15))

# Legend.
lg_x, lg_y = 1300, 120
p.append(f'<text x="{lg_x}" y="{lg_y}" class="lgd">Flow legend</text>')
legend = [(BLUE, "1-2, 8-13  edge / data"),
          (ORANGE, "3-5, 11  WAF / API / refund"),
          (PURPLE, "6-7  Strands &#8594; Bedrock"),
          (GREEN, "14-15  observability")]
for i, (c, t) in enumerate(legend):
    yy = lg_y + 20 + i * 22
    p.append(f'<line x1="{lg_x-6}" y1="{yy-4}" x2="{lg_x+20}" y2="{yy-4}" stroke="{c}" stroke-width="3"/>')
    p.append(f'<text x="{lg_x+28}" y="{yy}" class="lgd">{t}</text>')
p.append(f'<text x="{lg_x-6}" y="{lg_y + 20 + 4*22 + 4}" class="lgd" fill="#9aa9bf">dashed = async / config / crypto</text>')
p.append(f'<text x="{lg_x-6}" y="{lg_y + 20 + 4*22 + 22}" class="note">Guardrail does NOT see tool-call</text>')
p.append(f'<text x="{lg_x-6}" y="{lg_y + 20 + 4*22 + 37}" class="note">args; handlers mask PII themselves.</text>')
p.append(f'<text x="{lg_x-6}" y="{lg_y + 20 + 4*22 + 52}" class="note">Refund needs human confirmation.</text>')

p.append('</svg>')

with open(OUT, "w") as f:
    f.write("\n".join(p))
print("wrote", OUT, os.path.getsize(OUT), "bytes")
