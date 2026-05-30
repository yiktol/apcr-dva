"""
Generate architecture diagrams for each option of each question.
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


# Graph attributes for consistent styling
GRAPH_ATTR = {
    "fontsize": "14",
    "bgcolor": "#fafafa",
    "pad": "0.8",
    "splines": "spline",
    "nodesep": "1.0",
    "ranksep": "1.0",
    "fontname": "Helvetica",
}

# Cluster styles
CORRECT_CLUSTER = {"bgcolor": "#e8f5e9", "pencolor": "#2e7d32", "style": "rounded"}
INCORRECT_CLUSTER = {"bgcolor": "#fbe9e7", "pencolor": "#c62828", "style": "rounded"}
NEUTRAL_CLUSTER = {"bgcolor": "#e3f2fd", "pencolor": "#1565c0", "style": "rounded"}
SOURCE_CLUSTER = {"bgcolor": "#fff3e0", "pencolor": "#e65100", "style": "rounded"}

# Edge styles
CORRECT_EDGE = Edge(color="#2e7d32", style="bold", penwidth="2.0")
INCORRECT_EDGE = Edge(color="#c62828", style="bold", penwidth="2.0")
BLOCKED_EDGE = Edge(color="#c62828", style="dashed", penwidth="2.0")
WARNING_EDGE = Edge(color="#e65100", style="bold", penwidth="1.5")


def get_service_node(service_name: str):
    """Map a service name to its diagrams node class."""
    mapping = {
        "lambda": Lambda,
        "aws lambda": Lambda,
        "ec2": EC2,
        "elastic beanstalk": ElasticBeanstalk,
        "beanstalk": ElasticBeanstalk,
        "ecs": ECS,
        "fargate": Fargate,
        "s3": S3,
        "amazon s3": S3,
        "efs": EFS,
        "amazon efs": EFS,
        "ebs": EBS,
        "dynamodb": Dynamodb,
        "amazon dynamodb": Dynamodb,
        "rds": RDS,
        "amazon rds": RDS,
        "elasticache": ElastiCache,
        "neptune": Neptune,
        "aurora": RDS,
        "vpc": VPC,
        "nat gateway": NATGateway,
        "cloudfront": CloudFront,
        "elb": ELB,
        "alb": ELB,
        "api gateway": APIGateway,
        "amazon api gateway": APIGateway,
        "route53": Route53,
        "eventbridge": Eventbridge,
        "sqs": SQS,
        "sns": SNS,
        "step functions": StepFunctions,
        "codepipeline": Codepipeline,
        "codebuild": Codebuild,
        "codedeploy": Codedeploy,
        "codecommit": Codecommit,
        "x-ray": XRay,
        "xray": XRay,
        "iam": IAM,
        "kms": KMS,
        "secrets manager": SecretsManager,
        "cognito": Cognito,
        "waf": WAF,
        "cloudwatch": Cloudwatch,
        "cloudformation": Cloudformation,
        "systems manager": SystemsManager,
        "parameter store": SystemsManager,
        "cloudtrail": Cloudtrail,
        "kinesis": KinesisDataStreams,
        "users": Users,
        "client": Client,
    }
    key = service_name.lower().strip()
    return mapping.get(key, Lambda)  # Default to Lambda if unknown


def detect_services(text: str) -> list[str]:
    """Detect AWS services mentioned in text."""
    services = []
    patterns = [
        (r'API Gateway', 'api gateway'),
        (r'Lambda', 'lambda'),
        (r'DynamoDB', 'dynamodb'),
        (r'S3\b', 's3'),
        (r'EFS|Elastic File System', 'efs'),
        (r'EBS|Elastic Block Store', 'ebs'),
        (r'EC2', 'ec2'),
        (r'VPC', 'vpc'),
        (r'NAT Gateway', 'nat gateway'),
        (r'CloudFront', 'cloudfront'),
        (r'ELB|Load Balancer|ALB', 'elb'),
        (r'Route\s*53', 'route53'),
        (r'EventBridge', 'eventbridge'),
        (r'SQS', 'sqs'),
        (r'SNS', 'sns'),
        (r'Step Functions', 'step functions'),
        (r'CodePipeline', 'codepipeline'),
        (r'CodeBuild', 'codebuild'),
        (r'CodeDeploy', 'codedeploy'),
        (r'CodeCommit', 'codecommit'),
        (r'X-Ray|X Ray|XRay', 'xray'),
        (r'IAM', 'iam'),
        (r'KMS', 'kms'),
        (r'Secrets Manager', 'secrets manager'),
        (r'Cognito', 'cognito'),
        (r'WAF', 'waf'),
        (r'CloudWatch', 'cloudwatch'),
        (r'CloudFormation', 'cloudformation'),
        (r'Systems Manager|Parameter Store', 'parameter store'),
        (r'CloudTrail', 'cloudtrail'),
        (r'Kinesis', 'kinesis'),
        (r'ElastiCache|Redis', 'elasticache'),
        (r'RDS', 'rds'),
        (r'Aurora', 'aurora'),
        (r'Neptune', 'neptune'),
        (r'Elastic Beanstalk|Beanstalk', 'elastic beanstalk'),
        (r'ECS', 'ecs'),
        (r'Fargate', 'fargate'),
        (r'DAX', 'dynamodb'),
    ]

    for pattern, service in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            if service not in services:
                services.append(service)

    return services if services else ['lambda']


def create_diagram_for_option(
    question: dict,
    letter: str,
    output_path: str,
    is_correct: bool
):
    """Create a single architecture diagram for one option."""
    option = question["options"][letter]
    option_text = option["text"] + " " + option["explanation"]
    question_text = question["question"]

    # Detect services from option text and question context
    services = detect_services(option_text)
    if len(services) < 2:
        # Also check question text for context
        q_services = detect_services(question_text)
        for s in q_services:
            if s not in services:
                services.append(s)
                if len(services) >= 4:
                    break

    # Limit to 5 services max for readability
    services = services[:5]

    # Create the diagram
    cluster_style = CORRECT_CLUSTER if is_correct else INCORRECT_CLUSTER
    status_label = "✓ Correct" if is_correct else "✗ Incorrect"

    with Diagram(
        "",
        filename=output_path.replace(".png", ""),
        show=False,
        direction="LR",
        graph_attr=GRAPH_ATTR,
        outformat="png",
    ):
        # Create nodes
        nodes = []
        with Cluster(f"Option {letter}: {status_label}", graph_attr=cluster_style):
            for svc in services:
                node_class = get_service_node(svc)
                label = svc.replace("amazon ", "").title()
                nodes.append(node_class(label))

        # Connect nodes in sequence with appropriate edge style
        edge = CORRECT_EDGE if is_correct else INCORRECT_EDGE
        for i in range(len(nodes) - 1):
            nodes[i] >> edge >> nodes[i + 1]


def generate_diagrams_for_question(question: dict, session_num: int, q_num: int):
    """Generate diagrams for all options of a question."""
    q_dir = Path(f"session{session_num}/exam-strategy/q{q_num}")
    q_dir.mkdir(parents=True, exist_ok=True)

    for letter in sorted(question["options"].keys()):
        opt = question["options"][letter]
        is_correct = opt["correct"]
        output_path = str(q_dir / f"option_{letter.lower()}.png")

        try:
            create_diagram_for_option(question, letter, output_path, is_correct)
            print(f"    Created: option_{letter.lower()}.png")
        except Exception as e:
            print(f"    ERROR creating option_{letter.lower()}.png: {e}")


def generate_all_diagrams():
    """Generate diagrams for all sessions."""
    with open("extracted_questions.json") as f:
        sessions = json.load(f)

    for session_num_str, questions in sessions.items():
        session_num = int(session_num_str)
        print(f"\nSession {session_num}: generating diagrams for {len(questions)} questions")

        for q in questions:
            q_num = q["number"]
            print(f"  Q{q_num}:")
            generate_diagrams_for_question(q, session_num, q_num)


def generate_create_diagrams_script(question: dict, session_num: int, q_num: int):
    """Generate a standalone create_diagrams.py script for a question."""
    q_dir = Path(f"session{session_num}/exam-strategy/q{q_num}")
    q_dir.mkdir(parents=True, exist_ok=True)

    script_content = f'''"""Auto-generated script to regenerate diagrams for Session {session_num} Q{q_num}."""
import sys
sys.path.insert(0, "{Path.cwd()}")
from generate_diagrams import generate_diagrams_for_question
import json

with open("{Path.cwd()}/extracted_questions.json") as f:
    sessions = json.load(f)

question = sessions["{session_num}"][{q_num - 1}]
generate_diagrams_for_question(question, {session_num}, {q_num})
print("Done!")
'''
    script_path = q_dir / "create_diagrams.py"
    script_path.write_text(script_content)


if __name__ == "__main__":
    generate_all_diagrams()

    # Also generate per-question scripts
    with open("extracted_questions.json") as f:
        sessions = json.load(f)

    for session_num_str, questions in sessions.items():
        session_num = int(session_num_str)
        for q in questions:
            generate_create_diagrams_script(q, session_num, q["number"])
