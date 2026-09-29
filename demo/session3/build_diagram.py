#!/usr/bin/env python3
"""Generate a compelling, self-contained architecture SVG for the BeanThere demo.
Embeds the official AWS service icons (base64) from ../../aws-icons so the SVG
needs no external files. Features: color-coded group zones (AWS category colors),
curved bezier flow arrows, numbered steps, drop shadows, a legend.
Output: frontend/public/architecture.svg"""
import base64, os

ICON_BASE = "/Users/erictole/demo/apcr-dva/aws-icons/Architecture-Service-Icons_04302026"
OUT = os.path.join(os.path.dirname(__file__), "frontend", "public", "architecture.svg")

ICONS = {
    "cloudfront": "Arch_Networking-Content-Delivery/64/Arch_Amazon-CloudFront_64.png",
    "s3":         "Arch_Storage/64/Arch_Amazon-Simple-Storage-Service_64.png",
    "cognito":    "Arch_Security-Identity/64/Arch_Amazon-Cognito_64.png",
    "apigw":      "Arch_Networking-Content-Delivery/64/Arch_Amazon-API-Gateway_64.png",
    "lambda":     "Arch_Compute/64/Arch_AWS-Lambda_64.png",
    "elasticache":"Arch_Databases/64/Arch_Amazon-ElastiCache_64.png",
    "dynamodb":   "Arch_Databases/64/Arch_Amazon-DynamoDB_64.png",
    "sqs":        "Arch_Application-Integration/64/Arch_Amazon-Simple-Queue-Service_64.png",
    "sns":        "Arch_Application-Integration/64/Arch_Amazon-Simple-Notification-Service_64.png",
    "eventbridge":"Arch_Application-Integration/64/Arch_Amazon-EventBridge_64.png",
    "cloudwatch": "Arch_Management-Tools/64/Arch_Amazon-CloudWatch_64.png",
    "cloudtrail": "Arch_Management-Tools/64/Arch_AWS-CloudTrail_64.png",
}

def data_uri(rel):
    with open(os.path.join(ICON_BASE, rel), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()

U = {k: data_uri(v) for k, v in ICONS.items()}

W, H = 1280, 860
ICON = 58

# AWS-ish category palette for the group zones (fill, stroke, title)
ZONES = {
    "client": ("#fdeef7", "#d81b8c", "#b0166f"),   # front-end / delivery (pink)
    "compute": ("#fff2e6", "#ed7100", "#c25e00"),  # compute + DB (orange)
    "msg":     ("#f3eefc", "#8c4fff", "#6b2fd6"),  # application integration (purple)
    "obs":     ("#eaf4ec", "#3fa45b", "#2e7d45"),  # management/observability (green)
}

# Node coordinates: (cx, top-of-icon-y)
N = {
    "cloudfront":  (120, 150), "s3": (250, 150), "cognito": (135, 258),
    "apigw":       (420, 175),
    "lambda_api":  (600, 145), "elasticache": (770, 145), "dynamodb": (620, 268),
    "sqs":         (430, 480), "lambda_wk": (620, 480), "sns": (800, 480), "eventbridge": (980, 480),
    "cloudwatch":  (240, 700), "cwlogs": (490, 700), "cloudtrail": (720, 700),
}

def icon(cx, y, key, label, sub=""):
    x = cx - ICON // 2
    s = f'<g filter="url(#soft)"><rect x="{x-4}" y="{y-4}" width="{ICON+8}" height="{ICON+8}" rx="12" fill="#ffffff"/></g>'
    s += f'<image x="{x}" y="{y}" width="{ICON}" height="{ICON}" href="{U[key]}"/>'
    s += f'<text x="{cx}" y="{y + ICON + 15}" class="lbl">{label}</text>'
    if sub:
        s += f'<text x="{cx}" y="{y + ICON + 29}" class="sub">{sub}</text>'
    return s

def zone(x, y, w, h, title, kind, num=None):
    fill, stroke, tcol = ZONES[kind]
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill}" stroke="{stroke}" stroke-width="1.6" opacity="0.9"/>'
    if num is not None:
        s += f'<circle cx="{x+22}" cy="{y+22}" r="12" fill="{stroke}"/>'
        s += f'<text x="{x+22}" y="{y+26}" class="znum">{num}</text>'
        tx = x + 42
    else:
        tx = x + 16
    s += f'<text x="{tx}" y="{y+27}" class="ztitle" fill="{tcol}">{title}</text>'
    return s

def edge(a, b, label="", dash=False, color="#5b7089", bend=40, side="mid", num=None):
    """Curved bezier arrow between node centers, offset to icon edges."""
    ax, ay = N[a][0], N[a][1] + ICON // 2
    bx, by = N[b][0], N[b][1] + ICON // 2
    # control point: perpendicular-ish bend
    mx, my = (ax + bx) / 2, (ay + by) / 2
    if abs(bx - ax) >= abs(by - ay):
        cx, cy = mx, my - bend            # horizontal-ish -> bend vertically
    else:
        cx, cy = mx + bend, my            # vertical-ish -> bend horizontally
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
  .znum {{ fill:#fff; font-size:12px; font-weight:800; text-anchor:middle; }}
  .edge {{ fill:#3d5168; font-size:10.5px; font-weight:600; text-anchor:middle; }}
  .enum {{ fill:#fff; font-size:9px; font-weight:800; text-anchor:middle; }}
  .title {{ fill:#16273f; font-size:24px; font-weight:800; }}
  .cap {{ fill:#7a8aa0; font-size:13px; }}
  .lgd {{ fill:#48607c; font-size:11.5px; font-weight:600; }}
</style>
<rect x="0" y="0" width="{W}" height="{H}" fill="url(#bg)"/>
<text x="34" y="44" class="title">BeanThere &#8212; core-services architecture</text>
<text x="34" y="66" class="cap">A serverless coffee-ordering app. Follow the numbered path; each zone is one part of the stack.</text>
''')

# Zones (drawn first, behind nodes)
p.append(zone(50, 100, 330, 260, "1 · Client &amp; delivery", "client"))
p.append(zone(520, 100, 360, 280, "2 · Application in the VPC", "compute"))
p.append(zone(360, 430, 730, 180, "3 · Event-driven processing", "msg"))
p.append(zone(50, 640, 920, 180, "4 · Observability", "obs"))

# API Gateway sits between zone 1 and 2 (no zone box, it's the front door)
p.append(icon(*N["apigw"], "apigw", "API Gateway", "HTTP API + JWT"))

# Zone 1 nodes
p.append(icon(*N["cloudfront"], "cloudfront", "CloudFront"))
p.append(icon(*N["s3"], "s3", "S3", "React SPA"))
p.append(icon(*N["cognito"], "cognito", "Cognito", "user + identity pool"))

# Zone 2 nodes
p.append(icon(*N["lambda_api"], "lambda", "API Lambda", "menu / orders"))
p.append(icon(*N["elasticache"], "elasticache", "ElastiCache", "Valkey cache"))
p.append(icon(*N["dynamodb"], "dynamodb", "DynamoDB", "orders + menu"))

# Zone 3 nodes
p.append(icon(*N["sqs"], "sqs", "SQS", "queue + DLQ"))
p.append(icon(*N["lambda_wk"], "lambda", "Worker Lambda", "processes orders"))
p.append(icon(*N["sns"], "sns", "SNS", "fan-out"))
p.append(icon(*N["eventbridge"], "eventbridge", "EventBridge", "routes by content"))

# Zone 4 nodes
p.append(icon(*N["cloudwatch"], "cloudwatch", "CloudWatch", "metric + alarm"))
p.append(icon(*N["cwlogs"], "cloudwatch", "CloudWatch Logs", "structured JSON"))
p.append(icon(*N["cloudtrail"], "cloudtrail", "CloudTrail", "API audit"))

# Flow edges (numbered), color-coded by phase
PINK, ORANGE, PURPLE, GREEN = "#d81b8c", "#ed7100", "#8c4fff", "#3fa45b"
p.append(edge("cloudfront", "cognito", "sign in", color=PINK, bend=26, num=1))
p.append(edge("s3", "apigw", "request + JWT", color=PINK, bend=-46, num=2))
p.append(edge("apigw", "lambda_api", "invoke", color=ORANGE, bend=34, num=3))
p.append(edge("lambda_api", "elasticache", "lazy-load", dash=True, color=ORANGE, bend=24, num=4))
p.append(edge("lambda_api", "dynamodb", "read / write", color=ORANGE, bend=52, num=5))
p.append(edge("lambda_api", "sqs", "enqueue order", color=PURPLE, bend=80, num=6))
p.append(edge("sqs", "lambda_wk", "trigger", color=PURPLE, bend=28, num=7))
p.append(edge("lambda_wk", "sns", "publish (fan-out)", color=PURPLE, bend=-30, num=8))
p.append(edge("lambda_wk", "eventbridge", "put event", color=PURPLE, bend=64, num=9))
p.append(edge("lambda_wk", "cloudwatch", "metric + logs", color=GREEN, bend=60, num=10))
p.append(edge("eventbridge", "cwlogs", "OrderPlaced &#8594; Logs", dash=True, color=GREEN, bend=150, num=11))

# Legend (bottom-right)
lg_x, lg_y = 1000, 640
p.append(f'<text x="{lg_x}" y="{lg_y}" class="lgd">Flow legend</text>')
legend = [(PINK, "1-2  sign in &amp; request"), (ORANGE, "3-5  serve &amp; persist"),
          (PURPLE, "6-9  decouple &amp; route"), (GREEN, "10-11  observe")]
for i, (c, t) in enumerate(legend):
    yy = lg_y + 20 + i * 22
    p.append(f'<line x1="{lg_x}" y1="{yy-4}" x2="{lg_x+26}" y2="{yy-4}" stroke="{c}" stroke-width="3"/>')
    p.append(f'<text x="{lg_x+34}" y="{yy}" class="lgd">{t}</text>')
p.append(f'<text x="{lg_x}" y="{lg_y + 20 + 4*22 + 4}" class="lgd" fill="#9aa9bf">dashed = async / event</text>')

p.append('</svg>')

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    f.write("\n".join(p))
print("wrote", OUT, os.path.getsize(OUT), "bytes")
