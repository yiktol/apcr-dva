"""
Enhanced architecture diagram generator for ALL sessions (1-5).
Creates richer, more explanatory diagrams that visually illustrate WHY
each option is correct or incorrect.
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
from diagrams.aws.network import InternetGateway, VPCPeering, Endpoint
from diagrams.aws.integration import Eventbridge, SQS, SNS, StepFunctions
from diagrams.aws.devtools import Codepipeline, Codebuild, Codedeploy, Codecommit, XRay
from diagrams.aws.security import IAM, KMS, SecretsManager, Cognito, WAF
from diagrams.aws.management import Cloudwatch, Cloudformation, SystemsManager, Cloudtrail
from diagrams.aws.analytics import KinesisDataStreams
from diagrams.aws.general import Users, Client

# Import session 1 diagrams from existing file
from generate_diagrams_v2 import DIAGRAM_FUNCTIONS as S1_FUNCTIONS

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
# SESSION 2, QUESTION 1: Lambda Layers for dependencies
# ============================================================

def s2_q1_option_a(output_path):
    """Console editor - incorrect: doesn't solve package size."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Lambda Console Editor", graph_attr=INCORRECT_CLUSTER):
            lam = Lambda("Lambda Function")
            code = Client("Inline Code\n+ Dependencies")
        code >> incorrect_edge("✗ Still exceeds\npackage size quota") >> lam


def s2_q1_option_b(output_path):
    """Additional zip - incorrect: still part of deployment package."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Deployment Package", graph_attr=INCORRECT_CLUSTER):
            zip1 = Client("App Code\n(.zip)")
            zip2 = Client("Dependencies\n(.zip)")
            lam = Lambda("Lambda Function")
        zip1 >> incorrect_edge("Combined still\nexceeds quota ✗") >> lam
        zip2 >> incorrect_edge("Included in\nsame package") >> lam


def s2_q1_option_c(output_path):
    """Environment variables - incorrect: can't store code/libraries."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Environment Variables", graph_attr=INCORRECT_CLUSTER):
            env = SystemsManager("Env Vars\n(key=value strings)")
            lam = Lambda("Lambda Function")
        env >> blocked_edge("✗ Env vars store strings\nnot libraries/code") >> lam


def s2_q1_option_d(output_path):
    """Lambda Layer - correct: separates dependencies from deployment."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("Deployment Package (small)", graph_attr=NEUTRAL_CLUSTER):
            code = Client("App Code Only\n(.zip)")
        with Cluster("✓ Lambda Layer", graph_attr=CORRECT_CLUSTER):
            layer = Lambda("Layer\n(Dependencies)")
        with Cluster("Runtime", graph_attr=NEUTRAL_CLUSTER):
            lam = Lambda("Lambda Function")
        code >> correct_edge("Under size\nquota ✓") >> lam
        layer >> correct_edge("Attached separately\n(up to 5 layers)") >> lam


# ============================================================
# SESSION 2, QUESTION 2: API Gateway stages with Lambda aliases
# ============================================================

def s2_q2_option_a(output_path):
    """Separate REST APIs - incorrect: more configuration needed."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Two Separate APIs (More Config)", graph_attr=INCORRECT_CLUSTER):
            api_dev = APIGateway("REST API\n(dev)")
            api_prod = APIGateway("REST API\n(prod)")
        with Cluster("Lambda Aliases", graph_attr=NEUTRAL_CLUSTER):
            lam_dev = Lambda("dev alias")
            lam_prod = Lambda("prod alias")
        api_dev >> incorrect_edge("Duplicate\nAPI config ✗") >> lam_dev
        api_prod >> incorrect_edge("Duplicate\nAPI config ✗") >> lam_prod


def s2_q2_option_b(output_path):
    """One API + stage variables - correct: least configuration."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✓ Single REST API", graph_attr=CORRECT_CLUSTER):
            api = APIGateway("REST API")
            stage_dev = Client("Stage: dev\n(stageVar=dev)")
            stage_prod = Client("Stage: prod\n(stageVar=prod)")
        with Cluster("Lambda Aliases", graph_attr=NEUTRAL_CLUSTER):
            lam_dev = Lambda("dev alias")
            lam_prod = Lambda("prod alias")
        api >> correct_edge("Stage variable\nroutes to alias ✓") >> stage_dev
        api >> correct_edge("") >> stage_prod
        stage_dev >> correct_edge("${stageVariables.alias}") >> lam_dev
        stage_prod >> correct_edge("${stageVariables.alias}") >> lam_prod


def s2_q2_option_c(output_path):
    """Canary with dev integration - incorrect: canary is for gradual rollout."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Canary Misuse", graph_attr=INCORRECT_CLUSTER):
            api = APIGateway("REST API")
            canary = Client("Canary Release\n(random traffic split)")
        with Cluster("Lambda", graph_attr=NEUTRAL_CLUSTER):
            lam_dev = Lambda("dev alias")
            lam_prod = Lambda("prod alias")
        api >> warning_edge("dev integration") >> lam_dev
        canary >> incorrect_edge("✗ Canary splits traffic\nrandomly, not by\nenvironment") >> lam_prod


def s2_q2_option_d(output_path):
    """Canary with prod integration - incorrect: same issue as C."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Canary Misuse", graph_attr=INCORRECT_CLUSTER):
            api = APIGateway("REST API")
            canary = Client("Canary Release\n(random traffic split)")
        with Cluster("Lambda", graph_attr=NEUTRAL_CLUSTER):
            lam_dev = Lambda("dev alias")
            lam_prod = Lambda("prod alias")
        api >> warning_edge("prod integration") >> lam_prod
        canary >> incorrect_edge("✗ Canary is for gradual\nrollout, not env\nseparation") >> lam_dev


# ============================================================
# SESSION 2, QUESTION 3: Encrypted API key storage for Lambda
# ============================================================

def s2_q3_option_a(output_path):
    """Hard-coded in source - incorrect: not secure."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Hard-coded Secret", graph_attr=INCORRECT_CLUSTER):
            code = Client("Java Source Code\n(API key in plaintext)")
            lam = Lambda("Lambda Function")
        code >> incorrect_edge("✗ Not encrypted\n✗ Visible in source\n✗ Hard to rotate") >> lam


def s2_q3_option_b(output_path):
    """EBS volume - incorrect: Lambda can't mount EBS."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Incompatible Storage", graph_attr=INCORRECT_CLUSTER):
            ebs = EBS("EBS Volume")
            lam = Lambda("Lambda Function")
        ebs >> blocked_edge("✗ Lambda cannot\nmount EBS volumes\n(EC2 only)") >> lam


def s2_q3_option_c(output_path):
    """Packaged config file - incorrect: not externalized."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Co-packaged Config", graph_attr=INCORRECT_CLUSTER):
            config = Client("config.properties\n(in deployment .zip)")
            lam = Lambda("Lambda Function")
        config >> incorrect_edge("✗ Still in artifact\n✗ Not encrypted at rest\n✗ Redeploy to change") >> lam


def s2_q3_option_d(output_path):
    """Parameter Store SecureString - correct: encrypted, externalized."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✓ Externalized & Encrypted", graph_attr=CORRECT_CLUSTER):
            ssm = SystemsManager("Parameter Store\n(SecureString)")
            kms = KMS("KMS Key\n(encryption)")
        with Cluster("Runtime", graph_attr=NEUTRAL_CLUSTER):
            lam = Lambda("Lambda Function")
            api = Client("3rd Party API")
        kms >> correct_edge("Encrypts\nat rest") >> ssm
        lam >> correct_edge("Fetches decrypted\nkey at runtime") >> ssm
        lam >> neutral_edge("Calls with\nAPI key") >> api


# ============================================================
# SESSION 3, QUESTION 1: CodeDeploy appspec.yml location
# ============================================================

def s3_q1_option_a(output_path):
    """Root of source code - correct."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✓ Application Source Bundle", graph_attr=CORRECT_CLUSTER):
            root = Client("/ (root)\n├── appspec.yml ✓\n├── scripts/\n└── src/")
        with Cluster("Deployment", graph_attr=NEUTRAL_CLUSTER):
            cd = Codedeploy("CodeDeploy")
            ec2 = EC2("EC2 Instances\n(Auto Scaling)")
        root >> correct_edge("appspec.yml found\nat root ✓") >> cd
        cd >> correct_edge("Deploys to") >> ec2


def s3_q1_option_b(output_path):
    """CodeDeploy console - incorrect: only for Lambda deployments."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Console Input", graph_attr=INCORRECT_CLUSTER):
            console = Client("CodeDeploy Console\n(inline appspec)")
        with Cluster("Target", graph_attr=NEUTRAL_CLUSTER):
            lam = Lambda("Lambda\n(console works)")
            ec2 = EC2("EC2\n(needs file)")
        console >> warning_edge("Only works for\nLambda deploys") >> lam
        console >> blocked_edge("✗ Not supported\nfor EC2 deploys") >> ec2


def s3_q1_option_c(output_path):
    """.ebextensions - incorrect: that's Elastic Beanstalk."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Wrong Service", graph_attr=INCORRECT_CLUSTER):
            eb_folder = Client(".ebextensions/\n(Elastic Beanstalk)")
        with Cluster("Actual Service Used", graph_attr=NEUTRAL_CLUSTER):
            cd = Codedeploy("CodeDeploy")
        eb_folder >> blocked_edge("✗ .ebextensions is for\nElastic Beanstalk\nnot CodeDeploy") >> cd


def s3_q1_option_d(output_path):
    """Separate from bundle - incorrect: must be in bundle."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("Application Bundle", graph_attr=NEUTRAL_CLUSTER):
            bundle = Client("src/\nscripts/")
        with Cluster("✗ Separate Location", graph_attr=INCORRECT_CLUSTER):
            spec = Client("appspec.yml\n(outside bundle)")
        with Cluster("Deployment", graph_attr=NEUTRAL_CLUSTER):
            cd = Codedeploy("CodeDeploy")
        bundle >> neutral_edge("") >> cd
        spec >> blocked_edge("✗ Must be IN the\nbundle at root level") >> cd


# ============================================================
# SESSION 3, QUESTION 2: DynamoDB client-side encryption
# ============================================================

def s3_q2_option_a(output_path):
    """DynamoDB Encryption Client + KMS - correct."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✓ Client-Side Encryption", graph_attr=CORRECT_CLUSTER):
            app = Client("Python App")
            enc_client = Client("DynamoDB\nEncryption Client")
            kms = KMS("AWS KMS\n(CMK)")
        with Cluster("Storage", graph_attr=NEUTRAL_CLUSTER):
            ddb = Dynamodb("DynamoDB\n(encrypted items)")
        app >> correct_edge("Encrypts before\nsending ✓") >> enc_client
        enc_client >> correct_edge("Uses KMS key") >> kms
        enc_client >> correct_edge("Encrypted data\nin transit & at rest") >> ddb


def s3_q2_option_b(output_path):
    """KMS without encryption client - incorrect: need client library."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Missing Encryption Client", graph_attr=INCORRECT_CLUSTER):
            app = Client("Python App")
            kms = KMS("AWS KMS")
        with Cluster("Storage", graph_attr=NEUTRAL_CLUSTER):
            ddb = Dynamodb("DynamoDB")
        app >> incorrect_edge("✗ KMS alone doesn't\nprovide client-side\nencryption for DDB") >> kms
        app >> warning_edge("Data sent\nunencrypted") >> ddb


def s3_q2_option_c(output_path):
    """DynamoDB Encryption Client - correct: end-to-end protection."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✓ End-to-End Protection", graph_attr=CORRECT_CLUSTER):
            app = Client("Python App")
            enc_client = Client("DynamoDB\nEncryption Client")
        with Cluster("Protected Data", graph_attr=NEUTRAL_CLUSTER):
            transit = Client("In Transit\n(encrypted)")
            ddb = Dynamodb("At Rest\n(encrypted)")
        app >> correct_edge("Encrypt selected\nitems/attributes") >> enc_client
        enc_client >> correct_edge("Protected\nin transit ✓") >> transit
        transit >> correct_edge("Protected\nat rest ✓") >> ddb


def s3_q2_option_d(output_path):
    """Server-side encryption - incorrect: not client-side."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Server-Side Only", graph_attr=INCORRECT_CLUSTER):
            ddb = Dynamodb("DynamoDB\n(SSE enabled)")
            kms = KMS("AWS Managed Key")
        with Cluster("Client", graph_attr=NEUTRAL_CLUSTER):
            app = Client("Python App")
        app >> incorrect_edge("✗ Data sent in\nplaintext to DDB\n(not client-side)") >> ddb
        kms >> warning_edge("Encrypts only\nat rest on server") >> ddb


def s3_q2_option_e(output_path):
    """Server-side encryption variant - incorrect: same issue."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Server-Side Only", graph_attr=INCORRECT_CLUSTER):
            ddb = Dynamodb("DynamoDB\n(SSE-KMS)")
        with Cluster("Client", graph_attr=NEUTRAL_CLUSTER):
            app = Client("Python App")
        app >> incorrect_edge("✗ Not client-side\nencryption\n✗ No end-to-end\nprotection") >> ddb


# ============================================================
# SESSION 3, QUESTION 3: DynamoDB Scan limit parameter
# ============================================================

def s3_q3_option_a(output_path):
    """Parallel scan - incorrect: returns more items, not fewer."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Parallel Scan", graph_attr=INCORRECT_CLUSTER):
            app = Client("C++ App")
            ddb = Dynamodb("DynamoDB Table")
            seg1 = Client("Segment 1")
            seg2 = Client("Segment 2")
        app >> incorrect_edge("✗ Returns MORE items\n(multiple segments\nscanned in parallel)") >> ddb
        ddb >> incorrect_edge("") >> seg1
        ddb >> incorrect_edge("") >> seg2


def s3_q3_option_b(output_path):
    """Filter expression - incorrect: filters after scan, doesn't limit count."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Filter Expression", graph_attr=INCORRECT_CLUSTER):
            app = Client("C++ App")
            ddb = Dynamodb("DynamoDB\n(full scan first)")
            filter_node = Client("Filter\n(post-scan)")
        app >> warning_edge("Scans all items\nfirst") >> ddb
        ddb >> incorrect_edge("✗ Filters AFTER read\ndoesn't limit to 1 item\nfrom scan") >> filter_node


def s3_q3_option_c(output_path):
    """Limit parameter = 1 - correct."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✓ Limit Parameter", graph_attr=CORRECT_CLUSTER):
            app = Client("C++ App")
            ddb = Dynamodb("DynamoDB\nScan(Limit=1)")
        app >> correct_edge("Scan with Limit=1\n→ returns max 1 item ✓") >> ddb


def s3_q3_option_d(output_path):
    """Page-size - incorrect: controls pagination, not total results."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Page Size", graph_attr=INCORRECT_CLUSTER):
            app = Client("C++ App")
            ddb = Dynamodb("DynamoDB")
            pages = Client("Page 1 | Page 2 | ...")
        app >> warning_edge("page-size controls\nitems per page") >> ddb
        ddb >> incorrect_edge("✗ Still returns ALL items\njust in smaller pages\n(not a limit)") >> pages


# ============================================================
# SESSION 3, QUESTION 4: Step Functions HeartbeatSeconds + Retry
# ============================================================

def s3_q4_option_a(output_path):
    """States.Timeout at machine level - incorrect: wrong level."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Wrong Configuration Level", graph_attr=INCORRECT_CLUSTER):
            sf = StepFunctions("State Machine\n(top level)")
            state = Client("Activity State")
        sf >> incorrect_edge("✗ Retry is set per-state\nnot at machine level\n✗ States.Timeout is an\nerror name, not a field") >> state


def s3_q4_option_b(output_path):
    """States.TaskFailed - incorrect: error name, not a field."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Incorrect Field", graph_attr=INCORRECT_CLUSTER):
            state = Client("Activity State")
            err = Client("States.TaskFailed\n(error name)")
        state >> incorrect_edge("✗ States.TaskFailed is\nan error name\nnot a configurable field") >> err


def s3_q4_option_c(output_path):
    """TimeoutSeconds=30 - incorrect: kills long-running tasks."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ TimeoutSeconds = 30", graph_attr=INCORRECT_CLUSTER):
            state = Client("Activity State\n(long-running)")
            timeout = Client("TIMEOUT!")
        state >> incorrect_edge("✗ Kills task after 30s\nLong-running tasks\nwill always fail!") >> timeout


def s3_q4_option_d(output_path):
    """HeartbeatSeconds + Retry maxAttempts=3 - correct."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✓ HeartbeatSeconds + Retry", graph_attr=CORRECT_CLUSTER):
            state = Client("Activity State")
            hb = Client("HeartbeatSeconds\n(detect dead worker)")
            retry = Client("Retry\n(maxAttempts=3)")
        with Cluster("Workers", graph_attr=NEUTRAL_CLUSTER):
            tablet = Client("Tablet Worker")
        tablet >> correct_edge("Sends heartbeat\nperiodically") >> state
        state >> correct_edge("No heartbeat?\nReassign task ✓") >> hb
        hb >> correct_edge("Retry up to 3x\nthen fail ✓") >> retry


# ============================================================
# SESSION 3, QUESTION 5: Right database (DynamoDB + DAX)
# ============================================================

def s3_q5_option_a(output_path):
    """Aurora - incorrect: relational, not key-value, not microsecond."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Wrong Database Type", graph_attr=INCORRECT_CLUSTER):
            aurora = RDS("Aurora\n(Relational DB)")
        with Cluster("Requirements", graph_attr=NEUTRAL_CLUSTER):
            req = Client("Key-value store\nMicrosecond latency")
        aurora >> incorrect_edge("✗ Relational, not key-value\n✗ Cannot achieve\nmicrosecond latency") >> req


def s3_q5_option_b(output_path):
    """DynamoDB + DAX - correct: key-value with microsecond latency."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✓ Key-Value + Microsecond Cache", graph_attr=CORRECT_CLUSTER):
            app = Client("Application")
            dax = ElastiCache("DAX\n(in-memory cache)")
            ddb = Dynamodb("DynamoDB\n(key-value)")
        app >> correct_edge("Microsecond\nresponse ✓") >> dax
        dax >> correct_edge("Cache miss →\nread from DDB") >> ddb


def s3_q5_option_c(output_path):
    """Aurora + ElastiCache - incorrect: still relational."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Wrong DB Type + Cache", graph_attr=INCORRECT_CLUSTER):
            cache = ElastiCache("ElastiCache")
            aurora = RDS("Aurora\n(Relational)")
        with Cluster("Requirement", graph_attr=NEUTRAL_CLUSTER):
            req = Client("Key-value store")
        cache >> warning_edge("Cache helps latency\nbut...") >> aurora
        aurora >> incorrect_edge("✗ Still relational\nnot key-value") >> req


def s3_q5_option_d(output_path):
    """Neptune - incorrect: graph database."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Wrong Database Type", graph_attr=INCORRECT_CLUSTER):
            neptune = Neptune("Neptune\n(Graph DB)")
        with Cluster("Requirement", graph_attr=NEUTRAL_CLUSTER):
            req = Client("Key-value store\nMicrosecond latency")
        neptune >> incorrect_edge("✗ Graph database\n✗ For connected data\n✗ Not key-value") >> req


# ============================================================
# SESSION 4, QUESTION 1: X-Ray for microservice latency
# ============================================================

def s4_q1_option_a(output_path):
    """X-Ray - correct: traces requests across microservices."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✓ AWS X-Ray Service Map", graph_attr=CORRECT_CLUSTER):
            xray = XRay("X-Ray")
        with Cluster("Microservices", graph_attr=NEUTRAL_CLUSTER):
            svc1 = Lambda("Service A")
            svc2 = Lambda("Service B")
            svc3 = Lambda("Service C\n(slow!)")
        svc1 >> correct_edge("Trace") >> xray
        svc2 >> correct_edge("Trace") >> xray
        svc3 >> correct_edge("Identifies\nslow service ✓") >> xray


def s4_q1_option_b(output_path):
    """CloudTrail - incorrect: API audit, not performance tracing."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Wrong Tool", graph_attr=INCORRECT_CLUSTER):
            ct = Cloudtrail("CloudTrail\n(API audit log)")
        with Cluster("What's needed", graph_attr=NEUTRAL_CLUSTER):
            perf = Client("Performance\nTracing")
        ct >> incorrect_edge("✗ Records API calls\nfor compliance/audit\n✗ Not for latency\nanalysis") >> perf


def s4_q1_option_c(output_path):
    """EventBridge - incorrect: event routing, not tracing."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Wrong Tool", graph_attr=INCORRECT_CLUSTER):
            eb = Eventbridge("EventBridge\n(event bus)")
        with Cluster("What's needed", graph_attr=NEUTRAL_CLUSTER):
            perf = Client("Latency\nIdentification")
        eb >> incorrect_edge("✗ Routes events between\nservices\n✗ Not a tracing/\nperformance tool") >> perf


def s4_q1_option_d(output_path):
    """Trusted Advisor - incorrect: best practices, not tracing."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Wrong Tool", graph_attr=INCORRECT_CLUSTER):
            ta = Client("Trusted Advisor\n(best practices)")
        with Cluster("What's needed", graph_attr=NEUTRAL_CLUSTER):
            perf = Client("Service-level\nLatency Tracing")
        ta >> incorrect_edge("✗ Checks AWS best practices\n(cost, security, limits)\n✗ Cannot trace individual\nrequest latency") >> perf


# ============================================================
# SESSION 4, QUESTION 2: Session state across devices (ElastiCache)
# ============================================================

def s4_q2_option_a(output_path):
    """Sticky sessions - incorrect: doesn't work across devices."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Sticky Sessions", graph_attr=INCORRECT_CLUSTER):
            laptop = Client("Laptop\n(cookie A)")
            phone = Client("Phone\n(cookie B)")
            alb = ELB("ALB\n(sticky)")
        with Cluster("EC2 Instances", graph_attr=NEUTRAL_CLUSTER):
            ec2a = EC2("Instance A")
            ec2b = EC2("Instance B")
        laptop >> incorrect_edge("Cookie tied\nto Instance A") >> alb
        phone >> incorrect_edge("Different cookie!\n✗ Different instance\n✗ No shared state") >> alb
        alb >> warning_edge("") >> ec2a
        alb >> warning_edge("") >> ec2b


def s4_q2_option_b(output_path):
    """ElastiCache Redis - correct: shared session store."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("Clients", graph_attr=SOURCE_CLUSTER):
            laptop = Client("Laptop")
            phone = Client("Phone")
        with Cluster("Application Tier", graph_attr=NEUTRAL_CLUSTER):
            alb = ELB("ALB")
            ec2 = EC2("EC2 (ASG)")
        with Cluster("✓ Shared Session Store", graph_attr=CORRECT_CLUSTER):
            redis = ElastiCache("ElastiCache\nRedis")
        laptop >> neutral_edge("") >> alb
        phone >> neutral_edge("") >> alb
        alb >> neutral_edge("") >> ec2
        ec2 >> correct_edge("Read/write session\n(shared across all\ninstances & devices) ✓") >> redis


def s4_q2_option_c(output_path):
    """Local file - incorrect: not shared across instances."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Local Storage", graph_attr=INCORRECT_CLUSTER):
            ec2a = EC2("Instance A\n(local file)")
            ec2b = EC2("Instance B\n(no file!)")
        with Cluster("Clients", graph_attr=SOURCE_CLUSTER):
            phone = Client("Phone")
        phone >> incorrect_edge("✗ Routed to Instance B\n✗ Session file only\non Instance A") >> ec2b


def s4_q2_option_d(output_path):
    """Systems Manager State Manager - incorrect: wrong service."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Wrong Service", graph_attr=INCORRECT_CLUSTER):
            ssm = SystemsManager("State Manager\n(infra config)")
        with Cluster("What's needed", graph_attr=NEUTRAL_CLUSTER):
            session = Client("User Session\nState")
        ssm >> incorrect_edge("✗ Manages EC2 instance\nconfiguration state\n✗ Not user session data") >> session


# ============================================================
# SESSION 4, QUESTION 3: Lambda versions + aliases for dev/prod
# ============================================================

def s4_q3_option_a(output_path):
    """Lambda layer - incorrect: for shared code, not versioning."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Lambda Layer", graph_attr=INCORRECT_CLUSTER):
            layer = Lambda("Layer\n(shared libraries)")
            lam = Lambda("Lambda Function")
        layer >> incorrect_edge("✗ Layers are for\nshared dependencies\n✗ Not for code versioning") >> lam


def s4_q3_option_b(output_path):
    """Lambda versions - correct: immutable snapshots of code."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✓ Lambda Versions", graph_attr=CORRECT_CLUSTER):
            lam = Lambda("Lambda Function")
            v1 = Client("Version 1\n(stable)")
            v2 = Client("Version 2\n(new code)")
        lam >> correct_edge("Publish\nimmutable snapshot ✓") >> v1
        lam >> correct_edge("Latest changes") >> v2


def s4_q3_option_c(output_path):
    """Layer + alias to layer - incorrect: alias can't point to layer."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Invalid Configuration", graph_attr=INCORRECT_CLUSTER):
            layer = Lambda("Lambda Layer")
            alias = Client("Alias")
        alias >> blocked_edge("✗ Alias cannot point\nto a layer\n✗ Only points to\nfunction versions") >> layer


def s4_q3_option_d(output_path):
    """Aliases for prod/dev - correct: pointer to specific version."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✓ Lambda Aliases", graph_attr=CORRECT_CLUSTER):
            prod_alias = Client("Alias: prod\n→ Version 5")
            dev_alias = Client("Alias: dev\n→ Version 7")
        with Cluster("Versions", graph_attr=NEUTRAL_CLUSTER):
            v5 = Lambda("Version 5\n(stable)")
            v7 = Lambda("Version 7\n(latest)")
        prod_alias >> correct_edge("Points to\nstable version ✓") >> v5
        dev_alias >> correct_edge("Points to\nlatest version ✓") >> v7


def s4_q3_option_e(output_path):
    """Alias to unqualified ARN + LAMBDA_TASK_ROOT - incorrect."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Invalid Setup", graph_attr=INCORRECT_CLUSTER):
            alias = Client("Alias")
            arn = Client("Unqualified ARN\n($LATEST)")
            env = Client("LAMBDA_TASK_ROOT\n(internal path var)")
        alias >> incorrect_edge("✗ Points to $LATEST\n(not a specific version)") >> arn
        env >> blocked_edge("✗ Internal runtime var\nnot for versioning") >> alias


# ============================================================
# SESSION 4, QUESTION 4: DynamoDB Streams + Lambda to external API
# ============================================================

def s4_q4_option_a(output_path):
    """Enable DynamoDB Streams - correct."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✓ DynamoDB Streams", graph_attr=CORRECT_CLUSTER):
            ddb = Dynamodb("DynamoDB Table")
            stream = KinesisDataStreams("DynamoDB\nStream")
        with Cluster("Processing", graph_attr=NEUTRAL_CLUSTER):
            lam = Lambda("Lambda")
            api = Client("External API")
        ddb >> correct_edge("Change captured\nin stream ✓") >> stream
        stream >> correct_edge("Triggers Lambda") >> lam
        lam >> correct_edge("Sends to\nexternal API") >> api


def s4_q4_option_b(output_path):
    """EventBridge - incorrect: can't detect DynamoDB changes."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ EventBridge", graph_attr=INCORRECT_CLUSTER):
            eb = Eventbridge("EventBridge")
            ddb = Dynamodb("DynamoDB")
        eb >> blocked_edge("✗ Cannot detect\nDynamoDB item changes\n(no native integration)") >> ddb


def s4_q4_option_c(output_path):
    """Trigger on table - incorrect: need stream first."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Missing Stream", graph_attr=INCORRECT_CLUSTER):
            ddb = Dynamodb("DynamoDB Table\n(no stream)")
            lam = Lambda("Lambda\n(trigger)")
        ddb >> blocked_edge("✗ Cannot create trigger\ndirectly on table\n✗ Must enable DynamoDB\nStreams first") >> lam


def s4_q4_option_d(output_path):
    """Stream to create SNS topic - incorrect: streams don't create topics."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Invalid Flow", graph_attr=INCORRECT_CLUSTER):
            stream = KinesisDataStreams("DynamoDB Stream")
            sns = SNS("SNS Topic")
        stream >> blocked_edge("✗ Streams cannot\ncreate SNS topics\n✗ Stream triggers Lambda\nnot SNS directly") >> sns


def s4_q4_option_e(output_path):
    """Enable DynamoDB Streams + Lambda - correct."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✓ Stream + Lambda Pattern", graph_attr=CORRECT_CLUSTER):
            ddb = Dynamodb("DynamoDB")
            stream = KinesisDataStreams("Stream")
            lam = Lambda("Lambda")
        with Cluster("External", graph_attr=NEUTRAL_CLUSTER):
            api = Client("External API")
        ddb >> correct_edge("Enable stream ✓") >> stream
        stream >> correct_edge("Invoke Lambda ✓") >> lam
        lam >> correct_edge("Call API") >> api


# ============================================================
# SESSION 4, QUESTION 5: Lambda alias for event source mappings
# ============================================================

def s4_q5_option_a(output_path):
    """Layer ARN - incorrect: event source can't point to layer."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Invalid Target", graph_attr=INCORRECT_CLUSTER):
            esm = Client("Event Source\nMapping")
            layer = Lambda("Layer ARN")
        esm >> blocked_edge("✗ Event source mapping\ncannot point to\na layer ARN") >> layer


def s4_q5_option_b(output_path):
    """Create alias - correct: stable pointer to version."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✓ Lambda Alias", graph_attr=CORRECT_CLUSTER):
            alias = Client("Alias: live\n(stable ARN)")
            v1 = Lambda("Version N")
            v2 = Lambda("Version N+1")
        alias >> correct_edge("Points to\ncurrent version") >> v1
        alias >> correct_edge("Update alias\n(no ESM change) ✓") >> v2


def s4_q5_option_c(output_path):
    """New alias per version - incorrect: still need to update ESM."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ New Alias Each Time", graph_attr=INCORRECT_CLUSTER):
            a1 = Client("Alias: v1-alias")
            a2 = Client("Alias: v2-alias")
            esm = Client("Event Source\nMapping")
        esm >> incorrect_edge("✗ Each alias has\nunique ARN\n✗ Still must update\nESM each time") >> a1
        esm >> incorrect_edge("") >> a2


def s4_q5_option_d(output_path):
    """Alias pointing to alias - incorrect: not supported."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Invalid Configuration", graph_attr=INCORRECT_CLUSTER):
            alias1 = Client("Alias A")
            alias2 = Client("Alias B")
        alias1 >> blocked_edge("✗ An alias cannot\npoint to another alias\n(only to versions)") >> alias2


def s4_q5_option_e(output_path):
    """Use alias ARN in event source mapping - correct."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✓ Alias ARN in ESM", graph_attr=CORRECT_CLUSTER):
            esm = Client("Event Source\nMapping")
            alias = Client("Alias ARN\n(never changes)")
        with Cluster("Versions (updated behind alias)", graph_attr=NEUTRAL_CLUSTER):
            v1 = Lambda("Version 1")
            v2 = Lambda("Version 2")
        esm >> correct_edge("Points to alias ARN\n(stable, no updates\nneeded) ✓") >> alias
        alias >> neutral_edge("Resolves to\ncurrent version") >> v2


# ============================================================
# SESSION 5, QUESTION 1: S3 event-driven processing (same as S1Q2)
# ============================================================

def s5_q1_option_a(output_path):
    """EFS + Lambda - incorrect: no event trigger."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("Fulfillment System", graph_attr=SOURCE_CLUSTER):
            source = Client("JSON Files")
        with Cluster("✗ No Event Trigger", graph_attr=INCORRECT_CLUSTER):
            efs = EFS("EFS")
            lam = Lambda("Lambda")
        source >> warning_edge("Upload") >> efs
        efs >> blocked_edge("✗ EFS changes cannot\ninvoke Lambda") >> lam


def s5_q1_option_b(output_path):
    """EFS + scheduled Lambda - incorrect: polling delay."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("Fulfillment System", graph_attr=SOURCE_CLUSTER):
            source = Client("JSON Files")
        with Cluster("✗ Scheduled (Delayed)", graph_attr=INCORRECT_CLUSTER):
            efs = EFS("EFS")
            cw = Cloudwatch("Schedule\n(hourly)")
            lam = Lambda("Lambda")
        source >> warning_edge("Upload") >> efs
        cw >> incorrect_edge("✗ Up to 60 min delay\n✗ Not 'as soon as\nthey arrive'") >> lam


def s5_q1_option_c(output_path):
    """S3 + Lambda event - correct."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("Fulfillment System", graph_attr=SOURCE_CLUSTER):
            source = Client("JSON Files")
        with Cluster("✓ Event-Driven", graph_attr=CORRECT_CLUSTER):
            s3 = S3("S3 Bucket")
            lam = Lambda("Lambda")
        source >> correct_edge("Upload JSON") >> s3
        s3 >> correct_edge("S3 Event →\nimmediate trigger ✓") >> lam


def s5_q1_option_d(output_path):
    """S3 + scheduled Lambda - incorrect: right storage, wrong trigger."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("Fulfillment System", graph_attr=SOURCE_CLUSTER):
            source = Client("JSON Files")
        with Cluster("✗ Scheduled (Delayed)", graph_attr=INCORRECT_CLUSTER):
            s3 = S3("S3 Bucket ✓")
            cw = Cloudwatch("Schedule\n(hourly)")
            lam = Lambda("Lambda")
        source >> correct_edge("Upload") >> s3
        cw >> incorrect_edge("✗ Should use S3 events\nnot polling schedule") >> lam


# ============================================================
# SESSION 5, QUESTION 2: Lambda DB connection reuse
# ============================================================

def s5_q2_option_a(output_path):
    """Env var for connection string - incorrect: still re-initializes."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Connection in Handler", graph_attr=INCORRECT_CLUSTER):
            lam = Lambda("Lambda Handler\n(init connection\neach invocation)")
            env = Client("Env Var\n(connection string)")
            db = RDS("RDS")
        env >> warning_edge("Has the string\nbut...") >> lam
        lam >> incorrect_edge("✗ New JDBC connection\nevery invocation\n(latency!)") >> db


def s5_q2_option_b(output_path):
    """Init outside handler - correct: reused across invocations."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✓ Connection Outside Handler", graph_attr=CORRECT_CLUSTER):
            init = Client("Init Phase\n(module level)")
            conn = Client("DB Connection\n(reused!)")
        with Cluster("Invocations", graph_attr=NEUTRAL_CLUSTER):
            lam1 = Lambda("Invocation 1")
            lam2 = Lambda("Invocation 2")
        with Cluster("Database", graph_attr=NEUTRAL_CLUSTER):
            db = RDS("RDS")
        init >> correct_edge("Create connection\nonce ✓") >> conn
        conn >> correct_edge("Reused across\nwarm invocations ✓") >> lam1
        conn >> correct_edge("") >> lam2
        conn >> neutral_edge("Single JDBC\nconnection") >> db


def s5_q2_option_c(output_path):
    """Parameter Store + handler init - incorrect: still re-initializes."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Connection in Handler", graph_attr=INCORRECT_CLUSTER):
            ssm = SystemsManager("Parameter Store")
            lam = Lambda("Handler\n(init each time)")
            db = RDS("RDS")
        ssm >> warning_edge("Fetches config") >> lam
        lam >> incorrect_edge("✗ New connection\neach invocation\n(handler = per-call)") >> db


def s5_q2_option_d(output_path):
    """Init in handler - incorrect: re-creates every time."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Handler-Level Init", graph_attr=INCORRECT_CLUSTER):
            lam = Lambda("Handler Function\n(runs every call)")
            conn = Client("New Connection\n(every time!)")
        with Cluster("Database", graph_attr=NEUTRAL_CLUSTER):
            db = RDS("RDS")
        lam >> incorrect_edge("✗ Creates new JDBC\nconnection per invocation\n✗ Cold start latency\nevery time") >> conn
        conn >> warning_edge("") >> db


# ============================================================
# SESSION 5, QUESTION 3: IAM role permissions for DynamoDB
# ============================================================

def s5_q3_option_a(output_path):
    """Assume another role - incorrect: can only have one role."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Multiple Roles", graph_attr=INCORRECT_CLUSTER):
            ec2 = EC2("EC2 Instance")
            role1 = IAM("myRole\n(current)")
            role2 = IAM("New Role")
        ec2 >> incorrect_edge("✗ EC2 can only\nassume ONE role\nat a time") >> role1
        ec2 >> blocked_edge("✗ Cannot assume\nsecond role") >> role2


def s5_q3_option_b(output_path):
    """Add DynamoDB policy to existing role - correct."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✓ Add Policy to Existing Role", graph_attr=CORRECT_CLUSTER):
            role = IAM("myRole")
            policy = Client("DynamoDB\nAccess Policy")
        with Cluster("Resources", graph_attr=NEUTRAL_CLUSTER):
            ec2 = EC2("EC2 Instance")
            ddb = Dynamodb("DynamoDB")
        policy >> correct_edge("Attach policy\nto role ✓") >> role
        ec2 >> correct_edge("Uses myRole") >> role
        role >> correct_edge("Now has DynamoDB\npermissions ✓") >> ddb


def s5_q3_option_c(output_path):
    """Update credentials - incorrect: it's an auth error, not authn."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Wrong Fix", graph_attr=INCORRECT_CLUSTER):
            creds = Client("AWS Credentials\n(access keys)")
            ec2 = EC2("EC2 Instance")
        ec2 >> incorrect_edge("✗ AccessDenied = authorization\nnot authentication\n✗ Credentials are fine\n✗ Permissions are missing") >> creds


def s5_q3_option_d(output_path):
    """Rotate access keys - incorrect: same issue as C."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Wrong Fix", graph_attr=INCORRECT_CLUSTER):
            keys = Client("Access Keys\n(rotate)")
            ec2 = EC2("EC2 Instance")
        ec2 >> incorrect_edge("✗ AccessDenied ≠ bad keys\n✗ It's a PERMISSION issue\n✗ Role needs DynamoDB\npolicy attached") >> keys


# ============================================================
# SESSION 5, QUESTION 4: X-Ray for API Gateway microservices
# ============================================================

def s5_q4_option_a(output_path):
    """CloudWatch metrics - incorrect: too time-consuming."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Manual Metric Analysis", graph_attr=INCORRECT_CLUSTER):
            cw = Cloudwatch("CloudWatch\nMetrics")
            svc = Client("20+ Services\n(compare each)")
        cw >> incorrect_edge("✗ Time-consuming to\ncompare metrics across\n20+ services manually") >> svc


def s5_q4_option_b(output_path):
    """CloudWatch Logs - incorrect: not structured for tracing."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Log Analysis", graph_attr=INCORRECT_CLUSTER):
            logs = Cloudwatch("CloudWatch\nLogs")
            svc = Client("20+ Services\n(different log formats)")
        logs >> incorrect_edge("✗ Time-consuming\n✗ App-specific formats\n✗ Not all services\nsend logs") >> svc


def s5_q4_option_c(output_path):
    """X-Ray - correct: visual service map with latency."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✓ X-Ray Service Map", graph_attr=CORRECT_CLUSTER):
            xray = XRay("X-Ray")
        with Cluster("20+ Microservices", graph_attr=NEUTRAL_CLUSTER):
            api = APIGateway("API Gateway")
            svc1 = Lambda("Service A")
            svc2 = Lambda("Service B\n(SLOW)")
            svc3 = Lambda("Service C")
        api >> correct_edge("Trace") >> xray
        svc1 >> correct_edge("") >> xray
        svc2 >> correct_edge("Quickly identifies\nslow service ✓") >> xray
        svc3 >> correct_edge("") >> xray


def s5_q4_option_d(output_path):
    """CloudTrail - incorrect: API audit, not performance."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Wrong Tool", graph_attr=INCORRECT_CLUSTER):
            ct = Cloudtrail("CloudTrail\n(API audit)")
        ct >> incorrect_edge("✗ Records API calls\nfor governance/compliance\n✗ Not for identifying\nperformance bottlenecks") >> Client("Performance\nAnalysis")


# ============================================================
# SESSION 5, QUESTION 5: SAM deploy working directory
# ============================================================

def s5_q5_option_a(output_path):
    """Create subfolder - incorrect: template is in build output."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Wrong Fix", graph_attr=INCORRECT_CLUSTER):
            folder = Client("aws-sam/\nsubfolder")
            template = Client("template.yaml")
        folder >> incorrect_edge("✗ sam deploy looks in\ncurrent directory or\n.aws-sam/build/\n✗ Creating subfolder\ndoesn't help") >> template


def s5_q5_option_b(output_path):
    """Copy template - incorrect: build output has it."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Unnecessary Copy", graph_attr=INCORRECT_CLUSTER):
            src = Client("template.yaml\n(source)")
            dest = Client("aws-sam/\ntemplate.yaml")
        src >> incorrect_edge("✗ sam build already\ncreates output in\n.aws-sam/build/\n✗ Just cd to right dir") >> dest


def s5_q5_option_c(output_path):
    """Change to build directory - correct."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✓ Correct Working Directory", graph_attr=CORRECT_CLUSTER):
            build_dir = Client("cd to app root\n(where sam build ran)")
            sam = Client("sam deploy\n(finds .aws-sam/build/\ntemplate.yaml)")
        build_dir >> correct_edge("sam deploy looks for\ntemplate in current dir\nor .aws-sam/build/ ✓") >> sam


def s5_q5_option_d(output_path):
    """Rerun sam build - incorrect: build succeeded already."""
    with Diagram("", filename=output_path, show=False, direction="LR", graph_attr=GRAPH_ATTR, outformat="png"):
        with Cluster("✗ Unnecessary Rebuild", graph_attr=INCORRECT_CLUSTER):
            build = Client("sam build\n(already succeeded!)")
            deploy = Client("sam deploy")
        build >> incorrect_edge("✗ Build already worked\n✗ Issue is working\ndirectory, not build\n✗ Just cd to right path") >> deploy


# ============================================================
# Dispatch table for ALL sessions
# ============================================================

DIAGRAM_FUNCTIONS = {}
DIAGRAM_FUNCTIONS.update(S1_FUNCTIONS)

DIAGRAM_FUNCTIONS.update({
    (2, 1): {"a": s2_q1_option_a, "b": s2_q1_option_b, "c": s2_q1_option_c, "d": s2_q1_option_d},
    (2, 2): {"a": s2_q2_option_a, "b": s2_q2_option_b, "c": s2_q2_option_c, "d": s2_q2_option_d},
    (2, 3): {"a": s2_q3_option_a, "b": s2_q3_option_b, "c": s2_q3_option_c, "d": s2_q3_option_d},
    (3, 1): {"a": s3_q1_option_a, "b": s3_q1_option_b, "c": s3_q1_option_c, "d": s3_q1_option_d},
    (3, 2): {"a": s3_q2_option_a, "b": s3_q2_option_b, "c": s3_q2_option_c, "d": s3_q2_option_d, "e": s3_q2_option_e},
    (3, 3): {"a": s3_q3_option_a, "b": s3_q3_option_b, "c": s3_q3_option_c, "d": s3_q3_option_d},
    (3, 4): {"a": s3_q4_option_a, "b": s3_q4_option_b, "c": s3_q4_option_c, "d": s3_q4_option_d},
    (3, 5): {"a": s3_q5_option_a, "b": s3_q5_option_b, "c": s3_q5_option_c, "d": s3_q5_option_d},
    (4, 1): {"a": s4_q1_option_a, "b": s4_q1_option_b, "c": s4_q1_option_c, "d": s4_q1_option_d},
    (4, 2): {"a": s4_q2_option_a, "b": s4_q2_option_b, "c": s4_q2_option_c, "d": s4_q2_option_d},
    (4, 3): {"a": s4_q3_option_a, "b": s4_q3_option_b, "c": s4_q3_option_c, "d": s4_q3_option_d, "e": s4_q3_option_e},
    (4, 4): {"a": s4_q4_option_a, "b": s4_q4_option_b, "c": s4_q4_option_c, "d": s4_q4_option_d, "e": s4_q4_option_e},
    (4, 5): {"a": s4_q5_option_a, "b": s4_q5_option_b, "c": s4_q5_option_c, "d": s4_q5_option_d, "e": s4_q5_option_e},
    (5, 1): {"a": s5_q1_option_a, "b": s5_q1_option_b, "c": s5_q1_option_c, "d": s5_q1_option_d},
    (5, 2): {"a": s5_q2_option_a, "b": s5_q2_option_b, "c": s5_q2_option_c, "d": s5_q2_option_d},
    (5, 3): {"a": s5_q3_option_a, "b": s5_q3_option_b, "c": s5_q3_option_c, "d": s5_q3_option_d},
    (5, 4): {"a": s5_q4_option_a, "b": s5_q4_option_b, "c": s5_q4_option_c, "d": s5_q4_option_d},
    (5, 5): {"a": s5_q5_option_a, "b": s5_q5_option_b, "c": s5_q5_option_c, "d": s5_q5_option_d},
})


def generate_diagrams_for_question(session_num: int, q_num: int):
    """Generate enhanced diagrams for all options of a question."""
    q_dir = Path(f"session{session_num}/exam-strategy/q{q_num}")
    q_dir.mkdir(parents=True, exist_ok=True)

    key = (session_num, q_num)
    if key not in DIAGRAM_FUNCTIONS:
        print(f"  No custom diagrams defined for session {session_num} Q{q_num}")
        return

    options = DIAGRAM_FUNCTIONS[key]
    for letter, func in sorted(options.items()):
        output_path = str(q_dir / f"option_{letter}")
        try:
            func(output_path)
            print(f"    Created: option_{letter}.png")
        except Exception as e:
            print(f"    ERROR creating option_{letter}.png: {e}")


def generate_all_diagrams():
    """Generate all enhanced diagrams for all sessions."""
    with open("extracted_questions.json") as f:
        sessions = json.load(f)

    for session_str, questions in sessions.items():
        session_num = int(session_str)
        print(f"\n=== Session {session_num} ({len(questions)} questions) ===")
        for q in questions:
            q_num = q["number"]
            print(f"  Q{q_num}:")
            generate_diagrams_for_question(session_num, q_num)

    print("\nAll diagrams generated!")


if __name__ == "__main__":
    generate_all_diagrams()
