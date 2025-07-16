
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import utils.common as common
import utils.authenticate as authenticate
import json

# Page configuration
st.set_page_config(
    page_title="AWS Infrastructure as Code Hub",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# AWS Color Scheme
AWS_COLORS = {
    'primary': '#FF9900',
    'secondary': '#232F3E',
    'light_blue': '#4B9EDB',
    'dark_blue': '#1B2631',
    'light_gray': '#F2F3F3',
    'success': '#3FB34F',
    'warning': '#FF6B35'
}

def apply_custom_styles():
    """Apply custom CSS styling with AWS color scheme"""
    st.markdown(f"""
    <style>
        .main {{
            background-color: {AWS_COLORS['light_gray']};
        }}
        
        .stTabs [data-baseweb="tab-list"] {{
            gap: 20px;
            background-color: white;
            border-radius: 12px;
            padding: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            height: 65px;
            padding: 8px 20px;
            background-color: {AWS_COLORS['light_gray']};
            border-radius: 10px;
            color: {AWS_COLORS['secondary']};
            font-weight: 600;
            border: 2px solid transparent;
            font-size: 14px;
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: {AWS_COLORS['primary']};
            color: white;
            border: 2px solid {AWS_COLORS['secondary']};
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, {AWS_COLORS['primary']} 0%, {AWS_COLORS['light_blue']} 100%);
            padding: 20px;
            border-radius: 15px;
            color: white;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            margin: 10px 0;
        }}
        
        .concept-card {{
            background: white;
            padding: 15px;
            border-radius: 15px;
            border-left: 5px solid {AWS_COLORS['primary']};
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin: 5px 0;
        }}
        
        .highlight-box {{
            background: linear-gradient(135deg, {AWS_COLORS['light_blue']} 0%, {AWS_COLORS['primary']} 100%);
            padding: 20px;
            border-radius: 12px;
            color: white;
            margin: 15px 0;
        }}
        
        .warning-box {{
            background: linear-gradient(135deg, {AWS_COLORS['warning']} 0%, {AWS_COLORS['primary']} 100%);
            padding: 20px;
            border-radius: 12px;
            color: white;
            margin: 15px 0;
        }}
        
        .info-box {{
            background-color: #E6F2FF;
            padding: 10px;
            border-radius: 10px;
            margin-bottom: 10px;
            border-left: 5px solid #00A1C9;
        }}
        
        .footer {{
            margin-top: 10px;
            margin-bottom: 2px;
            padding: 5px;
            text-align: center;
            background-color: {AWS_COLORS['secondary']};
            color: white;
            border-radius: 10px;
        }}
        
        .code-container {{
            background-color: {AWS_COLORS['dark_blue']};
            color: white;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid {AWS_COLORS['primary']};
            margin: 15px 0;
        }}
        
        .language-selector {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            border: 2px solid {AWS_COLORS['light_blue']};
            margin: 15px 0;
        }}
        
        .paradigm-shift {{
            background: linear-gradient(135deg, {AWS_COLORS['success']} 0%, {AWS_COLORS['light_blue']} 100%);
            padding: 20px;
            border-radius: 12px;
            color: white;
            margin: 15px 0;
        }}
    </style>
    """, unsafe_allow_html=True)

def create_sidebar():
    """Create sidebar with app information and controls"""
    with st.sidebar:
        common.render_sidebar()
        
        # About section (collapsed by default)
        with st.expander("📖 About this App", expanded=False):
            st.markdown("""
            **Topics Covered:**
            - 🏗️ AWS CDK - Infrastructure as Code using programming languages
            - 🚀 AWS SAM - Serverless Application Model for serverless development
            
            **Learning Objectives:**
            - Understand Infrastructure as Code paradigms
            - Learn to build cloud resources with familiar programming languages
            - Master serverless application development and deployment
            - Practice with interactive CDK and SAM examples
            - Explore CI/CD pipeline integration
            """)

def create_cdk_paradigm_mermaid():
    """Create mermaid diagram for CDK paradigm shift"""
    return """
    graph LR
        subgraph "Traditional CloudFormation"
            A[Template A] --> B[Stack A]
            C[Template B] --> D[Stack B]
            E[Parameterized Template] --> F[Stack 1]
            E --> G[Stack 2]
        end
        
        subgraph "AWS CDK Approach"
            H[CDK App Source Code] --> I[Template A Generated]
            H --> J[Template B Generated]
            I --> K[Stack A]
            J --> L[Stack B]
        end
        
        style A fill:#FF9900,stroke:#232F3E,color:#fff
        style C fill:#FF9900,stroke:#232F3E,color:#fff
        style E fill:#FF9900,stroke:#232F3E,color:#fff
        style H fill:#3FB34F,stroke:#232F3E,color:#fff
        style I fill:#4B9EDB,stroke:#232F3E,color:#fff
        style J fill:#4B9EDB,stroke:#232F3E,color:#fff
    """

def create_cdk_construct_library_mermaid():
    """Create mermaid diagram for CDK construct library"""
    return """
    graph TB
        A[AWS CDK Construct Library] --> B[Foundational Services]
        A --> C[Serverless Applications]
        A --> D[Application Integration]
        A --> E[Containers]
        A --> F[CI/CD Pipelines]
        
        B --> B1[VPC, IAM, S3]
        C --> C1[Lambda, API Gateway, DynamoDB]
        D --> D1[SNS, SQS, EventBridge]
        E --> E1[ECS, EKS, Fargate]
        F --> F1[CodePipeline, CodeBuild]
        
        style A fill:#FF9900,stroke:#232F3E,color:#fff
        style B fill:#4B9EDB,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#232F3E,stroke:#FF9900,color:#fff
        style E fill:#FF6B35,stroke:#232F3E,color:#fff
        style F fill:#9D5AAE,stroke:#232F3E,color:#fff
    """

def create_sam_pipeline_mermaid():
    """Create mermaid diagram for SAM CI/CD pipeline"""
    return """
    graph LR
        A[GitHub Repository] --> B[Git Push]
        B --> C[CodePipeline Trigger]
        C --> D[CodeBuild]
        
        subgraph "Build Phase"
            D --> E[sam build]
            E --> F[sam package]
            F --> G[sam deploy]
        end
        
        G --> H[Deploy to DEV]
        H --> I[Run Tests]
        I --> J{Tests Pass?}
        J -->|Yes| K[Deploy to PROD]
        J -->|No| L[Notify Team]
        
        style A fill:#232F3E,stroke:#FF9900,color:#fff
        style C fill:#FF9900,stroke:#232F3E,color:#fff
        style D fill:#4B9EDB,stroke:#232F3E,color:#fff
        style H fill:#3FB34F,stroke:#232F3E,color:#fff
        style K fill:#3FB34F,stroke:#232F3E,color:#fff
        style L fill:#FF6B35,stroke:#232F3E,color:#fff
    """

def create_sam_architecture_mermaid():
    """Create mermaid diagram for SAM application architecture"""
    return """
    graph TB
        A[SAM Template] --> B[AWS Lambda Functions]
        A --> C[API Gateway]
        A --> D[DynamoDB Tables]
        A --> E[S3 Buckets]
        
        C --> B
        B --> D
        B --> E
        
        F[sam local start-api] --> G[Local Testing]
        F --> H[Local Debugging]
        
        I[sam deploy] --> J[CloudFormation Stack]
        J --> K[Production Resources]
        
        style A fill:#FF9900,stroke:#232F3E,color:#fff
        style B fill:#FF6B35,stroke:#232F3E,color:#fff
        style C fill:#4B9EDB,stroke:#232F3E,color:#fff
        style D fill:#3FB34F,stroke:#232F3E,color:#fff
        style F fill:#9D5AAE,stroke:#232F3E,color:#fff
    """

def cdk_tab():
    """Content for AWS CDK tab"""
    st.markdown("## 🏗️ AWS Cloud Development Kit (CDK)")
    st.markdown("*Define cloud infrastructure using familiar programming languages*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **AWS CDK** is an open-source software development framework to model and provision your cloud infrastructure 
    resources using familiar programming languages. It provides a high-level, object-oriented abstraction on top of CloudFormation.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # CDK Benefits
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 5+\n**Languages**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 1000+\n**Constructs**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### IDE\n**Support**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### Type\n**Safety**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Paradigm Shift
    st.markdown("### 🔄 Paradigm Shift: From Templates to Code")
    st.markdown('<div class="paradigm-shift">', unsafe_allow_html=True)
    st.markdown("""
    **Traditional Approach**: One parameterized template for multiple environments
    
    **CDK Approach**: Source code generates environment-specific templates
    - Better environment isolation and customization
    - Easier to maintain differences between dev/test/prod
    - Familiar programming language constructs (loops, conditions, functions)
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    common.mermaid(create_cdk_paradigm_mermaid(), height=800)
    
    # Interactive Language Selector
    st.markdown("### 💻 Choose Your Programming Language")
    
    languages = {
        'TypeScript': {
            'popularity': '⭐⭐⭐⭐⭐',
            'description': 'Most mature, extensive documentation',
            'use_case': 'Full-stack developers, Node.js teams'
        },
        'Python': {
            'popularity': '⭐⭐⭐⭐⭐',
            'description': 'Great for data science and automation',
            'use_case': 'Python developers, ML/AI teams'
        },
        'Java': {
            'popularity': '⭐⭐⭐⭐',
            'description': 'Enterprise-grade, strong typing',
            'use_case': 'Enterprise Java teams'
        },
        'C#': {
            'popularity': '⭐⭐⭐',
            'description': '.NET ecosystem integration',
            'use_case': 'Microsoft stack developers'
        },
        'Go': {
            'popularity': '⭐⭐⭐',
            'description': 'Fast compilation, simple syntax',
            'use_case': 'DevOps teams, microservices'
        }
    }
    
    selected_language = st.selectbox("Select Programming Language:", list(languages.keys()))
    
    if selected_language:
        lang_info = languages[selected_language]
        
        st.markdown('<div class="language-selector">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            **Language**: {selected_language}
            
            **Popularity**: {lang_info['popularity']}
            
            **Description**: {lang_info['description']}
            
            **Best For**: {lang_info['use_case']}
            """)
        
        with col2:
            if st.button(f"🚀 Start with {selected_language}", use_container_width=True):
                st.success(f"✅ Great choice! {selected_language} offers excellent CDK support!")
                if selected_language == 'TypeScript':
                    st.info("💡 TypeScript provides the richest CDK experience with comprehensive IntelliSense")
                elif selected_language == 'Python':
                    st.info("💡 Python CDK is perfect for rapid prototyping and data-driven applications")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # CDK Construct Library
    st.markdown("### 📚 CDK Construct Library")
    st.markdown("Ready-to-use cloud components with sensible defaults")
    
    common.mermaid(create_cdk_construct_library_mermaid(), height=350)
    
    # Interactive CDK App Builder
    st.markdown("### 🛠️ Interactive CDK Application Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏗️ Infrastructure Components")
        vpc_needed = st.checkbox("VPC with public/private subnets", value=True)
        database = st.selectbox("Database:", ["None", "RDS MySQL", "DynamoDB", "RDS PostgreSQL"])
        compute = st.selectbox("Compute:", ["Lambda Functions", "ECS Fargate", "EC2 Instances"])
        storage = st.multiselect("Storage:", ["S3 Bucket", "EFS", "EBS Volumes"])
    
    with col2:
        st.markdown("### ⚙️ Application Settings")
        app_name = st.text_input("Application Name:", "my-cdk-app")
        environment = st.selectbox("Environment:", ["dev", "staging", "production"])
        region = st.selectbox("AWS Region:", ["us-east-1", "us-west-2", "eu-west-1"])
        enable_monitoring = st.checkbox("Enable CloudWatch monitoring", value=True)
    
    if st.button("🏗️ Generate CDK Code", use_container_width=True):
        # Generate sample CDK code based on selections
        st.markdown("### 📝 Generated CDK Code (Python)")
        
        code = f'''#!/usr/bin/env python3
import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
)

class {app_name.replace("-", "_").title()}Stack(Stack):
    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        # Create VPC with public and private subnets
        {'vpc = ec2.Vpc(self, "VPC",' if vpc_needed else '# VPC creation skipped'}
        {'    max_azs=2,' if vpc_needed else ''}
        {'    subnet_configuration=[' if vpc_needed else ''}
        {'        ec2.SubnetConfiguration(' if vpc_needed else ''}
        {'            name="public",' if vpc_needed else ''}
        {'            subnet_type=ec2.SubnetType.PUBLIC,' if vpc_needed else ''}
        {'            cidr_mask=24' if vpc_needed else ''}
        {'        ),' if vpc_needed else ''}
        {'        ec2.SubnetConfiguration(' if vpc_needed else ''}
        {'            name="private",' if vpc_needed else ''}
        {'            subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,' if vpc_needed else ''}
        {'            cidr_mask=24' if vpc_needed else ''}
        {'        )' if vpc_needed else ''}
        {'    ]' if vpc_needed else ''}
        {')' if vpc_needed else ''}
        
        {f'# Database: {database}' if database != "None" else '# No database selected'}
        {f'# Compute: {compute}'}
        {f'# Storage: {", ".join(storage) if storage else "None"}'}
        
        # Environment-specific configurations
        env_config = {{
            "dev": {{"instance_size": "SMALL"}},
            "staging": {{"instance_size": "MEDIUM"}},
            "production": {{"instance_size": "LARGE"}}
        }}
        
        current_config = env_config["{environment}"]
        
        # Add CloudWatch monitoring
        {f'# Monitoring: {"Enabled" if enable_monitoring else "Disabled"}'}

app = cdk.App()
{app_name.replace("-", "_").title()}Stack(app, "{app_name}-{environment}",
    env=cdk.Environment(
        account=app.node.try_get_context("account"),
        region="{region}"
    )
)

app.synth()
'''
        
        st.markdown('<div class="code-container">', unsafe_allow_html=True)
        st.code(code, language='python')
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Deployment commands
        st.markdown("### 🚀 Deployment Commands")
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        **Deploy your CDK app:**
        ```bash
        # Install dependencies
        pip install aws-cdk-lib constructs
        
        # Bootstrap CDK (first time only)
        cdk bootstrap aws://ACCOUNT-NUMBER/{region}
        
        # Deploy the stack
        cdk deploy {app_name}-{environment}
        
        # View the generated CloudFormation template
        cdk synth {app_name}-{environment}
        ```
        
        **Estimated Resources:** {2 + (1 if vpc_needed else 0) + (1 if database != "None" else 0) + len(storage)} AWS resources
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # CDK vs CloudFormation Comparison
    st.markdown("### ⚖️ CDK vs Traditional CloudFormation")
    
    comparison_data = {
        'Aspect': ['Language', 'Learning Curve', 'IDE Support', 'Reusability', 'Testing', 'Community'],
        'CloudFormation': ['JSON/YAML', 'Moderate', 'Limited', 'Templates', 'Limited', 'AWS Official'],
        'CDK': ['Programming Languages', 'Steep initially', 'Excellent', 'Classes/Libraries', 'Unit Testing', 'Growing Rapidly'],
        'CDK Advantage': ['✅ Familiar syntax', '⚠️ Requires coding skills', '✅ IntelliSense/Debugging', '✅ OOP patterns', '✅ Jest/PyTest', '✅ Open source']
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True)
    
    # Advanced CDK Features
    st.markdown("### 🚀 Advanced CDK Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔧 Constructs & Patterns
        - **L1 Constructs**: Direct CloudFormation mapping
        - **L2 Constructs**: Opinionated defaults, best practices
        - **L3 Constructs**: Architectural patterns
        - **Custom Constructs**: Reusable components
        
        ### 🎯 Built-in Best Practices
        - Security: IAM least privilege
        - Monitoring: CloudWatch integration
        - Tagging: Automatic resource tagging
        - Networking: VPC best practices
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🧪 Testing & Validation
        - **Unit Testing**: Test construct logic
        - **Integration Testing**: Test deployments
        - **Snapshot Testing**: Detect template changes
        - **Property Testing**: Validate configurations
        
        ### 📦 Package Management
        - **npm/pip/Maven**: Standard package managers
        - **Versioning**: Semantic versioning
        - **Publishing**: Share constructs
        - **Dependencies**: Automatic resolution
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Real-world CDK Example
    st.markdown("### 💼 Real-world Example: Three-Tier Web Application")
    
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Complete three-tier web application with CDK
from aws_cdk import (
    Stack, Duration,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_elasticloadbalancingv2 as elbv2,
    aws_route53 as route53,
    aws_certificatemanager as acm,
    aws_logs as logs
)

class WebApplicationStack(Stack):
    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        # Create VPC with NAT Gateways for high availability
        vpc = ec2.Vpc(self, "WebAppVPC",
            max_azs=2,
            nat_gateways=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="database",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=28
                )
            ]
        )
        
        # Database tier - RDS with read replica
        db_security_group = ec2.SecurityGroup(self, "DatabaseSG",
            vpc=vpc,
            description="Security group for RDS database",
            allow_all_outbound=False
        )
        
        database = rds.DatabaseCluster(self, "WebAppDatabase",
            engine=rds.DatabaseClusterEngine.aurora_mysql(
                version=rds.AuroraMysqlEngineVersion.VER_8_0_28
            ),
            credentials=rds.Credentials.from_generated_secret("admin"),
            instance_props=rds.InstanceProps(
                instance_type=ec2.InstanceType.of(
                    ec2.InstanceClass.T3, ec2.InstanceSize.MEDIUM
                ),
                vpc_subnets=ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                ),
                vpc=vpc,
                security_groups=[db_security_group]
            ),
            instances=2,  # Primary + read replica
            backup=rds.BackupProps(
                retention=Duration.days(7)
            ),
            deletion_protection=True
        )
        
        # Application tier - ECS Fargate
        cluster = ecs.Cluster(self, "WebAppCluster", vpc=vpc)
        
        # Application Load Balanced Fargate Service
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "WebAppService",
            cluster=cluster,
            memory_limit_mib=2048,
            cpu=1024,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry("nginx:latest"),
                container_port=80,
                log_driver=ecs.LogDrivers.aws_logs(
                    stream_prefix="webapp",
                    log_retention=logs.RetentionDays.ONE_WEEK
                )
            ),
            public_load_balancer=True,
            desired_count=2,
            domain_zone=route53.HostedZone.from_hosted_zone_attributes(
                self, "Zone",
                zone_name="example.com",
                hosted_zone_id="Z123456789"
            ),
            domain_name="webapp.example.com",
            certificate=acm.Certificate.from_certificate_arn(
                self, "Cert",
                "arn:aws:acm:region:account:certificate/cert-id"
            )
        )
        
        # Allow ECS tasks to connect to database
        database.connections.allow_from(
            fargate_service.service,
            ec2.Port.tcp(3306),
            "Allow ECS tasks to connect to database"
        )
        
        # Auto Scaling
        fargate_service.service.auto_scale_task_count(
            max_capacity=10,
            min_capacity=2
        ).scale_on_cpu_utilization(
            "CpuScaling",
            target_utilization_percent=70,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60)
        )
        
        # CloudWatch Dashboard
        dashboard = cloudwatch.Dashboard(self, "WebAppDashboard",
            dashboard_name="WebApplication-Monitoring"
        )
        
        # Add widgets to dashboard
        dashboard.add_widgets(
            cloudwatch.GraphWidget(
                title="ECS Service CPU and Memory",
                left=[fargate_service.service.metric_cpu_utilization()],
                right=[fargate_service.service.metric_memory_utilization()]
            ),
            cloudwatch.GraphWidget(
                title="Database Connections",
                left=[database.metric_database_connections()]
            )
        )

# Deployment
app = cdk.App()
WebApplicationStack(app, "WebApp-Production",
    env=cdk.Environment(
        account="123456789012",
        region="us-east-1"
    ),
    tags={
        "Environment": "Production",
        "Application": "WebApp",
        "Owner": "DevOps Team"
    }
)

app.synth()
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def sam_tab():
    """Content for AWS SAM tab"""
    st.markdown("## 🚀 AWS Serverless Application Model (SAM)")
    st.markdown("*Framework for building serverless applications on AWS*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **AWS SAM** is an open-source framework that you can use to build serverless applications on AWS. 
    It provides shorthand syntax to express functions, APIs, databases, and event source mappings with fewer lines of YAML.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # SAM Benefits
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### Local\n**Testing**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### Built-in\n**Best Practices**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### Simple\n**Deployment**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### CI/CD\n**Integration**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # SAM Architecture Overview
    st.markdown("### 🏗️ SAM Application Architecture")
    common.mermaid(create_sam_architecture_mermaid(), height=450)
    
    # Interactive SAM Application Builder
    st.markdown("### 🛠️ Interactive SAM Application Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚡ Serverless Components")
        api_type = st.selectbox("API Gateway:", ["REST API", "HTTP API", "None"])
        functions = st.multiselect("Lambda Functions:", [
            "User Authentication", "Data Processing", "File Upload", 
            "Email Notifications", "Report Generation"
        ])
        database = st.selectbox("Database:", ["DynamoDB", "RDS Serverless", "Aurora Serverless", "None"])
        events = st.multiselect("Event Sources:", [
            "S3 Bucket", "DynamoDB Stream", "SQS Queue", "CloudWatch Events", "SNS Topic"
        ])
    
    with col2:
        st.markdown("### ⚙️ Configuration")
        app_name = st.text_input("Application Name:", "my-serverless-app")
        runtime = st.selectbox("Lambda Runtime:", [
            "python3.9", "nodejs18.x", "java11", "dotnet6", "go1.x"
        ])
        memory = st.slider("Lambda Memory (MB):", 128, 3008, 512)
        timeout = st.slider("Lambda Timeout (seconds):", 3, 900, 30)
        
        enable_xray = st.checkbox("Enable X-Ray tracing", value=True)
        enable_logs = st.checkbox("Enable structured logging", value=True)
    
    if st.button("🚀 Generate SAM Template", use_container_width=True):
        # Generate SAM template based on selections
        st.markdown("### 📄 Generated SAM Template (template.yaml)")
        
        template = f'''AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: >
  {app_name}
  
  SAM Template for serverless application

# Global configuration for all resources
Globals:
  Function:
    Timeout: {timeout}
    MemorySize: {memory}
    Runtime: {runtime}
    {'Tracing: Active' if enable_xray else '# X-Ray tracing disabled'}
    Environment:
      Variables:
        POWERTOOLS_SERVICE_NAME: {app_name}
        {'POWERTOOLS_LOGGER_LOG_LEVEL: INFO' if enable_logs else ''}
        {'LOG_LEVEL: INFO' if enable_logs else ''}

Resources:'''

        # Add API Gateway if selected
        if api_type != "None":
            template += f'''
  {app_name.replace("-", "")}Api:
    Type: AWS::Serverless::Api
    Properties:
      StageName: Prod
      {'RestApiId:' if api_type == "REST API" else 'HttpApiId:'}
        Description: {api_type} for {app_name}
      Cors:
        AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
        AllowHeaders: "'Content-Type,Authorization'"
        AllowOrigin: "'*'"
'''

        # Add Lambda functions
        for i, func in enumerate(functions):
            func_name = func.replace(" ", "")
            template += f'''
  {func_name}Function:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: {func_name.lower()}/
      Handler: app.lambda_handler
      Runtime: {runtime}
      Environment:
        Variables:
          TABLE_NAME: !Ref {app_name.replace("-", "")}Table
      Events:
        {func_name}:
          Type: Api
          Properties:
            Path: /{func_name.lower()}
            Method: {'GET' if 'Report' in func else 'POST'}
            {'RestApiId: !Ref ' + app_name.replace("-", "") + 'Api' if api_type == "REST API" else ''}
'''

        # Add DynamoDB table if selected
        if database == "DynamoDB":
            template += f'''
  {app_name.replace("-", "")}Table:
    Type: AWS::Serverless::SimpleTable
    Properties:
      PrimaryKey:
        Name: id
        Type: String
      BillingMode: PAY_PER_REQUEST
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES
'''

        # Add event sources
        for event in events:
            if event == "S3 Bucket":
                template += f'''
  {app_name.replace("-", "")}Bucket:
    Type: AWS::S3::Bucket
    Properties:
      NotificationConfiguration:
        LambdaConfigurations:
          - Event: s3:ObjectCreated:*
            Function: !GetAtt DataProcessingFunction.Arn
'''

        template += '''
Outputs:
  ApiEndpoint:
    Description: "API Gateway endpoint URL"
    Value: !Sub "https://${''' + app_name.replace("-", "") + '''Api}.execute-api.${AWS::Region}.amazonaws.com/Prod/"
  
  LambdaFunctions:
    Description: "Lambda Function ARNs"
    Value: !Join [", ", [''' + ', '.join([f'!GetAtt {func.replace(" ", "")}Function.Arn' for func in functions]) + ''']]
'''

        st.markdown('<div class="code-container">', unsafe_allow_html=True)
        st.code(template, language='yaml')
        st.markdown('</div>', unsafe_allow_html=True)
        
        # SAM CLI commands
        st.markdown("### 🛠️ SAM CLI Commands")
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        **Development Workflow:**
        ```bash
        # Initialize new SAM project
        sam init --runtime {runtime} --name {app_name}
        
        # Build the application
        sam build
        
        # Test locally
        sam local start-api --port 3000
        
        # Deploy to AWS
        sam deploy --guided
        
        # View logs
        sam logs -n {functions[0].replace(" ", "")}Function --stack-name {app_name} --tail
        
        # Clean up resources
        sam delete --stack-name {app_name}
        ```
        
        **Estimated Cost**: $0.20 per million requests + $0.0000166667 per GB-second
        **Deployment Time**: 2-5 minutes
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # SAM Benefits Deep Dive
    st.markdown("### ✨ SAM Benefits & Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🧪 Local Development
        - **sam local start-api**: Test API locally
        - **sam local invoke**: Test functions
        - **Step-through debugging** support
        - **Hot reload** for rapid development
        
        ### 📦 Built-in Best Practices
        - **Security**: IAM roles and policies
        - **Monitoring**: CloudWatch integration
        - **Error handling**: Dead letter queues
        - **Performance**: Provisioned concurrency
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🚀 Simplified Deployment
        - **sam deploy**: One-command deployment
        - **CloudFormation** under the hood
        - **Rollback** capabilities
        - **Parameter** management
        
        ### 📊 Observability
        - **AWS X-Ray** tracing
        - **CloudWatch Logs** centralization
        - **Custom metrics** support
        - **Alarms** and notifications
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔄 CI/CD Integration
        - **sam pipeline** bootstrap
        - **CodePipeline** integration
        - **GitHub Actions** support
        - **Multi-stage** deployments
        
        ### 🛡️ Security Features
        - **API Gateway** authentication
        - **Secrets Manager** integration
        - **VPC** configuration
        - **Resource policies**
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # SAM Pipeline Architecture
    st.markdown("### 🔄 SAM CI/CD Pipeline")
    common.mermaid(create_sam_pipeline_mermaid(), height=300)
    
    # SAM vs Other Frameworks
    st.markdown("### ⚖️ SAM vs Other Serverless Frameworks")
    
    framework_comparison = {
        'Feature': ['Learning Curve', 'AWS Integration', 'Local Testing', 'Multi-Cloud', 'Community', 'Cost'],
        'AWS SAM': ['Low', 'Excellent', 'Excellent', 'AWS Only', 'Growing', 'Free'],
        'Serverless Framework': ['Medium', 'Good', 'Good', 'Yes', 'Large', 'Free/Paid'],
        'CDK': ['High', 'Excellent', 'Limited', 'AWS Only', 'Growing', 'Free'],
        'Terraform': ['High', 'Good', 'Limited', 'Yes', 'Very Large', 'Free/Paid']
    }
    
    df_frameworks = pd.DataFrame(framework_comparison)
    st.dataframe(df_frameworks, use_container_width=True)
    
    # Real-world SAM Example
    st.markdown("### 💼 Real-world Example: E-commerce Order Processing")
    
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Complete e-commerce order processing system with SAM
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: E-commerce Order Processing System

Globals:
  Function:
    Timeout: 30
    MemorySize: 512
    Runtime: python3.9
    Tracing: Active
    Environment:
      Variables:
        ORDERS_TABLE: !Ref OrdersTable
        INVENTORY_TABLE: !Ref InventoryTable
        NOTIFICATION_TOPIC: !Ref OrderNotificationTopic

Resources:
  # API Gateway for order management
  OrderProcessingApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: prod
      Auth:
        DefaultAuthorizer: CognitoAuthorizer
        Authorizers:
          CognitoAuthorizer:
            UserPoolArn: !GetAtt UserPool.Arn
      Cors:
        AllowMethods: "'GET,POST,PUT,DELETE,OPTIONS'"
        AllowHeaders: "'Content-Type,Authorization'"
        AllowOrigin: "'https://mystore.com'"

  # Lambda Functions
  CreateOrderFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: orders/create/
      Handler: app.lambda_handler
      Description: Creates new customer orders
      Events:
        CreateOrder:
          Type: Api
          Properties:
            RestApiId: !Ref OrderProcessingApi
            Path: /orders
            Method: POST
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref OrdersTable
        - DynamoDBCrudPolicy:
            TableName: !Ref InventoryTable
        - SNSPublishMessagePolicy:
            TopicName: !GetAtt OrderNotificationTopic.TopicName

  ProcessPaymentFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: orders/payment/
      Handler: app.lambda_handler
      Description: Processes order payments
      Events:
        OrderCreated:
          Type: DynamoDB
          Properties:
            Stream: !GetAtt OrdersTable.StreamArn
            StartingPosition: TRIM_HORIZON
            FilterCriteria:
              Filters:
                - Pattern: '{"eventName": ["INSERT"], "dynamodb": {"NewImage": {"status": {"S": ["PENDING"]}}}}'
      Environment:
        Variables:
          STRIPE_SECRET_KEY: !Ref StripeSecretKey
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref OrdersTable
        - SSMParameterReadPolicy:
            ParameterName: /ecommerce/stripe/secret-key

  UpdateInventoryFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: inventory/update/
      Handler: app.lambda_handler
      Description: Updates inventory levels
      Events:
        PaymentProcessed:
          Type: SNS
          Properties:
            Topic: !Ref OrderNotificationTopic
            FilterPolicy:
              event_type:
                - payment_success
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref InventoryTable

  SendNotificationFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: notifications/
      Handler: app.lambda_handler
      Description: Sends order notifications
      Events:
        OrderStatusChange:
          Type: SNS
          Properties:
            Topic: !Ref OrderNotificationTopic
      Environment:
        Variables:
          SES_FROM_EMAIL: orders@mystore.com
      Policies:
        - SESCrudPolicy:
            IdentityName: orders@mystore.com

  # DynamoDB Tables
  OrdersTable:
    Type: AWS::Serverless::SimpleTable
    Properties:
      PrimaryKey:
        Name: order_id
        Type: String
      BillingMode: PAY_PER_REQUEST
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES
      PointInTimeRecoverySpecification:
        PointInTimeRecoveryEnabled: true
      SSESpecification:
        SSEEnabled: true

  InventoryTable:
    Type: AWS::DynamoDB::Table
    Properties:
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: product_id
          AttributeType: S
        - AttributeName: warehouse_id
          AttributeType: S
      KeySchema:
        - AttributeName: product_id
          KeyType: HASH
        - AttributeName: warehouse_id
          KeyType: RANGE
      GlobalSecondaryIndexes:
        - IndexName: WarehouseIndex
          KeySchema:
            - AttributeName: warehouse_id
              KeyType: HASH
          Projection:
            ProjectionType: ALL

  # SNS Topic for order events
  OrderNotificationTopic:
    Type: AWS::SNS::Topic
    Properties:
      DisplayName: Order Processing Notifications
      KmsMasterKeyId: alias/aws/sns

  # Cognito User Pool for API authentication
  UserPool:
    Type: AWS::Cognito::UserPool
    Properties:
      UserPoolName: EcommerceUserPool
      AutoVerifiedAttributes:
        - email
      Policies:
        PasswordPolicy:
          MinimumLength: 8
          RequireUppercase: true
          RequireLowercase: true
          RequireNumbers: true
          RequireSymbols: true

  # Step Functions for order workflow
  OrderWorkflowStateMachine:
    Type: AWS::Serverless::StateMachine
    Properties:
      DefinitionUri: statemachine/order-workflow.asl.json
      DefinitionSubstitutions:
        CreateOrderFunctionArn: !GetAtt CreateOrderFunction.Arn
        ProcessPaymentFunctionArn: !GetAtt ProcessPaymentFunction.Arn
        UpdateInventoryFunctionArn: !GetAtt UpdateInventoryFunction.Arn
      Policies:
        - LambdaInvokePolicy:
            FunctionName: !Ref CreateOrderFunction
        - LambdaInvokePolicy:
            FunctionName: !Ref ProcessPaymentFunction
        - LambdaInvokePolicy:
            FunctionName: !Ref UpdateInventoryFunction

  # Parameters
  StripeSecretKey:
    Type: AWS::SSM::Parameter
    Properties:
      Name: /ecommerce/stripe/secret-key
      Type: SecureString
      Value: sk_test_your_stripe_secret_key_here
      Description: Stripe API secret key

  # CloudWatch Dashboard
  OrderProcessingDashboard:
    Type: AWS::CloudWatch::Dashboard
    Properties:
      DashboardName: EcommerceOrderProcessing
      DashboardBody: !Sub |
        {
          "widgets": [
            {
              "type": "metric",
              "properties": {
                "metrics": [
                  ["AWS/Lambda", "Invocations", "FunctionName", "${CreateOrderFunction}"],
                  [".", "Duration", ".", "."],
                  [".", "Errors", ".", "."]
                ],
                "period": 300,
                "stat": "Sum",
                "region": "${AWS::Region}",
                "title": "Order Creation Metrics"
              }
            }
          ]
        }

Outputs:
  OrderApiEndpoint:
    Description: API Gateway endpoint URL for order processing
    Value: !Sub "https://${OrderProcessingApi}.execute-api.${AWS::Region}.amazonaws.com/prod/"
  
  UserPoolId:
    Description: Cognito User Pool ID
    Value: !Ref UserPool
    Export:
      Name: !Sub "${AWS::StackName}-UserPoolId"
  
  OrdersTableName:
    Description: DynamoDB table for orders
    Value: !Ref OrdersTable
    Export:
      Name: !Sub "${AWS::StackName}-OrdersTable"
    ''', language='yaml')
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Advanced SAM Features
    st.markdown("### 🚀 Advanced SAM Features")
    
    features_data = {
        'Feature': [
            'SAM Pipeline', 'Step Functions Integration', 'Event Source Mapping', 
            'Layer Management', 'Custom Resources', 'Policy Templates'
        ],
        'Description': [
            'CI/CD pipeline generation',
            'Serverless workflows with Step Functions',
            'Connect Lambda to event sources',
            'Shared code and dependencies',
            'CloudFormation custom resources',
            'Pre-built IAM policy templates'
        ],
        'Use Case': [
            'Automated deployments',
            'Complex business workflows',
            'Event-driven processing',
            'Code reuse across functions',
            'Custom AWS integrations',
            'Secure function permissions'
        ],
        'Complexity': ['Medium', 'High', 'Low', 'Low', 'High', 'Low']
    }
    
    df_features = pd.DataFrame(features_data)
    st.dataframe(df_features, use_container_width=True)

def main():
    """Main application function"""
    # Apply styling
    apply_custom_styles()
    
    # Initialize session
    common.initialize_session_state()
    common.initialize_mermaid()
    
    # Create sidebar
    create_sidebar()
    
    # Main header
    st.markdown("""
    # 🏗️ AWS Infrastructure as Code
    
    """)
    st.markdown("""<div class="info-box">
                Master Infrastructure as Code with AWS CDK and Serverless Application Model (SAM). Learn to define cloud infrastructure using familiar programming languages and build serverless applications with best practices built-in.
                </div>""", unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2 = st.tabs([
        "🏗️ AWS CDK", 
        "🚀 AWS SAM"
    ])
    
    with tab1:
        cdk_tab()
    
    with tab2:
        sam_tab()
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>© 2025, Amazon Web Services, Inc. or its affiliates. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)

# Main execution flow
if __name__ == "__main__":
    if 'localhost' in st.context.headers["host"]:
        main()
    else:
        # First check authentication
        is_authenticated = authenticate.login()
        
        # If authenticated, show the main app content
        if is_authenticated:
            main()
