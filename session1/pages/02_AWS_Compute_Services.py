
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import utils.common as common
import utils.authenticate as authenticate
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="AWS Compute Services Hub",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)
common.initialize_mermaid()
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
        
        .service-selector {{
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
            - ⚡ AWS Compute Offerings - Service comparison and selection
            - 🖼️ Amazon Machine Images (AMI) - Instance templates and configuration
            - 💾 EC2 Instance Storage Options - Storage types and use cases
            - 📈 Amazon EC2 Auto Scaling - Automatic capacity management
            - ⚖️ Elastic Load Balancing - Traffic distribution and high availability
            
            **Learning Objectives:**
            - Compare different AWS compute services
            - Understand AMI components and usage
            - Choose appropriate storage options for EC2
            - Implement auto scaling strategies
            - Configure load balancing for applications
            """)

def create_compute_services_mermaid():
    """Create mermaid diagram for AWS compute services comparison"""
    return """
    graph TD
        A[AWS Compute Services] --> B[Amazon EC2]
        A --> C[Amazon ECS]
        A --> D[AWS Fargate]
        A --> E[AWS Lambda]
        
        B --> B1[Full Control]
        B --> B2[Configure Servers]
        B --> B3[Manage OS]
        B --> B4[Scale Manually/Auto]
        
        C --> C1[Containerized Apps]
        C --> C2[Manage Cluster]
        C --> C3[Docker Support]
        C --> C4[Service Discovery]
        
        D --> D1[Serverless Containers]
        D --> D2[No Infrastructure]
        D --> D3[Pay per Use]
        D --> D4[Auto Scaling]
        
        E --> E1[Event-Driven]
        E --> E2[Serverless Functions]
        E --> E3[15-min Max Runtime]
        E --> E4[Pay per Invocation]
        
        style A fill:#FF9900,stroke:#232F3E,color:#fff
        style B fill:#4B9EDB,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#232F3E,stroke:#FF9900,color:#fff
        style E fill:#FF6B35,stroke:#232F3E,color:#fff
    """

def create_ami_components_mermaid():
    """Create mermaid diagram for AMI components"""
    return """
    graph TB
        A[Amazon Machine Image AMI] --> B[Root Volume Template]
        A --> C[Launch Permissions]
        A --> D[Block Device Mapping]
        
        B --> B1[EBS Snapshot]
        B --> B2[Instance Store Template]
        
        C --> C1[Public AMI]
        C --> C2[Private AMI]
        C --> C3[Shared AMI]
        
        D --> D1[Root Device]
        D --> D2[Additional Volumes]
        D --> D3[Volume Types]
        
        style A fill:#FF9900,stroke:#232F3E,color:#fff
        style B fill:#4B9EDB,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_storage_comparison_mermaid():
    """Create mermaid diagram for storage options comparison"""
    return """
    graph LR
        A[EC2 Instance] --> B[EBS Volumes]
        A --> C[Instance Store]
        A --> D[Amazon EFS]
        A --> E[Amazon S3]
        
        B --> B1[Persistent]
        B --> B2[Network Attached]
        B --> B3[Snapshots]
        B --> B4[Multiple Types]
        
        C --> C1[Temporary]
        C --> C2[High Performance]
        C --> C3[Physically Attached]
        C --> C4[Instance Lifecycle]
        
        D --> D1[Shared File System]
        D --> D2[Multiple Instances]
        D --> D3[POSIX Compliant]
        D --> D4[Elastic Scaling]
        
        E --> E1[Object Storage]
        E --> E2[Internet Accessible]
        E --> E3[Unlimited Capacity]
        E --> E4[Multiple Storage Classes]
        
        style A fill:#FF9900,stroke:#232F3E,color:#fff
        style B fill:#4B9EDB,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#232F3E,stroke:#FF9900,color:#fff
        style E fill:#FF6B35,stroke:#232F3E,color:#fff
    """

def create_auto_scaling_mermaid():
    """Create mermaid diagram for auto scaling architecture"""
    return """
    graph TD
        A[Auto Scaling Group] --> B[Launch Template]
        A --> C[Scaling Policies]
        A --> D[Health Checks]
        
        B --> B1[AMI ID]
        B --> B2[Instance Type]
        B --> B3[Security Groups]
        B --> B4[User Data]
        
        C --> C1[Target Tracking]
        C --> C2[Step Scaling]
        C --> C3[Scheduled Scaling]
        C --> C4[Predictive Scaling]
        
        D --> D1[EC2 Health]
        D --> D2[ELB Health]
        D --> D3[Custom Health]
        
        E[CloudWatch Metrics] --> C
        F[Application Load Balancer] --> D
        
        style A fill:#FF9900,stroke:#232F3E,color:#fff
        style B fill:#4B9EDB,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_load_balancer_mermaid():
    """Create mermaid diagram for load balancer types"""
    return """
    graph TB
        A[Elastic Load Balancing] --> B[Application Load Balancer]
        A --> C[Network Load Balancer]
        A --> D[Gateway Load Balancer]
        A --> E[Classic Load Balancer]
        
        B --> B1[Layer 7 HTTP/HTTPS]
        B --> B2[Content-based Routing]
        B --> B3[WebSocket Support]
        B --> B4[Container Integration]
        
        C --> C1[Layer 4 TCP/UDP]
        C --> C2[Ultra Performance]
        C --> C3[Static IP Addresses]
        C --> C4[Millions of Requests]
        
        D --> D1[Layer 3 Gateway]
        D --> D2[3rd Party Appliances]
        D --> D3[Transparent Network]
        D --> D4[Security Inspection]
        
        E --> E1[Legacy Support]
        E --> E2[EC2-Classic]
        E --> E3[Basic Load Balancing]
        E --> E4[Being Phased Out]
        
        style A fill:#FF9900,stroke:#232F3E,color:#fff
        style B fill:#4B9EDB,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#232F3E,stroke:#FF9900,color:#fff
        style E fill:#FF6B35,stroke:#232F3E,color:#fff
    """

def aws_compute_offerings_tab():
    """Content for AWS Compute Offerings tab"""
    st.markdown("## ⚡ AWS Compute Offerings")
    st.markdown("*Choose the right compute service for your application needs*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    AWS offers multiple compute services to meet different application requirements. Each service provides different levels of control, 
    management overhead, and pricing models to optimize for your specific use case.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Compute Services Overview
    st.markdown("### 🏗️ Compute Services Architecture")
    common.mermaid(create_compute_services_mermaid(), height=400)
    
    # Interactive Service Selector
    st.markdown("### 🔍 Interactive Compute Service Selector")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Your Requirements")
        control_level = st.selectbox("Required Control Level:", [
            "Full control over servers and OS",
            "Application-level control with container orchestration", 
            "Focus on code, minimal infrastructure management",
            "Event-driven, serverless execution"
        ])
        
        scalability = st.selectbox("Scalability Requirements:", [
            "Manual scaling with some automation",
            "Automatic container scaling",
            "Built-in auto scaling", 
            "Automatic scaling based on events"
        ])
        
        workload_type = st.selectbox("Workload Type:", [
            "Long-running applications (web servers, databases)",
            "Microservices and containerized applications",
            "Batch processing and background tasks",
            "Event processing and API backends"
        ])
    
    with col2:
        duration = st.selectbox("Expected Runtime:", [
            "Always running (24/7)",
            "Scheduled or predictable patterns",
            "Variable, based on demand",
            "Short bursts (< 15 minutes)"
        ])
        
        budget_priority = st.selectbox("Cost Optimization Priority:", [
            "Predictable costs with reserved capacity",
            "Balance of cost and performance",
            "Pay only for actual usage",
            "Minimize costs for sporadic workloads"
        ])
        
        complexity = st.selectbox("Management Complexity:", [
            "I want full control and can manage infrastructure",
            "I want orchestration but less server management",
            "I prefer managed services with less complexity",
            "I want to focus only on business logic"
        ])
    
    if st.button("🎯 Find My Ideal Compute Service", use_container_width=True):
        # Simple decision logic based on answers
        if "Full control" in control_level and "Long-running" in workload_type:
            recommendation = "Amazon EC2"
            explanation = "Perfect for applications requiring full OS control and long-running workloads"
            benefits = ["Complete infrastructure control", "Wide instance type selection", "Predictable pricing with Reserved Instances"]
        elif "container" in control_level.lower() or "Microservices" in workload_type:
            recommendation = "Amazon ECS or AWS Fargate"
            explanation = "Ideal for containerized applications with orchestration needs"
            benefits = ["Container orchestration", "Service discovery", "Integrated with AWS services"]
        elif "Event processing" in workload_type or "Short bursts" in duration:
            recommendation = "AWS Lambda"
            explanation = "Best for event-driven, short-duration workloads"
            benefits = ["No server management", "Automatic scaling", "Pay per invocation"]
        else:
            recommendation = "AWS Fargate"
            explanation = "Great balance of control and serverless benefits"
            benefits = ["Serverless containers", "No infrastructure management", "Pay for what you use"]
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""### 🎉 Recommended Service: {recommendation}

**Why this fits your needs:**  
{explanation}

**Key Benefits:**  
• {benefits[0]}  
• {benefits[1]}  
• {benefits[2]}

**Next Steps:**
1. Review pricing for your expected usage
2. Create a proof of concept
3. Consider hybrid approaches for different workload components""")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed Service Comparison
    st.markdown("### 📊 Detailed Service Comparison")
    
    comparison_data = {
        'Service': ['Amazon EC2', 'Amazon ECS', 'AWS Fargate', 'AWS Lambda'],
        'Control Level': ['High', 'Medium', 'Low', 'Very Low'],
        'Management Overhead': ['High', 'Medium', 'Low', 'Very Low'],
        'Pricing Model': ['Hourly/Monthly', 'Hourly + Task', 'Per Task', 'Per Invocation'],
        'Best For': [
            'Traditional applications, full control needed',
            'Containerized apps, service orchestration',
            'Serverless containers, reduced management',
            'Event-driven functions, microservices'
        ],
        'Max Runtime': ['Unlimited', 'Unlimited', 'Unlimited', '15 minutes'],
        'Cold Start': ['N/A', 'Seconds', 'Seconds', 'Milliseconds']
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True)
    
    # Use Case Examples
    st.markdown("### 🌟 Real-World Use Case Examples")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🖥️ Amazon EC2 Use Cases
        
        **E-commerce Web Application:**
        - Full control over web server configuration
        - Custom security and compliance requirements
        - Integration with legacy systems
        
        **High-Performance Computing:**
        - Scientific simulations and modeling
        - Custom software installation requirements
        - GPU-intensive workloads
        
        **Database Servers:**
        - Self-managed databases (MySQL, PostgreSQL)
        - Custom database configurations
        - Performance tuning requirements
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🐳 Amazon ECS Use Cases
        
        **Microservices Architecture:**
        - Multiple containerized services
        - Service discovery and load balancing
        - Development team collaboration
        
        **CI/CD Pipelines:**
        - Containerized build environments
        - Scalable testing infrastructure
        - Deployment automation
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🚀 AWS Fargate Use Cases
        
        **API Backends:**
        - RESTful API services
        - Reduced operational overhead
        - Variable traffic patterns
        
        **Batch Processing:**
        - Data transformation jobs
        - Scheduled tasks
        - Container-based workflows
        
        **Modern Web Applications:**
        - React/Angular frontends with API backends
        - Serverless-first architecture
        - Development team productivity
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚡ AWS Lambda Use Cases
        
        **Event Processing:**
        - S3 file uploads triggering processing
        - DynamoDB change streams
        - IoT sensor data processing
        
        **API Gateways:**
        - Serverless REST APIs
        - Authentication functions
        - Data validation and transformation
        
        **Scheduled Tasks:**
        - Daily report generation
        - Database cleanup jobs
        - Monitoring and alerting
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Cost Comparison Calculator
    st.markdown("### 💰 Interactive Cost Comparison")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        monthly_hours = st.slider("Monthly Runtime Hours:", 1, 744, 168)  # 744 = 24*31
        cpu_requirements = st.selectbox("CPU Requirements:", ["1 vCPU", "2 vCPU", "4 vCPU", "8 vCPU"])
        
    with col2:
        memory_gb = st.slider("Memory Requirements (GB):", 1, 64, 4)
        requests_per_month = st.slider("Requests/Invocations per Month:", 1000, 10000000, 100000)
    
    with col3:
        region = st.selectbox("AWS Region:", ["us-east-1", "us-west-2", "eu-west-1"])
        usage_pattern = st.selectbox("Usage Pattern:", ["Consistent", "Variable", "Bursty"])
    
    if st.button("💰 Calculate Monthly Costs", use_container_width=True):
        # Simplified cost calculations (actual prices vary)
        cpu_multiplier = {"1 vCPU": 1, "2 vCPU": 2, "4 vCPU": 4, "8 vCPU": 8}[cpu_requirements]
        
        # EC2 cost (t3.small to t3.2xlarge estimates)
        ec2_hourly = 0.0208 * cpu_multiplier
        ec2_monthly = ec2_hourly * monthly_hours
        
        # ECS cost (EC2 + ECS service overhead)
        ecs_monthly = ec2_monthly * 1.1  # 10% overhead for ECS management
        
        # Fargate cost
        fargate_hourly = (cpu_multiplier * 0.04048) + (memory_gb * 0.004445)
        fargate_monthly = fargate_hourly * monthly_hours
        
        # Lambda cost
        lambda_requests = requests_per_month / 1000000  # per million requests
        lambda_compute = (cpu_multiplier * memory_gb * 0.0000166667) * (requests_per_month / 1000)  # per GB-second
        lambda_monthly = lambda_requests * 0.20 + lambda_compute
        
        # Create cost comparison chart
        services = ['EC2', 'ECS', 'Fargate', 'Lambda']
        costs = [ec2_monthly, ecs_monthly, fargate_monthly, lambda_monthly]
        
        fig = px.bar(x=services, y=costs, 
                     title=f'Monthly Cost Comparison - {cpu_requirements}, {memory_gb}GB RAM',
                     color=services,
                     color_discrete_sequence=[AWS_COLORS['primary'], AWS_COLORS['light_blue'], 
                                            AWS_COLORS['success'], AWS_COLORS['warning']])
        fig.update_yaxis(title="Monthly Cost (USD)")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display detailed breakdown
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("EC2", f"${ec2_monthly:.2f}/month", f"${ec2_hourly:.3f}/hour")
        with col2:
            st.metric("ECS", f"${ecs_monthly:.2f}/month", "EC2 + management")
        with col3:
            st.metric("Fargate", f"${fargate_monthly:.2f}/month", "Per task")
        with col4:
            st.metric("Lambda", f"${lambda_monthly:.2f}/month", "Per invocation")
    
    # Code Example
    st.markdown("### 💻 Code Example: Service Selection Decision Tree")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# AWS Compute Service Selection Helper
import boto3
from datetime import datetime

class ComputeServiceSelector:
    def __init__(self):
        self.recommendations = {}
    
    def analyze_requirements(self, requirements):
        """Analyze requirements and recommend appropriate compute service"""
        score = {
            'ec2': 0,
            'ecs': 0, 
            'fargate': 0,
            'lambda': 0
        }
        
        # Control level scoring
        if requirements.get('control_level') == 'full':
            score['ec2'] += 3
        elif requirements.get('control_level') == 'container':
            score['ecs'] += 3
            score['fargate'] += 2
        elif requirements.get('control_level') == 'minimal':
            score['fargate'] += 3
            score['lambda'] += 3
        
        # Runtime duration scoring
        runtime = requirements.get('max_runtime_minutes', 0)
        if runtime > 900:  # > 15 minutes
            score['ec2'] += 2
            score['ecs'] += 2
            score['fargate'] += 2
        elif runtime <= 15:
            score['lambda'] += 3
        
        # Workload pattern scoring
        pattern = requirements.get('workload_pattern', '')
        if pattern == 'always_on':
            score['ec2'] += 2
            score['ecs'] += 2
        elif pattern == 'event_driven':
            score['lambda'] += 3
        elif pattern == 'batch':
            score['fargate'] += 2
            score['ecs'] += 1
        
        # Cost sensitivity scoring
        if requirements.get('cost_sensitive', False):
            if runtime < 60:  # Short runtimes favor Lambda
                score['lambda'] += 2
            score['fargate'] += 1  # Pay-per-use model
        
        # Container preference
        if requirements.get('containerized', False):
            score['ecs'] += 2
            score['fargate'] += 2
        
        return max(score, key=score.get), score
    
    def generate_recommendation(self, requirements):
        """Generate detailed recommendation with rationale"""
        service, scores = self.analyze_requirements(requirements)
        
        recommendations = {
            'ec2': {
                'name': 'Amazon EC2',
                'use_case': 'Full control applications',
                'benefits': [
                    'Complete infrastructure control',
                    'Wide instance type selection', 
                    'Custom OS configurations',
                    'Predictable pricing with Reserved Instances'
                ],
                'considerations': [
                    'Higher management overhead',
                    'Need to manage OS patches and updates',
                    'Scaling requires configuration'
                ]
            },
            'ecs': {
                'name': 'Amazon ECS',
                'use_case': 'Container orchestration',
                'benefits': [
                    'Docker container support',
                    'Service discovery and load balancing',
                    'Integration with AWS services',
                    'Flexible deployment options'
                ],
                'considerations': [
                    'Container expertise required',
                    'Cluster management needed',
                    'Additional complexity vs EC2'
                ]
            },
            'fargate': {
                'name': 'AWS Fargate',
                'use_case': 'Serverless containers',
                'benefits': [
                    'No server management',
                    'Pay only for running tasks',
                    'Automatic scaling',
                    'Built-in security isolation'
                ],
                'considerations': [
                    'Higher per-hour cost than EC2',
                    'Less control over underlying infrastructure',
                    'Container size limitations'
                ]
            },
            'lambda': {
                'name': 'AWS Lambda',
                'use_case': 'Event-driven functions',
                'benefits': [
                    'No server management',
                    'Automatic scaling',
                    'Pay per invocation',
                    'Built-in fault tolerance'
                ],
                'considerations': [
                    '15-minute execution limit',
                    'Cold start latency',
                    'Language runtime limitations'
                ]
            }
        }
        
        return {
            'recommended_service': service,
            'confidence_score': scores[service],
            'details': recommendations[service],
            'all_scores': scores
        }

def deploy_application(service_type, config):
    """Deploy application using recommended service"""
    
    if service_type == 'ec2':
        return deploy_ec2_application(config)
    elif service_type == 'ecs':
        return deploy_ecs_application(config)
    elif service_type == 'fargate':
        return deploy_fargate_application(config)
    elif service_type == 'lambda':
        return deploy_lambda_application(config)

def deploy_ec2_application(config):
    """Deploy application on EC2"""
    ec2 = boto3.client('ec2')
    
    # Launch EC2 instance
    response = ec2.run_instances(
        ImageId=config['ami_id'],
        MinCount=config.get('min_count', 1),
        MaxCount=config.get('max_count', 1),
        InstanceType=config.get('instance_type', 't3.micro'),
        KeyName=config.get('key_name'),
        SecurityGroupIds=config.get('security_groups', []),
        SubnetId=config.get('subnet_id'),
        UserData=config.get('user_data', ''),
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [
                {'Key': 'Name', 'Value': config.get('name', 'MyApp')},
                {'Key': 'Environment', 'Value': config.get('environment', 'dev')}
            ]
        }]
    )
    
    instance_id = response['Instances'][0]['InstanceId']
    print(f"EC2 Instance launched: {instance_id}")
    
    return {'service': 'ec2', 'instance_id': instance_id}

def deploy_lambda_application(config):
    """Deploy application as Lambda function"""
    lambda_client = boto3.client('lambda')
    
    # Create Lambda function
    response = lambda_client.create_function(
        FunctionName=config['function_name'],
        Runtime=config.get('runtime', 'python3.9'),
        Role=config['role_arn'],
        Handler=config.get('handler', 'index.handler'),
        Code={
            'ZipFile': config['code_zip']
        },
        Description=config.get('description', 'My serverless application'),
        Timeout=config.get('timeout', 30),
        MemorySize=config.get('memory', 128),
        Environment={
            'Variables': config.get('environment_variables', {})
        },
        Tags=config.get('tags', {})
    )
    
    function_arn = response['FunctionArn']
    print(f"Lambda function created: {function_arn}")
    
    return {'service': 'lambda', 'function_arn': function_arn}

# Example usage
selector = ComputeServiceSelector()

# Define application requirements
app_requirements = {
    'control_level': 'minimal',  # full, container, minimal
    'max_runtime_minutes': 5,
    'workload_pattern': 'event_driven',  # always_on, event_driven, batch
    'cost_sensitive': True,
    'containerized': False,
    'expected_requests_per_day': 10000
}

# Get recommendation
recommendation = selector.generate_recommendation(app_requirements)

print(f"Recommended Service: {recommendation['recommended_service']}")
print(f"Confidence Score: {recommendation['confidence_score']}")
print(f"Use Case: {recommendation['details']['use_case']}")
print("Benefits:")
for benefit in recommendation['details']['benefits']:
    print(f"  • {benefit}")
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def amazon_machine_images_tab():
    """Content for Amazon Machine Images tab"""
    st.markdown("## 🖼️ Amazon Machine Images (AMI)")
    st.markdown("*Templates that contain the software configuration needed to launch EC2 instances*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    An **Amazon Machine Image (AMI)** provides the information required to launch an instance. You must specify an AMI 
    when you launch an instance. An AMI includes the operating system, application server, applications, and any additional software.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # AMI Components
    st.markdown("### 🏗️ AMI Components")
    common.mermaid(create_ami_components_mermaid(), height=300)
    
    # Interactive AMI Builder
    st.markdown("### 🛠️ Interactive AMI Configuration Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🖥️ Base Configuration")
        os_type = st.selectbox("Operating System:", [
            "Amazon Linux 2023", "Ubuntu 22.04 LTS", "Windows Server 2022", 
            "Red Hat Enterprise Linux 9", "SUSE Linux Enterprise Server 15"
        ])
        
        architecture = st.selectbox("Architecture:", ["x86_64", "ARM64 (Graviton)"])
        
        root_device = st.selectbox("Root Device Type:", [
            "EBS-backed (recommended)", "Instance Store-backed"
        ])
        
        virtualization = st.selectbox("Virtualization Type:", [
            "HVM (Hardware Virtual Machine)", "Paravirtual (PV) - Legacy"
        ])
    
    with col2:
        st.markdown("### 🔧 Software Stack")
        web_server = st.multiselect("Web Server:", ["Apache", "Nginx", "IIS", "None"])
        
        runtime = st.multiselect("Runtime/Language:", [
            "Python 3.11", "Node.js 18", "Java 17", "PHP 8.2", ".NET 6", "Go 1.21"
        ])
        
        database = st.multiselect("Database Client:", [
            "MySQL Client", "PostgreSQL Client", "MongoDB Tools", "Redis CLI"
        ])
        
        monitoring = st.multiselect("Monitoring Tools:", [
            "CloudWatch Agent", "New Relic", "Datadog Agent", "Prometheus Node Exporter"
        ])
    
    # Advanced Configuration
    st.markdown("### ⚙️ Advanced Configuration")
    col3, col4 = st.columns(2)
    
    with col3:
        encrypt_root = st.checkbox("Encrypt Root Volume", value=True)
        ena_support = st.checkbox("Enhanced Networking (ENA)", value=True)
        sriov_support = st.checkbox("SR-IOV Support", value=True)
    
    with col4:
        public_ami = st.checkbox("Make AMI Public", value=False)
        sharing_accounts = st.text_input("Share with AWS Account IDs (comma-separated):")
        description = st.text_area("AMI Description:", "Custom AMI for my application")
    
    if st.button("🚀 Generate AMI Configuration", use_container_width=True):
        # Generate AMI ID (simulated)
        ami_id = f"ami-{np.random.randint(100000000000, 999999999999):012x}"
        
        # Calculate estimated AMI size
        base_size = {"Amazon Linux": 2, "Ubuntu": 2.5, "Windows": 30, "Red Hat": 4, "SUSE": 3}
        estimated_size = base_size.get(os_type.split()[0], 2) + len(web_server) * 0.5 + len(runtime) * 0.3
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ AMI Configuration Generated!
        
        **AMI Details:**
        - **AMI ID**: `{ami_id}`
        - **Name**: Custom-{os_type.replace(' ', '-')}-{datetime.now().strftime('%Y%m%d')}`
        - **Operating System**: {os_type}
        - **Architecture**: {architecture}
        - **Root Device**: {root_device}
        - **Estimated Size**: {estimated_size:.1f} GB
        
        **Software Stack:**
        - **Web Servers**: {', '.join(web_server) if web_server else 'None'}
        - **Runtimes**: {', '.join(runtime) if runtime else 'None'}
        - **Database Tools**: {', '.join(database) if database else 'None'}
        - **Monitoring**: {', '.join(monitoring) if monitoring else 'None'}
        
        **Security Features:**
        - **Root Volume Encryption**: {'✅ Enabled' if encrypt_root else '❌ Disabled'}
        - **Enhanced Networking**: {'✅ Enabled' if ena_support else '❌ Disabled'}
        - **Public Access**: {'✅ Public' if public_ami else '🔒 Private'}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # AMI Types Comparison
    st.markdown("### 📊 AMI Types and Sources")
    
    ami_types_data = {
        'AMI Source': ['AWS Quick Start', 'AWS Marketplace', 'Community AMIs', 'Custom AMIs'],
        'Provider': ['Amazon', '3rd Party Vendors', 'Community', 'You/Your Team'],
        'Cost': ['Free', 'Paid (hourly)', 'Free', 'Storage only'],
        'Support': ['AWS Support', 'Vendor Support', 'Community', 'Self-Support'],
        'Security Updates': ['AWS Managed', 'Vendor Managed', 'Community', 'Self Managed'],
        'Customization': ['Limited', 'Some', 'Variable', 'Full Control'],
        'Best For': [
            'Quick starts, testing',
            'Enterprise software',
            'Specialized configs',
            'Production workloads'
        ]
    }
    
    df_ami_types = pd.DataFrame(ami_types_data)
    st.dataframe(df_ami_types, use_container_width=True)
    
    # AMI Lifecycle Management
    st.markdown("### 🔄 AMI Lifecycle Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 1️⃣ Creation Phase
        
        **Methods:**
        - Launch instance and customize
        - Create image from running instance
        - Use EC2 Image Builder pipeline
        - Import from on-premises
        
        **Best Practices:**
        - Stop instance before imaging
        - Remove sensitive data
        - Test thoroughly before use
        - Document configuration changes
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 2️⃣ Management Phase
        
        **Key Activities:**
        - Version control and tagging
        - Security patch management
        - Performance optimization
        - Access control and sharing
        
        **Governance:**
        - Regular security scans
        - Compliance validation
        - Cost optimization reviews
        - Backup and recovery procedures
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 3️⃣ Retirement Phase
        
        **Cleanup Activities:**
        - Deregister unused AMIs
        - Delete associated snapshots
        - Update launch templates
        - Notify stakeholders
        
        **Cost Impact:**
        - AMI storage charges
        - Snapshot storage costs
        - Administrative overhead
        - Compliance requirements
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Regional AMI Management
    st.markdown("### 🌍 Cross-Region AMI Management")
    
    regions_data = {
        'Region': ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1'],
        'AMI Status': ['✅ Primary', '🔄 Copied', '🔄 Copied', '❌ Not Available'],
        'Last Updated': ['2024-07-10', '2024-07-10', '2024-07-09', 'N/A'],
        'Copy Cost': ['$0.00', '$0.05', '$0.05', '$0.05'],
        'Use Case': ['Primary deployment', 'DR site', 'EU compliance', 'Future expansion']
    }
    
    df_regions = pd.DataFrame(regions_data)
    st.dataframe(df_regions, use_container_width=True)
    
    # AMI Security Best Practices
    st.markdown("### 🛡️ AMI Security Best Practices")
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 🔒 Security Checklist
    
    **Before Creating AMI:**
    - Remove SSH private keys and certificates
    - Clear shell history and temporary files
    - Remove application logs with sensitive data
    - Reset database passwords and API keys
    - Disable unnecessary services and users
    
    **AMI Access Control:**
    - Use least privilege principle for sharing
    - Regularly audit AMI permissions
    - Implement proper tagging and naming conventions
    - Monitor AMI usage and access patterns
    - Consider AMI encryption for sensitive workloads
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: AMI Management Automation")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# AMI Management and Automation
import boto3
from datetime import datetime, timedelta
import json

class AMIManager:
    def __init__(self, region='us-east-1'):
        self.ec2 = boto3.client('ec2', region_name=region)
        self.region = region
    
    def create_ami(self, instance_id, ami_name, description=""):
        """Create AMI from existing EC2 instance"""
        try:
            response = self.ec2.create_image(
                InstanceId=instance_id,
                Name=ami_name,
                Description=description or f"AMI created from {instance_id} on {datetime.now().strftime('%Y-%m-%d')}",
                NoReboot=True,  # Create AMI without stopping instance
                TagSpecifications=[
                    {
                        'ResourceType': 'image',
                        'Tags': [
                            {'Key': 'Name', 'Value': ami_name},
                            {'Key': 'CreatedBy', 'Value': 'AMI-Manager'},
                            {'Key': 'CreatedDate', 'Value': datetime.now().strftime('%Y-%m-%d')},
                            {'Key': 'SourceInstance', 'Value': instance_id}
                        ]
                    }
                ]
            )
            
            ami_id = response['ImageId']
            print(f"✅ AMI creation initiated: {ami_id}")
            
            # Wait for AMI to be available
            waiter = self.ec2.get_waiter('image_available')
            print("⏳ Waiting for AMI to become available...")
            waiter.wait(ImageIds=[ami_id])
            
            print(f"🎉 AMI {ami_id} is now available!")
            return ami_id
            
        except Exception as e:
            print(f"❌ Error creating AMI: {e}")
            return None
    
    def copy_ami_to_regions(self, ami_id, target_regions, encrypted=False):
        """Copy AMI to multiple regions"""
        copy_results = {}
        
        # Get AMI details first
        try:
            response = self.ec2.describe_images(ImageIds=[ami_id])
            source_ami = response['Images'][0]
            ami_name = source_ami['Name']
            description = source_ami.get('Description', '')
            
        except Exception as e:
            print(f"❌ Error getting AMI details: {e}")
            return copy_results
        
        for region in target_regions:
            try:
                target_ec2 = boto3.client('ec2', region_name=region)
                
                copy_params = {
                    'Name': f"{ami_name}-{region}",
                    'Description': f"{description} (copied to {region})",
                    'SourceImageId': ami_id,
                    'SourceRegion': self.region
                }
                
                if encrypted:
                    copy_params['Encrypted'] = True
                
                response = target_ec2.copy_image(**copy_params)
                copy_ami_id = response['ImageId']
                
                # Add tags to copied AMI
                target_ec2.create_tags(
                    Resources=[copy_ami_id],
                    Tags=[
                        {'Key': 'Name', 'Value': f"{ami_name}-{region}"},
                        {'Key': 'SourceAMI', 'Value': ami_id},
                        {'Key': 'SourceRegion', 'Value': self.region},
                        {'Key': 'CopiedDate', 'Value': datetime.now().strftime('%Y-%m-%d')}
                    ]
                )
                
                copy_results[region] = {
                    'ami_id': copy_ami_id,
                    'status': 'copying',
                    'message': f'AMI copy initiated to {region}'
                }
                
                print(f"✅ AMI copy to {region} initiated: {copy_ami_id}")
                
            except Exception as e:
                copy_results[region] = {
                    'ami_id': None,
                    'status': 'failed',
                    'message': f'Error copying to {region}: {e}'
                }
                print(f"❌ Error copying AMI to {region}: {e}")
        
        return copy_results
    
    def cleanup_old_amis(self, days_old=30, dry_run=True):
        """Clean up AMIs older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        try:
            # Get all AMIs owned by current account
            response = self.ec2.describe_images(Owners=['self'])
            old_amis = []
            
            for ami in response['Images']:
                creation_date = datetime.strptime(ami['CreationDate'], '%Y-%m-%dT%H:%M:%S.%fZ')
                
                if creation_date < cutoff_date:
                    old_amis.append({
                        'ami_id': ami['ImageId'],
                        'name': ami['Name'],
                        'creation_date': ami['CreationDate'],
                        'snapshots': [bdm['Ebs']['SnapshotId'] for bdm in ami.get('BlockDeviceMappings', []) 
                                    if 'Ebs' in bdm and 'SnapshotId' in bdm['Ebs']]
                    })
            
            if dry_run:
                print(f"🔍 DRY RUN: Found {len(old_amis)} AMIs older than {days_old} days:")
                for ami in old_amis:
                    print(f"  - {ami['ami_id']}: {ami['name']} (created: {ami['creation_date']})")
                return old_amis
            
            # Actually delete AMIs and snapshots
            deleted_count = 0
            for ami in old_amis:
                try:
                    # Deregister AMI
                    self.ec2.deregister_image(ImageId=ami['ami_id'])
                    print(f"🗑️  Deregistered AMI: {ami['ami_id']}")
                    
                    # Delete associated snapshots
                    for snapshot_id in ami['snapshots']:
                        try:
                            self.ec2.delete_snapshot(SnapshotId=snapshot_id)
                            print(f"🗑️  Deleted snapshot: {snapshot_id}")
                        except Exception as e:
                            print(f"⚠️  Warning: Could not delete snapshot {snapshot_id}: {e}")
                    
                    deleted_count += 1
                    
                except Exception as e:
                    print(f"❌ Error deleting AMI {ami['ami_id']}: {e}")
            
            print(f"✅ Cleanup complete: {deleted_count} AMIs deleted")
            return old_amis
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            return []
    
    def get_ami_usage_report(self):
        """Generate report of AMI usage across launch templates and auto scaling groups"""
        report = {
            'total_amis': 0,
            'used_amis': set(),
            'unused_amis': [],
            'launch_templates': {},
            'auto_scaling_groups': {}
        }
        
        try:
            # Get all owned AMIs
            amis_response = self.ec2.describe_images(Owners=['self'])
            all_amis = {ami['ImageId']: ami for ami in amis_response['Images']}
            report['total_amis'] = len(all_amis)
            
            # Check launch templates
            lt_response = self.ec2.describe_launch_templates()
            for lt in lt_response['LaunchTemplates']:
                lt_id = lt['LaunchTemplateId'] 
                versions = self.ec2.describe_launch_template_versions(
                    LaunchTemplateId=lt_id
                )
                
                for version in versions['LaunchTemplateVersions']:
                    ami_id = version['LaunchTemplateData'].get('ImageId')
                    if ami_id and ami_id in all_amis:
                        report['used_amis'].add(ami_id)
                        if lt_id not in report['launch_templates']:
                            report['launch_templates'][lt_id] = []
                        report['launch_templates'][lt_id].append(ami_id)
            
            # Check Auto Scaling Groups
            autoscaling = boto3.client('autoscaling', region_name=self.region)
            asg_response = autoscaling.describe_auto_scaling_groups()
            
            for asg in asg_response['AutoScalingGroups']:
                if 'LaunchTemplate' in asg:
                    lt_id = asg['LaunchTemplate']['LaunchTemplateId']
                    if lt_id in report['launch_templates']:
                        report['auto_scaling_groups'][asg['AutoScalingGroupName']] = lt_id
            
            # Find unused AMIs
            for ami_id, ami_data in all_amis.items():
                if ami_id not in report['used_amis']:
                    report['unused_amis'].append({
                        'ami_id': ami_id,
                        'name': ami_data['Name'],
                        'creation_date': ami_data['CreationDate'],
                        'size_gb': sum([bdm.get('Ebs', {}).get('VolumeSize', 0) 
                                      for bdm in ami_data.get('BlockDeviceMappings', [])])
                    })
            
            return report
            
        except Exception as e:
            print(f"❌ Error generating usage report: {e}")
            return report

# Example usage
def main():
    # Initialize AMI manager
    ami_manager = AMIManager(region='us-east-1')
    
    # Create AMI from instance
    instance_id = 'i-1234567890abcdef0'
    ami_name = f'my-app-v1.0-{datetime.now().strftime("%Y%m%d")}'
    
    ami_id = ami_manager.create_ami(
        instance_id=instance_id,
        ami_name=ami_name,
        description='Production ready AMI with latest security patches'
    )
    
    if ami_id:
        # Copy AMI to other regions for disaster recovery
        target_regions = ['us-west-2', 'eu-west-1']
        copy_results = ami_manager.copy_ami_to_regions(
            ami_id=ami_id,
            target_regions=target_regions,
            encrypted=True
        )
        
        print("Copy Results:")
        for region, result in copy_results.items():
            print(f"  {region}: {result['message']}")
    
    # Generate usage report
    print("\n📊 AMI Usage Report:")
    usage_report = ami_manager.get_ami_usage_report()
    print(f"Total AMIs: {usage_report['total_amis']}")
    print(f"Used AMIs: {len(usage_report['used_amis'])}")
    print(f"Unused AMIs: {len(usage_report['unused_amis'])}")
    
    # Cleanup old AMIs (dry run first)
    print("\n🧹 Cleanup Analysis:")
    old_amis = ami_manager.cleanup_old_amis(days_old=90, dry_run=True)

if __name__ == "__main__":
    main()
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def ec2_instance_storage_tab():
    """Content for EC2 Instance Storage Options tab"""
    st.markdown("## 💾 Amazon EC2 Instance Storage Options")
    st.markdown("*Choose the right storage solution for your EC2 instances*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    EC2 instances can use multiple storage options, each optimized for different use cases. Understanding the characteristics 
    of each storage type helps you design cost-effective and performant applications.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Storage Architecture
    st.markdown("### 🏗️ EC2 Storage Architecture")
    common.mermaid(create_storage_comparison_mermaid(), height=300)
    
    # Interactive Storage Selector
    st.markdown("### 🔍 Interactive Storage Selector")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Application Requirements")
        data_persistence = st.selectbox("Data Persistence Need:", [
            "Data must survive instance termination",
            "Temporary data, can be lost with instance",
            "Shared data across multiple instances",
            "Backup and archival storage"
        ])
        
        performance_requirement = st.selectbox("Performance Requirements:", [
            "High IOPS for databases (>10,000 IOPS)",
            "Moderate performance for web applications",
            "Maximum throughput for big data",
            "Basic performance for development/testing"
        ])
        
        access_pattern = st.selectbox("Access Pattern:", [
            "Frequent random access",
            "Sequential large file access", 
            "Infrequent but fast access needed",
            "Archive with occasional retrieval"
        ])
    
    with col2:
        st.markdown("### 💰 Budget & Scale")
        budget_constraint = st.selectbox("Budget Priority:", [
            "Performance is priority, cost secondary",
            "Balance performance and cost",
            "Cost optimization is critical",
            "Predictable monthly costs preferred"
        ])
        
        storage_size = st.slider("Expected Storage Size (GB):", 1, 10000, 100)
        
        backup_requirement = st.selectbox("Backup Requirements:", [
            "Point-in-time snapshots needed",
            "Simple file-level backups sufficient",
            "No backup needed (ephemeral data)",
            "Cross-region backup required"
        ])
    
    if st.button("🎯 Recommend Storage Solution", use_container_width=True):
        # Decision logic for storage recommendation
        if "must survive" in data_persistence and "High IOPS" in performance_requirement:
            recommendation = "Amazon EBS (io2 Block Express)"
            use_case = "High-performance persistent storage"
            benefits = ["Up to 256,000 IOPS", "Persistent storage", "Point-in-time snapshots", "99.999% availability"]
        elif "Shared data" in data_persistence:
            recommendation = "Amazon EFS (Elastic File System)"
            use_case = "Shared file system across instances"
            benefits = ["POSIX-compliant", "Automatic scaling", "Multi-AZ access", "Concurrent access"]
        elif "Temporary data" in data_persistence and "Maximum throughput" in performance_requirement:
            recommendation = "EC2 Instance Store"
            use_case = "High-throughput temporary storage"
            benefits = ["Highest performance", "No additional cost", "Ideal for caching", "NVMe SSD available"]
        elif "Archive" in access_pattern:
            recommendation = "Amazon S3 (with appropriate storage class)"
            use_case = "Cost-effective archival and backup"
            benefits = ["Multiple storage classes", "Lifecycle policies", "99.999999999% durability", "Global access"]
        else:
            recommendation = "Amazon EBS (gp3)"
            use_case = "General purpose persistent storage"
            benefits = ["Balance of price and performance", "3,000 IOPS baseline", "Independent IOPS and throughput", "Cost-effective"]
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 🎉 Recommended Storage: {recommendation}
        
        **Use Case:** {use_case}
        
        **Key Benefits:**
        {chr(10).join([f"•{benefit}" for benefit in benefits])}
        
        **Configuration Suggestions:**
        • **Storage Size**: {storage_size} GB
        • **Estimated Monthly Cost**: ${storage_size * 0.08:.2f} - ${storage_size * 0.125:.2f}
        • **Backup Strategy**: {"EBS Snapshots" if "EBS" in recommendation else "Application-level backups"}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed Storage Comparison
    st.markdown("### 📊 Detailed Storage Comparison")
    
    storage_data = {
        'Storage Type': ['EBS gp3', 'EBS io2', 'Instance Store', 'EFS', 'S3'],
        'Persistence': ['Persistent', 'Persistent', 'Temporary', 'Persistent', 'Persistent'],
        'Performance (IOPS)': ['3,000-16,000', '100-256,000', '100,000+', '7,000+', 'N/A'],
        'Durability': ['99.999%', '99.999%', 'Instance lifecycle', '99.999999999%', '99.999999999%'],
        'Use Case': [
            'General purpose workloads',
            'High-performance databases',
            'Caching, temporary data',
            'Shared file systems',
            'Object storage, backups'
        ],
        'Cost ($/GB/month)': ['$0.08', '$0.125', 'Included', '$0.30', '$0.023']
    }
    
    df_storage = pd.DataFrame(storage_data)
    st.dataframe(df_storage, use_container_width=True)
    
    # EBS Volume Types Deep Dive
    st.markdown("### 💽 EBS Volume Types Deep Dive")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚡ General Purpose SSD (gp3)
        
        **Specifications:**
        - **Size**: 1 GB - 16 TB
        - **IOPS**: 3,000 baseline (up to 16,000)
        - **Throughput**: 125 MB/s baseline (up to 1,000 MB/s)
        - **Price**: $0.08/GB/month
        
        **Best For:**
        - Boot volumes
        - Web applications
        - Development environments
        - Small to medium databases
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🚀 Provisioned IOPS SSD (io2)
        
        **Specifications:**
        - **Size**: 4 GB - 64 TB
        - **IOPS**: 100 - 256,000 (50:1 ratio)
        - **Throughput**: Up to 4,000 MB/s
        - **Price**: $0.125/GB/month + $0.065 per IOPS
        
        **Best For:**
        - Critical business applications
        - Large relational databases
        - NoSQL databases
        - I/O-intensive workloads
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 💿 Throughput Optimized HDD (st1)
        
        **Specifications:**
        - **Size**: 125 GB - 16 TB
        - **Throughput**: 40 MB/s/TB (up to 500 MB/s)
        - **IOPS**: 500 per volume
        - **Price**: $0.045/GB/month
        
        **Best For:**
        - Big data workloads
        - Data warehouses
        - Log processing
        - Sequential access patterns
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🗄️ Cold HDD (sc1)
        
        **Specifications:**
        - **Size**: 125 GB - 16 TB
        - **Throughput**: 12 MB/s/TB (up to 250 MB/s)
        - **IOPS**: 250 per volume
        - **Price**: $0.015/GB/month
        
        **Best For:**
        - Infrequently accessed data
        - Archive storage
        - Backup storage
        - Cost-sensitive workloads
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Performance Comparison Chart
    st.markdown("### 📈 Performance vs Cost Analysis")
    
    # Create performance vs cost chart
    storage_types = ['sc1', 'st1', 'gp3', 'io2']
    max_iops = [250, 500, 16000, 256000]
    cost_per_gb = [0.015, 0.045, 0.08, 0.125]
    
    fig = px.scatter(x=cost_per_gb, y=max_iops, 
                     text=storage_types,
                     title='Storage Performance vs Cost',
                     labels={'x': 'Cost per GB/month ($)', 'y': 'Maximum IOPS'},
                     size=[100]*4,
                     color=storage_types,
                     color_discrete_sequence=[AWS_COLORS['success'], AWS_COLORS['light_blue'], 
                                            AWS_COLORS['primary'], AWS_COLORS['warning']])
    
    fig.update_traces(textposition="middle center", textfont_size=12)
    fig.update_layout(height=400, showlegend=False)
    fig.update_yaxes(type="log")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Instance Store Deep Dive
    st.markdown("### ⚡ Instance Store Deep Dive")
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 🚨 Instance Store Characteristics
    
    **High Performance:**
    - Very high random I/O performance
    - Low latency access
    - No network bottlenecks
    - NVMe SSD on modern instances
    
    **Temporary Storage:**
    - Data lost when instance stops/terminates
    - Data persists through reboots
    - Cannot be detached/attached
    - Size varies by instance type
    
    **Best Use Cases:**
    - Caching layers (Redis, Memcached)
    - Temporary processing data
    - High-performance scratch space
    - Replicated data (databases with replicas)
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Instance Store by Instance Type
    instance_store_data = {
        'Instance Type': ['m5d.large', 'm5d.xlarge', 'r5d.large', 'c5d.large', 'i3.large'],
        'Instance Store': ['1x 75 GB NVMe', '1x 150 GB NVMe', '1x 75 GB NVMe', '1x 50 GB NVMe', '1x 475 GB NVMe'],
        'Network Performance': ['Up to 10 Gbps', 'Up to 10 Gbps', 'Up to 10 Gbps', 'Up to 10 Gbps', 'Up to 10 Gbps'],
        'Use Case': [
            'General purpose with local storage',
            'Larger general purpose workloads', 
            'Memory-intensive with local storage',
            'Compute-intensive with local storage',
            'Storage-optimized applications'
        ]
    }
    
    df_instance_store = pd.DataFrame(instance_store_data)
    st.dataframe(df_instance_store, use_container_width=True)
    
    # Storage Best Practices
    st.markdown("### 💡 Storage Best Practices")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🛡️ Data Protection
        
        **EBS Snapshots:**
        - Regular automated snapshots
        - Cross-region backup for DR
        - Lifecycle policies for cost optimization
        - Test restore procedures regularly
        
        **Encryption:**
        - Enable EBS encryption by default
        - Use AWS KMS for key management
        - Encrypt snapshots and AMIs
        - Consider application-level encryption
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📊 Performance Optimization
        
        **EBS Optimization:**
        - Use EBS-optimized instances
        - Avoid small random I/O when possible
        - Pre-warm volumes from snapshots
        - Monitor CloudWatch metrics
        
        **File System:**
        - Choose appropriate file system (ext4, xfs)
        - Align partitions properly
        - Use appropriate mount options
        - Regular filesystem maintenance
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Storage Configuration and Management")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# EC2 Storage Management and Optimization
import boto3
from datetime import datetime, timedelta
import time

class EC2StorageManager:
    def __init__(self, region='us-east-1'):
        self.ec2 = boto3.client('ec2', region_name=region)
        self.region = region
    
    def create_optimized_volume(self, size_gb, volume_type='gp3', iops=None, throughput=None):
        """Create optimized EBS volume"""
        
        volume_config = {
            'Size': size_gb,
            'VolumeType': volume_type,
            'Encrypted': True,  # Always encrypt
            'TagSpecifications': [
                {
                    'ResourceType': 'volume',
                    'Tags': [
                        {'Key': 'Name', 'Value': f'optimized-volume-{datetime.now().strftime("%Y%m%d")}'},
                        {'Key': 'CreatedBy', 'Value': 'StorageManager'},
                        {'Key': 'Environment', 'Value': 'production'}
                    ]
                }
            ]
        }
        
        # Set performance parameters based on volume type
        if volume_type == 'gp3':
            if iops and 3000 <= iops <= 16000:
                volume_config['Iops'] = iops
            if throughput and 125 <= throughput <= 1000:
                volume_config['Throughput'] = throughput
        
        elif volume_type in ['io1', 'io2']:
            if not iops:
                iops = min(50 * size_gb, 64000)  # Default to 50 IOPS per GB
            volume_config['Iops'] = iops
        
        try:
            response = self.ec2.create_volume(**volume_config)
            volume_id = response['VolumeId']
            
            print(f"✅ Created {volume_type} volume: {volume_id}")
            print(f"   Size: {size_gb} GB")
            if 'Iops' in volume_config:
                print(f"   IOPS: {volume_config['Iops']}")
            if 'Throughput' in volume_config:
                print(f"   Throughput: {volume_config['Throughput']} MB/s")
            
            return volume_id
            
        except Exception as e:
            print(f"❌ Error creating volume: {e}")
            return None
    
    def attach_volume_to_instance(self, volume_id, instance_id, device='/dev/sdf'):
        """Attach EBS volume to EC2 instance"""
        try:
            response = self.ec2.attach_volume(
                VolumeId=volume_id,
                InstanceId=instance_id,
                Device=device
            )
            
            print(f"📎 Attaching volume {volume_id} to instance {instance_id}")
            
            # Wait for attachment to complete
            waiter = self.ec2.get_waiter('volume_in_use')
            waiter.wait(VolumeIds=[volume_id])
            
            print(f"✅ Volume {volume_id} successfully attached to {instance_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error attaching volume: {e}")
            return False
    
    def create_snapshot(self, volume_id, description=""):
        """Create EBS snapshot with proper tagging"""
        try:
            response = self.ec2.create_snapshot(
                VolumeId=volume_id,
                Description=description or f"Snapshot of {volume_id} created on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                TagSpecifications=[
                    {
                        'ResourceType': 'snapshot',
                        'Tags': [
                            {'Key': 'Name', 'Value': f'snapshot-{volume_id}-{datetime.now().strftime("%Y%m%d-%H%M")}'},
                            {'Key': 'SourceVolume', 'Value': volume_id},
                            {'Key': 'CreatedBy', 'Value': 'StorageManager'},
                            {'Key': 'BackupDate', 'Value': datetime.now().strftime('%Y-%m-%d')}
                        ]
                    }
                ]
            )
            
            snapshot_id = response['SnapshotId']
            print(f"📸 Snapshot creation initiated: {snapshot_id}")
            
            return snapshot_id
            
        except Exception as e:
            print(f"❌ Error creating snapshot: {e}")
            return None
    
    def setup_automated_snapshots(self, volume_ids, schedule='daily'):
        """Setup automated snapshot schedule using Data Lifecycle Manager"""
        dlm = boto3.client('dlm', region_name=self.region)
        
        policy_document = {
            'ResourceTypes': ['VOLUME'],
            'TargetTags': [
                {'Key': 'Environment', 'Value': 'production'}
            ],
            'Schedules': [
                {
                    'Name': f'{schedule}-snapshots',
                    'CreateRule': {
                        'Interval': 24 if schedule == 'daily' else 168,  # hours
                        'IntervalUnit': 'HOURS',
                        'Times': ['23:00']  # 11 PM UTC
                    },
                    'RetentionRule': {
                        'Count': 7 if schedule == 'daily' else 4  # Keep 7 daily or 4 weekly
                    },
                    'TagsToAdd': [
                        {'Key': 'CreatedBy', 'Value': 'DLM'},
                        {'Key': 'Schedule', 'Value': schedule}
                    ],
                    'CopyTags': True
                }
            ]
        }
        
        try:
            response = dlm.create_lifecycle_policy(
                ExecutionRoleArn=f'arn:aws:iam::{boto3.client("sts").get_caller_identity()["Account"]}:role/AWSDataLifecycleManagerDefaultRole',
                Description=f'Automated {schedule} snapshots for production volumes',
                State='ENABLED',
                PolicyDetails=policy_document
            )
            
            policy_id = response['PolicyId']
            print(f"🔄 Automated snapshot policy created: {policy_id}")
            return policy_id
            
        except Exception as e:
            print(f"❌ Error creating snapshot policy: {e}")
            return None
    
    def monitor_storage_performance(self, volume_id, duration_minutes=60):
        """Monitor EBS volume performance using CloudWatch"""
        cloudwatch = boto3.client('cloudwatch', region_name=self.region)
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=duration_minutes)
        
        metrics_to_check = [
            'VolumeReadOps', 'VolumeWriteOps',
            'VolumeTotalReadTime', 'VolumeTotalWriteTime',
            'VolumeQueueLength', 'VolumeThroughputPercentage',
            'VolumeConsumedReadWriteOps'
        ]
        
        performance_data = {}
        
        for metric in metrics_to_check:
            try:
                response = cloudwatch.get_metric_statistics(
                    Namespace='AWS/EBS',
                    MetricName=metric,
                    Dimensions=[
                        {'Name': 'VolumeId', 'Value': volume_id}
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=300,  # 5-minute intervals
                    Statistics=['Average', 'Maximum']
                )
                
                if response['Datapoints']:
                    avg_value = sum([dp['Average'] for dp in response['Datapoints']]) / len(response['Datapoints'])
                    max_value = max([dp['Maximum'] for dp in response['Datapoints']])
                    performance_data[metric] = {'average': avg_value, 'maximum': max_value}
                
            except Exception as e:
                print(f"Warning: Could not get {metric} for {volume_id}: {e}")
        
        return performance_data
    
    def optimize_volume_performance(self, volume_id):
        """Analyze and provide optimization recommendations"""
        print(f"🔍 Analyzing performance for volume {volume_id}")
        
        # Get volume details
        try:
            response = self.ec2.describe_volumes(VolumeIds=[volume_id])
            volume = response['Volumes'][0]
            
            volume_type = volume['VolumeType']
            size = volume['Size']
            iops = volume.get('Iops', 0)
            
            print(f"📊 Volume Details:")
            print(f"   Type: {volume_type}")
            print(f"   Size: {size} GB") 
            print(f"   Provisioned IOPS: {iops}")
            
        except Exception as e:
            print(f"❌ Error getting volume details: {e}")
            return
        
        # Get performance metrics
        perf_data = self.monitor_storage_performance(volume_id)
        
        recommendations = []
        
        # Analyze IOPS utilization
        if 'VolumeConsumedReadWriteOps' in perf_data:
            consumed_iops = perf_data['VolumeConsumedReadWriteOps']['average']
            if volume_type == 'gp3' and consumed_iops > 2400:  # 80% of baseline
                recommendations.append(
                    f"Consider increasing IOPS from {iops} to {int(consumed_iops * 1.5)} for better performance"
                )
        
        # Analyze queue depth
        if 'VolumeQueueLength' in perf_data:
            avg_queue = perf_data['VolumeQueueLength']['average']
            if avg_queue > 32:
                recommendations.append(
                    "High queue depth detected - consider io2 volume type for lower latency"
                )
        
        # Analyze utilization percentage
        if 'VolumeThroughputPercentage' in perf_data:
            throughput_pct = perf_data['VolumeThroughputPercentage']['average']
            if throughput_pct > 80:
                recommendations.append(
                    "High throughput utilization - consider increasing volume throughput or using st1 for sequential workloads"
                )
        
        print(f"\n💡 Optimization Recommendations:")
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        else:
            print("   Volume performance appears to be well-optimized!")
        
        return recommendations

# Example usage
def main():
    storage_manager = EC2StorageManager()
    
    # Create high-performance volume for database
    volume_id = storage_manager.create_optimized_volume(
        size_gb=500,
        volume_type='gp3',
        iops=5000,
        throughput=250
    )
    
    if volume_id:
        # Attach to instance
        instance_id = 'i-1234567890abcdef0'
        storage_manager.attach_volume_to_instance(volume_id, instance_id)
        
        # Create initial snapshot
        snapshot_id = storage_manager.create_snapshot(
            volume_id, 
            "Initial snapshot after volume setup"
        )
        
        # Setup automated backups
        policy_id = storage_manager.setup_automated_snapshots([volume_id])
        
        # Monitor performance (would run after some usage)
        time.sleep(300)  # Wait 5 minutes for some metrics
        storage_manager.optimize_volume_performance(volume_id)

if __name__ == "__main__":
    main()
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def ec2_auto_scaling_tab():
    """Content for Amazon EC2 Auto Scaling tab"""
    st.markdown("## 📈 Amazon EC2 Auto Scaling")
    st.markdown("*Automatically adjust EC2 capacity to meet demand while optimizing costs*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Amazon EC2 Auto Scaling** helps you maintain application availability and allows you to automatically add or remove 
    EC2 instances according to conditions you define. It helps ensure you have the right number of instances available 
    to handle the load for your application.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Auto Scaling Architecture
    st.markdown("### 🏗️ Auto Scaling Architecture")
    common.mermaid(create_auto_scaling_mermaid(), height=400)
    
    # Interactive Auto Scaling Configuration
    st.markdown("### 🛠️ Interactive Auto Scaling Group Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚙️ Basic Configuration")
        asg_name = st.text_input("Auto Scaling Group Name:", "my-web-app-asg")
        min_capacity = st.slider("Minimum Capacity:", 1, 10, 2)
        desired_capacity = st.slider("Desired Capacity:", min_capacity, 20, 4)
        max_capacity = st.slider("Maximum Capacity:", desired_capacity, 100, 10)
        
        instance_types = st.multiselect("Instance Types:", [
            "t3.micro", "t3.small", "t3.medium", "m5.large", "m5.xlarge", "c5.large"
        ], default=["t3.small", "t3.medium"], key="instance_types")
        
        availability_zones = st.multiselect("Availability Zones:", [
            "us-east-1a", "us-east-1b", "us-east-1c"
        ], default=["us-east-1a", "us-east-1b"], key="availability_zones")
    
    with col2:
        st.markdown("### 📊 Scaling Policies")
        scaling_policy = st.selectbox("Primary Scaling Policy:", [
            "Target Tracking (CPU Utilization)",
            "Target Tracking (ALB Request Count)",
            "Step Scaling (Custom Metrics)",
            "Scheduled Scaling",
            "Predictive Scaling"
        ])
        
        if "CPU" in scaling_policy:
            target_cpu = st.slider("Target CPU Utilization (%):", 10, 90, 70)
        elif "ALB" in scaling_policy:
            target_requests = st.slider("Target Requests per Instance:", 100, 5000, 1000)
        
        health_check = st.selectbox("Health Check Type:", [
            "EC2 (Default)", "ELB", "EC2 + ELB"
        ])
        
        warmup_time = st.slider("Instance Warm-up Time (seconds):", 60, 600, 300)
    
    # Advanced Settings
    st.markdown("### 🔧 Advanced Configuration")
    col3, col4 = st.columns(2)
    
    with col3:
        termination_policy = st.multiselect("Termination Policies:", [
            "OldestInstance", "NewestInstance", "OldestLaunchTemplate", "Default"
        ], default=["Default"])
        
        mixed_instances = st.checkbox("Use Mixed Instance Types", value=True)
        spot_instances = st.checkbox("Include Spot Instances", value=False)
    
    with col4:
        lifecycle_hooks = st.checkbox("Enable Lifecycle Hooks", value=False)
        notifications = st.checkbox("Send SNS Notifications", value=True)
        
        if spot_instances:
            spot_percentage = st.slider("Spot Instance Percentage:", 0, 100, 30)
    
    if st.button("🚀 Create Auto Scaling Configuration", use_container_width=True):
        # Calculate estimated costs
        base_cost_per_hour = {"t3.micro": 0.0104, "t3.small": 0.0208, "t3.medium": 0.0416,
                             "m5.large": 0.096, "m5.xlarge": 0.192, "c5.large": 0.085}
        avg_cost = sum([base_cost_per_hour.get(inst, 0.05) for inst in instance_types]) / len(instance_types)
        estimated_monthly_cost = avg_cost * desired_capacity * 24 * 30
        
        if spot_instances:
            estimated_monthly_cost *= (1 - (spot_percentage / 100) * 0.7)  # Assume 70% savings on spot
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ Auto Scaling Group Configuration Complete!
        
        **Basic Settings:**
        - **Name**: {asg_name}
        - **Capacity**: Min={min_capacity}, Desired={desired_capacity}, Max={max_capacity}
        - **Instance Types**: {', '.join(instance_types)}
        - **Availability Zones**: {', '.join(availability_zones)}
        
        **Scaling Configuration:**
        - **Policy**: {scaling_policy}
        - **Health Check**: {health_check}
        - **Warm-up Time**: {warmup_time} seconds
        
        **Advanced Features:**
        - **Mixed Instances**: {'✅ Enabled' if mixed_instances else '❌ Disabled'}
        - **Spot Instances**: {'✅ ' + str(spot_percentage) + '%' if spot_instances else '❌ Disabled'}
        - **Lifecycle Hooks**: {'✅ Enabled' if lifecycle_hooks else '❌ Disabled'}
        
        **💰 Estimated Monthly Cost**: ${estimated_monthly_cost:.2f}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Scaling Policies Deep Dive
    st.markdown("### 📊 Scaling Policies Explained")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 Target Tracking Scaling
        
        **How it works:**
        - Set a target value for a specific metric
        - Auto Scaling automatically creates CloudWatch alarms
        - Scales in/out to maintain target value
        
        **Common Metrics:**
        - Average CPU Utilization
        - ALB Request Count per Target
        - Custom CloudWatch metrics
        
        **Best For:**
        - Most common scaling scenarios
        - Predictable performance requirements
        - Simple configuration and management
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📈 Step Scaling
        
        **How it works:**
        - Define multiple scaling steps
        - Different scaling amounts for different alarm ranges
        - More granular control over scaling decisions
        
        **Example:**
        - CPU 50-70%: Add 1 instance
        - CPU 70-85%: Add 2 instances  
        - CPU >85%: Add 3 instances
        
        **Best For:**
        - Complex scaling requirements
        - Applications with non-linear scaling needs
        - Custom metric-based scaling
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ⏰ Scheduled Scaling
        
        **How it works:**
        - Scale based on predictable time patterns
        - Set minimum, maximum, and desired capacity
        - Supports one-time or recurring schedules
        
        **Use Cases:**
        - Business hours scaling (9 AM - 5 PM)
        - Weekend scale-down
        - Seasonal traffic patterns
        - Batch processing windows
        
        **Best For:**
        - Predictable traffic patterns
        - Cost optimization
        - Proactive scaling
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔮 Predictive Scaling
        
        **How it works:**
        - Machine learning analyzes historical data
        - Predicts future traffic patterns
        - Pre-scales instances before load increases
        
        **Requirements:**
        - At least 14 days of historical data
        - Regular, predictable traffic patterns
        - Works with target tracking policies
        
        **Best For:**
        - Applications with regular patterns
        - Reducing scaling lag time
        - Improved user experience
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Scaling Metrics Visualization
    st.markdown("### 📊 Scaling Metrics Simulation")
    
    # Interactive scaling simulation
    col1, col2 = st.columns(2)
    
    with col1:
        simulation_hours = st.slider("Simulation Duration (hours):", 6, 48, 24)
        traffic_pattern = st.selectbox("Traffic Pattern:", [
            "Business Hours (9-5)", "E-commerce (Evening Peak)", "Gaming (Night Peak)", "Global (24/7)"
        ])
    
    with col2:
        target_utilization = st.slider("Target CPU Utilization (%):", 50, 80, 70)
        scale_out_cooldown = st.slider("Scale-out Cooldown (minutes):", 1, 10, 5)
    
    if st.button("📊 Run Scaling Simulation"):
        # Generate simulated traffic data
        hours = list(range(simulation_hours))
        
        if traffic_pattern == "Business Hours (9-5)":
            traffic = [30 + 40 * max(0, min(1, (h % 24 - 8) / 8)) if 8 <= h % 24 <= 17 else 20 for h in hours]
        elif traffic_pattern == "E-commerce (Evening Peak)":
            traffic = [30 + 50 * max(0, 1 - abs(h % 24 - 20) / 10) for h in hours]
        elif traffic_pattern == "Gaming (Night Peak)":
            traffic = [25 + 45 * max(0, 1 - abs(h % 24 - 2) / 8) for h in hours]
        else:  # Global
            traffic = [40 + 20 * np.sin(h * np.pi / 12) + np.random.normal(0, 5) for h in hours]
        
        # Calculate required instances (simplified)
        required_instances = [max(1, int(t / target_utilization * 2)) for t in traffic]
        
        # Create visualization
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Traffic Load (%)', 'Auto Scaling Response'),
            shared_xaxes=True
        )
        
        fig.add_trace(
            go.Scatter(x=hours, y=traffic, name='CPU Utilization', 
                      line=dict(color=AWS_COLORS['warning'])),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=hours, y=[target_utilization]*len(hours), 
                      name='Target Utilization', 
                      line=dict(color=AWS_COLORS['primary'], dash='dash')),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=hours, y=required_instances, name='Instance Count',
                      line=dict(color=AWS_COLORS['light_blue']), fill='tonexty'),
            row=2, col=1
        )
        
        fig.update_layout(height=500, showlegend=True)
        fig.update_xaxes(title_text="Time (hours)", row=2, col=1)
        fig.update_yaxes(title_text="CPU %", row=1, col=1)
        fig.update_yaxes(title_text="Instances", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate savings
        max_instances = max(required_instances)
        avg_instances = sum(required_instances) / len(required_instances)
        cost_with_scaling = avg_instances * 0.10 * simulation_hours  # $0.10/hour per instance
        cost_without_scaling = max_instances * 0.10 * simulation_hours
        savings = cost_without_scaling - cost_with_scaling
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Peak Instances", max_instances)
        with col2:
            st.metric("Average Instances", f"{avg_instances:.1f}")
        with col3:
            st.metric("Cost Savings", f"${savings:.2f}", f"{(savings/cost_without_scaling)*100:.1f}%")
    
    # Best Practices
    st.markdown("### 💡 Auto Scaling Best Practices")
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Configuration Best Practices
    
    **Capacity Planning:**
    - Start with desired capacity = minimum capacity
    - Set maximum capacity 2-3x higher than typical peak
    - Use multiple instance types for better availability
    - Distribute across multiple AZs
    
    **Scaling Policies:**
    - Use target tracking for most scenarios
    - Set appropriate warm-up times (typically 300 seconds)
    - Avoid aggressive scaling to prevent thrashing
    - Monitor and adjust thresholds based on metrics
    
    **Health Checks:**
    - Use ELB health checks for web applications
    - Set appropriate health check grace period
    - Consider custom health checks for complex applications
    - Monitor failed health checks and fix root causes
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Auto Scaling Group Management")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Complete Auto Scaling Group Management
import boto3
import json
from datetime import datetime, timedelta

class AutoScalingManager:
    def __init__(self, region='us-east-1'):
        self.asg_client = boto3.client('autoscaling', region_name=region)
        self.ec2_client = boto3.client('ec2', region_name=region)
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        self.region = region
    
    def create_launch_template(self, template_name, ami_id, instance_types, security_groups, user_data=""):
        """Create launch template for Auto Scaling Group"""
        
        template_data = {
            'ImageId': ami_id,
            'SecurityGroupIds': security_groups,
            'UserData': user_data,
            'TagSpecifications': [
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {'Key': 'Name', 'Value': 'AutoScaled-Instance'},
                        {'Key': 'Environment', 'Value': 'production'},
                        {'Key': 'ManagedBy', 'Value': 'AutoScaling'}
                    ]
                }
            ],
            'MetadataOptions': {
                'HttpTokens': 'required',  # IMDSv2 only
                'HttpPutResponseHopLimit': 2
            },
            'Monitoring': {'Enabled': True}  # Enable detailed monitoring
        }
        
        # For mixed instance types, don't specify InstanceType in template
        if len(instance_types) == 1:
            template_data['InstanceType'] = instance_types[0]
        
        try:
            response = self.ec2_client.create_launch_template(
                LaunchTemplateName=template_name,
                LaunchTemplateData=template_data
            )
            
            template_id = response['LaunchTemplate']['LaunchTemplateId']
            print(f"✅ Created launch template: {template_id}")
            return template_id
            
        except Exception as e:
            print(f"❌ Error creating launch template: {e}")
            return None
    
    def create_auto_scaling_group(self, asg_config):
        """Create Auto Scaling Group with comprehensive configuration"""
        
        try:
            # Basic ASG configuration
            asg_params = {
                'AutoScalingGroupName': asg_config['name'],
                'MinSize': asg_config['min_size'],
                'MaxSize': asg_config['max_size'],
                'DesiredCapacity': asg_config['desired_capacity'],
                'VPCZoneIdentifier': ','.join(asg_config['subnets']),
                'HealthCheckType': asg_config.get('health_check_type', 'EC2'),
                'HealthCheckGracePeriod': asg_config.get('health_check_grace_period', 300),
                'DefaultCooldown': asg_config.get('default_cooldown', 300),
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': asg_config['name'],
                        'PropagateAtLaunch': True,
                        'ResourceId': asg_config['name'],
                        'ResourceType': 'auto-scaling-group'
                    }
                ]
            }
            
            # Configure launch template or mixed instances
            if asg_config.get('mixed_instances', False):
                asg_params['MixedInstancesPolicy'] = {
                    'LaunchTemplate': {
                        'LaunchTemplateSpecification': {
                            'LaunchTemplateId': asg_config['launch_template_id'],
                            'Version': '$Latest'
                        },
                        'Overrides': [
                            {'InstanceType': inst_type} for inst_type in asg_config['instance_types']
                        ]
                    },
                    'InstancesDistribution': {
                        'OnDemandBaseCapacity': asg_config.get('on_demand_base', 1),
                        'OnDemandPercentageAboveBaseCapacity': asg_config.get('on_demand_percentage', 50),
                        'SpotAllocationStrategy': 'diversified'
                    }
                }
            else:
                asg_params['LaunchTemplate'] = {
                    'LaunchTemplateId': asg_config['launch_template_id'],
                    'Version': '$Latest'
                }
            
            # Add target group ARNs if provided
            if asg_config.get('target_group_arns'):
                asg_params['TargetGroupARNs'] = asg_config['target_group_arns']
            
            response = self.asg_client.create_auto_scaling_group(**asg_params)
            
            print(f"✅ Created Auto Scaling Group: {asg_config['name']}")
            return asg_config['name']
            
        except Exception as e:
            print(f"❌ Error creating Auto Scaling Group: {e}")
            return None
    
    def create_target_tracking_policy(self, asg_name, policy_name, target_value, metric_type='cpu'):
        """Create target tracking scaling policy"""
        
        # Define target tracking configuration based on metric type
        if metric_type == 'cpu':
            target_tracking_config = {
                'PredefinedMetricSpecification': {
                    'PredefinedMetricType': 'ASGAverageCPUUtilization'
                },
                'TargetValue': target_value,
                'ScaleOutCooldown': 300,
                'ScaleInCooldown': 300
            }
        elif metric_type == 'alb_requests':
            target_tracking_config = {
                'PredefinedMetricSpecification': {
                    'PredefinedMetricType': 'ALBRequestCountPerTarget',
                    'ResourceLabel': 'app/my-load-balancer/50dc6c495c0c9188/targetgroup/my-targets/73e2d6bc24d8a067'
                },
                'TargetValue': target_value,
                'ScaleOutCooldown': 300,
                'ScaleInCooldown': 300
            }
        
        try:
            response = self.asg_client.put_scaling_policy(
                PolicyName=policy_name,
                AutoScalingGroupName=asg_name,
                PolicyType='TargetTrackingScaling',
                TargetTrackingConfiguration=target_tracking_config
            )
            
            policy_arn = response['PolicyARN']
            print(f"✅ Created target tracking policy: {policy_name}")
            return policy_arn
            
        except Exception as e:
            print(f"❌ Error creating scaling policy: {e}")
            return None
    
    def create_scheduled_action(self, asg_name, action_name, schedule, desired_capacity, min_size=None, max_size=None):
        """Create scheduled scaling action"""
        
        try:
            params = {
                'AutoScalingGroupName': asg_name,
                'ScheduledActionName': action_name,
                'Recurrence': schedule,  # Cron expression
                'DesiredCapacity': desired_capacity
            }
            
            if min_size is not None:
                params['MinSize'] = min_size
            if max_size is not None:
                params['MaxSize'] = max_size
            
            self.asg_client.put_scheduled_update_group_action(**params)
            print(f"✅ Created scheduled action: {action_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating scheduled action: {e}")
            return False
    
    def monitor_asg_performance(self, asg_name, hours=24):
        """Monitor Auto Scaling Group performance and health"""
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        metrics = {}
        
        # Get Auto Scaling metrics
        asg_metrics = [
            'GroupMinSize', 'GroupMaxSize', 'GroupDesiredCapacity',
            'GroupInServiceInstances', 'GroupTotalInstances'
        ]
        
        for metric in asg_metrics:
            try:
                response = self.cloudwatch.get_metric_statistics(
                    Namespace='AWS/AutoScaling',
                    MetricName=metric,
                    Dimensions=[
                        {'Name': 'AutoScalingGroupName', 'Value': asg_name}
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=3600,  # 1 hour
                    Statistics=['Average', 'Maximum', 'Minimum']
                )
                
                if response['Datapoints']:
                    metrics[metric] = {
                        'average': sum([dp['Average'] for dp in response['Datapoints']]) / len(response['Datapoints']),
                        'maximum': max([dp['Maximum'] for dp in response['Datapoints']]),
                        'minimum': min([dp['Minimum'] for dp in response['Datapoints']])
                    }
                    
            except Exception as e:
                print(f"Warning: Could not retrieve {metric}: {e}")
        
        # Get scaling activities
        try:
            activities = self.asg_client.describe_scaling_activities(
                AutoScalingGroupName=asg_name,
                MaxRecords=50
            )
            
            recent_activities = []
            for activity in activities['Activities']:
                if activity['StartTime'] >= start_time:
                    recent_activities.append({
                        'time': activity['StartTime'],
                        'description': activity['Description'],
                        'status': activity['StatusCode'],
                        'cause': activity.get('Cause', 'N/A')
                    })
            
            metrics['scaling_activities'] = recent_activities
            
        except Exception as e:
            print(f"Warning: Could not retrieve scaling activities: {e}")
        
        return metrics
    
    def optimize_asg_configuration(self, asg_name):
        """Analyze ASG performance and provide optimization recommendations"""
        
        print(f"🔍 Analyzing Auto Scaling Group: {asg_name}")
        
        # Get current configuration
        try:
            response = self.asg_client.describe_auto_scaling_groups(
                AutoScalingGroupNames=[asg_name]
            )
            asg = response['AutoScalingGroups'][0]
            
            print(f"📊 Current Configuration:")
            print(f"   Min: {asg['MinSize']}, Desired: {asg['DesiredCapacity']}, Max: {asg['MaxSize']}")
            print(f"   Instances: {len(asg['Instances'])} in service")
            print(f"   Health Check: {asg['HealthCheckType']}")
            
        except Exception as e:
            print(f"❌ Error getting ASG configuration: {e}")
            return
        
        # Get performance metrics
        metrics = self.monitor_asg_performance(asg_name)
        
        recommendations = []
        
        # Analyze capacity utilization
        if 'GroupDesiredCapacity' in metrics and 'GroupMaxSize' in metrics:
            avg_desired = metrics['GroupDesiredCapacity']['average']
            max_capacity = metrics['GroupMaxSize']['maximum']
            
            utilization = avg_desired / max_capacity
            
            if utilization > 0.8:
                recommendations.append(
                    f"High capacity utilization ({utilization:.1%}) - consider increasing max capacity"
                )
            elif utilization < 0.3:
                recommendations.append(
                    f"Low capacity utilization ({utilization:.1%}) - consider reducing max capacity to save costs"
                )
        
        # Analyze scaling frequency
        if 'scaling_activities' in metrics:
            scale_out_activities = [a for a in metrics['scaling_activities'] if 'scale out' in a['description'].lower()]
            scale_in_activities = [a for a in metrics['scaling_activities'] if 'scale in' in a['description'].lower()]
            
            if len(scale_out_activities) > 10:
                recommendations.append(
                    "Frequent scale-out activities detected - consider predictive scaling or lower target utilization"
                )
            
            if len(scale_in_activities) < 2 and len(scale_out_activities) > 5:
                recommendations.append(
                    "Instances scaling out but not scaling in - review scale-in policies and cooldowns"
                )
        
        # Check instance health
        unhealthy_instances = [i for i in asg['Instances'] if i['HealthStatus'] != 'Healthy']
        if unhealthy_instances:
            recommendations.append(
                f"{len(unhealthy_instances)} unhealthy instances detected - investigate root cause"
            )
        
        print(f"\n💡 Optimization Recommendations:")
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        else:
            print("   Auto Scaling Group appears to be well-configured!")
        
        return recommendations

# Example usage
def main():
    asg_manager = AutoScalingManager()
    
    # Create launch template
    template_id = asg_manager.create_launch_template(
        template_name='web-app-template',
        ami_id='ami-0abcdef1234567890',
        instance_types=['t3.small', 't3.medium'],
        security_groups=['sg-12345678'],
        user_data="""#!/bin/bash
        yum update -y
        yum install -y httpd
        systemctl start httpd
        systemctl enable httpd
        echo "<h1>Auto Scaled Instance $(curl -s http://169.254.169.254/latest/meta-data/instance-id)</h1>" > /var/www/html/index.html
        """
    )
    
    if template_id:
        # Create Auto Scaling Group
        asg_config = {
            'name': 'my-web-app-asg',
            'min_size': 2,
            'max_size': 10,
            'desired_capacity': 3,
            'launch_template_id': template_id,
            'instance_types': ['t3.small', 't3.medium'],
            'subnets': ['subnet-12345', 'subnet-67890'],
            'health_check_type': 'ELB',
            'health_check_grace_period': 300,
            'mixed_instances': True,
            'on_demand_percentage': 70
        }
        
        asg_name = asg_manager.create_auto_scaling_group(asg_config)
        
        if asg_name:
            # Create scaling policies
            asg_manager.create_target_tracking_policy(
                asg_name=asg_name,
                policy_name='cpu-target-tracking',
                target_value=70.0,
                metric_type='cpu'
            )
            
            # Create scheduled actions
            asg_manager.create_scheduled_action(
                asg_name=asg_name,
                action_name='scale-up-business-hours',
                schedule='0 8 * * MON-FRI',  # 8 AM Monday-Friday
                desired_capacity=5,
                min_size=3
            )
            
            asg_manager.create_scheduled_action(
                asg_name=asg_name,
                action_name='scale-down-evening',
                schedule='0 18 * * *',  # 6 PM daily
                desired_capacity=2,
                min_size=2
            )
            
            # Monitor and optimize (would run after some time)
            asg_manager.optimize_asg_configuration(asg_name)

if __name__ == "__main__":
    main()
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def elastic_load_balancing_tab():
    """Content for Elastic Load Balancing tab"""
    st.markdown("## ⚖️ Elastic Load Balancing")
    st.markdown("*Distribute network traffic to improve application scalability and availability*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Elastic Load Balancing (ELB)** automatically distributes incoming application traffic across multiple targets, 
    such as Amazon EC2 instances, containers, IP addresses, Lambda functions, and virtual appliances. It helps ensure 
    no single resource is overwhelmed and provides fault tolerance.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Load Balancer Types
    st.markdown("### 🏗️ Load Balancer Types Overview")
    common.mermaid(create_load_balancer_mermaid(), height=400)
    
    # Interactive Load Balancer Selector
    st.markdown("### 🔍 Interactive Load Balancer Selector")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Application Requirements")
        protocol_type = st.selectbox("Primary Protocol:", [
            "HTTP/HTTPS (Web applications)",
            "TCP/UDP (Database, gaming, IoT)",
            "Mixed protocols with 3rd party inspection",
            "Legacy applications (HTTP/HTTPS/TCP)"
        ])
        
        performance_needs = st.selectbox("Performance Requirements:", [
            "Standard web application performance",
            "Ultra-high performance (millions RPS)",
            "Low latency for real-time applications",
            "Basic load distribution"
        ])
        
        routing_complexity = st.selectbox("Routing Requirements:", [
            "Simple round-robin distribution",
            "Content-based routing (path, host, headers)",
            "IP address preservation required",
            "3rd party security appliance integration"
        ])
    
    with col2:
        st.markdown("### 🌐 Architecture Needs")
        target_types = st.multiselect("Target Types:", [
            "EC2 Instances", "ECS Tasks", "Lambda Functions", 
            "IP Addresses", "Auto Scaling Groups"
        ], default=["EC2 Instances"])
        
        availability_zones = st.multiselect("Availability Zones:", [
            "us-east-1a", "us-east-1b", "us-east-1c"
        ], default=["us-east-1a", "us-east-1b"])
        
        ssl_termination = st.checkbox("SSL/TLS Termination at Load Balancer", value=True)
        sticky_sessions = st.checkbox("Session Affinity (Sticky Sessions)", value=False)
    
    if st.button("🎯 Recommend Load Balancer Type", use_container_width=True):
        # Decision logic for load balancer recommendation
        if "Ultra-high performance" in performance_needs or "TCP/UDP" in protocol_type:
            recommendation = "Network Load Balancer (NLB)"
            use_case = "High-performance Layer 4 load balancing"
            benefits = ["Millions of requests per second", "Ultra-low latency", "Static IP addresses", "Source IP preservation"]
            considerations = ["No content-based routing", "TCP/UDP only", "More expensive than ALB"]
        elif "Content-based routing" in routing_complexity or "Lambda Functions" in target_types:
            recommendation = "Application Load Balancer (ALB)"
            use_case = "Advanced Layer 7 HTTP/HTTPS load balancing"
            benefits = ["Content-based routing", "WebSocket support", "Lambda integration", "Container support"]
            considerations = ["HTTP/HTTPS only", "Slightly higher latency than NLB", "More complex configuration"]
        elif "3rd party security" in routing_complexity:
            recommendation = "Gateway Load Balancer (GWLB)"
            use_case = "3rd party security appliance integration"
            benefits = ["Transparent network gateway", "3rd party appliance support", "Security inspection", "High availability"]
            considerations = ["Specialized use case", "Requires compatible appliances", "Additional complexity"]
        elif "Legacy applications" in protocol_type:
            recommendation = "Classic Load Balancer (CLB) - Consider Migration"
            use_case = "Legacy support (migration recommended)"
            benefits = ["Simple configuration", "EC2-Classic support", "Basic Layer 4/7 features"]
            considerations = ["Being phased out", "Limited features", "No container support", "Higher cost"]
        else:
            recommendation = "Application Load Balancer (ALB)"
            use_case = "Standard web application load balancing"
            benefits = ["Cost-effective", "Advanced routing", "Container support", "AWS integration"]
            considerations = ["HTTP/HTTPS only", "Learning curve for advanced features"]
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 🎉 Recommended: {recommendation}
        
        **Use Case:** {use_case}
        
        **Key Benefits:**
        {chr(10).join([f"• {benefit}" for benefit in benefits])}
        
        **Considerations:**
        {chr(10).join([f"• {consideration}" for consideration in considerations])}
        
        **Configuration:**
        - **Target Types**: {', '.join(target_types)}
        - **Availability Zones**: {', '.join(availability_zones)}
        - **SSL Termination**: {'✅ Enabled' if ssl_termination else '❌ Disabled'}
        - **Sticky Sessions**: {'✅ Enabled' if sticky_sessions else '❌ Disabled'}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed Comparison
    st.markdown("### 📊 Load Balancer Detailed Comparison")
    
    comparison_data = {
        'Feature': [
            'OSI Layer', 'Protocols', 'Targets', 'Routing', 'Performance',
            'Static IP', 'SSL Termination', 'WebSocket', 'Container Support',
            'Pricing Model', 'Best For'
        ],
        'Application LB': [
            'Layer 7', 'HTTP/HTTPS', 'EC2, ECS, Lambda, IP', 'Content-based',
            'High', 'No', 'Yes', 'Yes', 'Native',
            'LCU-based', 'Web applications'
        ],
        'Network LB': [
            'Layer 4', 'TCP/UDP/TLS', 'EC2, ECS, IP', 'Flow hash',
            'Ultra High', 'Yes', 'TLS only', 'No', 'Via IP',
            'LCU-based', 'High performance'
        ],
        'Gateway LB': [
            'Layer 3', 'All IP packets', 'EC2, IP', 'Flow hash',
            'High', 'No', 'No', 'No', 'Via IP',
            'LCU-based', '3rd party appliances'
        ],
        'Classic LB': [
            'Layer 4/7', 'HTTP/HTTPS/TCP', 'EC2 only', 'Basic',
            'Medium', 'No', 'Yes', 'No', 'Limited',
            'Hour + Data', 'Legacy (deprecated)'
        ]
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True)
    
    # Health Checks Deep Dive
    st.markdown("### 🏥 Health Checks Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚡ Application Load Balancer Health Checks
        
        **HTTP/HTTPS Health Checks:**
        - **Path**: `/health`, `/status`, `/`
        - **Status Codes**: 200, 202, 302 (customizable)
        - **Timeout**: 2-120 seconds (default: 5s)
        - **Interval**: 5-300 seconds (default: 30s)
        - **Thresholds**: 2-10 (healthy/unhealthy)
        
        **Advanced Features:**
        - Custom request headers
        - Response body pattern matching
        - gRPC health checks
        - Port override per target
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🌐 Network Load Balancer Health Checks
        
        **TCP Health Checks:**
        - Connection establishment test
        - Port-level health verification
        - No HTTP-level checks
        
        **HTTP/HTTPS Health Checks:**
        - Available for HTTP/HTTPS listeners
        - Same configuration as ALB
        - More comprehensive than TCP
        
        **Characteristics:**
        - Faster failure detection
        - Lower overhead
        - Suitable for non-HTTP services
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Health Check Configuration
    st.markdown("### 🔧 Interactive Health Check Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        health_check_protocol = st.selectbox("Health Check Protocol:", ["HTTP", "HTTPS", "TCP"])
        health_check_path = st.text_input("Health Check Path:", "/health")
        health_check_port = st.number_input("Health Check Port:", 1, 65535, 80)
    
    with col2:
        health_check_interval = st.slider("Interval (seconds):", 5, 300, 30)
        health_check_timeout = st.slider("Timeout (seconds):", 2, 120, 5)
        healthy_threshold = st.slider("Healthy Threshold:", 2, 10, 2)
    
    with col3:
        unhealthy_threshold = st.slider("Unhealthy Threshold:", 2, 10, 2)
        success_codes = st.text_input("Success Codes:", "200,202")
        health_check_grace = st.slider("Grace Period (seconds):", 0, 7200, 300)
    
    if st.button("✅ Validate Health Check Configuration"):
        # Calculate health check timing
        time_to_healthy = healthy_threshold * health_check_interval
        time_to_unhealthy = unhealthy_threshold * health_check_interval
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 🔍 Health Check Analysis
        
        **Configuration Summary:**
        - **Protocol**: {health_check_protocol}
        - **Endpoint**: {health_check_protocol.lower()}://target:{health_check_port}{health_check_path}
        - **Check Frequency**: Every {health_check_interval} seconds
        - **Timeout**: {health_check_timeout} seconds per check
        
        **Timing Analysis:**
        - **Time to Healthy**: {time_to_healthy} seconds ({healthy_threshold} consecutive successes)
        - **Time to Unhealthy**: {time_to_unhealthy} seconds ({unhealthy_threshold} consecutive failures)
        - **Grace Period**: {health_check_grace} seconds (new instances)
        
        **Recommendations:**
        {f"• Consider reducing interval to {health_check_interval//2}s for faster detection" if health_check_interval > 30 else "• Health check frequency is appropriate"}
        {f"• Timeout of {health_check_timeout}s is {'appropriate' if health_check_timeout <= health_check_interval//2 else 'too high - should be < ' + str(health_check_interval//2) + 's'}"}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Advanced Features
    st.markdown("### 🚀 Advanced Load Balancer Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 Application Load Balancer Advanced Features
        
        **Content-Based Routing:**
        - Path-based routing (`/api/*`, `/images/*`)
        - Host-based routing (`api.example.com`)
        - HTTP header routing
        - Query parameter routing
        - Source IP routing
        
        **Authentication & Authorization:**
        - OIDC integration
        - SAML federation
        - AWS Cognito integration
        - Built-in authentication
        
        **Security Features:**
        - AWS WAF integration
        - Security headers insertion
        - Request/response modification
        - Rate limiting
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚡ Network Load Balancer Advanced Features
        
        **Performance Optimizations:**
        - Connection multiplexing
        - Cross-zone load balancing
        - Flow hash algorithm selection
        - Source IP preservation
        
        **Integration Features:**
        - AWS Global Accelerator
        - AWS PrivateLink endpoints
        - Elastic IP association
        - Multi-target group support
        
        **Monitoring & Logging:**
        - VPC Flow Logs
        - CloudWatch metrics
        - Access logging
        - Connection tracking
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Load Balancer Pricing Calculator
    st.markdown("### 💰 Load Balancer Cost Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        lb_type_calc = st.selectbox("Load Balancer Type:", ["Application", "Network", "Gateway", "Classic"])
        data_processed_gb = st.slider("Data Processed per Month (GB):", 1, 10000, 1000)
        new_connections = st.slider("New Connections per Second:", 1, 100000, 1000)
    
    with col2:
        active_connections = st.slider("Active Connections (concurrent):", 1, 1000000, 10000)
        rule_evaluations = st.slider("Rule Evaluations per Second:", 1, 100000, 5000)
    
    if st.button("💰 Calculate Monthly Cost"):
        # Simplified pricing calculations (actual prices vary by region)
        if lb_type_calc == "Application":
            fixed_cost = 22.50  # $0.0225/hour * 24 * 30
            lcu_cost = max(
                new_connections / 25,  # New connections dimension
                active_connections / 3000,  # Active connections dimension
                data_processed_gb / 1000,  # Bandwidth dimension
                rule_evaluations / 1000   # Rule evaluations dimension
            )
            variable_cost = lcu_cost * 0.008 * 24 * 30  # $0.008 per LCU-hour
            total_cost = fixed_cost + variable_cost
            
        elif lb_type_calc == "Network":
            fixed_cost = 22.50
            nlcu_cost = max(
                new_connections / 800,  # New flows dimension
                active_connections / 100000,  # Active flows dimension
                data_processed_gb / 1000   # Bandwidth dimension
            )
            variable_cost = nlcu_cost * 0.006 * 24 * 30  # $0.006 per NLCU-hour
            total_cost = fixed_cost + variable_cost
            
        elif lb_type_calc == "Classic":
            fixed_cost = 18.00  # $0.025/hour * 24 * 30
            data_cost = data_processed_gb * 0.008
            total_cost = fixed_cost + data_cost
            
        else:  # Gateway
            fixed_cost = 22.50
            glcu_cost = max(
                new_connections / 800,
                active_connections / 100000,
                data_processed_gb / 1000
            )
            variable_cost = glcu_cost * 0.006 * 24 * 30
            total_cost = fixed_cost + variable_cost
        
        # Create cost breakdown chart
        cost_breakdown = {
            'Cost Component': ['Fixed Cost', 'Variable Cost'],
            'Amount': [fixed_cost, variable_cost if lb_type_calc != "Classic" else data_cost]
        }
        
        fig = px.pie(values=cost_breakdown['Amount'], names=cost_breakdown['Cost Component'],
                     title=f'{lb_type_calc} Load Balancer - Monthly Cost Breakdown',
                     color_discrete_sequence=[AWS_COLORS['primary'], AWS_COLORS['light_blue']])
        
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Fixed Cost", f"${fixed_cost:.2f}/month")
        with col2:
            st.metric("Variable Cost", f"${variable_cost if lb_type_calc != 'Classic' else data_cost:.2f}/month")
        with col3:
            st.metric("Total Cost", f"${total_cost:.2f}/month")
    
    # Best Practices
    st.markdown("### 💡 Load Balancer Best Practices")
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Configuration Best Practices
    
    **High Availability:**
    - Deploy load balancers across multiple AZs
    - Use health checks appropriate for your application
    - Configure proper timeouts and thresholds
    - Monitor target health and performance metrics
    
    **Security:**
    - Use HTTPS listeners with proper SSL certificates
    - Implement AWS WAF for web application protection
    - Configure security groups to restrict access
    - Enable access logging for audit and troubleshooting
    
    **Performance:**
    - Choose the right load balancer type for your use case
    - Enable cross-zone load balancing when appropriate
    - Optimize health check intervals and thresholds
    - Monitor and tune based on CloudWatch metrics
    
    **Cost Optimization:**
    - Right-size your load balancer capacity
    - Use Application Load Balancer for HTTP/HTTPS workloads
    - Consider Regional optimization for multi-region deployments
    - Regularly review usage patterns and adjust configuration
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Load Balancer Setup and Management")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Comprehensive Load Balancer Management
import boto3
import json
from datetime import datetime, timedelta

class LoadBalancerManager:
    def __init__(self, region='us-east-1'):
        self.elbv2 = boto3.client('elbv2', region_name=region)
        self.ec2 = boto3.client('ec2', region_name=region)
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        self.region = region
    
    def create_application_load_balancer(self, lb_config):
        """Create Application Load Balancer with comprehensive configuration"""
        
        try:
            # Create the load balancer
            response = self.elbv2.create_load_balancer(
                Name=lb_config['name'],
                Subnets=lb_config['subnets'],
                SecurityGroups=lb_config['security_groups'],
                Scheme=lb_config.get('scheme', 'internet-facing'),
                Tags=[
                    {'Key': 'Name', 'Value': lb_config['name']},
                    {'Key': 'Environment', 'Value': lb_config.get('environment', 'production')},
                    {'Key': 'Application', 'Value': lb_config.get('application', 'web-app')}
                ],
                Type='application',
                IpAddressType=lb_config.get('ip_address_type', 'ipv4')
            )
            
            lb_arn = response['LoadBalancers'][0]['LoadBalancerArn']
            lb_dns = response['LoadBalancers'][0]['DNSName']
            
            print(f"✅ Created Application Load Balancer: {lb_config['name']}")
            print(f"   ARN: {lb_arn}")
            print(f"   DNS: {lb_dns}")
            
            return lb_arn, lb_dns
            
        except Exception as e:
            print(f"❌ Error creating load balancer: {e}")
            return None, None
    
    def create_target_group(self, tg_config):
        """Create target group with health check configuration"""
        
        try:
            response = self.elbv2.create_target_group(
                Name=tg_config['name'],
                Protocol=tg_config.get('protocol', 'HTTP'),
                Port=tg_config.get('port', 80),
                VpcId=tg_config['vpc_id'],
                TargetType=tg_config.get('target_type', 'instance'),
                HealthCheckProtocol=tg_config.get('health_check_protocol', 'HTTP'),
                HealthCheckPath=tg_config.get('health_check_path', '/health'),
                HealthCheckPort=tg_config.get('health_check_port', 'traffic-port'),
                HealthCheckIntervalSeconds=tg_config.get('health_check_interval', 30),
                HealthCheckTimeoutSeconds=tg_config.get('health_check_timeout', 5),
                HealthyThresholdCount=tg_config.get('healthy_threshold', 2),
                UnhealthyThresholdCount=tg_config.get('unhealthy_threshold', 2),
                Matcher={'HttpCode': tg_config.get('success_codes', '200')},
                Tags=[
                    {'Key': 'Name', 'Value': tg_config['name']},
                    {'Key': 'Protocol', 'Value': tg_config.get('protocol', 'HTTP')}
                ]
            )
            
            tg_arn = response['TargetGroups'][0]['TargetGroupArn']
            print(f"✅ Created target group: {tg_config['name']} ({tg_arn})")
            
            return tg_arn
            
        except Exception as e:
            print(f"❌ Error creating target group: {e}")
            return None
    
    def register_targets(self, target_group_arn, targets):
        """Register targets to target group"""
        
        try:
            # Format targets for registration
            target_list = []
            for target in targets:
                if isinstance(target, str):
                    # EC2 instance ID
                    target_list.append({'Id': target})
                elif isinstance(target, dict):
                    # Custom target with port
                    target_list.append(target)
            
            response = self.elbv2.register_targets(
                TargetGroupArn=target_group_arn,
                Targets=target_list
            )
            
            print(f"✅ Registered {len(target_list)} targets to target group")
            return True
            
        except Exception as e:
            print(f"❌ Error registering targets: {e}")
            return False
    
    def create_listener_with_rules(self, lb_arn, listener_config):
        """Create listener with routing rules"""
        
        try:
            # Create the listener
            response = self.elbv2.create_listener(
                LoadBalancerArn=lb_arn,
                Protocol=listener_config.get('protocol', 'HTTP'),
                Port=listener_config.get('port', 80),
                DefaultActions=listener_config['default_actions'],
                Certificates=listener_config.get('certificates', []),
                SslPolicy=listener_config.get('ssl_policy', 'ELBSecurityPolicy-TLS-1-2-2017-01')
            )
            
            listener_arn = response['Listener']['ListenerArn']
            print(f"✅ Created listener on port {listener_config.get('port', 80)}")
            
            # Create routing rules if specified
            if 'rules' in listener_config:
                for i, rule in enumerate(listener_config['rules'], 1):
                    try:
                        self.elbv2.create_rule(
                            ListenerArn=listener_arn,
                            Conditions=rule['conditions'],
                            Priority=rule.get('priority', i * 10),
                            Actions=rule['actions']
                        )
                        print(f"   ✅ Created routing rule {i}")
                    except Exception as e:
                        print(f"   ❌ Error creating rule {i}: {e}")
            
            return listener_arn
            
        except Exception as e:
            print(f"❌ Error creating listener: {e}")
            return None
    
    def configure_ssl_certificate(self, listener_arn, certificate_arn):
        """Configure SSL certificate for HTTPS listener"""
        
        try:
            response = self.elbv2.modify_listener(
                ListenerArn=listener_arn,
                Certificates=[{'CertificateArn': certificate_arn}]
            )
            
            print(f"✅ SSL certificate configured for listener")
            return True
            
        except Exception as e:
            print(f"❌ Error configuring SSL certificate: {e}")
            return False
    
    def monitor_load_balancer_health(self, lb_arn, hours=24):
        """Monitor load balancer performance and health"""
        
        # Get load balancer name from ARN
        lb_name = lb_arn.split('/')[-3] + '/' + lb_arn.split('/')[-2] + '/' + lb_arn.split('/')[-1]
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        metrics = {}
        
        # Load balancer metrics to monitor
        lb_metrics = [
            'RequestCount', 'TargetResponseTime', 'HTTPCode_Target_2XX_Count',
            'HTTPCode_Target_4XX_Count', 'HTTPCode_Target_5XX_Count',
            'HTTPCode_ELB_5XX_Count', 'NewConnectionCount', 'ActiveConnectionCount'
        ]
        
        for metric in lb_metrics:
            try:
                response = self.cloudwatch.get_metric_statistics(
                    Namespace='AWS/ApplicationELB',
                    MetricName=metric,
                    Dimensions=[
                        {'Name': 'LoadBalancer', 'Value': lb_name}
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=3600,  # 1 hour
                    Statistics=['Sum', 'Average']
                )
                
                if response['Datapoints']:
                    total_sum = sum([dp['Sum'] for dp in response['Datapoints']])
                    avg_value = sum([dp['Average'] for dp in response['Datapoints']]) / len(response['Datapoints'])
                    metrics[metric] = {'total': total_sum, 'average': avg_value}
                    
            except Exception as e:
                print(f"Warning: Could not retrieve {metric}: {e}")
        
        return metrics
    
    def check_target_health(self, target_group_arn):
        """Check health status of all targets in target group"""
        
        try:
            response = self.elbv2.describe_target_health(
                TargetGroupArn=target_group_arn
            )
            
            health_status = {}
            for target in response['TargetHealthDescriptions']:
                target_id = target['Target']['Id']
                health_state = target['TargetHealth']['State']
                health_description = target['TargetHealth'].get('Description', '')
                
                health_status[target_id] = {
                    'state': health_state,
                    'description': health_description
                }
            
            return health_status
            
        except Exception as e:
            print(f"❌ Error checking target health: {e}")
            return {}
    
    def setup_comprehensive_monitoring(self, lb_arn, target_group_arns):
        """Set up comprehensive monitoring with CloudWatch alarms"""
        
        lb_name = lb_arn.split('/')[-3] + '/' + lb_arn.split('/')[-2] + '/' + lb_arn.split('/')[-1]
        
        # Create CloudWatch alarms for key metrics
        alarms = [
            {
                'name': f'{lb_name.replace("/", "-")}-high-response-time',
                'metric': 'TargetResponseTime',
                'threshold': 2.0,  # 2 seconds
                'comparison': 'GreaterThanThreshold',
                'description': 'Average response time is too high'
            },
            {
                'name': f'{lb_name.replace("/", "-")}-high-5xx-errors',
                'metric': 'HTTPCode_Target_5XX_Count',
                'threshold': 10,
                'comparison': 'GreaterThanThreshold',
                'description': 'High number of 5xx errors'
            },
            {
                'name': f'{lb_name.replace("/", "-")}-elb-5xx-errors',
                'metric': 'HTTPCode_ELB_5XX_Count',
                'threshold': 5,
                'comparison': 'GreaterThanThreshold',
                'description': 'ELB is generating 5xx errors'
            }
        ]
        
        created_alarms = []
        
        for alarm in alarms:
            try:
                response = self.cloudwatch.put_metric_alarm(
                    AlarmName=alarm['name'],
                    ComparisonOperator=alarm['comparison'],
                    EvaluationPeriods=2,
                    MetricName=alarm['metric'],
                    Namespace='AWS/ApplicationELB',
                    Period=300,  # 5 minutes
                    Statistic='Average' if 'ResponseTime' in alarm['metric'] else 'Sum',
                    Threshold=alarm['threshold'],
                    ActionsEnabled=True,
                    AlarmDescription=alarm['description'],
                    Dimensions=[
                        {'Name': 'LoadBalancer', 'Value': lb_name}
                    ],
                    Unit='Seconds' if 'ResponseTime' in alarm['metric'] else 'Count'
                )
                
                created_alarms.append(alarm['name'])
                print(f"✅ Created CloudWatch alarm: {alarm['name']}")
                
            except Exception as e:
                print(f"❌ Error creating alarm {alarm['name']}: {e}")
        
        return created_alarms

# Example usage
def main():
    lb_manager = LoadBalancerManager()
    
    # Create Application Load Balancer
    lb_config = {
        'name': 'my-web-app-alb',
        'subnets': ['subnet-12345', 'subnet-67890'],
        'security_groups': ['sg-12345678'],
        'scheme': 'internet-facing',
        'environment': 'production',
        'application': 'web-app'
    }
    
    lb_arn, lb_dns = lb_manager.create_application_load_balancer(lb_config)
    
    if lb_arn:
        # Create target group
        tg_config = {
            'name': 'web-app-targets',
            'protocol': 'HTTP',
            'port': 80,
            'vpc_id': 'vpc-12345678',
            'health_check_path': '/health',
            'health_check_interval': 30,
            'healthy_threshold': 2,
            'unhealthy_threshold': 3
        }
        
        tg_arn = lb_manager.create_target_group(tg_config)
        
        if tg_arn:
            # Register EC2 instances as targets
            targets = ['i-1234567890abcdef0', 'i-0987654321fedcba0']
            lb_manager.register_targets(tg_arn, targets)
            
            # Create HTTP listener with routing rules
            listener_config = {
                'protocol': 'HTTP',
                'port': 80,
                'default_actions': [
                    {
                        'Type': 'forward',
                        'TargetGroupArn': tg_arn
                    }
                ],
                'rules': [
                    {
                        'conditions': [
                            {
                                'Field': 'path-pattern',
                                'Values': ['/api/*']
                            }
                        ],
                        'actions': [
                            {
                                'Type': 'forward',
                                'TargetGroupArn': tg_arn
                            }
                        ],
                        'priority': 10
                    }
                ]
            }
            
            listener_arn = lb_manager.create_listener_with_rules(lb_arn, listener_config)
            
            # Set up monitoring
            lb_manager.setup_comprehensive_monitoring(lb_arn, [tg_arn])
            
            # Check target health
            health_status = lb_manager.check_target_health(tg_arn)
            print("\n🏥 Target Health Status:")
            for target_id, health in health_status.items():
                print(f"   {target_id}: {health['state']} - {health['description']}")
            
            print(f"\n🎉 Load balancer setup complete!")
            print(f"URL: http://{lb_dns}")

if __name__ == "__main__":
    main()
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application function"""
    # Apply styling
    apply_custom_styles()
    
    # Initialize session
    common.initialize_session_state()
    
    # Create sidebar
    create_sidebar()
    
    # Main header
    st.markdown("""
    # ⚡ AWS Compute Services Hub
    
    """)
    st.markdown("""<div class="info-box">
                Learn to choose the right compute service, configure AMIs, optimize storage, implement auto scaling, and set up load balancing for high-performance, cost-effective applications.
                </div>""", unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "⚡ AWS Compute Offerings", 
        "🖼️ Amazon Machine Images (AMI)", 
        "💾 EC2 Instance Storage Options",
        "📈 Amazon EC2 Auto Scaling",
        "⚖️ Elastic Load Balancing"
    ])
    
    with tab1:
        aws_compute_offerings_tab()
    
    with tab2:
        amazon_machine_images_tab()
    
    with tab3:
        ec2_instance_storage_tab()
    
    with tab4:
        ec2_auto_scaling_tab()
        
    with tab5:
        elastic_load_balancing_tab()
    
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
