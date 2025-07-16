import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import utils.common as common
import utils.authenticate as authenticate
import json
import random
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="AWS Deployment Services Hub",
    page_icon="🚀",
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
        
        .deployment-selector {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            border: 2px solid {AWS_COLORS['light_blue']};
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
            - 🌱 AWS Elastic Beanstalk - Easy web app deployment
            - 🚀 AWS CodeDeploy - Automated application deployment
            - 🐳 Amazon ECS - Container orchestration service
            - ☸️ Amazon EKS - Managed Kubernetes service  
            - 📋 AWS CloudFormation - Infrastructure as Code
            
            **Learning Objectives:**
            - Understand different deployment approaches
            - Learn when to use each deployment service
            - Practice with interactive deployment scenarios
            - Explore Infrastructure as Code concepts
            """)

def create_elastic_beanstalk_architecture():
    """Create mermaid diagram for Elastic Beanstalk architecture"""
    return """
    graph TB
        A[Developer] --> B[Upload Code]
        B --> C[AWS Elastic Beanstalk]
        
        C --> D[Application Load Balancer]
        C --> E[Auto Scaling Group]
        C --> F[EC2 Instances]
        C --> G[RDS Database]
        C --> H[CloudWatch Monitoring]
        
        D --> F
        E --> F
        F --> G
        
        subgraph "Managed by Beanstalk"
            D
            E
            F
            G
            H
        end
        
        style A fill:#4B9EDB,stroke:#232F3E,color:#fff
        style C fill:#FF9900,stroke:#232F3E,color:#fff
        style D fill:#3FB34F,stroke:#232F3E,color:#fff
        style E fill:#3FB34F,stroke:#232F3E,color:#fff
        style F fill:#3FB34F,stroke:#232F3E,color:#fff
        style G fill:#232F3E,stroke:#FF9900,color:#fff
        style H fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_codedeploy_workflow():
    """Create mermaid diagram for CodeDeploy workflow"""
    return """
    graph LR
        A[Source Code] --> B[CodePipeline]
        B --> C[CodeBuild]
        C --> D[Build Artifacts]
        D --> E[CodeDeploy]
        
        E --> F[Application Revision]
        F --> G[Deployment Group]
        
        G --> H[EC2 Instances]
        G --> I[Auto Scaling Group]
        G --> J[On-Premises Servers]
        
        subgraph "Deployment Strategies"
            K[In-Place]
            L[Blue/Green]
            M[Rolling]
        end
        
        E --> K
        E --> L
        E --> M
        
        style A fill:#4B9EDB,stroke:#232F3E,color:#fff
        style E fill:#FF9900,stroke:#232F3E,color:#fff
        style F fill:#3FB34F,stroke:#232F3E,color:#fff
        style G fill:#3FB34F,stroke:#232F3E,color:#fff
        style K fill:#232F3E,stroke:#FF9900,color:#fff
        style L fill:#232F3E,stroke:#FF9900,color:#fff
        style M fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_ecs_architecture():
    """Create mermaid diagram for ECS architecture"""
    return """
    graph TB
        A[Container Image] --> B[Amazon ECR]
        B --> C[ECS Cluster]
        
        C --> D[ECS Service]
        C --> E[ECS Tasks]
        
        D --> F[Task Definition]
        E --> F
        
        F --> G[Container 1]
        F --> H[Container 2]
        
        I[Application Load Balancer] --> D
        J[Auto Scaling] --> D
        
        subgraph "Launch Types"
            K[EC2]
            L[Fargate]
        end
        
        C --> K
        C --> L
        
        style A fill:#4B9EDB,stroke:#232F3E,color:#fff
        style B fill:#FF9900,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#3FB34F,stroke:#232F3E,color:#fff
        style F fill:#232F3E,stroke:#FF9900,color:#fff
        style G fill:#232F3E,stroke:#FF9900,color:#fff
        style H fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_eks_architecture():
    """Create mermaid diagram for EKS architecture"""
    return """
    graph TB
        A[Kubernetes Manifest] --> B[kubectl/Helm]
        B --> C[Amazon EKS Control Plane]
        
        C --> D[Worker Nodes]
        C --> E[Managed Node Groups]
        C --> F[Fargate Pods]
        
        D --> G[Pod 1]
        D --> H[Pod 2]
        E --> I[Pod 3]
        E --> J[Pod 4]
        
        K[Application Load Balancer] --> D
        K --> E
        
        L[VPC CNI] --> C
        M[CoreDNS] --> C
        N[kube-proxy] --> C
        
        style A fill:#4B9EDB,stroke:#232F3E,color:#fff
        style C fill:#FF9900,stroke:#232F3E,color:#fff
        style D fill:#3FB34F,stroke:#232F3E,color:#fff
        style E fill:#3FB34F,stroke:#232F3E,color:#fff
        style F fill:#232F3E,stroke:#FF9900,color:#fff
        style G fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_cloudformation_workflow():
    """Create mermaid diagram for CloudFormation workflow"""
    return """
    graph TD
        A[Template Author] --> B[CloudFormation Template]
        B --> C[AWS CloudFormation]
        
        C --> D[Stack Creation]
        D --> E[Resource Provisioning]
        
        E --> F[EC2 Instances]
        E --> G[VPC Networks]
        E --> H[Security Groups]
        E --> I[Load Balancers]
        E --> J[Databases]
        
        K[Stack Update] --> L[Change Set]
        L --> M[Review Changes]
        M --> N[Execute Changes]
        
        C --> K
        
        style A fill:#4B9EDB,stroke:#232F3E,color:#fff
        style C fill:#FF9900,stroke:#232F3E,color:#fff
        style D fill:#3FB34F,stroke:#232F3E,color:#fff
        style E fill:#3FB34F,stroke:#232F3E,color:#fff
        style L fill:#232F3E,stroke:#FF9900,color:#fff
    """

def elastic_beanstalk_tab():
    """Content for AWS Elastic Beanstalk tab"""
    st.markdown("## 🌱 AWS Elastic Beanstalk")
    st.markdown("*Upload your code and Elastic Beanstalk automatically handles the deployment*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **AWS Elastic Beanstalk** is an easy-to-use service for deploying and scaling web applications and services. 
    Simply upload your code and Elastic Beanstalk automatically handles deployment, from capacity provisioning, 
    load balancing, auto-scaling to application health monitoring.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Beanstalk Architecture
    st.markdown("### 🏗️ Elastic Beanstalk Architecture")
    common.mermaid(create_elastic_beanstalk_architecture(), height=700)
    
    # Supported Platforms
    st.markdown("### 🔧 Supported Application Platforms")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🟨 Languages
        - **Java** (Tomcat, Corretto)
        - **Python** (Django, Flask)
        - **.NET** (Windows, Linux)
        - **Node.js** (Express, React)
        - **Ruby** (Passenger, Puma)
        - **Go** (Gin, Echo)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🐳 Containers
        - **Docker** single/multi-container
        - **Pre-configured** Docker platforms
        - **Custom** Docker images
        - **ECS** integration
        - **Fargate** support
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🌐 Web Servers
        - **Apache** HTTP Server
        - **Nginx** reverse proxy
        - **IIS** (Windows)
        - **Passenger** (Ruby)
        - **Tomcat** (Java)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Application Deployment
    st.markdown("### 🚀 Interactive Application Deployment")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Application Configuration")
        app_name = st.text_input("Application Name:", "my-web-app")
        platform = st.selectbox("Platform:", [
            "Python 3.11 running on Amazon Linux 2023",
            "Node.js 18 running on Amazon Linux 2023", 
            "Java 11 running on Amazon Linux 2023",
            ".NET 6 running on Amazon Linux 2023",
            "Docker running on Amazon Linux 2023"
        ])
        
        environment_name = st.text_input("Environment Name:", f"{app_name}-env")
        instance_type = st.selectbox("Instance Type:", [
            "t3.micro (1 vCPU, 1GB RAM) - Free Tier",
            "t3.small (2 vCPU, 2GB RAM)",
            "t3.medium (2 vCPU, 4GB RAM)",
            "m5.large (2 vCPU, 8GB RAM)"
        ])
    
    with col2:
        st.markdown("### ⚙️ Environment Settings")
        deployment_policy = st.selectbox("Deployment Policy:", [
            "All at once (fastest deployment)",
            "Rolling (maintain capacity)",
            "Rolling with additional batch (zero downtime)",
            "Immutable (safest, new instances)"
        ])
        
        auto_scaling = st.checkbox("Enable Auto Scaling", value=True)
        if auto_scaling:
            min_instances = st.slider("Min Instances:", 1, 10, 1)
            max_instances = st.slider("Max Instances:", 1, 20, 4)
        
        load_balancer = st.checkbox("Enable Load Balancer", value=True, key="load_balancer")
        health_reporting = st.selectbox("Health Reporting:", ["Basic", "Enhanced"],  key="health_reporting")
    
    # Advanced Configuration
    st.markdown("### 🔧 Advanced Configuration")
    
    col3, col4 = st.columns(2)
    with col3:
        monitoring = st.checkbox("CloudWatch Monitoring", value=True)
        notifications = st.checkbox("SNS Notifications", value=False, key="notifications")
        database = st.selectbox("Database:", ["None", "RDS MySQL", "RDS PostgreSQL"])
    
    with col4:
        vpc_config = st.checkbox("Custom VPC Configuration", value=False)
        https_redirect = st.checkbox("Force HTTPS Redirect", value=True)
        log_retention = st.selectbox("Log Retention:", ["1 day", "3 days", "1 week", "1 month"])
    
    if st.button("🚀 Deploy to Elastic Beanstalk", use_container_width=True):
        # Simulate deployment
        deployment_time = random.randint(3, 8)
        monthly_cost = random.uniform(15, 150)
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ Elastic Beanstalk Deployment Initiated!
        
        **Application Details:**
        - **Application**: {app_name}
        - **Environment**: {environment_name}
        - **Platform**: {platform.split()[0]} {platform.split()[1]}
        - **Instance Type**: {instance_type.split()[0]}
        - **Deployment Policy**: {deployment_policy.split()[0]}
        
        **Infrastructure:**
        - **Auto Scaling**: {'✅ Enabled' if auto_scaling else '❌ Disabled'}
        {f"- **Scaling**: {min_instances}-{max_instances} instances" if auto_scaling else ""}
        - **Load Balancer**: {'✅ Application Load Balancer' if load_balancer else '❌ None'}
        - **Database**: {database if database != "None" else "❌ None"}
        
        **Deployment Status:**
        - **Estimated Time**: {deployment_time} minutes
        - **Health Checks**: Starting in 2 minutes
        - **Estimated Monthly Cost**: ${monthly_cost:.2f}
        
        🌐 **Application URL**: http://{environment_name}.elasticbeanstalk.com
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Beanstalk Benefits
    st.markdown("### ✨ Elastic Beanstalk Benefits")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🚀 Fast & Simple
        - **Quick deployments** - just upload your code
        - **No infrastructure management** needed
        - **Built-in best practices** for scalability
        - **Easy version management** and rollbacks
        
        ### 💰 Cost Effective  
        - **No additional charges** - pay only for AWS resources
        - **Right-sizing** with auto scaling
        - **Free tier eligible** with t3.micro instances
        - **Resource optimization** recommendations
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔧 Full Control
        - **Complete resource control** when needed
        - **Access to underlying resources** (EC2, RDS)
        - **Custom configuration** options
        - **Integration** with other AWS services
        
        ### 📊 Monitoring & Management
        - **CloudWatch integration** for metrics
        - **Application health monitoring**
        - **Log file management** and access
        - **Performance insights** and alerts
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Deployment Policies Comparison
    st.markdown("### 📊 Deployment Policies Comparison")
    
    policies_data = {
        'Policy': ['All at once', 'Rolling', 'Rolling with additional batch', 'Immutable'],
        'Downtime': ['Yes', 'No', 'No', 'No'],
        'Deployment Speed': ['Fastest', 'Slow', 'Medium', 'Slowest'],
        'Rollback Time': ['Manual', 'Manual', 'Manual', 'Fast'],
        'Cost': ['Lowest', 'Low', 'Medium', 'Highest'],
        'Best For': ['Dev/Test', 'Production', 'Critical Production', 'High-risk deployments']
    }
    
    df_policies = pd.DataFrame(policies_data)
    st.dataframe(df_policies, use_container_width=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Elastic Beanstalk with Python Flask")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# application.py - Simple Flask application for Elastic Beanstalk
from flask import Flask, render_template, jsonify
import os
import boto3
from datetime import datetime

# Create Flask application
application = Flask(__name__)

# Configuration
application.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
application.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

@application.route('/')
def home():
    """Home page with environment information"""
    env_info = {
        'timestamp': datetime.now().isoformat(),
        'environment': os.environ.get('ENVIRONMENT', 'development'),
        'instance_id': get_instance_id(),
        'availability_zone': get_availability_zone(),
        'platform': os.environ.get('PLATFORM', 'Python 3.11')
    }
    return render_template('index.html', env_info=env_info)

@application.route('/health')
def health_check():
    """Health check endpoint for load balancer"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }), 200

@application.route('/api/info')
def api_info():
    """API endpoint returning application information"""
    return jsonify({
        'application': 'My Web App',
        'version': '1.0.0',
        'environment': os.environ.get('ENVIRONMENT', 'development'),
        'instance_id': get_instance_id(),
        'uptime': get_uptime()
    })

def get_instance_id():
    """Get EC2 instance ID from metadata service"""
    try:
        import urllib3
        http = urllib3.PoolManager()
        response = http.request('GET', 
            'http://169.254.169.254/latest/meta-data/instance-id',
            timeout=2.0)
        return response.data.decode('utf-8')
    except:
        return 'unknown'

def get_availability_zone():
    """Get availability zone from metadata service"""
    try:
        import urllib3
        http = urllib3.PoolManager()
        response = http.request('GET', 
            'http://169.254.169.254/latest/meta-data/placement/availability-zone',
            timeout=2.0)
        return response.data.decode('utf-8')
    except:
        return 'unknown'

def get_uptime():
    """Get application uptime"""
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            return f"{uptime_seconds:.0f} seconds"
    except:
        return 'unknown'

if __name__ == '__main__':
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    application.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )

# requirements.txt for the Flask application
"""
Flask==2.3.3
boto3==1.35.36
urllib3==2.0.7
"""

# .ebextensions/python.config - Elastic Beanstalk configuration
"""
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: application.py
  aws:elasticbeanstalk:application:environment:
    FLASK_DEBUG: "false"
    ENVIRONMENT: "production"
    PLATFORM: "Python 3.11 on Amazon Linux 2023"
  aws:autoscaling:asg:
    MinSize: 1
    MaxSize: 4
  aws:autoscaling:launchconfiguration:
    InstanceType: t3.small
    SecurityGroups: default
  aws:elasticbeanstalk:healthreporting:system:
    SystemType: enhanced
"""

# Deploy to Elastic Beanstalk using AWS CLI
"""
# Initialize Elastic Beanstalk application
eb init my-web-app --platform python-3.11 --region us-east-1

# Create environment and deploy
eb create production-env --instance-type t3.small --enable-spot

# Deploy new version
eb deploy

# Open application in browser
eb open

# View logs
eb logs

# Check status
eb status

# Terminate environment
eb terminate production-env
"""
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def codedeploy_tab():
    """Content for AWS CodeDeploy tab"""
    st.markdown("## 🚀 AWS CodeDeploy")
    st.markdown("*Automate code deployments to any instance, including EC2 instances and on-premises servers*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **AWS CodeDeploy** is a deployment service that automates application deployments to Amazon EC2 instances, 
    on-premises instances, serverless Lambda functions, or Amazon ECS services. It helps you rapidly release 
    new features, avoid downtime during deployment, and handle the complexity of updating your applications.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # CodeDeploy Workflow
    st.markdown("### 🔄 CodeDeploy Workflow")
    common.mermaid(create_codedeploy_workflow(), height=500)
    
    # Deployment Strategies
    st.markdown("### 🎯 Deployment Strategies")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔄 In-Place Deployment
        - **Same instances** used for deployment
        - **Application stopped** during update
        - **Quick rollback** by redeploying previous version
        - **Lower cost** - no additional instances
        
        **Best for:**
        - Development environments
        - Non-critical applications
        - Cost-sensitive deployments
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔵🟢 Blue/Green Deployment
        - **New instances** provisioned for deployment
        - **Zero downtime** during deployment
        - **Easy rollback** by switching back
        - **Higher cost** - double instances temporarily
        
        **Best for:**
        - Production environments
        - Critical applications
        - Zero-downtime requirements
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📊 Rolling Deployment
        - **Gradual replacement** of instances
        - **Configurable batch size**
        - **Balanced approach** between speed and safety
        - **Moderate cost** - some additional instances
        
        **Best for:**
        - Production with flexibility
        - Large-scale applications
        - Controlled risk deployment
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Deployment Configuration
    st.markdown("### 🛠️ Interactive Deployment Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Application Configuration")
        app_name = st.text_input("Application Name:", "my-web-application")
        compute_platform = st.selectbox("Compute Platform:", [
            "EC2/On-premises", "AWS Lambda", "Amazon ECS"
        ])
        
        if compute_platform == "EC2/On-premises":
            deployment_type = st.selectbox("Deployment Type:", [
                "In-place", "Blue/Green"
            ])
            
            deployment_config = st.selectbox("Deployment Configuration:", [
                "CodeDeployDefault.AllAtOnce",
                "CodeDeployDefault.HalfAtATime", 
                "CodeDeployDefault.OneAtATime",
                "CodeDeployDefault.AllAtOnceBlueGreen",
                "Custom Configuration"
            ])
        
        elif compute_platform == "AWS Lambda":
            deployment_config = st.selectbox("Lambda Deployment Configuration:", [
                "CodeDeployDefault.LambdaAllAtOnce",
                "CodeDeployDefault.LambdaLinear10PercentEvery3Minutes",
                "CodeDeployDefault.LambdaCanary10Percent5Minutes"
            ])
        
        else:  # ECS
            deployment_config = st.selectbox("ECS Deployment Configuration:", [
                "CodeDeployDefault.ECSAllAtOnce",
                "CodeDeployDefault.ECSLinear10PercentEvery1Minutes",
                "CodeDeployDefault.ECSCanary10Percent15Minutes"
            ])
    
    with col2:
        st.markdown("### 🎯 Deployment Group Settings")
        deployment_group = st.text_input("Deployment Group Name:", "production-group")
        
        if compute_platform == "EC2/On-premises":
            target_selection = st.selectbox("Target Selection:", [
                "Auto Scaling Groups", "EC2 Instance Tags", "On-premises Instance Tags"
            ])
            
            if target_selection == "Auto Scaling Groups":
                asg_names = st.text_area("Auto Scaling Group Names:", "my-asg-1\nmy-asg-2")
            else:
                tag_filters = st.text_area("Tag Filters:", "Environment:Production\nApplication:WebApp")
        
        load_balancer = st.checkbox("Enable Load Balancer", value=True, key="load_balancer_2")
        if load_balancer:
            lb_name = st.text_input("Load Balancer Name:", "my-application-lb")
        
        rollback_enabled = st.checkbox("Enable Automatic Rollback", value=True)
        if rollback_enabled:
            rollback_events = st.multiselect("Rollback Events:", [
                "Deployment failure", "Deployment stops", "CloudWatch alarm threshold reached"
            ], default=["Deployment failure"])
    
    # Advanced Settings
    st.markdown("### 🔧 Advanced Deployment Settings")
    
    col3, col4 = st.columns(2)
    with col3:
        cloudwatch_alarms = st.checkbox("CloudWatch Alarms", value=True)
        if cloudwatch_alarms:
            alarm_config = st.text_area("Alarm Names:", "HighErrorRate\nHighLatency")
        
        sns_notifications = st.checkbox("SNS Notifications", value=False)
        if sns_notifications:
            sns_topic = st.text_input("SNS Topic ARN:", "arn:aws:sns:us-east-1:123456789012:deployment-notifications")
    
    with col4:
        trigger_config = st.checkbox("Deployment Triggers", value=False)
        if trigger_config:
            trigger_events = st.multiselect("Trigger Events:", [
                "DeploymentStart", "DeploymentSuccess", "DeploymentFailure", "DeploymentStop"
            ])
        
        timeout_behavior = st.selectbox("Deployment Timeout Action:", [
            "CONTINUE_DEPLOYMENT", "STOP_DEPLOYMENT"
        ])
        timeout_minutes = st.slider("Timeout (minutes):", 5, 480, 60)
    
    if st.button("🚀 Create CodeDeploy Deployment", use_container_width=True):
        # Simulate deployment creation
        deployment_id = f"d-{random.randint(100000, 999999)}"
        estimated_time = random.randint(5, 30)
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ CodeDeploy Deployment Created!
        
        **Deployment Details:**
        - **Application**: {app_name}
        - **Deployment ID**: {deployment_id}
        - **Deployment Group**: {deployment_group}
        - **Platform**: {compute_platform}
        - **Strategy**: {deployment_type if compute_platform == "EC2/On-premises" else "Managed"}
        - **Configuration**: {deployment_config}
        
        **Target Environment:**
        - **Load Balancer**: {'✅ ' + lb_name if load_balancer else '❌ None'}
        - **Auto Rollback**: {'✅ Enabled' if rollback_enabled else '❌ Disabled'}
        - **Timeout**: {timeout_minutes} minutes
        
        **Monitoring:**
        - **CloudWatch Alarms**: {'✅ Enabled' if cloudwatch_alarms else '❌ Disabled'}
        - **SNS Notifications**: {'✅ Enabled' if sns_notifications else '❌ Disabled'}
        
        ⏱️ **Estimated Deployment Time**: {estimated_time} minutes
        📊 **Status**: In Progress - Starting deployment...
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Deployment Configurations Comparison
    st.markdown("### 📊 Deployment Configurations Comparison")
    
    config_data = {
        'Configuration': [
            'AllAtOnce', 'HalfAtATime', 'OneAtATime', 
            'Linear10PercentEvery3Minutes', 'Canary10Percent5Minutes'
        ],
        'Speed': ['Fastest', 'Medium', 'Slowest', 'Slow', 'Medium'],
        'Risk': ['Highest', 'Medium', 'Lowest', 'Low', 'Low'],
        'Rollback Impact': ['High', 'Medium', 'Low', 'Low', 'Low'],
        'Best Use Case': [
            'Dev/Test environments',
            'Balanced production deployments',
            'Critical production systems',
            'Gradual feature rollouts',
            'High-risk deployments with quick validation'
        ]
    }
    
    df_configs = pd.DataFrame(config_data)
    st.dataframe(df_configs, use_container_width=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: CodeDeploy with appspec.yml")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# appspec.yml - CodeDeploy application specification file
version: 0.0
os: linux
files:
  - source: /
    destination: /var/www/html
    overwrite: yes
permissions:
  - object: /var/www/html
    pattern: "**"
    owner: apache
    group: apache
    mode: 755
hooks:
  BeforeInstall:
    - location: scripts/install_dependencies.sh
      timeout: 300
      runas: root
  ApplicationStart:
    - location: scripts/start_server.sh
      timeout: 300
      runas: root
  ApplicationStop:
    - location: scripts/stop_server.sh
      timeout: 300
      runas: root
  ValidateService:
    - location: scripts/validate_service.sh
      timeout: 300
      runas: root

---

# scripts/install_dependencies.sh
#!/bin/bash
yum update -y
yum install -y httpd
yum install -y php
yum install -y mysql

# Install application dependencies
pip3 install -r requirements.txt

# Configure application
cp config/production.conf /etc/httpd/conf.d/
chown apache:apache /var/www/html -R

---

# scripts/start_server.sh
#!/bin/bash
service httpd start
chkconfig httpd on

# Start application services
systemctl start myapp
systemctl enable myapp

# Verify services are running
sleep 10
systemctl status httpd
systemctl status myapp

---

# scripts/stop_server.sh
#!/bin/bash
# Gracefully stop services
systemctl stop myapp
service httpd stop

# Clean up temporary files
rm -rf /tmp/myapp-*

---

# scripts/validate_service.sh
#!/bin/bash
# Health check script
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:80/health)

if [ "$response" -eq 200 ]; then
    echo "Health check passed"
    exit 0
else
    echo "Health check failed with status: $response"
    exit 1
fi

# Additional validation
if pgrep -f "myapp" > /dev/null; then
    echo "Application process is running"
else
    echo "Application process not found"
    exit 1
fi

---

# Python script to create CodeDeploy deployment
import boto3
import json

def create_codedeploy_deployment():
    codedeploy = boto3.client('codedeploy')
    
    try:
        # Create application
        codedeploy.create_application(
            applicationName='MyWebApplication',
            computePlatform='Server'
        )
        
        # Create deployment group
        deployment_group_response = codedeploy.create_deployment_group(
            applicationName='MyWebApplication',
            deploymentGroupName='ProductionGroup',
            serviceRoleArn='arn:aws:iam::123456789012:role/CodeDeployServiceRole',
            deploymentConfigName='CodeDeployDefault.OneAtATime',
            ec2TagFilters=[
                {
                    'Type': 'KEY_AND_VALUE',
                    'Key': 'Environment',
                    'Value': 'Production'
                }
            ],
            autoRollbackConfiguration={
                'enabled': True,
                'events': ['DEPLOYMENT_FAILURE', 'DEPLOYMENT_STOP_ON_ALARM']
            },
            alarmConfiguration={
                'enabled': True,
                'alarms': [
                    {'name': 'HighErrorRate'},
                    {'name': 'HighLatency'}
                ]
            },
            loadBalancerInfo={
                'targetGroupInfoList': [
                    {'name': 'my-target-group'}
                ]
            }
        )
        
        print(f"✅ Deployment group created: {deployment_group_response['deploymentGroupId']}")
        
        # Create deployment
        deployment_response = codedeploy.create_deployment(
            applicationName='MyWebApplication',
            deploymentGroupName='ProductionGroup',
            deploymentConfigName='CodeDeployDefault.OneAtATime',
            revision={
                'revisionType': 'S3',
                's3Location': {
                    'bucket': 'my-codedeploy-bucket',
                    'key': 'myapp-v1.0.zip',
                    'bundleType': 'zip'
                }
            },
            description='Production deployment v1.0',
            ignoreApplicationStopFailures=False,
            autoRollbackConfiguration={
                'enabled': True,
                'events': ['DEPLOYMENT_FAILURE']
            }
        )
        
        deployment_id = deployment_response['deploymentId']
        print(f"🚀 Deployment created: {deployment_id}")
        
        # Monitor deployment status
        monitor_deployment(codedeploy, deployment_id)
        
        return deployment_id
        
    except Exception as e:
        print(f"❌ Error creating deployment: {e}")
        return None

def monitor_deployment(codedeploy, deployment_id):
    """Monitor deployment progress"""
    import time
    
    while True:
        try:
            response = codedeploy.get_deployment(deploymentId=deployment_id)
            deployment = response['deploymentInfo']
            
            status = deployment['status']
            print(f"📊 Deployment Status: {status}")
            
            if status in ['Succeeded', 'Failed', 'Stopped']:
                break
                
            # Show deployment summary
            if 'deploymentOverview' in deployment:
                overview = deployment['deploymentOverview']
                print(f"  In Progress: {overview.get('InProgress', 0)}")
                print(f"  Succeeded: {overview.get('Succeeded', 0)}")
                print(f"  Failed: {overview.get('Failed', 0)}")
            
            time.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            print(f"Error monitoring deployment: {e}")
            break
    
    print(f"✅ Deployment {deployment_id} completed with status: {status}")

# Create and monitor deployment
if __name__ == "__main__":
    deployment_id = create_codedeploy_deployment()
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def ecs_tab():
    """Content for Amazon ECS tab"""
    st.markdown("## 🐳 Amazon Elastic Container Service (ECS)")
    st.markdown("*Highly scalable, fast container management service*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Amazon ECS** is a fully managed container orchestration service that helps you deploy, manage, and scale 
    containerized applications. ECS eliminates the need to install and operate your own container orchestration 
    software, manage and scale a cluster of virtual machines, or schedule containers on those machines.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ECS Architecture
    st.markdown("### 🏗️ ECS Architecture Overview")
    common.mermaid(create_ecs_architecture(), height=700)
    
    # ECS Core Components
    st.markdown("### 🔧 ECS Core Components")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🏢 ECS Cluster
        - **Logical grouping** of compute resources
        - **Can span multiple AZs** for high availability
        - **Supports EC2 and Fargate** launch types
        - **Auto Scaling** and capacity management
        
        ### 📋 Task Definition
        - **Blueprint** for your application
        - **Container specifications** (CPU, memory, ports)
        - **Networking** and storage configurations
        - **IAM roles** and security settings
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 ECS Service
        - **Maintains desired number** of running tasks
        - **Load balancer integration**
        - **Auto Scaling** based on metrics
        - **Rolling deployments** and health checks
        
        ### 📦 ECS Task
        - **Running instance** of a task definition
        - **One or more containers** working together
        - **Ephemeral** - can be stopped and started
        - **Scheduled** or service-managed
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Launch Types
    st.markdown("### 🚀 ECS Launch Types")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🖥️ EC2 Launch Type
        - **Full control** over EC2 instances
        - **Cost optimization** with Reserved/Spot instances
        - **Custom AMIs** and bootstrapping
        - **SSH access** to underlying instances
        
        **Best for:**
        - Cost-sensitive workloads
        - Custom instance configurations
        - GPU/specialized hardware needs
        - Long-running applications
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚡ Fargate Launch Type
        - **Serverless containers** - no EC2 management
        - **Pay per task** execution time
        - **Built-in security** and isolation
        - **Automatic scaling** and patching
        
        **Best for:**
        - Microservices architectures
        - Batch processing jobs
        - Variable workloads
        - Focus on application, not infrastructure
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive ECS Service Configuration
    st.markdown("### 🛠️ Interactive ECS Service Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏗️ Cluster Configuration")
        cluster_name = st.text_input("Cluster Name:", "my-ecs-cluster")
        launch_type = st.selectbox("Launch Type:", ["AWS Fargate", "EC2", "External (ECS Anywhere)"])
        
        if launch_type == "EC2":
            instance_type = st.selectbox("Instance Type:", [
                "t3.micro", "t3.small", "t3.medium", "t3.large",
                "m5.large", "m5.xlarge", "c5.large", "c5.xlarge"
            ])
            cluster_size = st.slider("Initial Cluster Size:", 1, 10, 2)
            auto_scaling = st.checkbox("Enable Cluster Auto Scaling", value=True)
        
        vpc_config = st.selectbox("VPC Configuration:", [
            "Default VPC", "Custom VPC", "Create New VPC"
        ])
    
    with col2:
        st.markdown("### 📋 Task Definition")
        task_family = st.text_input("Task Definition Family:", "my-web-app")
        
        # Container Configuration
        container_name = st.text_input("Container Name:", "web-server")
        container_image = st.text_input("Container Image:", "nginx:latest")
        
        if launch_type == "AWS Fargate":
            cpu_units = st.selectbox("CPU Units:", ["256", "512", "1024", "2048", "4096"])
            memory_mb = st.selectbox("Memory (MB):", ["512", "1024", "2048", "4096", "8192"])
        else:
            cpu_units = st.slider("CPU Units:", 128, 4096, 512)
            memory_mb = st.slider("Memory (MB):", 128, 8192, 1024)
        
        port_mappings = st.text_area("Port Mappings (container:host):", "80:80\n443:443")
    
    # Service Configuration
    st.markdown("### 🎯 Service Configuration")
    
    col3, col4 = st.columns(2)
    
    with col3:
        service_name = st.text_input("Service Name:", f"{task_family}-service")
        desired_count = st.slider("Desired Task Count:", 1, 20, 2)
        
        deployment_config = st.selectbox("Deployment Configuration:", [
            "Rolling update", "Blue/green", "External"
        ])
        
        if deployment_config == "Rolling update":
            min_healthy_percent = st.slider("Minimum Healthy Percent:", 0, 100, 50)
            max_percent = st.slider("Maximum Percent:", 100, 200, 200)
    
    with col4:
        load_balancer = st.checkbox("Enable Load Balancer", value=True)
        if load_balancer:
            lb_type = st.selectbox("Load Balancer Type:", [
                "Application Load Balancer", "Network Load Balancer"
            ])
            target_group = st.text_input("Target Group Name:", f"{service_name}-tg")
        
        auto_scaling_service = st.checkbox("Enable Service Auto Scaling", value=True)
        if auto_scaling_service:
            min_capacity = st.slider("Min Capacity:", 1, 50, 1)
            max_capacity = st.slider("Max Capacity:", 1, 100, 10)
            target_cpu = st.slider("Target CPU Utilization (%):", 10, 90, 70)
    
    if st.button("🚀 Create ECS Service", use_container_width=True):
        # Calculate estimated costs
        if launch_type == "AWS Fargate":
            cpu_cost = int(cpu_units) * 0.04048 / 1024 * 24 * 30  # per month
            mem_cost = int(memory_mb) * 0.004445 / 1024 * 24 * 30  # per month
            monthly_cost = (cpu_cost + mem_cost) * desired_count
        else:
            # Simplified EC2 cost calculation
            instance_costs = {"t3.micro": 8.76, "t3.small": 17.52, "t3.medium": 35.04, "t3.large": 70.08}
            monthly_cost = instance_costs.get(instance_type, 35.04) * cluster_size
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ ECS Service Configuration Complete!
        
        **Cluster Details:**
        - **Cluster**: {cluster_name}
        - **Launch Type**: {launch_type}
        {"- **Instance Type**: " + instance_type if launch_type == "EC2" else ""}
        {"- **Cluster Size**: " + str(cluster_size) if launch_type == "EC2" else ""}
        
        **Task Definition:**
        - **Family**: {task_family}
        - **CPU**: {cpu_units} units
        - **Memory**: {memory_mb} MB
        - **Container**: {container_name} ({container_image})
        
        **Service Configuration:**
        - **Service**: {service_name}
        - **Desired Count**: {desired_count} tasks
        - **Deployment**: {deployment_config}
        - **Load Balancer**: {'✅ ' + lb_type if load_balancer else '❌ None'}
        - **Auto Scaling**: {'✅ Enabled' if auto_scaling_service else '❌ Disabled'}
        
        **Estimated Monthly Cost:** ${monthly_cost:.2f}
        
        🔧 **Next Steps:**
        1. Review task definition JSON
        2. Configure networking and security groups
        3. Set up CloudWatch logging
        4. Deploy and monitor service health
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ECS vs EKS Comparison
    st.markdown("### ⚖️ ECS vs EKS Comparison")
    
    comparison_data = {
        'Feature': ['Learning Curve', 'AWS Integration', 'Kubernetes Compatibility', 'Cost', 'Ecosystem', 'Flexibility'],
        'Amazon ECS': ['Easy', 'Native', 'No', 'Lower', 'AWS-focused', 'Good'],
        'Amazon EKS': ['Steep', 'Good', 'Full', 'Higher', 'CNCF/K8s', 'Excellent'],
        'Best Choice': [
            'ECS for AWS-first teams',
            'ECS for tight AWS integration', 
            'EKS for K8s workloads',
            'ECS for cost optimization',
            'EKS for open-source tools',
            'EKS for complex orchestration'
        ]
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: ECS Service with Fargate")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Create ECS cluster, task definition, and service using boto3
import boto3
import json

def create_ecs_infrastructure():
    ecs = boto3.client('ecs')
    ec2 = boto3.client('ec2')
    elbv2 = boto3.client('elbv2')
    
    cluster_name = 'my-web-cluster'
    service_name = 'web-service'
    task_family = 'web-app-task'
    
    try:
        # 1. Create ECS Cluster
        print("🏗️ Creating ECS cluster...")
        cluster_response = ecs.create_cluster(
            clusterName=cluster_name,
            tags=[
                {'key': 'Environment', 'value': 'Production'},
                {'key': 'Application', 'value': 'WebApp'}
            ],
            capacityProviders=['FARGATE', 'FARGATE_SPOT'],
            defaultCapacityProviderStrategy=[
                {
                    'capacityProvider': 'FARGATE',
                    'weight': 1,
                    'base': 1
                },
                {
                    'capacityProvider': 'FARGATE_SPOT',
                    'weight': 4,
                    'base': 0
                }
            ]
        )
        
        cluster_arn = cluster_response['cluster']['clusterArn']
        print(f"✅ Cluster created: {cluster_arn}")
        
        # 2. Create Task Definition
        print("📋 Creating task definition...")
        task_definition = {
            'family': task_family,
            'networkMode': 'awsvpc',
            'requiresCompatibilities': ['FARGATE'],
            'cpu': '512',
            'memory': '1024',
            'executionRoleArn': 'arn:aws:iam::123456789012:role/ecsTaskExecutionRole',
            'taskRoleArn': 'arn:aws:iam::123456789012:role/ecsTaskRole',
            'containerDefinitions': [
                {
                    'name': 'web-server',
                    'image': 'nginx:latest',
                    'portMappings': [
                        {
                            'containerPort': 80,
                            'protocol': 'tcp'
                        }
                    ],
                    'essential': True,
                    'logConfiguration': {
                        'logDriver': 'awslogs',
                        'options': {
                            'awslogs-group': f'/ecs/{task_family}',
                            'awslogs-region': 'us-east-1',
                            'awslogs-stream-prefix': 'ecs'
                        }
                    },
                    'environment': [
                        {'name': 'ENVIRONMENT', 'value': 'production'},
                        {'name': 'APP_NAME', 'value': 'my-web-app'}
                    ],
                    'healthCheck': {
                        'command': ['CMD-SHELL', 'curl -f http://localhost/ || exit 1'],
                        'interval': 30,
                        'timeout': 5,
                        'retries': 3,
                        'startPeriod': 60
                    }
                }
            ]
        }
        
        task_response = ecs.register_task_definition(**task_definition)
        task_arn = task_response['taskDefinition']['taskDefinitionArn']
        print(f"✅ Task definition created: {task_arn}")
        
        # 3. Create Application Load Balancer
        print("⚖️ Creating load balancer...")
        
        # Get default VPC and subnets
        vpc_response = ec2.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])
        vpc_id = vpc_response['Vpcs'][0]['VpcId']
        
        subnets_response = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
        subnet_ids = [subnet['SubnetId'] for subnet in subnets_response['Subnets'][:2]]
        
        # Create security group for load balancer
        sg_response = ec2.create_security_group(
            GroupName='ecs-alb-sg',
            Description='Security group for ECS ALB',
            VpcId=vpc_id
        )
        alb_sg_id = sg_response['GroupId']
        
        # Allow HTTP traffic
        ec2.authorize_security_group_ingress(
            GroupId=alb_sg_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                }
            ]
        )
        
        # Create ALB
        alb_response = elbv2.create_load_balancer(
            Name='ecs-web-alb',
            Subnets=subnet_ids,
            SecurityGroups=[alb_sg_id],
            Scheme='internet-facing',
            Type='application',
            IpAddressType='ipv4'
        )
        
        alb_arn = alb_response['LoadBalancers'][0]['LoadBalancerArn']
        alb_dns = alb_response['LoadBalancers'][0]['DNSName']
        
        # Create target group
        tg_response = elbv2.create_target_group(
            Name='ecs-web-tg',
            Protocol='HTTP',
            Port=80,
            VpcId=vpc_id,
            HealthCheckProtocol='HTTP',
            HealthCheckPath='/',
            HealthCheckIntervalSeconds=30,
            HealthyThresholdCount=2,
            UnhealthyThresholdCount=5,
            TargetType='ip'
        )
        
        tg_arn = tg_response['TargetGroups'][0]['TargetGroupArn']
        
        # Create listener
        elbv2.create_listener(
            LoadBalancerArn=alb_arn,
            Protocol='HTTP',
            Port=80,
            DefaultActions=[
                {
                    'Type': 'forward',
                    'TargetGroupArn': tg_arn
                }
            ]
        )
        
        print(f"✅ Load balancer created: {alb_dns}")
        
        # 4. Create security group for ECS tasks
        ecs_sg_response = ec2.create_security_group(
            GroupName='ecs-tasks-sg',
            Description='Security group for ECS tasks',
            VpcId=vpc_id
        )
        ecs_sg_id = ecs_sg_response['GroupId']
        
        # Allow traffic from ALB
        ec2.authorize_security_group_ingress(
            GroupId=ecs_sg_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 80,
                    'ToPort': 80,
                    'UserIdGroupPairs': [{'GroupId': alb_sg_id}]
                }
            ]
        )
        
        # 5. Create ECS Service
        print("🎯 Creating ECS service...")
        service_response = ecs.create_service(
            cluster=cluster_name,
            serviceName=service_name,
            taskDefinition=task_family,
            desiredCount=2,
            launchType='FARGATE',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': subnet_ids,
                    'securityGroups': [ecs_sg_id],
                    'assignPublicIp': 'ENABLED'
                }
            },
            loadBalancers=[
                {
                    'targetGroupArn': tg_arn,
                    'containerName': 'web-server',
                    'containerPort': 80
                }
            ],
            deploymentConfiguration={
                'maximumPercent': 200,
                'minimumHealthyPercent': 50,
                'deploymentCircuitBreaker': {
                    'enable': True,
                    'rollback': True
                }
            },
            enableExecuteCommand=True,
            tags=[
                {'key': 'Environment', 'value': 'Production'},
                {'key': 'Application', 'value': 'WebApp'}
            ]
        )
        
        service_arn = service_response['service']['serviceArn']
        print(f"✅ Service created: {service_arn}")
        
        # 6. Configure Auto Scaling
        print("📈 Setting up auto scaling...")
        autoscaling = boto3.client('application-autoscaling')
        
        # Register scalable target
        autoscaling.register_scalable_target(
            ServiceNamespace='ecs',
            ResourceId=f'service/{cluster_name}/{service_name}',
            ScalableDimension='ecs:service:DesiredCount',
            MinCapacity=1,
            MaxCapacity=10,
            RoleArn='arn:aws:iam::123456789012:role/application-autoscaling-ecs-service'
        )
        
        # Create scaling policy
        autoscaling.put_scaling_policy(
            PolicyName='cpu-scaling-policy',
            ServiceNamespace='ecs',
            ResourceId=f'service/{cluster_name}/{service_name}',
            ScalableDimension='ecs:service:DesiredCount',
            PolicyType='TargetTrackingScaling',
            TargetTrackingScalingPolicyConfiguration={
                'TargetValue': 70.0,
                'PredefinedMetricSpecification': {
                    'PredefinedMetricType': 'ECSServiceAverageCPUUtilization'
                },
                'ScaleOutCooldown': 300,
                'ScaleInCooldown': 300
            }
        )
        
        print("✅ Auto scaling configured")
        
        return {
            'cluster_arn': cluster_arn,
            'service_arn': service_arn,
            'task_definition_arn': task_arn,
            'load_balancer_dns': alb_dns,
            'status': 'created'
        }
        
    except Exception as e:
        print(f"❌ Error creating ECS infrastructure: {e}")
        return None

def monitor_service_health(cluster_name, service_name):
    """Monitor ECS service health and status"""
    ecs = boto3.client('ecs')
    
    try:
        response = ecs.describe_services(
            cluster=cluster_name,
            services=[service_name]
        )
        
        service = response['services'][0]
        
        print(f"📊 Service Status: {service['status']}")
        print(f"Running Tasks: {service['runningCount']}")
        print(f"Pending Tasks: {service['pendingCount']}")
        print(f"Desired Tasks: {service['desiredCount']}")
        
        # Check deployment status
        for deployment in service['deployments']:
            print(f"\n🚀 Deployment Status: {deployment['status']}")
            print(f"Running Count: {deployment['runningCount']}")
            print(f"Desired Count: {deployment['desiredCount']}")
            
        # Get task health
        tasks_response = ecs.list_tasks(
            cluster=cluster_name,
            serviceName=service_name
        )
        
        if tasks_response['taskArns']:
            task_details = ecs.describe_tasks(
                cluster=cluster_name,
                tasks=tasks_response['taskArns']
            )
            
            print(f"\n📋 Task Details:")
            for task in task_details['tasks']:
                print(f"  Task: {task['taskArn'].split('/')[-1]}")
                print(f"  Status: {task['lastStatus']}")
                print(f"  Health: {task.get('healthStatus', 'UNKNOWN')}")
                print()
        
    except Exception as e:
        print(f"Error monitoring service: {e}")

# Create the ECS infrastructure
if __name__ == "__main__":
    result = create_ecs_infrastructure()
    if result:
        print(f"🌐 Application URL: http://{result['load_balancer_dns']}")
        
        # Monitor service health
        import time
        time.sleep(60)  # Wait for service to start
        monitor_service_health('my-web-cluster', 'web-service')
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def eks_tab():
    """Content for Amazon EKS tab"""
    st.markdown("## ☸️ Amazon Elastic Kubernetes Service (EKS)")
    st.markdown("*Managed Kubernetes service to run Kubernetes in the AWS cloud and on-premises*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Amazon EKS** is a managed service that makes it easy for you to run Kubernetes on AWS without needing 
    to install, operate, and maintain your own Kubernetes control plane or nodes. EKS runs upstream Kubernetes 
    and is certified Kubernetes conformant, so existing applications running on upstream Kubernetes are compatible with Amazon EKS.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # EKS Architecture
    st.markdown("### 🏗️ EKS Architecture Overview")
    common.mermaid(create_eks_architecture(), height=500)
    
    # EKS Components
    st.markdown("### 🔧 EKS Core Components")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎛️ EKS Control Plane
        - **Managed Kubernetes API server**
        - **etcd** distributed key-value store
        - **Multi-AZ** deployment for high availability
        - **Automatic updates** and security patches
        
        ### 👥 Worker Node Groups
        - **Managed node groups** - AWS managed EC2 instances
        - **Self-managed nodes** - you manage EC2 instances
        - **Fargate pods** - serverless compute for pods
        - **Auto Scaling** and spot instance support
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🌐 Networking
        - **VPC CNI** - native AWS networking
        - **Pod-to-pod** communication
        - **Service discovery** with CoreDNS
        - **Load balancer** integration (ALB, NLB)
        
        ### 🔒 Security & Identity
        - **IAM integration** for authentication
        - **RBAC** (Role-Based Access Control)
        - **Pod Security Standards**
        - **Network policies** and encryption
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # EKS Node Types
    st.markdown("### 🚀 EKS Node Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🛠️ Managed Node Groups
        - **AWS managed** EC2 instances
        - **Automatic updates** and patching
        - **Auto Scaling Group** integration
        - **Spot instance** support
        
        **Best for:**
        - Standard workloads
        - Simplified management
        - Cost optimization with Spot
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚙️ Self-Managed Nodes
        - **Full control** over EC2 instances
        - **Custom AMIs** and configurations
        - **Advanced networking** setups
        - **Specialized hardware** (GPU, etc.)
        
        **Best for:**
        - Custom requirements
        - Legacy applications
        - Specialized workloads
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚡ Fargate Pods
        - **Serverless compute** for pods
        - **No node management** required
        - **Pay per pod** execution time
        - **Isolated compute** environment
        
        **Best for:**
        - Microservices
        - Batch jobs
        - Variable workloads
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive EKS Cluster Configuration
    st.markdown("### 🛠️ Interactive EKS Cluster Setup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏗️ Cluster Configuration")
        cluster_name = st.text_input("Cluster Name:", "my-eks-cluster")
        k8s_version = st.selectbox("Kubernetes Version:", [
            "1.28", "1.27", "1.26", "1.25"
        ])
        
        region = st.selectbox("AWS Region:", [
            "us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"
        ])
        
        vpc_config = st.selectbox("VPC Configuration:", [
            "Create new VPC", "Use existing VPC", "Use default VPC"
        ])
        
        endpoint_access = st.multiselect("API Server Endpoint Access:", [
            "Public", "Private"
        ], default=["Public"])
        
        logging_types = st.multiselect("Control Plane Logs:", [
            "API", "Audit", "Authenticator", "ControllerManager", "Scheduler"
        ], default=["API", "Audit"])
    
    with col2:
        st.markdown("### 👥 Node Group Configuration")
        node_group_name = st.text_input("Node Group Name:", "standard-workers")
        node_type = st.selectbox("Node Type:", [
            "Managed Node Group", "Self-Managed Nodes", "Fargate Profile"
        ])
        
        if node_type != "Fargate Profile":
            instance_types = st.multiselect("Instance Types:", [
                "t3.medium", "t3.large", "m5.large", "m5.xlarge", 
                "c5.large", "c5.xlarge", "r5.large"
            ], default=["t3.medium"])
            
            capacity_type = st.selectbox("Capacity Type:", [
                "ON_DEMAND", "SPOT", "MIXED"
            ])
            
            scaling_config = st.columns(3)
            with scaling_config[0]:
                min_size = st.number_input("Min Size:", 1, 100, 1)
            with scaling_config[1]:
                max_size = st.number_input("Max Size:", 1, 100, 10)
            with scaling_config[2]:
                desired_size = st.number_input("Desired Size:", 1, 100, 3)
        
        else:  # Fargate Profile
            fargate_namespace = st.text_input("Namespace Pattern:", "default")
            fargate_labels = st.text_area("Pod Labels:", "app: web\nenv: production")
    
    # Add-ons Configuration
    st.markdown("### 🔌 EKS Add-ons")
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("### 🌐 Networking Add-ons")
        vpc_cni = st.checkbox("Amazon VPC CNI", value=True)
        if vpc_cni:
            cni_version = st.selectbox("VPC CNI Version:", ["v1.14.1-eksbuild.1", "v1.13.4-eksbuild.1"])
        
        coredns = st.checkbox("CoreDNS", value=True)
        if coredns:
            coredns_version = st.selectbox("CoreDNS Version:", ["v1.10.1-eksbuild.1", "v1.9.3-eksbuild.1"])
    
    with col4:
        st.markdown("### 🛡️ Security & Observability")
        kube_proxy = st.checkbox("kube-proxy", value=True)
        ebs_csi = st.checkbox("Amazon EBS CSI Driver", value=False)
        cloudwatch_observability = st.checkbox("CloudWatch Observability", value=False)
        
        # Additional tools
        aws_lb_controller = st.checkbox("AWS Load Balancer Controller", value=True)
        cluster_autoscaler = st.checkbox("Cluster Autoscaler", value=True)
    
    if st.button("🚀 Create EKS Cluster", use_container_width=True):
        # Calculate estimated costs
        control_plane_cost = 0.10 * 24 * 30  # $0.10/hour
        
        if node_type == "Fargate Profile":
            # Fargate pricing is per vCPU-hour and per GB-hour
            estimated_cost = control_plane_cost + 50  # Simplified estimate
            node_info = f"Fargate Profile: {fargate_namespace}"
        else:
            # EC2 node pricing (simplified)
            instance_costs = {
                "t3.medium": 30.37, "t3.large": 60.74, "m5.large": 70.08,
                "m5.xlarge": 140.16, "c5.large": 62.56, "c5.xlarge": 125.12
            }
            base_cost = instance_costs.get(instance_types[0], 60.74)
            if capacity_type == "SPOT":
                base_cost *= 0.3  # Spot discount
            estimated_cost = control_plane_cost + (base_cost * desired_size)
            node_info = f"{node_type}: {desired_size} x {instance_types[0]}"
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ EKS Cluster Configuration Complete!
        
        **Cluster Details:**
        - **Name**: {cluster_name}
        - **Kubernetes Version**: {k8s_version}
        - **Region**: {region}
        - **Endpoint Access**: {', '.join(endpoint_access)}
        - **Control Plane Logs**: {', '.join(logging_types)}
        
        **Compute Configuration:**
        - **Node Configuration**: {node_info}
        - **Capacity Type**: {capacity_type if node_type != "Fargate Profile" else "Serverless"}
        
        **Add-ons Enabled:**
        - **VPC CNI**: {'✅' if vpc_cni else '❌'}
        - **CoreDNS**: {'✅' if coredns else '❌'}
        - **kube-proxy**: {'✅' if kube_proxy else '❌'}
        - **AWS Load Balancer Controller**: {'✅' if aws_lb_controller else '❌'}
        - **Cluster Autoscaler**: {'✅' if cluster_autoscaler else '❌'}
        
        **Estimated Monthly Cost**: ${estimated_cost:.2f}
        
        ⏱️ **Cluster Creation Time**: 10-15 minutes
        📋 **Next Steps**: Configure kubectl, deploy applications, set up monitoring
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # EKS vs ECS Decision Matrix
    st.markdown("### 🤔 When to Choose EKS vs ECS")
    
    decision_data = {
        'Criteria': [
            'Kubernetes Experience',
            'Ecosystem Requirements', 
            'Multi-Cloud Strategy',
            'Complex Orchestration',
            'AWS-Native Integration',
            'Learning Curve',
            'Operational Overhead',
            'Cost Sensitivity'
        ],
        'Choose EKS If': [
            'Team has K8s expertise',
            'Need CNCF ecosystem tools',
            'Planning multi-cloud deployment',
            'Complex scheduling requirements',
            'Moderate AWS integration needs',
            'Can invest in K8s learning',
            'Have dedicated DevOps team',
            'Cost is secondary to features'
        ],
        'Choose ECS If': [
            'New to container orchestration',
            'AWS-first approach',
            'Single cloud deployment',
            'Simple container orchestration',
            'Deep AWS service integration',
            'Want quick start',
            'Prefer managed services',
            'Cost optimization is priority'
        ]
    }
    
    df_decision = pd.DataFrame(decision_data)
    st.dataframe(df_decision, use_container_width=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: EKS Cluster with Terraform")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# main.tf - Terraform configuration for EKS cluster
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# Data sources
data "aws_availability_zones" "available" {
  filter {
    name   = "opt-in-status"
    values = ["opt-in-not-required"]
  }
}

data "aws_caller_identity" "current" {}

# VPC for EKS cluster
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.cluster_name}-vpc"
  cidr = "10.0.0.0/16"

  azs             = slice(data.aws_availability_zones.available.names, 0, 3)
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.4.0/24", "10.0.5.0/24", "10.0.6.0/24"]

  enable_nat_gateway   = true
  single_nat_gateway   = false
  enable_dns_hostnames = true
  enable_dns_support   = true

  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
  }

  tags = {
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
  }
}

# EKS Cluster
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = var.cluster_name
  cluster_version = var.kubernetes_version

  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = true

  # EKS Managed Node Groups
  eks_managed_node_groups = {
    blue = {
      name = "blue-node-group"
      
      instance_types = ["t3.medium"]
      capacity_type  = "ON_DEMAND"
      
      min_size     = 1
      max_size     = 10
      desired_size = 3

      # Launch template configuration
      launch_template_name        = "${var.cluster_name}-blue"
      launch_template_description = "EKS managed node group launch template"
      
      update_config = {
        max_unavailable_percentage = 33
      }

      labels = {
        Environment = "production"
        NodeGroup   = "blue"
      }

      taints = {
        dedicated = {
          key    = "dedicated"
          value  = "blue"
          effect = "NO_SCHEDULE"
        }
      }

      tags = {
        ExtraTag = "EKS managed node group"
      }
    }

    green = {
      name = "green-node-group"
      
      instance_types = ["t3.medium"]
      capacity_type  = "SPOT"
      
      min_size     = 0
      max_size     = 5
      desired_size = 1

      labels = {
        Environment = "production"
        NodeGroup   = "green"
      }

      tags = {
        ExtraTag = "EKS managed node group - Spot instances"
      }
    }
  }

  # Fargate Profile
  fargate_profiles = {
    default = {
      name = "default"
      selectors = [
        {
          namespace = "default"
          labels = {
            app = "web"
          }
        },
        {
          namespace = "kube-system"
          labels = {
            k8s-app = "kube-dns"
          }
        }
      ]

      tags = {
        Owner = "test"
      }

      timeouts = {
        create = "20m"
        delete = "20m"
      }
    }
  }

  # EKS Add-ons
  cluster_addons = {
    coredns = {
      most_recent = true
      resolve_conflicts = "OVERWRITE"
    }
    kube-proxy = {
      most_recent = true
      resolve_conflicts = "OVERWRITE"
    }
    vpc-cni = {
      most_recent = true
      resolve_conflicts = "OVERWRITE"
    }
    aws-ebs-csi-driver = {
      most_recent = true
      resolve_conflicts = "OVERWRITE"
    }
  }

  # Cluster access entry
  enable_cluster_creator_admin_permissions = true

  tags = {
    Environment = "production"
    Terraform   = "true"
  }
}

# Kubernetes provider configuration
provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args        = ["eks", "get-token", "--cluster-name", module.eks.cluster_name]
  }
}

# Sample application deployment
resource "kubernetes_deployment" "nginx" {
  metadata {
    name = "nginx-deployment"
    labels = {
      app = "nginx"
    }
  }

  spec {
    replicas = 3

    selector {
      match_labels = {
        app = "nginx"
      }
    }

    template {
      metadata {
        labels = {
          app = "nginx"
        }
      }

      spec {
        container {
          image = "nginx:1.25.2"
          name  = "nginx"

          port {
            container_port = 80
          }

          resources {
            limits = {
              cpu    = "0.5"
              memory = "512Mi"
            }
            requests = {
              cpu    = "250m"
              memory = "256Mi"
            }
          }

          liveness_probe {
            http_get {
              path = "/"
              port = 80
            }
            initial_delay_seconds = 30
            period_seconds        = 10
          }

          readiness_probe {
            http_get {
              path = "/"
              port = 80
            }
            initial_delay_seconds = 5
            period_seconds        = 5
          }
        }
      }
    }
  }
}

# Service to expose the deployment
resource "kubernetes_service" "nginx" {
  metadata {
    name = "nginx-service"
  }

  spec {
    selector = {
      app = "nginx"
    }

    port {
      port        = 80
      target_port = 80
    }

    type = "LoadBalancer"
  }
}

# Variables
variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "my-eks-cluster"
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28"
}

# Outputs
output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "Security group ids attached to the cluster control plane"
  value       = module.eks.cluster_security_group_id
}

output "kubectl_config" {
  description = "kubectl config as generated by the module"
  value       = "aws eks update-kubeconfig --region ${var.region} --name ${module.eks.cluster_name}"
}

output "nginx_load_balancer" {
  description = "Load balancer hostname"
  value       = kubernetes_service.nginx.status.0.load_balancer.0.ingress.0.hostname
}

# Deploy with Terraform
"""
# Initialize Terraform
terraform init

# Plan the deployment
terraform plan

# Apply the configuration
terraform apply

# Get kubectl config
aws eks update-kubeconfig --region us-east-1 --name my-eks-cluster

# Verify the cluster
kubectl get nodes
kubectl get pods --all-namespaces

# Access the nginx service
kubectl get service nginx-service

# Clean up resources
terraform destroy
"""
    ''', language='hcl')
    st.markdown('</div>', unsafe_allow_html=True)

def cloudformation_tab():
    """Content for AWS CloudFormation tab"""
    st.markdown("## 📋 AWS CloudFormation")
    st.markdown("*Create templates of your infrastructure and provision AWS resources*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **AWS CloudFormation** provides a common language for you to model and provision AWS and third-party 
    application resources in your cloud environment. CloudFormation allows you to use programming languages 
    or a simple text file to model and provision, in an automated and secure manner, all the resources 
    needed for your applications across all regions and accounts.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # CloudFormation Workflow
    st.markdown("### 🔄 CloudFormation Workflow")
    common.mermaid(create_cloudformation_workflow(), height=750)
    
    # Template Structure
    st.markdown("### 📝 CloudFormation Template Structure")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🏗️ Required Sections
        - **AWSTemplateFormatVersion**: Template format version
        - **Resources**: AWS resources to create (REQUIRED)
        
        ### 📋 Optional Sections
        - **Description**: Template description
        - **Parameters**: Input values for template
        - **Mappings**: Static lookup tables
        - **Conditions**: Control resource creation
        - **Outputs**: Return values from stack
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔧 Template Formats
        - **JSON**: JavaScript Object Notation
        - **YAML**: Yet Another Markup Language
        
        ### 🎯 Key Benefits
        - **Infrastructure as Code** (IaC)
        - **Version control** for infrastructure
        - **Repeatable deployments**
        - **Rollback capabilities**
        - **Change set** preview
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Template Builder
    st.markdown("### 🛠️ Interactive CloudFormation Template Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Template Configuration")
        template_name = st.text_input("Template Name:", "web-infrastructure")
        template_description = st.text_area("Description:", 
            "CloudFormation template for web application infrastructure")
        
        template_format = st.selectbox("Template Format:", ["YAML", "JSON"])
        
        # Parameters
        st.markdown("### 🔧 Parameters")
        add_params = st.checkbox("Add Parameters", value=True)
        if add_params:
            param_configs = []
            
            env_param = st.checkbox("Environment Parameter", value=True)
            if env_param:
                param_configs.append("Environment")
            
            instance_param = st.checkbox("Instance Type Parameter", value=True)
            if instance_param:
                param_configs.append("InstanceType")
            
            key_param = st.checkbox("Key Pair Parameter", value=True)
            if key_param:
                param_configs.append("KeyPair")
    
    with col2:
        st.markdown("### 🏗️ Resources to Include")
        
        # Infrastructure Resources
        vpc_resources = st.checkbox("VPC Network Resources", value=True)
        if vpc_resources:
            vpc_cidr = st.text_input("VPC CIDR:", "10.0.0.0/16")
            num_azs = st.slider("Number of AZs:", 1, 3, 2)
        
        compute_resources = st.checkbox("Compute Resources", value=True)
        if compute_resources:
            ec2_instances = st.checkbox("EC2 Instances", value=True)
            auto_scaling = st.checkbox("Auto Scaling Group", value=True)
            load_balancer = st.checkbox("Application Load Balancer", value=True)
        
        storage_resources = st.checkbox("Storage Resources", value=False)
        if storage_resources:
            s3_bucket = st.checkbox("S3 Bucket", value=True)
            rds_database = st.checkbox("RDS Database", value=False)
        
        security_resources = st.checkbox("Security Resources", value=True)
        if security_resources:
            security_groups = st.checkbox("Security Groups", value=True)
            iam_roles = st.checkbox("IAM Roles", value=True)
    
    # Advanced Configuration
    st.markdown("### 🔧 Advanced Configuration")
    
    col3, col4 = st.columns(2)
    
    with col3:
        add_mappings = st.checkbox("Add Mappings", value=False)
        if add_mappings:
            mapping_type = st.selectbox("Mapping Type:", [
                "AMI IDs by Region", "Environment Configuration", "Instance Type Configuration"
            ])
        
        add_conditions = st.checkbox("Add Conditions", value=False)
        if add_conditions:
            condition_type = st.selectbox("Condition Type:", [
                "Environment-based", "Feature flags", "Resource size conditions"
            ])
    
    with col4:
        add_outputs = st.checkbox("Add Outputs", value=True)
        if add_outputs:
            output_types = st.multiselect("Output Types:", [
                "VPC ID", "Subnet IDs", "Security Group IDs", 
                "Load Balancer DNS", "Instance IDs"
            ], default=["VPC ID", "Load Balancer DNS"])
        
        stack_policy = st.checkbox("Add Stack Policy", value=False)
        termination_protection = st.checkbox("Enable Termination Protection", value=True)
    
    if st.button("🚀 Generate CloudFormation Template", use_container_width=True):
        # Generate template preview
        resource_count = 0
        
        if vpc_resources:
            resource_count += 5 + (num_azs * 2)  # VPC, IGW, subnets, route tables
        if ec2_instances:
            resource_count += 1
        if auto_scaling:
            resource_count += 2  # ASG + Launch Template
        if load_balancer:
            resource_count += 3  # ALB + Target Group + Listener
        if s3_bucket:
            resource_count += 1
        if rds_database:
            resource_count += 2  # DB + Subnet Group
        if security_groups:
            resource_count += 2  # Web and DB security groups
        if iam_roles:
            resource_count += 2  # Role + Instance Profile
        
        estimated_time = max(5, resource_count * 1.5)  # Rough estimate
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ CloudFormation Template Generated!
        
        **Template Details:**
        - **Name**: {template_name}
        - **Format**: {template_format}
        - **Description**: {template_description}
        - **Estimated Resources**: {resource_count}
        
        **Included Components:**
        - **VPC Network**: {'✅' if vpc_resources else '❌'}
        - **Compute Resources**: {'✅' if compute_resources else '❌'}
        - **Storage Resources**: {'✅' if storage_resources else '❌'}
        - **Security Resources**: {'✅' if security_resources else '❌'}
        - **Parameters**: {'✅' if add_params else '❌'}
        - **Outputs**: {'✅' if add_outputs else '❌'}
        
        **Stack Configuration:**
        - **Termination Protection**: {'✅ Enabled' if termination_protection else '❌ Disabled'}
        - **Estimated Deployment Time**: {estimated_time:.0f} minutes
        
        📁 **Next Steps**: Review template, validate syntax, deploy stack
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Stack Lifecycle
    st.markdown("### 🔄 CloudFormation Stack Lifecycle")
    
    lifecycle_data = {
        'Operation': ['Create', 'Update', 'Delete', 'Rollback'],
        'Description': [
            'Create new stack from template',
            'Modify existing stack resources',
            'Remove stack and all resources',
            'Revert to previous stable state'
        ],
        'Typical Duration': ['5-30 minutes', '5-30 minutes', '5-15 minutes', '5-20 minutes'],
        'Risk Level': ['Medium', 'High', 'Low', 'Low'],
        'Best Practice': [
            'Use parameters for flexibility',
            'Use change sets to preview',
            'Ensure no dependencies exist',
            'Enable automatic rollback'
        ]
    }
    
    df_lifecycle = pd.DataFrame(lifecycle_data)
    st.dataframe(df_lifecycle, use_container_width=True)
    
    # CloudFormation vs Other IaC Tools
    st.markdown("### ⚖️ CloudFormation vs Other IaC Tools")
    
    comparison_data = {
        'Feature': ['Cloud Support', 'Learning Curve', 'State Management', 'Cost', 'AWS Integration', 'Community'],
        'CloudFormation': ['AWS Only', 'Medium', 'AWS Managed', 'Free', 'Native', 'Large'],
        'Terraform': ['Multi-Cloud', 'Steep', 'Self-Managed', 'Free/Paid', 'Good', 'Very Large'],
        'AWS CDK': ['AWS Focus', 'Medium', 'CF Backend', 'Free', 'Native', 'Growing'],
        'Pulumi': ['Multi-Cloud', 'Medium', 'Cloud Backend', 'Free/Paid', 'Good', 'Medium']
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Complete Web Infrastructure Template")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# web-infrastructure.yaml - Complete CloudFormation template
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Complete web application infrastructure with VPC, ALB, Auto Scaling, and RDS'

Parameters:
  Environment:
    Type: String
    Default: production
    AllowedValues: [development, staging, production]
    Description: Environment name
  
  InstanceType:
    Type: String
    Default: t3.micro
    AllowedValues: [t3.micro, t3.small, t3.medium, m5.large]
    Description: EC2 instance type
  
  KeyPairName:
    Type: AWS::EC2::KeyPair::KeyName
    Description: EC2 Key Pair for SSH access
  
  DBUsername:
    Type: String
    Default: admin
    Description: Database administrator username
  
  DBPassword:
    Type: String
    NoEcho: true
    MinLength: 8
    Description: Database administrator password

Mappings:
  AWSRegionAMI:
    us-east-1:
      AMI: ami-0abcdef1234567890
    us-west-2:
      AMI: ami-0123456789abcdef0
    eu-west-1:
      AMI: ami-0987654321fedcba0
  
  EnvironmentConfig:
    development:
      InstanceCount: 1
      DBInstanceClass: db.t3.micro
    staging:
      InstanceCount: 2
      DBInstanceClass: db.t3.small
    production:
      InstanceCount: 3
      DBInstanceClass: db.t3.medium

Conditions:
  IsProduction: !Equals [!Ref Environment, production]
  CreateDatabase: !Not [!Equals [!Ref Environment, development]]

Resources:
  # VPC and Networking
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-vpc'
        - Key: Environment
          Value: !Ref Environment

  InternetGateway:
    Type: AWS::EC2::InternetGateway
    Properties:
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-igw'

  InternetGatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      InternetGatewayId: !Ref InternetGateway
      VpcId: !Ref VPC

  # Public Subnets
  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: 10.0.1.0/24
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-public-subnet-1'

  PublicSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: 10.0.2.0/24
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-public-subnet-2'

  # Private Subnets
  PrivateSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [0, !GetAZs '']
      CidrBlock: 10.0.3.0/24
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-private-subnet-1'

  PrivateSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      AvailabilityZone: !Select [1, !GetAZs '']
      CidrBlock: 10.0.4.0/24
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-private-subnet-2'

  # NAT Gateways
  NatGateway1EIP:
    Type: AWS::EC2::EIP
    DependsOn: InternetGatewayAttachment
    Properties:
      Domain: vpc

  NatGateway1:
    Type: AWS::EC2::NatGateway
    Properties:
      AllocationId: !GetAtt NatGateway1EIP.AllocationId
      SubnetId: !Ref PublicSubnet1

  # Route Tables
  PublicRouteTable:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-public-routes'

  DefaultPublicRoute:
    Type: AWS::EC2::Route
    DependsOn: InternetGatewayAttachment
    Properties:
      RouteTableId: !Ref PublicRouteTable
      DestinationCidrBlock: 0.0.0.0/0
      GatewayId: !Ref InternetGateway

  PublicSubnet1RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      RouteTableId: !Ref PublicRouteTable
      SubnetId: !Ref PublicSubnet1

  PublicSubnet2RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      RouteTableId: !Ref PublicRouteTable
      SubnetId: !Ref PublicSubnet2

  PrivateRouteTable1:
    Type: AWS::EC2::RouteTable
    Properties:
      VpcId: !Ref VPC
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-private-routes-1'

  DefaultPrivateRoute1:
    Type: AWS::EC2::Route
    Properties:
      RouteTableId: !Ref PrivateRouteTable1
      DestinationCidrBlock: 0.0.0.0/0
      NatGatewayId: !Ref NatGateway1

  PrivateSubnet1RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      RouteTableId: !Ref PrivateRouteTable1
      SubnetId: !Ref PrivateSubnet1

  PrivateSubnet2RouteTableAssociation:
    Type: AWS::EC2::SubnetRouteTableAssociation
    Properties:
      RouteTableId: !Ref PrivateRouteTable1
      SubnetId: !Ref PrivateSubnet2

  # Security Groups
  LoadBalancerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub '${AWS::StackName}-alb-sg'
      GroupDescription: Security group for Application Load Balancer
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          CidrIp: 0.0.0.0/0
        - IpProtocol: tcp
          FromPort: 443
          ToPort: 443
          CidrIp: 0.0.0.0/0
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-alb-sg'

  WebServerSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupName: !Sub '${AWS::StackName}-web-sg'
      GroupDescription: Security group for web servers
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 80
          ToPort: 80
          SourceSecurityGroupId: !Ref LoadBalancerSecurityGroup
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 10.0.0.0/16
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-web-sg'

  DatabaseSecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Condition: CreateDatabase
    Properties:
      GroupName: !Sub '${AWS::StackName}-db-sg'
      GroupDescription: Security group for database
      VpcId: !Ref VPC
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 3306
          ToPort: 3306
          SourceSecurityGroupId: !Ref WebServerSecurityGroup
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-db-sg'

  # IAM Role for EC2 instances
  EC2Role:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy
        - arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-ec2-role'

  EC2InstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Roles:
        - !Ref EC2Role

  # Launch Template
  LaunchTemplate:
    Type: AWS::EC2::LaunchTemplate
    Properties:
      LaunchTemplateName: !Sub '${AWS::StackName}-launch-template'
      LaunchTemplateData:
        ImageId: !FindInMap [AWSRegionAMI, !Ref 'AWS::Region', AMI]
        InstanceType: !Ref InstanceType
        KeyName: !Ref KeyPairName
        IamInstanceProfile:
          Arn: !GetAtt EC2InstanceProfile.Arn
        SecurityGroupIds:
          - !Ref WebServerSecurityGroup
        UserData:
          Fn::Base64: !Sub |
            #!/bin/bash
            yum update -y
            yum install -y httpd
            systemctl start httpd
            systemctl enable httpd
            echo "<h1>Hello from ${Environment} environment!</h1>" > /var/www/html/index.html
            echo "<p>Instance ID: $(curl -s http://169.254.169.254/latest/meta-data/instance-id)</p>" >> /var/www/html/index.html
            
            # Install CloudWatch agent
            wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
            rpm -U ./amazon-cloudwatch-agent.rpm
        TagSpecifications:
          - ResourceType: instance
            Tags:
              - Key: Name
                Value: !Sub '${AWS::StackName}-web-server'
              - Key: Environment
                Value: !Ref Environment

  # Auto Scaling Group
  AutoScalingGroup:
    Type: AWS::AutoScaling::AutoScalingGroup
    Properties:
      AutoScalingGroupName: !Sub '${AWS::StackName}-asg'
      VPCZoneIdentifier:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
      LaunchTemplate:
        LaunchTemplateId: !Ref LaunchTemplate
        Version: !GetAtt LaunchTemplate.LatestVersionNumber
      MinSize: 1
      MaxSize: 6
      DesiredCapacity: !FindInMap [EnvironmentConfig, !Ref Environment, InstanceCount]
      TargetGroupARNs:
        - !Ref TargetGroup
      HealthCheckType: ELB
      HealthCheckGracePeriod: 300
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-asg'
          PropagateAtLaunch: false
        - Key: Environment
          Value: !Ref Environment
          PropagateAtLaunch: true

  # Application Load Balancer
  ApplicationLoadBalancer:
    Type: AWS::ElasticLoadBalancingV2::LoadBalancer
    Properties:
      Name: !Sub '${AWS::StackName}-alb'
      Scheme: internet-facing
      Type: application
      Subnets:
        - !Ref PublicSubnet1
        - !Ref PublicSubnet2
      SecurityGroups:
        - !Ref LoadBalancerSecurityGroup
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-alb'
        - Key: Environment
          Value: !Ref Environment

  TargetGroup:
    Type: AWS::ElasticLoadBalancingV2::TargetGroup
    Properties:
      Name: !Sub '${AWS::StackName}-tg'
      Port: 80
      Protocol: HTTP
      VpcId: !Ref VPC
      HealthCheckPath: /
      HealthCheckProtocol: HTTP
      HealthCheckIntervalSeconds: 30
      HealthyThresholdCount: 2
      UnhealthyThresholdCount: 5
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-tg'

  Listener:
    Type: AWS::ElasticLoadBalancingV2::Listener
    Properties:
      DefaultActions:
        - Type: forward
          TargetGroupArn: !Ref TargetGroup
      LoadBalancerArn: !Ref ApplicationLoadBalancer
      Port: 80
      Protocol: HTTP

  # RDS Database
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Condition: CreateDatabase
    Properties:
      DBSubnetGroupName: !Sub '${AWS::StackName}-db-subnet-group'
      DBSubnetGroupDescription: Subnet group for RDS database
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-db-subnet-group'

  Database:
    Type: AWS::RDS::DBInstance
    Condition: CreateDatabase
    DeletionPolicy: Snapshot
    Properties:
      DBInstanceIdentifier: !Sub '${AWS::StackName}-database'
      DBInstanceClass: !FindInMap [EnvironmentConfig, !Ref Environment, DBInstanceClass]
      Engine: mysql
      EngineVersion: '8.0.35'
      AllocatedStorage: 20
      StorageType: gp2
      StorageEncrypted: !If [IsProduction, true, false]
      MasterUsername: !Ref DBUsername
      MasterUserPassword: !Ref DBPassword
      VPCSecurityGroups:
        - !Ref DatabaseSecurityGroup
      DBSubnetGroupName: !Ref DBSubnetGroup
      BackupRetentionPeriod: !If [IsProduction, 7, 1]
      MultiAZ: !If [IsProduction, true, false]
      PubliclyAccessible: false
      DeletionProtection: !If [IsProduction, true, false]
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-database'
        - Key: Environment
          Value: !Ref Environment

  # Auto Scaling Policies
  ScaleUpPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      AdjustmentType: ChangeInCapacity
      AutoScalingGroupName: !Ref AutoScalingGroup
      Cooldown: 300
      ScalingAdjustment: 1

  ScaleDownPolicy:
    Type: AWS::AutoScaling::ScalingPolicy
    Properties:
      AdjustmentType: ChangeInCapacity
      AutoScalingGroupName: !Ref AutoScalingGroup
      Cooldown: 300
      ScalingAdjustment: -1

  # CloudWatch Alarms
  CPUAlarmHigh:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmDescription: Scale up on high CPU
      AlarmActions:
        - !Ref ScaleUpPolicy
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 70
      ComparisonOperator: GreaterThanThreshold
      Dimensions:
        - Name: AutoScalingGroupName
          Value: !Ref AutoScalingGroup

  CPUAlarmLow:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmDescription: Scale down on low CPU
      AlarmActions:
        - !Ref ScaleDownPolicy
      MetricName: CPUUtilization
      Namespace: AWS/EC2
      Statistic: Average
      Period: 300
      EvaluationPeriods: 2
      Threshold: 30
      ComparisonOperator: LessThanThreshold
      Dimensions:
        - Name: AutoScalingGroupName
          Value: !Ref AutoScalingGroup

Outputs:
  VPCId:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub '${AWS::StackName}-vpc-id'

  PublicSubnets:
    Description: Public subnet IDs
    Value: !Join [',', [!Ref PublicSubnet1, !Ref PublicSubnet2]]
    Export:
      Name: !Sub '${AWS::StackName}-public-subnets'

  PrivateSubnets:
    Description: Private subnet IDs
    Value: !Join [',', [!Ref PrivateSubnet1, !Ref PrivateSubnet2]]
    Export:
      Name: !Sub '${AWS::StackName}-private-subnets'

  LoadBalancerDNS:
    Description: Application Load Balancer DNS name
    Value: !GetAtt ApplicationLoadBalancer.DNSName
    Export:
      Name: !Sub '${AWS::StackName}-alb-dns'

  LoadBalancerZone:
    Description: Application Load Balancer hosted zone
    Value: !GetAtt ApplicationLoadBalancer.CanonicalHostedZoneID
    Export:
      Name: !Sub '${AWS::StackName}-alb-zone'

  DatabaseEndpoint:
    Description: RDS database endpoint
    Value: !If [CreateDatabase, !GetAtt Database.Endpoint.Address, 'No database created']
    Condition: CreateDatabase
    Export:
      Name: !Sub '${AWS::StackName}-db-endpoint'

  ApplicationURL:
    Description: Application URL
    Value: !Sub 'http://${ApplicationLoadBalancer.DNSName}'

# Deploy this template using AWS CLI:
# aws cloudformation create-stack --stack-name my-web-app --template-body file://web-infrastructure.yaml --parameters ParameterKey=KeyPairName,ParameterValue=my-key-pair ParameterKey=DBPassword,ParameterValue=MySecurePassword123 --capabilities CAPABILITY_IAM
    ''', language='yaml')
    st.markdown('</div>', unsafe_allow_html=True)

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
    st.markdown("# 🚀 AWS Deployment Services")
    
    st.markdown("""
    <div class="info-box">
    Master AWS deployment services to efficiently deploy, manage, and scale applications. Learn the differences between various deployment approaches and when to use each service for optimal results.
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌱 AWS Elastic Beanstalk",
        "🚀 AWS CodeDeploy", 
        "🐳 Amazon ECS",
        "☸️ Amazon EKS",
        "📋 AWS CloudFormation"
    ])
    
    with tab1:
        elastic_beanstalk_tab()
    
    with tab2:
        codedeploy_tab()
    
    with tab3:
        ecs_tab()
        
    with tab4:
        eks_tab()
        
    with tab5:
        cloudformation_tab()
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>© 2025, Amazon Web Services, Inc. or its affiliates. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)

# Main execution flow
if __name__ == "__main__":
    if 'localhost' in st.context.headers.get("host", ""):
        main()
    else:
        # First check authentication
        is_authenticated = authenticate.login()
        
        # If authenticated, show the main app content
        if is_authenticated:
            main()
