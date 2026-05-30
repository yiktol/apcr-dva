"""
Enhanced architecture diagram generator for AWS exam strategy questions.
Creates richer, more explanatory diagrams that visually illustrate WHY
each option is correct or incorrect.

Uses the mingrammer/diagrams library with AWS service icons.
"""

import json
import os
import re
from pathlib import Path
from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Lambda, EC2, ElasticBeanstalk, ECS, Fargate
from diagrams.aws.storage import S3, EFS, EBS
from diagrams.aws.database import Dynamodb, RDS, ElastiCache, Neptune
from diagrams.aws.network import VPC, NATGateway, CloudFront, ELB, APIGateway, Route53
from diagrams.aws.integration import Eventbridge, SQS, SNS, StepFunctions
from diagrams.aws.devtools import Codepipeline, Codebuild, Codedeploy, Codecommit, XRay
from diagrams.aws.security import IAM, KMS, SecretsManager, Cognito, WAF
from diagrams.aws.management import Cloudwatch, Cloudformation, SystemsManager, Cloudtrail
from diagrams.aws.analytics import KinesisDataStreams
from diagrams.aws.general import Users, Client
from diagrams.aws.network import InternetGateway, VPCPeering, Endpoint


# Graph attributes for consistent styling
GRAPH_ATTR = {
    "fontsize": "16",
    "bgcolor": "#fafafa",
    "pad": "1.0",
    "splines": "spline",
    "nodesep": "1.2",
    "ranksep": "1.5",
    "fontname": "Helvetica",
    "dpi": "150",
}

# Cluster styles
CORRECT_CLUSTER = {"bgcolor": "#e8f5e9", "pencolor": "#2e7d32", "style": "rounded", "fontsize": "13", "fontname": "Helvetica Bold"}
INCORRECT_CLUSTER = {"bgcolor": "#fbe9e7", "pencolor": "#c62828", "style": "rounded", "fontsize": "13", "fontname": "Helvetica Bold"}
NEUTRAL_CLUSTER = {"bgcolor": "#e3f2fd", "pencolor": "#1565c0", "style": "rounded", "fontsize": "13", "fontname": "Helvetica Bold"}
SOURCE_CLUSTER = {"bgcolor": "#fff3e0", "pencolor": "#e65100", "style": "rounded", "fontsize": "13", "fontname": "Helvetica Bold"}
VPC_CLUSTER = {"bgcolor": "#f3e5f5", "pencolor": "#6a1b9a", "style": "rounded", "fontsize": "13", "fontname": "Helvetica Bold"}
TIER_CLUSTER = {"bgcolor": "#e8eaf6", "pencolor": "#283593", "style": "rounded", "fontsize": "12", "fontname": "Helvetica"}


def correct_edge(label=""):
    return Edge(color="#2e7d32", style="bold", penwidth="2.5", label=label, fontsize="11", fontcolor="#2e7d32", fontname="Helvetica")


def incorrect_edge(label=""):
    return Edge(color="#c62828", style="bold", penwidth="2.5", label=label, fontsize="11", fontcolor="#c62828", fontname="Helvetica")


def blocked_edge(label=""):
    return Edge(color="#c62828", style="dashed", penwidth="2.0", label=label, fontsize="11", fontcolor="#c62828", fontname="Helvetica")


def neutral_edge(label=""):
    return Edge(color="#1565c0", style="bold", penwidth="2.0", label=label, fontsize="11", fontcolor="#1565c0", fontname="Helvetica")


def warning_edge(label=""):
    return Edge(color="#e65100", style="bold", penwidth="2.0", label=label, fontsize="11", fontcolor="#e65100", fontname="Helvetica")


# ============================================================
# SESSION 1, QUESTION 1: Event-driven serverless microservices
# ============================================================

def s1_q1_option_b(output_path):
    """API Gateway - correct: enables HTTP API calls for customers."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("Customers", graph_attr=SOURCE_CLUSTER):
            users = Users("HTTP Clients")

        with Cluster("✓ API Layer", graph_attr=CORRECT_CLUSTER):
            apigw = APIGateway("API Gateway")

        with Cluster("Backend Services", graph_attr=NEUTRAL_CLUSTER):
            lam = Lambda("Business Logic")
            db = Dynamodb("Data Store")

        users >> correct_edge("HTTP API calls\n(REST/HTTP)") >> apigw
        apigw >> correct_edge("Invokes") >> lam
        lam >> correct_edge("Read/Write") >> db


def s1_q1_option_d(output_path):
    """DynamoDB - correct: persistent NoSQL data store."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("Customers", graph_attr=SOURCE_CLUSTER):
            users = Users("HTTP Clients")

        with Cluster("API & Compute", graph_attr=NEUTRAL_CLUSTER):
            apigw = APIGateway("API Gateway")
            lam = Lambda("Lambda")

        with Cluster("✓ Persistent Storage", graph_attr=CORRECT_CLUSTER):
            db = Dynamodb("DynamoDB")

        users >> neutral_edge("HTTP Request") >> apigw
        apigw >> neutral_edge("Invoke") >> lam
        lam >> correct_edge("Persist\nmicroservices data") >> db


def s1_q1_option_e(output_path):
    """Lambda - correct: serverless compute for business logic."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("Customers", graph_attr=SOURCE_CLUSTER):
            users = Users("HTTP Clients")

        with Cluster("API Layer", graph_attr=NEUTRAL_CLUSTER):
            apigw = APIGateway("API Gateway")

        with Cluster("✓ Serverless Compute", graph_attr=CORRECT_CLUSTER):
            lam = Lambda("Lambda\n(Business Logic)")

        with Cluster("Data Layer", graph_attr=NEUTRAL_CLUSTER):
            db = Dynamodb("DynamoDB")

        users >> neutral_edge("HTTP Request") >> apigw
        apigw >> correct_edge("Event-driven\ninvocation") >> lam
        lam >> neutral_edge("Store data") >> db


def s1_q1_option_a(output_path):
    """CloudWatch - incorrect: monitoring, not event-driven architecture."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("Customers", graph_attr=SOURCE_CLUSTER):
            users = Users("HTTP Clients")

        with Cluster("✗ Monitoring Only", graph_attr=INCORRECT_CLUSTER):
            cw = Cloudwatch("CloudWatch")

        users >> blocked_edge("✗ Cannot receive\nHTTP API calls") >> cw


def s1_q1_option_c(output_path):
    """Secrets Manager - incorrect: manages secrets, not API/compute/storage."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("Customers", graph_attr=SOURCE_CLUSTER):
            users = Users("HTTP Clients")

        with Cluster("✗ Secret Management Only", graph_attr=INCORRECT_CLUSTER):
            sm = SecretsManager("Secrets Manager")

        with Cluster("What's actually needed", graph_attr=NEUTRAL_CLUSTER):
            apigw = APIGateway("API Gateway")
            lam = Lambda("Lambda")
            db = Dynamodb("DynamoDB")

        users >> blocked_edge("✗ Not an API\nendpoint") >> sm
        apigw >> neutral_edge("") >> lam >> neutral_edge("") >> db


def s1_q1_option_f(output_path):
    """Elastic Beanstalk - incorrect: not serverless, not event-driven."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("Customers", graph_attr=SOURCE_CLUSTER):
            users = Users("HTTP Clients")

        with Cluster("✗ Server-based (Not Serverless)", graph_attr=INCORRECT_CLUSTER):
            eb = ElasticBeanstalk("Elastic Beanstalk")
            ec2 = EC2("EC2 Instances")

        with Cluster("Requirement: Serverless", graph_attr=CORRECT_CLUSTER):
            lam = Lambda("Lambda\n(Serverless ✓)")

        users >> warning_edge("Deploys to\nmanaged servers") >> eb
        eb >> incorrect_edge("Provisions\nEC2 instances") >> ec2
        users >> correct_edge("Should use\nserverless") >> lam


# ============================================================
# SESSION 1, QUESTION 2: S3 event-driven file processing
# ============================================================

def s1_q2_option_c(output_path):
    """S3 + Lambda event source - correct: immediate processing on upload."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("Fulfillment System", graph_attr=SOURCE_CLUSTER):
            source = Client("JSON Files")

        with Cluster("✓ Event-Driven Processing", graph_attr=CORRECT_CLUSTER):
            s3 = S3("S3 Bucket")
            lam = Lambda("Lambda\n(Processor)")

        source >> correct_edge("Upload JSON") >> s3
        s3 >> correct_edge("S3 Event\n(immediate trigger)") >> lam


def s1_q2_option_a(output_path):
    """EFS + Lambda event source - incorrect: EFS doesn't have native event triggers."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("Fulfillment System", graph_attr=SOURCE_CLUSTER):
            source = Client("JSON Files")

        with Cluster("✗ No Native Event Trigger", graph_attr=INCORRECT_CLUSTER):
            efs = EFS("EFS")
            lam = Lambda("Lambda")

        source >> warning_edge("Upload JSON") >> efs
        efs >> blocked_edge("✗ EFS has no\nevent source\nfor Lambda") >> lam


def s1_q2_option_b(output_path):
    """EFS + scheduled Lambda - incorrect: hourly polling causes delays."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("Fulfillment System", graph_attr=SOURCE_CLUSTER):
            source = Client("JSON Files")

        with Cluster("✗ Delayed Processing", graph_attr=INCORRECT_CLUSTER):
            efs = EFS("EFS")
            cw = Cloudwatch("CloudWatch\nSchedule Rule")
            lam = Lambda("Lambda")

        source >> warning_edge("Upload JSON") >> efs
        cw >> incorrect_edge("Triggers every\n1 hour ✗\n(up to 60 min delay)") >> lam
        lam >> warning_edge("Polls for files") >> efs


def s1_q2_option_d(output_path):
    """S3 + scheduled Lambda - incorrect: right storage, wrong trigger."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("Fulfillment System", graph_attr=SOURCE_CLUSTER):
            source = Client("JSON Files")

        with Cluster("✗ Right Storage, Wrong Trigger", graph_attr=INCORRECT_CLUSTER):
            s3 = S3("S3 Bucket")
            cw = Cloudwatch("CloudWatch\nSchedule Rule")
            lam = Lambda("Lambda")

        source >> correct_edge("Upload JSON\n(S3 is correct ✓)") >> s3
        cw >> incorrect_edge("Triggers every\n1 hour ✗\n(should use S3 events)") >> lam
        lam >> warning_edge("Polls S3") >> s3


# ============================================================
# SESSION 1, QUESTION 3: Same as Q2 (duplicate in source data)
# ============================================================

s1_q3_option_c = s1_q2_option_c
s1_q3_option_a = s1_q2_option_a
s1_q3_option_b = s1_q2_option_b
s1_q3_option_d = s1_q2_option_d


# ============================================================
# SESSION 1, QUESTION 4: VPC Endpoint for secure S3 access
# ============================================================

def s1_q4_option_d(output_path):
    """VPC Endpoint - correct: private access to S3 without Internet."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("VPC", graph_attr=VPC_CLUSTER):
            with Cluster("Private Subnet", graph_attr=NEUTRAL_CLUSTER):
                ec2 = EC2("EC2 Instance")
            with Cluster("✓ VPC Endpoint", graph_attr=CORRECT_CLUSTER):
                vpce = Endpoint("S3 Gateway\nEndpoint")

        with Cluster("AWS Service", graph_attr=NEUTRAL_CLUSTER):
            s3 = S3("S3 Bucket\n(Sensitive Data)")

        ec2 >> correct_edge("Private connection\n(no Internet)") >> vpce
        vpce >> correct_edge("AWS internal\nnetwork ✓") >> s3


def s1_q4_option_a(output_path):
    """Internet Gateway - incorrect: still uses public Internet."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("VPC", graph_attr=VPC_CLUSTER):
            with Cluster("Public Subnet", graph_attr=INCORRECT_CLUSTER):
                ec2 = EC2("EC2 Instance")
            igw = InternetGateway("Internet\nGateway")

        with Cluster("✗ Public Internet", graph_attr=INCORRECT_CLUSTER):
            internet = Client("Internet")

        s3 = S3("S3 Bucket\n(Sensitive Data)")

        ec2 >> incorrect_edge("Public route") >> igw
        igw >> incorrect_edge("✗ Traverses\npublic Internet") >> internet
        internet >> incorrect_edge("Security risk!") >> s3


def s1_q4_option_b(output_path):
    """VPN - incorrect: still goes over Internet (encrypted but not private)."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("VPC", graph_attr=VPC_CLUSTER):
            ec2 = EC2("EC2 Instance")

        with Cluster("✗ VPN (Still Internet-based)", graph_attr=INCORRECT_CLUSTER):
            internet = Client("Internet\n(Encrypted tunnel)")

        s3 = S3("S3 Bucket\n(Sensitive Data)")

        ec2 >> warning_edge("VPN tunnel") >> internet
        internet >> incorrect_edge("✗ Still traverses\npublic Internet\n(encrypted ≠ private)") >> s3


def s1_q4_option_c(output_path):
    """NAT Gateway - incorrect: enables outbound Internet, doesn't secure S3 access."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("VPC", graph_attr=VPC_CLUSTER):
            with Cluster("Private Subnet", graph_attr=NEUTRAL_CLUSTER):
                ec2 = EC2("EC2 Instance")
            nat = NATGateway("NAT Gateway")

        with Cluster("✗ Public Internet", graph_attr=INCORRECT_CLUSTER):
            internet = Client("Internet")

        s3 = S3("S3 Bucket\n(Sensitive Data)")

        ec2 >> warning_edge("Outbound traffic") >> nat
        nat >> incorrect_edge("✗ Routes through\npublic Internet") >> internet
        internet >> incorrect_edge("Not secure!") >> s3


# ============================================================
# SESSION 1, QUESTION 5: Three-tier security groups
# ============================================================

def s1_q5_option_a(output_path):
    """presentation-sg: Allow 80/443 from 0.0.0.0/0 - correct."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("Internet", graph_attr=SOURCE_CLUSTER):
            users = Users("Web Users\n(0.0.0.0/0)")

        with Cluster("✓ Presentation Tier", graph_attr=CORRECT_CLUSTER):
            sg = ELB("presentation-sg")
            ec2 = EC2("Web Server")

        users >> correct_edge("Port 80 (HTTP) ✓\nPort 443 (HTTPS) ✓") >> sg
        sg >> correct_edge("Allowed") >> ec2


def s1_q5_option_b(output_path):
    """data-sg: Allow 1433 from presentation-sg - incorrect: skips logic tier."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("Presentation Tier", graph_attr=SOURCE_CLUSTER):
            web = EC2("Web Server\n(presentation-sg)")

        with Cluster("Logic Tier (SKIPPED!)", graph_attr=NEUTRAL_CLUSTER):
            api = EC2("API Server\n(logic-sg)")

        with Cluster("✗ Data Tier", graph_attr=INCORRECT_CLUSTER):
            db = RDS("SQL Server\n(data-sg)")

        web >> incorrect_edge("✗ Direct DB access\nfrom Presentation!\n(bypasses Logic Tier)") >> db
        web >> blocked_edge("Should go\nthrough here") >> api
        api >> correct_edge("Correct path") >> db


def s1_q5_option_c(output_path):
    """data-sg: Allow 1433 from logic-sg - correct."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("Logic Tier", graph_attr=NEUTRAL_CLUSTER):
            api = EC2("API Server\n(logic-sg)")

        with Cluster("✓ Data Tier", graph_attr=CORRECT_CLUSTER):
            db = RDS("SQL Server\n(data-sg)")

        api >> correct_edge("Port 1433 ✓\n(from logic-sg only)") >> db


def s1_q5_option_d(output_path):
    """presentation-sg: Allow 1433 from data-sg - incorrect: wrong direction."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("Data Tier", graph_attr=NEUTRAL_CLUSTER):
            db = RDS("SQL Server\n(data-sg)")

        with Cluster("✗ Presentation Tier", graph_attr=INCORRECT_CLUSTER):
            web = EC2("Web Server\n(presentation-sg)")

        db >> incorrect_edge("✗ Port 1433\nWRONG DIRECTION!\n(DB → Web makes no sense)") >> web


def s1_q5_option_e(output_path):
    """logic-sg: Allow 443 from presentation-sg - correct."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("Presentation Tier", graph_attr=SOURCE_CLUSTER):
            web = EC2("Web Server\n(presentation-sg)")

        with Cluster("✓ Logic Tier", graph_attr=CORRECT_CLUSTER):
            api = EC2("API Server\n(logic-sg)")

        web >> correct_edge("Port 443 (HTTPS) ✓\n(from presentation-sg)") >> api


def s1_q5_option_f(output_path):
    """logic-sg: Allow 443 from 0.0.0.0/0 - incorrect: too permissive."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Entire Internet", graph_attr=INCORRECT_CLUSTER):
            users = Users("Anyone\n(0.0.0.0/0)")
            attacker = Client("Attackers")

        with Cluster("Logic Tier (Exposed!)", graph_attr=INCORRECT_CLUSTER):
            api = EC2("API Server\n(logic-sg)")

        users >> incorrect_edge("✗ Port 443\nfrom ANYWHERE\n(too permissive!)") >> api
        attacker >> incorrect_edge("Direct access\n(security risk)") >> api


# ============================================================
# SESSION 1, QUESTION 6: IAM Policy conditions (AND logic)
# ============================================================

def s1_q6_option_a(output_path):
    """AND conditions with SourceVpc - correct."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✓ Both Conditions Must Be True (AND)", graph_attr=CORRECT_CLUSTER):
            with Cluster("Condition 1: Time Window", graph_attr=NEUTRAL_CLUSTER):
                cw = Cloudwatch("Jul 1 - Dec 31\n2020 (UTC)")
            with Cluster("Condition 2: Source VPC", graph_attr=NEUTRAL_CLUSTER):
                vpc = VPC("vpc-111bbb22")

        with Cluster("IAM Action", graph_attr=NEUTRAL_CLUSTER):
            iam = IAM("Allow\nGetItem")
            db = Dynamodb("DynamoDB\n(Resource: *)")

        vpc >> correct_edge("Request from\nthis VPC ✓") >> iam
        cw >> correct_edge("Within time\nwindow ✓") >> iam
        iam >> correct_edge("Allowed") >> db


def s1_q6_option_b(output_path):
    """OR logic - incorrect: IAM conditions use AND, not OR."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ OR Logic (Incorrect interpretation)", graph_attr=INCORRECT_CLUSTER):
            with Cluster("Condition 1: Time", graph_attr=NEUTRAL_CLUSTER):
                cw = Cloudwatch("Jul 1 - Dec 31")
            with Cluster("Condition 2: VPC", graph_attr=NEUTRAL_CLUSTER):
                vpc = VPC("vpc-111bbb22")

        with Cluster("IAM", graph_attr=NEUTRAL_CLUSTER):
            iam = IAM("GetItem")

        cw >> incorrect_edge("✗ OR is wrong!\nIAM uses AND\nfor multiple conditions") >> iam
        vpc >> incorrect_edge("✗ Both must\nbe true, not either") >> iam


def s1_q6_option_c(output_path):
    """VPC endpoint mentioned - incorrect: policy says SourceVpc, not VPC endpoint."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Misinterpretation", graph_attr=INCORRECT_CLUSTER):
            vpce = Endpoint("VPC Endpoint\n(NOT in policy!)")

        with Cluster("What policy actually says", graph_attr=CORRECT_CLUSTER):
            vpc = VPC("aws:SourceVpc\n= vpc-111bbb22")

        with Cluster("IAM", graph_attr=NEUTRAL_CLUSTER):
            iam = IAM("GetItem")

        vpce >> blocked_edge("✗ Policy uses\naws:SourceVpc\nNOT aws:SourceVpce") >> iam
        vpc >> correct_edge("Correct condition\nkey") >> iam


def s1_q6_option_d(output_path):
    """OR + VPC endpoint - incorrect: both wrong (OR logic + wrong condition key)."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Two Errors", graph_attr=INCORRECT_CLUSTER):
            with Cluster("Error 1: OR logic", graph_attr=INCORRECT_CLUSTER):
                cw = Cloudwatch("Time condition")
            with Cluster("Error 2: VPC Endpoint", graph_attr=INCORRECT_CLUSTER):
                vpce = Endpoint("VPC Endpoint\n(wrong key)")

        with Cluster("IAM", graph_attr=NEUTRAL_CLUSTER):
            iam = IAM("GetItem")

        cw >> incorrect_edge("✗ OR is wrong") >> iam
        vpce >> incorrect_edge("✗ SourceVpce\nis wrong key") >> iam


# ============================================================
# Dispatch table mapping session/question/option to functions
# ============================================================

DIAGRAM_FUNCTIONS = {
    (1, 1): {
        "a": s1_q1_option_a,
        "b": s1_q1_option_b,
        "c": s1_q1_option_c,
        "d": s1_q1_option_d,
        "e": s1_q1_option_e,
        "f": s1_q1_option_f,
    },
    (1, 2): {
        "a": s1_q2_option_a,
        "b": s1_q2_option_b,
        "c": s1_q2_option_c,
        "d": s1_q2_option_d,
    },
    (1, 3): {
        "a": s1_q3_option_a,
        "b": s1_q3_option_b,
        "c": s1_q3_option_c,
        "d": s1_q3_option_d,
    },
    (1, 4): {
        "a": s1_q4_option_a,
        "b": s1_q4_option_b,
        "c": s1_q4_option_c,
        "d": s1_q4_option_d,
    },
    (1, 5): {
        "a": s1_q5_option_a,
        "b": s1_q5_option_b,
        "c": s1_q5_option_c,
        "d": s1_q5_option_d,
        "e": s1_q5_option_e,
        "f": s1_q5_option_f,
    },
    (1, 6): {
        "a": s1_q6_option_a,
        "b": s1_q6_option_b,
        "c": s1_q6_option_c,
        "d": s1_q6_option_d,
    },
}


def generate_diagrams_for_question_v2(session_num: int, q_num: int):
    """Generate enhanced diagrams for all options of a question."""
    q_dir = Path(f"session{session_num}/exam-strategy/q{q_num}")
    q_dir.mkdir(parents=True, exist_ok=True)

    key = (session_num, q_num)
    if key not in DIAGRAM_FUNCTIONS:
        print(f"  No custom diagrams defined for session {session_num} Q{q_num}, skipping.")
        return

    options = DIAGRAM_FUNCTIONS[key]
    for letter, func in sorted(options.items()):
        output_path = str(q_dir / f"option_{letter}")
        try:
            func(output_path)
            print(f"    Created: option_{letter}.png")
        except Exception as e:
            print(f"    ERROR creating option_{letter}.png: {e}")


def generate_all_session1_diagrams():
    """Generate all enhanced diagrams for session 1."""
    print("Generating enhanced diagrams for Session 1...")
    for q_num in range(1, 7):
        print(f"  Q{q_num}:")
        generate_diagrams_for_question_v2(1, q_num)
    print("\nDone! All session 1 diagrams regenerated.")


if __name__ == "__main__":
    generate_all_session1_diagrams()
