#!/usr/bin/env python3
"""Generate a self-contained architecture SVG for the Coffee Shop REAL app.

Embeds the official AWS service icons (base64) from the repo's aws-icons set so
the SVG needs no external files. Uses
color-coded group zones (AWS category colors), curved bezier flow arrows,
numbered steps, drop shadows, a legend. Unlike session3 (which embeds PNGs),
this embeds the vector ``*_64.svg`` icons as ``data:image/svg+xml;base64``.

Two deploy environments are drawn distinctly:
  * TEST  — User -> CloudFront (test) -> test ALB -> test ECS service, deployed
    by a rolling ``EcsDeployAction`` (circuit breaker).
  * PROD  — User -> CloudFront (prod) -> prod ALB (blue/green target groups) ->
    prod ECS service (CODE_DEPLOY controller), deployed by a
    ``CodeDeployEcsDeployAction`` doing a blue/green canary 10%/5min with
    automatic alarm rollback.

Lanes:
  * Runtime  — User -> CloudFront(prod/test) -> ALB -> ECS Fargate ->
    DynamoDB orders + SSM rate.
  * CI/CD    — source.zip in S3 -> EventBridge -> CodePipeline -> CodeBuild
    (docker build/push) -> ECR -> EcsDeployAction (rolling) to TEST, then a
    manual Approval gate, then CodeDeployEcsDeployAction (blue/green) to PROD.

Output: container/architecture.svg (next to this script).
"""
import base64
import os

ICON_BASE = "/Users/erictole/demo/apcr-dva/aws-icons/Architecture-Service-Icons_04302026"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "architecture.svg")

# Official *_64.svg icons for the services in this architecture.
ICONS = {
    "cloudfront": "Arch_Networking-Content-Delivery/64/Arch_Amazon-CloudFront_64.svg",
    "alb":        "Arch_Networking-Content-Delivery/64/Arch_Elastic-Load-Balancing_64.svg",
    "ecs":        "Arch_Containers/64/Arch_Amazon-Elastic-Container-Service_64.svg",
    "fargate":    "Arch_Containers/64/Arch_AWS-Fargate_64.svg",
    "ecr":        "Arch_Containers/64/Arch_Amazon-Elastic-Container-Registry_64.svg",
    "dynamodb":   "Arch_Databases/64/Arch_Amazon-DynamoDB_64.svg",
    "ssm":        "Arch_Management-Tools/64/Arch_AWS-Systems-Manager_64.svg",
    "pipeline":   "Arch_Developer-Tools/64/Arch_AWS-CodePipeline_64.svg",
    "codebuild":  "Arch_Developer-Tools/64/Arch_AWS-CodeBuild_64.svg",
    "codedeploy": "Arch_Developer-Tools/64/Arch_AWS-CodeDeploy_64.svg",
    "s3":         "Arch_Storage/64/Arch_Amazon-Simple-Storage-Service_64.svg",
    "eventbridge":"Arch_Application-Integration/64/Arch_Amazon-EventBridge_64.svg",
}


def data_uri(rel):
    with open(os.path.join(ICON_BASE, rel), "rb") as f:
        return "data:image/svg+xml;base64," + base64.b64encode(f.read()).decode()


U = {k: data_uri(v) for k, v in ICONS.items()}

W, H = 1360, 860
ICON = 56

# AWS-ish category palette for the group zones (fill, stroke, title).
ZONES = {
    "test":    ("#eafaf1", "#1f9d55", "#157a40"),   # TEST env (green)
    "prod":    ("#fff2e6", "#ed7100", "#c25e00"),   # PROD env (orange)
    "data":    ("#eaf0fb", "#4d72d6", "#2f52b0"),   # data plane (blue)
    "cicd":    ("#f3eefc", "#8c4fff", "#6b2fd6"),    # developer tools (purple)
}

# Node coordinates: (cx, top-of-icon-y). A separate User node is drawn by hand.
N = {
    # TEST runtime lane (upper)
    "cf_test":  (360, 150), "alb_test": (570, 150), "ecs_test": (790, 150),
    # PROD runtime lane (lower)
    "cf_prod":  (360, 320), "alb_prod": (570, 320), "ecs_prod": (790, 320),
    # Data plane (right)
    "dynamodb": (1030, 170), "ssm": (1030, 300),
    # CI/CD lane (bottom)
    "s3":          (170, 660), "eventbridge": (355, 660), "pipeline": (545, 660),
    "codebuild":   (735, 660), "ecr": (925, 660), "codedeploy": (1120, 660),
}

USER = (130, 235)  # User node center (cx, top-of-icon-y) drawn as a glyph


def icon(cx, y, key, label, sub=""):
    x = cx - ICON // 2
    s = f'<g filter="url(#soft)"><rect x="{x-4}" y="{y-4}" width="{ICON+8}" height="{ICON+8}" rx="12" fill="#ffffff"/></g>'
    s += f'<image x="{x}" y="{y}" width="{ICON}" height="{ICON}" href="{U[key]}"/>'
    s += f'<text x="{cx}" y="{y + ICON + 15}" class="lbl">{label}</text>'
    if sub:
        s += f'<text x="{cx}" y="{y + ICON + 29}" class="sub">{sub}</text>'
    return s


def user_node(cx, y, label="User", sub="browser"):
    """A simple person glyph for the human initiating the flow."""
    x = cx - ICON // 2
    s = f'<g filter="url(#soft)"><rect x="{x-4}" y="{y-4}" width="{ICON+8}" height="{ICON+8}" rx="12" fill="#ffffff"/></g>'
    s += f'<circle cx="{cx}" cy="{y+18}" r="10" fill="#48607c"/>'
    s += f'<path d="M {cx-16} {y+ICON-6} q 16 -22 32 0 z" fill="#48607c"/>'
    s += f'<text x="{cx}" y="{y + ICON + 15}" class="lbl">{label}</text>'
    s += f'<text x="{cx}" y="{y + ICON + 29}" class="sub">{sub}</text>'
    return s


def zone(x, y, w, h, title, kind):
    fill, stroke, tcol = ZONES[kind]
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="{fill}" stroke="{stroke}" stroke-width="1.6" opacity="0.9"/>'
    s += f'<text x="{x+16}" y="{y+27}" class="ztitle" fill="{tcol}">{title}</text>'
    return s


def _center(key):
    if key == "user":
        return USER[0], USER[1] + ICON // 2
    return N[key][0], N[key][1] + ICON // 2


def edge(a, b, label="", dash=False, color="#5b7089", bend=40, num=None):
    """Curved bezier arrow between node centers, offset to icon edges."""
    ax, ay = _center(a)
    bx, by = _center(b)
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
  .edge {{ fill:#3d5168; font-size:10.5px; font-weight:600; text-anchor:middle; }}
  .enum {{ fill:#fff; font-size:9px; font-weight:800; text-anchor:middle; }}
  .title {{ fill:#16273f; font-size:24px; font-weight:800; }}
  .cap {{ fill:#7a8aa0; font-size:13px; }}
  .lgd {{ fill:#48607c; font-size:11.5px; font-weight:600; }}
  .note {{ fill:#7a8aa0; font-size:10.5px; }}
</style>
<rect x="0" y="0" width="{W}" height="{H}" fill="url(#bg)"/>
<text x="34" y="44" class="title">Coffee Shop &#8212; two environments: TEST (rolling) &amp; PROD (blue/green)</text>
<text x="34" y="66" class="cap">Order coffee through CloudFront; one CodePipeline rolls TEST then does a CodeDeploy blue/green canary to PROD. Region ap-southeast-1.</text>
''')

# Zones (behind nodes). TEST env on top, PROD env below, data plane right.
p.append(zone(300, 100, 620, 130, "TEST env &#8212; coffee-shop-test (rolling)", "test"))
p.append(zone(300, 270, 620, 130, "PROD env &#8212; coffee-shop-prod (blue/green)", "prod"))
p.append(zone(970, 120, 160, 290, "Data plane", "data"))
p.append(zone(120, 610, 1130, 180, "CI/CD lane &#8212; one pipeline, two deploy actions", "cicd"))

# User (hand-drawn glyph, outside the zones)
p.append(user_node(*USER))

# TEST runtime lane nodes
p.append(icon(*N["cf_test"], "cloudfront", "CloudFront", "TestCloudFrontUrl"))
p.append(icon(*N["alb_test"], "alb", "test ALB", "HTTP"))
p.append(icon(*N["ecs_test"], "ecs", "test ECS", "coffee-shop-test"))

# PROD runtime lane nodes
p.append(icon(*N["cf_prod"], "cloudfront", "CloudFront", "CloudFrontUrl"))
p.append(icon(*N["alb_prod"], "alb", "prod ALB", "blue/green TGs"))
p.append(icon(*N["ecs_prod"], "ecs", "prod ECS", "coffee-shop-prod"))

# Data plane nodes
p.append(icon(*N["dynamodb"], "dynamodb", "DynamoDB", "coffee-shop-orders"))
p.append(icon(*N["ssm"], "ssm", "SSM Parameter", "loyalty rate"))

# CI/CD lane nodes
p.append(icon(*N["s3"], "s3", "S3 source", "source.zip"))
p.append(icon(*N["eventbridge"], "eventbridge", "EventBridge", "Object Created"))
p.append(icon(*N["pipeline"], "pipeline", "CodePipeline", "coffee-shop"))
p.append(icon(*N["codebuild"], "codebuild", "CodeBuild", "docker build/push"))
p.append(icon(*N["ecr"], "ecr", "ECR", "coffee-shop repo"))
p.append(icon(*N["codedeploy"], "codedeploy", "CodeDeploy", "blue/green canary"))

# VPC note under the PROD lane.
p.append('<text x="316" y="420" class="note">Both ALBs run in the VPC (public subnets, no NAT).</text>')

GREEN, ORANGE, BLUE, PURPLE = "#1f9d55", "#ed7100", "#4d72d6", "#8c4fff"

# TEST runtime flow (numbered 1-3).
p.append(edge("user", "cf_test", "order (test)", color=GREEN, bend=30, num=1))
p.append(edge("cf_test", "alb_test", "forward", color=GREEN, bend=22, num=2))
p.append(edge("alb_test", "ecs_test", "route", color=GREEN, bend=22, num=3))

# PROD runtime flow (numbered 4-6).
p.append(edge("user", "cf_prod", "order (prod)", color=ORANGE, bend=30, num=4))
p.append(edge("cf_prod", "alb_prod", "forward", color=ORANGE, bend=22, num=5))
p.append(edge("alb_prod", "ecs_prod", "blue/green", color=ORANGE, bend=22, num=6))

# Data-plane flow (numbered 7-8): prod service reads/writes DynamoDB + SSM.
p.append(edge("ecs_prod", "dynamodb", "put / scan orders", color=BLUE, bend=40, num=7))
p.append(edge("ecs_prod", "ssm", "get loyalty rate", dash=True, color=BLUE, bend=40, num=8))

# CI/CD flow (numbered 9-13).
p.append(edge("s3", "eventbridge", "Object Created", color=PURPLE, bend=20, num=9))
p.append(edge("eventbridge", "pipeline", "start", color=PURPLE, bend=20, num=10))
p.append(edge("pipeline", "codebuild", "build stage", color=PURPLE, bend=20, num=11))
p.append(edge("codebuild", "ecr", "push image", color=PURPLE, bend=20, num=12))
# Deploy-Test: EcsDeployAction rolls the ECR image onto the TEST service.
p.append(edge("ecr", "ecs_test", "EcsDeployAction (rolling)", color=GREEN, bend=150, num=13))
# Deploy-Prod: after the manual Approval gate, CodeDeploy does blue/green canary.
p.append(edge("ecr", "codedeploy", "after Approval", color=PURPLE, bend=20, num=14))
p.append(edge("codedeploy", "ecs_prod", "CodeDeployEcsDeployAction (blue/green canary 10%/5m)", color=ORANGE, bend=150, num=15))

# Legend (bottom-right, above the CI/CD zone title area).
lg_x, lg_y = 1270, 150
p.append(f'<text x="{lg_x}" y="{lg_y}" class="lgd">Flow legend</text>')
legend = [(GREEN, "1-3  TEST runtime"),
          (ORANGE, "4-6  PROD runtime"),
          (BLUE, "7-8  data &amp; config"),
          (PURPLE, "9-15 CI/CD pipeline")]
for i, (c, t) in enumerate(legend):
    yy = lg_y + 20 + i * 22
    p.append(f'<line x1="{lg_x-6}" y1="{yy-4}" x2="{lg_x+20}" y2="{yy-4}" stroke="{c}" stroke-width="3"/>')
    p.append(f'<text x="{lg_x+28}" y="{yy}" class="lgd">{t}</text>')
p.append(f'<text x="{lg_x-6}" y="{lg_y + 20 + 4*22 + 4}" class="lgd" fill="#9aa9bf">dashed = cached / async</text>')
p.append(f'<text x="{lg_x-6}" y="{lg_y + 20 + 4*22 + 22}" class="note">TEST = rolling EcsDeployAction;</text>')
p.append(f'<text x="{lg_x-6}" y="{lg_y + 20 + 4*22 + 37}" class="note">PROD = CodeDeploy blue/green</text>')
p.append(f'<text x="{lg_x-6}" y="{lg_y + 20 + 4*22 + 52}" class="note">canary 10%/5m + alarm rollback.</text>')

p.append('</svg>')

with open(OUT, "w") as f:
    f.write("\n".join(p))
print("wrote", OUT, os.path.getsize(OUT), "bytes")
