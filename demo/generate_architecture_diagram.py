"""
Generate architecture diagram for APCR-DVA Session 1 Demo
using the 'diagrams' library with official AWS icons.
"""

import os
from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom

# Use absolute paths for icons
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS_BASE = os.path.join(BASE_DIR, "aws-icons", "Architecture-Service-Icons_04302026")

# Service icons (64px)
CLOUDFRONT_ICON = os.path.join(ICONS_BASE, "Arch_Networking-Content-Delivery", "64", "Arch_Amazon-CloudFront_64.png")
APIGW_ICON = os.path.join(ICONS_BASE, "Arch_Networking-Content-Delivery", "64", "Arch_Amazon-API-Gateway_64.png")
LAMBDA_ICON = os.path.join(ICONS_BASE, "Arch_Compute", "64", "Arch_AWS-Lambda_64.png")
DYNAMODB_ICON = os.path.join(ICONS_BASE, "Arch_Databases", "64", "Arch_Amazon-DynamoDB_64.png")
IAM_ICON = os.path.join(ICONS_BASE, "Arch_Security-Identity", "64", "Arch_AWS-Identity-and-Access-Management_64.png")
PRIVATELINK_ICON = os.path.join(ICONS_BASE, "Arch_Networking-Content-Delivery", "64", "Arch_AWS-PrivateLink_64.png")
ROUTE53_ICON = os.path.join(ICONS_BASE, "Arch_Networking-Content-Delivery", "64", "Arch_Amazon-Route-53_64.png")

# Resource icons
RES_ICONS_BASE = os.path.join(BASE_DIR, "aws-icons", "Resource-Icons_04302026")
USERS_ICON = os.path.join(RES_ICONS_BASE, "Res_General-Icons", "Res_48_Light", "Res_Users_48_Light.png")

# Verify icons exist
for name, path in [("Users", USERS_ICON), ("CloudFront", CLOUDFRONT_ICON), ("API GW", APIGW_ICON),
                   ("Lambda", LAMBDA_ICON), ("DynamoDB", DYNAMODB_ICON),
                   ("IAM", IAM_ICON), ("PrivateLink", PRIVATELINK_ICON), ("Route53", ROUTE53_ICON)]:
    assert os.path.exists(path), f"Icon not found: {name} at {path}"
    print(f"OK: {name}")

graph_attr = {
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "0.5",
    "ranksep": "1.0",
    "nodesep": "0.8",
    "label": "",
    "splines": "curved",
    "dpi": "300",
}

output_path = os.path.join(BASE_DIR, "demo", "architecture-diagram")

with Diagram(
    "",
    filename=output_path,
    show=False,
    direction="LR",
    graph_attr=graph_attr,
    outformat="png",
):
    # Users / Internet entry
    users = Custom("Internet\nUsers", USERS_ICON)

    # Route 53 (DNS)
    route53 = Custom("Route 53\n(DNS Alias)", ROUTE53_ICON)

    # CloudFront (Edge)
    cloudfront = Custom("Amazon\nCloudFront\n(CDN)", CLOUDFRONT_ICON)

    # API Gateway
    apigw = Custom("Amazon\nAPI Gateway\n(REST API)", APIGW_ICON)

    # IAM
    iam = Custom("AWS IAM\n(Roles, Policies,\nSTS)", IAM_ICON)

    with Cluster("VPC (10.0.0.0/16)"):

        with Cluster("Private Subnets (AZ-a + AZ-b)\n[NACL: Stateless filtering]  [Security Group: Stateful]"):
            # Lambda
            lambda_fn = Custom("AWS Lambda\n(Inventory API)", LAMBDA_ICON)

        with Cluster("VPC Gateway Endpoint"):
            vpce = Custom("DynamoDB\nVPC Endpoint\n(No Internet)", PRIVATELINK_ICON)

    # DynamoDB (outside VPC visually but accessed via endpoint)
    dynamodb = Custom("Amazon\nDynamoDB\n(Inventory Table)", DYNAMODB_ICON)

    # Flow
    users >> Edge(label="HTTPS", color="darkgreen") >> route53
    route53 >> Edge(label="Alias\nRecord", color="darkgreen") >> cloudfront
    cloudfront >> Edge(label="Origin", color="blue") >> apigw
    apigw >> Edge(label="Proxy Integration", color="blue", minlen="2") >> lambda_fn
    lambda_fn >> Edge(label="Private\n(no internet)", color="red", style="bold") >> vpce
    vpce >> Edge(label="Gateway\nEndpoint", color="red", style="bold") >> dynamodb

    # IAM association
    iam >> Edge(label="Least Privilege\nExecution Role", color="orange", style="dashed", minlen="2") >> lambda_fn

print(f"Diagram generated: {output_path}.png")
