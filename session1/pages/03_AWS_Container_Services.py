
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import utils.common as common
import utils.authenticate as authenticate

# Page configuration
st.set_page_config(
    page_title="AWS Container Services Hub",
    page_icon="📦",
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
            - 📦 Amazon ECS - Fully managed container orchestration
            - ☸️ Amazon EKS - Kubernetes service for containerized apps
            - 🚀 AWS Fargate - Serverless compute engine for containers
            
            **Learning Objectives:**
            - Understand container orchestration concepts
            - Learn differences between ECS, EKS, and Fargate
            - Explore container deployment strategies
            - Practice with interactive examples and code samples
            """)

def create_container_comparison_mermaid():
    """Create mermaid diagram comparing container services"""
    return """
    graph TD
        A[Container Services] --> B[Amazon ECS]
        A --> C[Amazon EKS]
        A --> D[AWS Fargate]
        
        B --> B1[Docker Containers]
        B --> B2[Task Definitions]
        B --> B3[ECS Clusters]
        B --> B4[Service Discovery]
        
        C --> C1[Kubernetes Pods]
        C --> C2[Managed Control Plane]
        C --> C3[Worker Nodes]
        C --> C4[Kubernetes API]
        
        D --> D1[Serverless Compute]
        D --> D2[No Server Management]
        D --> D3[Pay per Task]
        D --> D4[Works with ECS & EKS]
        
        style A fill:#FF9900,stroke:#232F3E,color:#fff
        style B fill:#4B9EDB,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_ecs_architecture_mermaid():
    """Create mermaid diagram for ECS architecture"""
    return """
    graph TB
        subgraph "ECS Cluster"
            subgraph "EC2 Instances"
                EC21[EC2 Instance 1<br/>ECS Agent]
                EC22[EC2 Instance 2<br/>ECS Agent]
            end
            
            subgraph "ECS Tasks"
                T1[Task 1<br/>Web Server]
                T2[Task 2<br/>Database]
                T3[Task 3<br/>Cache]
            end
        end
        
        ELB[Application Load Balancer] --> T1
        T1 --> T2
        T1 --> T3
        
        TD[Task Definition] --> T1
        TD --> T2
        TD --> T3
        
        ECR[Elastic Container Registry] --> T1
        ECR --> T2
        ECR --> T3
        
        style ELB fill:#FF9900,stroke:#232F3E,color:#fff
        style TD fill:#4B9EDB,stroke:#232F3E,color:#fff
        style ECR fill:#3FB34F,stroke:#232F3E,color:#fff
        style T1 fill:#232F3E,stroke:#FF9900,color:#fff
        style T2 fill:#232F3E,stroke:#FF9900,color:#fff
        style T3 fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_eks_architecture_mermaid():
    """Create mermaid diagram for EKS architecture"""
    return """
    graph TB
        subgraph "Amazon EKS"
            subgraph "Control Plane (Managed)"
                API[Kubernetes API Server]
                ETCD[etcd Database]
                SCH[Scheduler]
                CM[Controller Manager]
            end
            
            subgraph "Worker Nodes"
                WN1[Worker Node 1<br/>kubelet, kube-proxy]
                WN2[Worker Node 2<br/>kubelet, kube-proxy]
                WN3[Worker Node 3<br/>kubelet, kube-proxy]
            end
            
            subgraph "Pods"
                P1[Pod 1<br/>Web App]
                P2[Pod 2<br/>API Service]
                P3[Pod 3<br/>Database]
            end
        end
        
        kubectl[kubectl CLI] --> API
        API --> WN1
        API --> WN2
        API --> WN3
        
        WN1 --> P1
        WN2 --> P2
        WN3 --> P3
        
        ECR[Container Registry] --> P1
        ECR --> P2
        ECR --> P3
        
        style API fill:#FF9900,stroke:#232F3E,color:#fff
        style kubectl fill:#4B9EDB,stroke:#232F3E,color:#fff
        style ECR fill:#3FB34F,stroke:#232F3E,color:#fff
    """

def create_fargate_architecture_mermaid():
    """Create mermaid diagram for Fargate architecture"""
    return """
    graph TD
        A[Your Application] --> B{Choose Launch Type}
        
        B --> C[AWS Fargate]
        B --> D[EC2 Launch Type]
        
        C --> E[No Server Management]
        C --> F[Serverless Containers]
        C --> G[Pay per Task]
        
        D --> H[Manage EC2 Instances]
        D --> I[Install ECS Agent]
        D --> J[Handle Scaling]
        
        E --> K[ECS Tasks on Fargate]
        F --> K
        G --> K
        
        K --> L[Container 1]
        K --> M[Container 2] 
        K --> N[Container 3]
        
        style A fill:#FF9900,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#4B9EDB,stroke:#232F3E,color:#fff
        style K fill:#232F3E,stroke:#FF9900,color:#fff
    """

def amazon_ecs_tab():
    """Content for Amazon ECS tab"""
    st.markdown("## 📦 Amazon Elastic Container Service (ECS)")
    st.markdown("*Fully managed container orchestration service that helps you easily deploy, manage, and scale containerized applications*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Amazon ECS** is a fully managed container orchestration service that makes it easy to deploy, manage, and scale 
    containerized applications. It eliminates the need to install, operate, and scale your own cluster management infrastructure.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ECS Architecture
    st.markdown("### 🏗️ ECS Architecture Overview")
    common.mermaid(create_ecs_architecture_mermaid(), height=650)
    
    # ECS Core Components
    st.markdown("### 🔧 ECS Core Components")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 Clusters
        - **Logical grouping** of compute resources
        - Can contain EC2 instances or Fargate
        - **Namespace** for services and tasks
        - Regional resources with AZ distribution
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📋 Task Definitions
        - **Blueprint** for your application
        - Specifies containers, CPU, memory
        - **Docker image** and port mappings
        - Environment variables and volumes
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚡ Services
        - **Desired state** management
        - Load balancer integration
        - **Auto scaling** and health checks
        - Rolling deployments
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive ECS Service Builder
    st.markdown("### 🛠️ Interactive ECS Service Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Application Configuration")
        app_name = st.text_input("Application Name:", "my-web-app")
        container_image = st.selectbox("Container Image:", [
            "nginx:latest", "httpd:latest", "node:18-alpine", "python:3.11-slim", "custom-app:v1.0"
        ])
        
        cpu_units = st.selectbox("CPU Units:", [256, 512, 1024, 2048, 4096])
        memory_mb = st.selectbox("Memory (MB):", [512, 1024, 2048, 4096, 8192])
        
        port = st.number_input("Container Port:", 1, 65535, 80)
    
    with col2:
        st.markdown("### ⚙️ Cluster Configuration")
        launch_type = st.selectbox("Launch Type:", ["AWS Fargate", "EC2"])
        
        if launch_type == "EC2":
            instance_type = st.selectbox("EC2 Instance Type:", [
                "t3.micro", "t3.small", "t3.medium", "t3.large", "m5.large", "c5.large"
            ])
        
        desired_count = st.slider("Desired Task Count:", 1, 10, 2)
        enable_logging = st.checkbox("Enable CloudWatch Logging", value=True)
        enable_load_balancer = st.checkbox("Enable Application Load Balancer", value=True)
    
    if st.button("🚀 Deploy ECS Service", use_container_width=True):
        # Calculate costs
        if launch_type == "AWS Fargate":
            vcpu_cost = (cpu_units / 1024) * 0.04048 * 24  # per day
            memory_cost = (memory_mb / 1024) * 0.004445 * 24  # per day
            total_cost_per_task = vcpu_cost + memory_cost
        else:
            # Simplified EC2 cost calculation
            instance_costs = {
                "t3.micro": 0.0104, "t3.small": 0.0208, "t3.medium": 0.0416,
                "t3.large": 0.0832, "m5.large": 0.096, "c5.large": 0.085
            }
            total_cost_per_task = instance_costs.get(instance_type, 0.05) * 24
        
        total_daily_cost = total_cost_per_task * desired_count
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ ECS Service Successfully Configured!
        
        **Service Details:**
        - **Service Name**: {app_name}
        - **Container Image**: {container_image}
        - **Launch Type**: {launch_type}
        - **Resources**: {cpu_units} CPU units, {memory_mb} MB memory
        - **Port**: {port}
        - **Task Count**: {desired_count}
        
        **Features Enabled:**
        - **CloudWatch Logs**: {'✅ Yes' if enable_logging else '❌ No'}
        - **Load Balancer**: {'✅ Yes' if enable_load_balancer else '❌ No'}
        
        💰 **Estimated Cost**: ${total_daily_cost:.2f}/day
        ⏱️ **Deployment Time**: 5-10 minutes
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ECS Launch Types Comparison
    st.markdown("### ⚖️ ECS Launch Types: EC2 vs Fargate")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🖥️ EC2 Launch Type
        
        **You Manage:**
        - EC2 instances and capacity
        - ECS agent installation
        - Instance scaling and patching
        - Instance-level monitoring
        
        **Best For:**
        - **Cost optimization** with Reserved Instances
        - Consistent workloads
        - Custom instance configurations
        - **High compute** requirements
        
        **Pricing:** EC2 instance rates
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🚀 Fargate Launch Type
        
        **AWS Manages:**
        - Server provisioning and management
        - Infrastructure scaling
        - Patching and updates
        - Resource allocation
        
        **Best For:**
        - **Serverless** containerized applications
        - Variable or unpredictable workloads
        - Microservices architectures
        - **Quick deployment** needs
        
        **Pricing:** Pay per task (vCPU + memory)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ECS Use Cases
    st.markdown("### 🌟 Common ECS Use Cases")
    
    use_cases_data = {
        'Use Case': ['Web Applications', 'Microservices', 'Batch Processing', 'CI/CD Pipelines', 'API Services'],
        'Architecture Pattern': ['Multi-tier app', 'Service mesh', 'Job queues', 'Build automation', 'RESTful APIs'],
        'Launch Type': ['Fargate/EC2', 'Fargate', 'EC2', 'Fargate', 'Fargate'],
        'Key Benefit': ['Auto scaling', 'Service isolation', 'Cost efficiency', 'Fast deployment', 'High availability']
    }
    
    df_use_cases = pd.DataFrame(use_cases_data)
    st.dataframe(df_use_cases, use_container_width=True)
    
    # Performance Metrics Visualization
    st.markdown("### 📊 ECS Performance Metrics")
    
    # Simulate performance data
    metrics_data = {
        'Metric': ['Task Start Time', 'CPU Utilization', 'Memory Utilization', 'Request Latency'],
        'EC2 Launch Type': [45, 65, 70, 120],
        'Fargate Launch Type': [30, 60, 68, 110]
    }
    
    df_metrics = pd.DataFrame(metrics_data)
    
    fig = px.bar(df_metrics, x='Metric', y=['EC2 Launch Type', 'Fargate Launch Type'],
                 title='Performance Comparison: EC2 vs Fargate Launch Types',
                 color_discrete_sequence=[AWS_COLORS['light_blue'], AWS_COLORS['primary']])
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: ECS Service Deployment")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Deploy containerized application using Amazon ECS
import boto3
import json

def create_ecs_service(cluster_name, service_name, task_definition_arn, 
                      subnet_ids, security_group_id, target_group_arn=None):
    """Create ECS service with Fargate launch type"""
    
    ecs = boto3.client('ecs')
    
    # Service configuration
    service_config = {
        'cluster': cluster_name,
        'serviceName': service_name,
        'taskDefinition': task_definition_arn,
        'desiredCount': 2,
        'launchType': 'FARGATE',
        'networkConfiguration': {
            'awsvpcConfiguration': {
                'subnets': subnet_ids,
                'securityGroups': [security_group_id],
                'assignPublicIp': 'ENABLED'
            }
        },
        'enableExecuteCommand': True,  # Enable ECS Exec for debugging
        'tags': [
            {'key': 'Environment', 'value': 'Production'},
            {'key': 'Application', 'value': service_name}
        ]
    }
    
    # Add load balancer if target group provided
    if target_group_arn:
        service_config['loadBalancers'] = [
            {
                'targetGroupArn': target_group_arn,
                'containerName': 'web-server',
                'containerPort': 80
            }
        ]
    
    try:
        response = ecs.create_service(**service_config)
        service_arn = response['service']['serviceArn']
        
        print(f"✅ ECS Service created successfully!")
        print(f"Service ARN: {service_arn}")
        print(f"Service Name: {service_name}")
        print(f"Cluster: {cluster_name}")
        
        return service_arn
        
    except Exception as e:
        print(f"❌ Error creating ECS service: {e}")
        return None

def create_task_definition(family_name, container_configs):
    """Create ECS task definition for containerized application"""
    
    ecs = boto3.client('ecs')
    
    # Default task role ARN (should be created beforehand)
    task_role_arn = 'arn:aws:iam::123456789012:role/ecsTaskRole'
    execution_role_arn = 'arn:aws:iam::123456789012:role/ecsTaskExecutionRole'
    
    task_definition = {
        'family': family_name,
        'networkMode': 'awsvpc',
        'requiresCompatibilities': ['FARGATE'],
        'cpu': '512',  # 0.5 vCPU
        'memory': '1024',  # 1 GB
        'taskRoleArn': task_role_arn,
        'executionRoleArn': execution_role_arn,
        'containerDefinitions': []
    }
    
    # Add container definitions
    for container in container_configs:
        container_def = {
            'name': container['name'],
            'image': container['image'],
            'portMappings': [
                {
                    'containerPort': container.get('port', 80),
                    'protocol': 'tcp'
                }
            ],
            'essential': True,
            'logConfiguration': {
                'logDriver': 'awslogs',
                'options': {
                    'awslogs-group': f'/ecs/{family_name}',
                    'awslogs-region': 'us-east-1',
                    'awslogs-stream-prefix': 'ecs'
                }
            }
        }
        
        # Add environment variables if provided
        if 'environment' in container:
            container_def['environment'] = [
                {'name': k, 'value': v} for k, v in container['environment'].items()
            ]
        
        # Add health check if provided
        if 'health_check' in container:
            container_def['healthCheck'] = {
                'command': container['health_check']['command'],
                'interval': container['health_check'].get('interval', 30),
                'timeout': container['health_check'].get('timeout', 5),
                'retries': container['health_check'].get('retries', 3),
                'startPeriod': container['health_check'].get('start_period', 60)
            }
        
        task_definition['containerDefinitions'].append(container_def)
    
    try:
        response = ecs.register_task_definition(**task_definition)
        task_def_arn = response['taskDefinition']['taskDefinitionArn']
        
        print(f"✅ Task definition registered successfully!")
        print(f"Task Definition ARN: {task_def_arn}")
        print(f"Family: {family_name}")
        print(f"Revision: {response['taskDefinition']['revision']}")
        
        return task_def_arn
        
    except Exception as e:
        print(f"❌ Error registering task definition: {e}")
        return None

def deploy_web_application():
    """Complete example: Deploy web application on ECS"""
    
    # Step 1: Create cluster
    ecs = boto3.client('ecs')
    
    cluster_response = ecs.create_cluster(
        clusterName='my-web-app-cluster',
        capacityProviders=['FARGATE'],
        defaultCapacityProviderStrategy=[
            {
                'capacityProvider': 'FARGATE',
                'weight': 1
            }
        ],
        tags=[
            {'key': 'Environment', 'value': 'Production'},
            {'key': 'Project', 'value': 'WebApp'}
        ]
    )
    
    cluster_arn = cluster_response['cluster']['clusterArn']
    print(f"📦 Cluster created: {cluster_arn}")
    
    # Step 2: Create task definition
    containers = [
        {
            'name': 'web-server',
            'image': 'nginx:latest',
            'port': 80,
            'environment': {
                'ENV': 'production',
                'LOG_LEVEL': 'info'
            },
            'health_check': {
                'command': ['CMD-SHELL', 'curl -f http://localhost/ || exit 1'],
                'interval': 30,
                'timeout': 5,
                'retries': 3,
                'start_period': 60
            }
        }
    ]
    
    task_def_arn = create_task_definition('web-app-task', containers)
    
    if not task_def_arn:
        return False
    
    # Step 3: Create service
    service_arn = create_ecs_service(
        cluster_name='my-web-app-cluster',
        service_name='web-app-service',
        task_definition_arn=task_def_arn,
        subnet_ids=['subnet-12345678', 'subnet-87654321'],
        security_group_id='sg-12345678'
    )
    
    if service_arn:
        print("🎉 Web application deployed successfully on ECS!")
        print(f"Access your application through the load balancer URL")
        return True
    
    return False

def monitor_ecs_service(cluster_name, service_name):
    """Monitor ECS service health and performance"""
    ecs = boto3.client('ecs')
    cloudwatch = boto3.client('cloudwatch')
    
    try:
        # Get service details
        services = ecs.describe_services(
            cluster=cluster_name,
            services=[service_name]
        )
        
        if not services['services']:
            print(f"❌ Service {service_name} not found")
            return
        
        service = services['services'][0]
        
        print(f"📊 Service Status: {service['status']}")
        print(f"🎯 Desired Count: {service['desiredCount']}")
        print(f"🏃 Running Count: {service['runningCount']}")
        print(f"⏸️ Pending Count: {service['pendingCount']}")
        
        # Get CloudWatch metrics
        from datetime import datetime, timedelta
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        
        cpu_metrics = cloudwatch.get_metric_statistics(
            Namespace='AWS/ECS',
            MetricName='CPUUtilization',
            Dimensions=[
                {'Name': 'ServiceName', 'Value': service_name},
                {'Name': 'ClusterName', 'Value': cluster_name}
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=300,
            Statistics=['Average']
        )
        
        if cpu_metrics['Datapoints']:
            avg_cpu = sum([dp['Average'] for dp in cpu_metrics['Datapoints']]) / len(cpu_metrics['Datapoints'])
            print(f"💻 Average CPU Utilization: {avg_cpu:.2f}%")
        
        return service
        
    except Exception as e:
        print(f"❌ Error monitoring service: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Deploy a complete web application
    deployment_success = deploy_web_application()
    
    if deployment_success:
        # Monitor the deployed service
        monitor_ecs_service('my-web-app-cluster', 'web-app-service')
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def amazon_eks_tab():
    """Content for Amazon EKS tab"""
    st.markdown("## ☸️ Amazon Elastic Kubernetes Service (EKS)")
    st.markdown("*Gives you the flexibility to start, run, and scale Kubernetes applications in the AWS Cloud or on-premises*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Amazon EKS** is a managed Kubernetes service that makes it easy to run Kubernetes on AWS without needing to 
    install, operate, and maintain your own Kubernetes control plane or nodes. It's fully compatible with standard Kubernetes.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # EKS Architecture
    st.markdown("### 🏗️ EKS Architecture Overview")
    common.mermaid(create_eks_architecture_mermaid(), height=650)
    
    # EKS Core Components
    st.markdown("### ⚙️ EKS Core Components")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎛️ Control Plane (AWS Managed)
        - **Kubernetes API Server** - Entry point for all REST commands
        - **etcd Database** - Consistent and distributed key-value store
        - **Scheduler** - Assigns pods to nodes
        - **Controller Manager** - Runs background tasks
        - **High Availability** across multiple AZs
        - **Automatic patching** and updates
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🖥️ Worker Nodes (You Manage)
        - **EC2 Instances** or **Fargate** (serverless)
        - **kubelet** - Node agent that communicates with control plane
        - **kube-proxy** - Network proxy for Kubernetes networking
        - **Container Runtime** - Docker or containerd
        - **Node Groups** for easier management
        - **Auto Scaling Groups** integration
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive EKS Cluster Builder
    st.markdown("### 🛠️ Interactive EKS Cluster Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Cluster Configuration")
        cluster_name = st.text_input("Cluster Name:", "my-k8s-cluster")
        k8s_version = st.selectbox("Kubernetes Version:", ["1.28", "1.27", "1.26", "1.25"])
        
        endpoint_access = st.selectbox("API Server Endpoint Access:", [
            "Public and Private", "Private Only", "Public Only"
        ])
        
        logging_types = st.multiselect("Enable Logging:", [
            "api", "audit", "authenticator", "controllerManager", "scheduler"
        ], default=["api", "audit"])
    
    with col2:
        st.markdown("### 👥 Node Group Configuration")
        node_group_name = st.text_input("Node Group Name:", "worker-nodes")
        instance_types = st.multiselect("Instance Types:", [
            "t3.medium", "t3.large", "m5.large", "m5.xlarge", "c5.large", "c5.xlarge"
        ], default=["t3.medium"])
        
        scaling_config = st.columns(3)
        with scaling_config[0]:
            min_size = st.number_input("Min Nodes:", 1, 20, 1)
        with scaling_config[1]:
            max_size = st.number_input("Max Nodes:", 1, 100, 10)
        with scaling_config[2]:
            desired_size = st.number_input("Desired Nodes:", 1, 50, 3)
    
    # Advanced Configuration
    st.markdown("### 🔧 Advanced Configuration")
    col3, col4 = st.columns(2)
    
    with col3:
        compute_type = st.selectbox("Compute Type:", ["EC2", "Fargate", "Mixed (EC2 + Fargate)"])
        network_policy = st.checkbox("Enable Calico Network Policy", value=False)
    
    with col4:
        secrets_encryption = st.checkbox("Enable Secrets Encryption", value=True)
        enable_oidc = st.checkbox("Enable OIDC Identity Provider", value=True)
    
    if st.button("🚀 Create EKS Cluster", use_container_width=True):
        # Calculate estimated costs
        control_plane_cost = 0.10 * 24 * 30  # $0.10/hour for control plane
        
        node_costs = {
            "t3.medium": 0.0416, "t3.large": 0.0832, "m5.large": 0.096,
            "m5.xlarge": 0.192, "c5.large": 0.085, "c5.xlarge": 0.17
        }
        
        avg_node_cost = sum([node_costs.get(t, 0.1) for t in instance_types]) / len(instance_types)
        monthly_node_cost = avg_node_cost * 24 * 30 * desired_size
        
        total_monthly_cost = control_plane_cost + monthly_node_cost
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ EKS Cluster Configuration Complete!
        
        **Cluster Details:**
        - **Cluster Name**: {cluster_name}
        - **Kubernetes Version**: {k8s_version}
        - **Endpoint Access**: {endpoint_access}
        - **Logging**: {', '.join(logging_types) if logging_types else 'Disabled'}
        
        **Node Group:**
        - **Name**: {node_group_name}
        - **Instance Types**: {', '.join(instance_types)}
        - **Scaling**: {min_size} - {max_size} nodes (desired: {desired_size})
        - **Compute Type**: {compute_type}
        
        **Security Features:**
        - **Secrets Encryption**: {'✅ Enabled' if secrets_encryption else '❌ Disabled'}
        - **OIDC Provider**: {'✅ Enabled' if enable_oidc else '❌ Disabled'}
        - **Network Policy**: {'✅ Enabled' if network_policy else '❌ Disabled'}
        
        💰 **Estimated Monthly Cost**: ${total_monthly_cost:.2f}
        ⏱️ **Cluster Creation Time**: 15-20 minutes
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Kubernetes vs EKS Benefits
    st.markdown("### 🆚 Self-Managed Kubernetes vs Amazon EKS")
    
    comparison_data = {
        'Aspect': ['Control Plane Management', 'High Availability', 'Security Updates', 'Monitoring', 'Integration', 'Cost'],
        'Self-Managed K8s': [
            'You manage masters', 
            'Manual HA setup',
            'Manual patching',
            'Setup monitoring stack',
            'Manual AWS integration',
            'Infrastructure + Management'
        ],
        'Amazon EKS': [
            'AWS manages for you',
            'Multi-AZ by default', 
            'Automatic patching',
            'CloudWatch integration',
            'Native AWS services',
            '$0.10/hour + worker nodes'
        ]
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True)
    
    # EKS Add-ons
    st.markdown("### 🔌 EKS Add-ons & Integrations")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🌐 Networking
        - **Amazon VPC CNI** - Native VPC networking
        - **AWS Load Balancer Controller** - ALB/NLB integration
        - **Calico** - Network policies
        - **CoreDNS** - Service discovery
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📊 Observability
        - **CloudWatch Container Insights** - Monitoring
        - **AWS X-Ray** - Distributed tracing
        - **Fluent Bit** - Log forwarding
        - **Prometheus** - Metrics collection
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🛡️ Security
        - **AWS IAM** - Access control
        - **Pod Identity** - Service accounts
        - **Secrets Store CSI** - External secrets
        - **Falco** - Runtime security
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # EKS vs ECS Decision Matrix
    st.markdown("### 🤔 When to Choose EKS vs ECS")
    
    decision_data = {
        'Criteria': ['Team Kubernetes Experience', 'Application Complexity', 'Multi-Cloud Strategy', 'Ecosystem Requirements', 'Learning Curve'],
        'Choose EKS If': [
            'High - experienced with K8s',
            'Complex microservices',
            'Need portability',
            'Rich K8s ecosystem needed',
            'Team willing to learn K8s'
        ],
        'Choose ECS If': [
            'Low - want simple container service',
            'Simple containerized apps',
            'AWS-only deployment',
            'Basic orchestration sufficient',
            'Want AWS-native simplicity'
        ]
    }
    
    df_decision = pd.DataFrame(decision_data)
    st.dataframe(df_decision, use_container_width=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: EKS Cluster and Application Deployment")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Deploy application on Amazon EKS using boto3 and kubectl
import boto3
import subprocess
import json
import time

def create_eks_cluster(cluster_name, role_arn, subnet_ids, security_group_ids):
    """Create EKS cluster with specified configuration"""
    
    eks = boto3.client('eks')
    
    cluster_config = {
        'name': cluster_name,
        'version': '1.28',
        'roleArn': role_arn,
        'resourcesVpcConfig': {
            'subnetIds': subnet_ids,
            'securityGroupIds': security_group_ids,
            'endpointConfigPublic': True,
            'endpointConfigPrivate': True,
            'publicAccessCidrs': ['0.0.0.0/0']
        },
        'logging': {
            'enable': [
                {
                    'types': ['api', 'audit', 'authenticator']
                }
            ]
        },
        'encryptionConfig': [
            {
                'resources': ['secrets'],
                'provider': {
                    'keyArn': 'arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012'
                }
            }
        ],
        'tags': {
            'Environment': 'Production',
            'Project': 'WebApp'
        }
    }
    
    try:
        response = eks.create_cluster(**cluster_config)
        cluster_arn = response['cluster']['arn']
        
        print(f"✅ EKS cluster creation initiated!")
        print(f"Cluster ARN: {cluster_arn}")
        print(f"Status: {response['cluster']['status']}")
        print("⏳ Waiting for cluster to become active (this may take 15-20 minutes)...")
        
        # Wait for cluster to become active
        waiter = eks.get_waiter('cluster_active')
        waiter.wait(name=cluster_name)
        
        print(f"🎉 Cluster {cluster_name} is now active!")
        return cluster_arn
        
    except Exception as e:
        print(f"❌ Error creating cluster: {e}")
        return None

def create_node_group(cluster_name, node_group_name, node_role_arn, subnet_ids):
    """Create managed node group for EKS cluster"""
    
    eks = boto3.client('eks')
    
    node_group_config = {
        'clusterName': cluster_name,
        'nodegroupName': node_group_name,
        'scalingConfig': {
            'minSize': 1,
            'maxSize': 10,
            'desiredSize': 3
        },
        'instanceTypes': ['t3.medium'],
        'amiType': 'AL2_x86_64',
        'nodeRole': node_role_arn,
        'subnets': subnet_ids,
        'remoteAccess': {
            'ec2SshKey': 'my-key-pair'
        },
        'tags': {
            'Environment': 'Production',
            'NodeGroup': node_group_name
        }
    }
    
    try:
        response = eks.create_nodegroup(**node_group_config)
        node_group_arn = response['nodegroup']['nodegroupArn']
        
        print(f"✅ Node group creation initiated!")
        print(f"Node Group ARN: {node_group_arn}")
        print("⏳ Waiting for node group to become active...")
        
        # Wait for node group to become active
        waiter = eks.get_waiter('nodegroup_active')
        waiter.wait(clusterName=cluster_name, nodegroupName=node_group_name)
        
        print(f"🎉 Node group {node_group_name} is now active!")
        return node_group_arn
        
    except Exception as e:
        print(f"❌ Error creating node group: {e}")
        return None

def configure_kubectl(cluster_name, region='us-east-1'):
    """Configure kubectl to connect to EKS cluster"""
    
    try:
        # Update kubeconfig
        cmd = f"aws eks update-kubeconfig --region {region} --name {cluster_name}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ kubectl configured for cluster {cluster_name}")
            
            # Test connection
            cmd = "kubectl get nodes"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("🔗 Successfully connected to cluster:")
                print(result.stdout)
                return True
            else:
                print(f"❌ Failed to connect to cluster: {result.stderr}")
                return False
        else:
            print(f"❌ Failed to configure kubectl: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error configuring kubectl: {e}")
        return False

def deploy_sample_application():
    """Deploy a sample web application to EKS cluster"""
    
    # Kubernetes manifests
    deployment_yaml = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.24
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: LoadBalancer
    """
    
    try:
        # Write manifest to file
        with open('/tmp/nginx-app.yaml', 'w') as f:
            f.write(deployment_yaml)
        
        # Apply manifest
        cmd = "kubectl apply -f /tmp/nginx-app.yaml"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Application deployed successfully!")
            print("🔍 Checking deployment status...")
            
            # Check deployment status
            cmd = "kubectl get deployments"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            print(result.stdout)
            
            # Get service information
            cmd = "kubectl get services"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            print("🌐 Services:")
            print(result.stdout)
            
            return True
        else:
            print(f"❌ Failed to deploy application: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error deploying application: {e}")
        return False

def install_aws_load_balancer_controller(cluster_name):
    """Install AWS Load Balancer Controller for advanced load balancing"""
    
    try:
        # Create service account
        cmd = f"""kubectl apply -f - <<EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  labels:
    app.kubernetes.io/component: controller
    app.kubernetes.io/name: aws-load-balancer-controller
  name: aws-load-balancer-controller
  namespace: kube-system
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/AmazonEKSLoadBalancerControllerRole
EOF"""
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Service account created for Load Balancer Controller")
        
        # Install controller using Helm
        helm_commands = [
            "helm repo add eks https://aws.github.io/eks-charts",
            "helm repo update",
            f"helm install aws-load-balancer-controller eks/aws-load-balancer-controller "
            f"-n kube-system --set clusterName={cluster_name} "
            f"--set serviceAccount.create=false "
            f"--set serviceAccount.name=aws-load-balancer-controller"
        ]
        
        for cmd in helm_commands:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"⚠️ Warning: {cmd} failed: {result.stderr}")
        
        print("🎉 AWS Load Balancer Controller installation completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error installing Load Balancer Controller: {e}")
        return False

def monitor_cluster_health(cluster_name):
    """Monitor EKS cluster health and performance"""
    
    try:
        # Check cluster status
        eks = boto3.client('eks')
        response = eks.describe_cluster(name=cluster_name)
        cluster = response['cluster']
        
        print(f"📊 CLUSTER HEALTH REPORT")
        print(f"Cluster Name: {cluster['name']}")
        print(f"Status: {cluster['status']}")
        print(f"Version: {cluster['version']}")
        print(f"Endpoint: {cluster['endpoint']}")
        print(f"Platform Version: {cluster['platformVersion']}")
        
        # Check node health
        cmd = "kubectl get nodes -o wide"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("\\n🖥️ NODE STATUS:")
            print(result.stdout)
        
        # Check pod health across all namespaces
        cmd = "kubectl get pods --all-namespaces"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("\\n🐳 POD STATUS:")
            print(result.stdout)
        
        # Get cluster resource usage
        cmd = "kubectl top nodes"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("\\n📈 RESOURCE USAGE:")
            print(result.stdout)
        
        return True
        
    except Exception as e:
        print(f"❌ Error monitoring cluster: {e}")
        return False

# Example usage - Complete EKS deployment workflow
def main():
    cluster_name = "my-production-cluster"
    
    # Step 1: Create EKS cluster
    cluster_arn = create_eks_cluster(
        cluster_name=cluster_name,
        role_arn="arn:aws:iam::123456789012:role/eksServiceRole",
        subnet_ids=["subnet-12345678", "subnet-87654321", "subnet-11111111"],
        security_group_ids=["sg-12345678"]
    )
    
    if not cluster_arn:
        return False
    
    # Step 2: Create node group
    node_group_arn = create_node_group(
        cluster_name=cluster_name,
        node_group_name="worker-nodes",
        node_role_arn="arn:aws:iam::123456789012:role/NodeInstanceRole",
        subnet_ids=["subnet-12345678", "subnet-87654321"]
    )
    
    if not node_group_arn:
        return False
    
    # Step 3: Configure kubectl
    if not configure_kubectl(cluster_name):
        return False
    
    # Step 4: Install AWS Load Balancer Controller
    install_aws_load_balancer_controller(cluster_name)
    
    # Step 5: Deploy sample application
    if deploy_sample_application():
        print("\\n🎉 EKS cluster setup and application deployment completed!")
        
        # Step 6: Monitor cluster
        monitor_cluster_health(cluster_name)
        
        return True
    
    return False

if __name__ == "__main__":
    success = main()
    if success:
        print("✅ EKS deployment workflow completed successfully!")
    else:
        print("❌ EKS deployment workflow failed!")
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def aws_fargate_tab():
    """Content for AWS Fargate tab"""
    st.markdown("## 🚀 AWS Fargate")
    st.markdown("*Serverless, pay-as-you-go compute engine that lets you focus on building applications without managing servers*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **AWS Fargate** is a serverless compute engine for containers that works with both Amazon ECS and Amazon EKS. 
    With Fargate, you no longer have to provision, configure, or scale clusters of virtual machines to run containers.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Fargate Architecture
    st.markdown("### 🏗️ Fargate vs EC2 Launch Types")
    common.mermaid(create_fargate_architecture_mermaid(), height=800)
    
    # Fargate Benefits
    st.markdown("### ✨ Key Benefits of AWS Fargate")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 Serverless
        - **No server management** required
        - AWS handles infrastructure provisioning
        - **Focus on applications**, not infrastructure
        - Automatic scaling up and down
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 💰 Cost Efficient
        - **Pay only for resources used**
        - No over-provisioning waste
        - **Per-second billing** granularity
        - No idle server costs
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🛡️ Secure & Isolated
        - **Task-level isolation** boundaries
        - VPC networking support
        - **IAM integration** for fine-grained permissions
        - Compliance-ready architecture
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Fargate Cost Calculator
    st.markdown("### 💰 Interactive Fargate Cost Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⚙️ Resource Configuration")
        
        # vCPU options: 0.25, 0.5, 1, 2, 4, 8, 16
        vcpu = st.selectbox("vCPU:", [0.25, 0.5, 1, 2, 4, 8, 16])
        
        # Memory options depend on vCPU
        memory_options = {
            0.25: [0.5, 1, 2],
            0.5: [1, 2, 3, 4],
            1: [2, 3, 4, 5, 6, 7, 8],
            2: [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
            4: [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
            8: [16, 17, 18, 19, 20, 25, 30, 35, 40, 45, 50, 55, 60],
            16: [32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120]
        }
        
        memory_gb = st.selectbox("Memory (GB):", memory_options[vcpu])
        
        tasks_count = st.slider("Number of Tasks:", 1, 50, 5)
        hours_per_day = st.slider("Hours per Day:", 1, 24, 12)
    
    with col2:
        st.markdown("### 📊 Usage Patterns")
        
        architecture = st.selectbox("Architecture:", ["Linux/x64", "Linux/ARM64", "Windows/x64"])
        
        usage_pattern = st.selectbox("Usage Pattern:", [
            "Consistent (24/7)", "Business Hours (8h/day)", "Peak Hours (4h/day)", "Batch Jobs (Variable)"
        ])
        
        region = st.selectbox("AWS Region:", [
            "us-east-1 (N. Virginia)", "us-west-2 (Oregon)", "eu-west-1 (Ireland)", "ap-southeast-1 (Singapore)"
        ])
    
    if st.button("💵 Calculate Fargate Costs", use_container_width=True):
        # Fargate pricing (simplified - actual prices vary by region)
        if "ARM64" in architecture:
            vcpu_price_per_hour = 0.03238  # ARM64 vCPU pricing
            memory_price_per_gb_hour = 0.00356  # ARM64 memory pricing
            performance_note = "20% better price performance vs x86"
        else:
            vcpu_price_per_hour = 0.04048  # x86 vCPU pricing
            memory_price_per_gb_hour = 0.004445  # x86 memory pricing
            performance_note = "Standard x86 performance"
        
        # Windows pricing is higher
        if "Windows" in architecture:
            vcpu_price_per_hour *= 2.0
            memory_price_per_gb_hour *= 2.0
            performance_note = "Windows containers (higher pricing)"
        
        # Calculate costs
        hourly_cost = (vcpu * vcpu_price_per_hour) + (memory_gb * memory_price_per_gb_hour)
        daily_cost = hourly_cost * hours_per_day * tasks_count
        monthly_cost = daily_cost * 30
        
        # Compare with EC2 equivalent
        ec2_hourly_costs = {
            0.25: 0.0104,  # t3.micro
            0.5: 0.0208,   # t3.small
            1: 0.0416,     # t3.medium
            2: 0.0832,     # t3.large
            4: 0.1664,     # t3.xlarge
            8: 0.3328,     # t3.2xlarge
            16: 0.6656     # t3.4xlarge (approximate)
        }
        
        equivalent_ec2_cost = ec2_hourly_costs.get(vcpu, 0.1) * 24 * 30  # Monthly
        savings_percentage = ((equivalent_ec2_cost - monthly_cost) / equivalent_ec2_cost) * 100
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 💰 Fargate Cost Analysis
        
        **Resource Configuration:**
        - **vCPU**: {vcpu} 
        - **Memory**: {memory_gb} GB
        - **Architecture**: {architecture}
        - **Tasks**: {tasks_count}
        - **Runtime**: {hours_per_day} hours/day
        
        **Cost Breakdown:**
        - **Hourly Cost per Task**: ${hourly_cost:.4f}
        - **Daily Cost**: ${daily_cost:.2f}
        - **Monthly Cost**: ${monthly_cost:.2f}
        
        **Comparison with EC2:**
        - **EC2 Monthly Cost**: ${equivalent_ec2_cost:.2f} (24/7 runtime)
        - **Fargate Savings**: {abs(savings_percentage):.1f}% {'💰 Cheaper' if savings_percentage > 0 else '📈 More Expensive'}
        
        **Performance**: {performance_note}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Fargate vs EC2 Comparison
    st.markdown("### ⚖️ AWS Fargate vs EC2 Launch Type Comparison")
    
    comparison_data = {
        'Aspect': ['Server Management', 'Scaling', 'Pricing Model', 'Cold Start Time', 'Resource Utilization', 'Best For'],
        'AWS Fargate': [
            'Serverless - AWS manages',
            'Automatic, instant',
            'Pay per task (vCPU + memory)',
            '1-2 minutes',
            'Right-sized per task',
            'Variable workloads, microservices'
        ],
        'EC2 Launch Type': [
            'You manage instances',
            'Manual or Auto Scaling Groups',
            'Pay for EC2 instances',
            '30-60 seconds (warm instances)',
            'May have unused capacity',
            'Consistent workloads, cost optimization'
        ]
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True)
    
    # Fargate Task Configuration
    st.markdown("### 🎛️ Fargate Task Size Options")
    
    # Create visualization for Fargate task sizes
    task_sizes = {
        'vCPU': [0.25, 0.5, 1, 2, 4, 8, 16],
        'Min Memory (GB)': [0.5, 1, 2, 4, 8, 16, 32],
        'Max Memory (GB)': [2, 4, 8, 16, 30, 60, 120],
        'Use Case': [
            'Light web services',
            'API endpoints', 
            'Web applications',
            'Backend services',
            'Batch processing',
            'Data processing',
            'ML workloads'
        ]
    }
    
    df_sizes = pd.DataFrame(task_sizes)
    
    fig = px.scatter(df_sizes, x='vCPU', y='Max Memory (GB)', 
                     size='Max Memory (GB)', 
                     hover_data=['Min Memory (GB)', 'Use Case'],
                     title='Fargate Task Configuration Options',
                     color='vCPU',
                     color_continuous_scale='Viridis')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Fargate Use Cases
    st.markdown("### 🌟 Ideal Fargate Use Cases")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ✅ Perfect for Fargate
        - **Microservices** architectures
        - **Event-driven** applications
        - **Batch jobs** and data processing  
        - **CI/CD workloads** and build tasks
        - **Variable traffic** web applications
        - **Development/testing** environments
        - **Seasonal workloads**
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚠️ Consider EC2 Instead
        - **High-performance computing** (HPC)
        - **GPU workloads** (use EC2 with GPU instances)
        - **Persistent storage** requirements
        - **Custom kernel modules** needed
        - **Extremely cost-sensitive** steady workloads
        - **Windows containers** with specific requirements
        - **Long-running daemons** (24/7)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Real-world Performance Metrics
    st.markdown("### 📊 Fargate Performance Characteristics")
    
    performance_data = {
        'Metric': ['Cold Start Time', 'Task Launch Speed', 'Network Performance', 'Storage Performance'],
        'Fargate': ['60-120 seconds', 'Fast (pre-warmed)', '10 Gbps network', 'EBS optimized'],
        'EC2 (warm)': ['5-30 seconds', 'Very fast', '10+ Gbps (instance dependent)', 'Instance store available']
    }
    
    df_performance = pd.DataFrame(performance_data)
    st.dataframe(df_performance, use_container_width=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Deploying Applications with Fargate")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Deploy containerized applications using AWS Fargate
import boto3
import json
from datetime import datetime

def create_fargate_task_definition(family_name, containers):
    """Create task definition optimized for Fargate"""
    
    ecs = boto3.client('ecs')
    
    # Task definition for Fargate
    task_definition = {
        'family': family_name,
        'networkMode': 'awsvpc',  # Required for Fargate
        'requiresCompatibilities': ['FARGATE'],
        'cpu': '1024',  # 1 vCPU (256, 512, 1024, 2048, 4096, 8192, 16384)
        'memory': '2048',  # 2 GB (512, 1024, 2048, etc.)
        'executionRoleArn': 'arn:aws:iam::123456789012:role/ecsTaskExecutionRole',
        'taskRoleArn': 'arn:aws:iam::123456789012:role/ecsTaskRole',
        'containerDefinitions': []
    }
    
    # Add container definitions
    for container in containers:
        container_def = {
            'name': container['name'],
            'image': container['image'],
            'essential': True,
            'portMappings': [
                {
                    'containerPort': container.get('port', 80),
                    'protocol': 'tcp'
                }
            ],
            'logConfiguration': {
                'logDriver': 'awslogs',
                'options': {
                    'awslogs-group': f'/ecs/{family_name}',
                    'awslogs-region': 'us-east-1',
                    'awslogs-stream-prefix': 'fargate',
                    'awslogs-create-group': 'true'
                }
            }
        }
        
        # Add environment variables
        if 'environment' in container:
            container_def['environment'] = [
                {'name': k, 'value': v} for k, v in container['environment'].items()
            ]
        
        # Add secrets from Systems Manager Parameter Store or Secrets Manager
        if 'secrets' in container:
            container_def['secrets'] = [
                {
                    'name': secret['name'],
                    'valueFrom': secret['valueFrom']
                } for secret in container['secrets']
            ]
        
        # Add health check for better reliability
        if 'healthCheck' in container:
            container_def['healthCheck'] = {
                'command': container['healthCheck']['command'],
                'interval': container['healthCheck'].get('interval', 30),
                'timeout': container['healthCheck'].get('timeout', 5),
                'retries': container['healthCheck'].get('retries', 3),
                'startPeriod': container['healthCheck'].get('startPeriod', 60)
            }
        
        task_definition['containerDefinitions'].append(container_def)
    
    try:
        response = ecs.register_task_definition(**task_definition)
        task_def_arn = response['taskDefinition']['taskDefinitionArn']
        
        print(f"✅ Fargate task definition registered!")
        print(f"Task Definition ARN: {task_def_arn}")
        print(f"CPU: {task_definition['cpu']} units")
        print(f"Memory: {task_definition['memory']} MB")
        
        return task_def_arn
        
    except Exception as e:
        print(f"❌ Error registering task definition: {e}")
        return None

def deploy_fargate_service(cluster_name, service_name, task_definition_arn, 
                          subnet_ids, security_group_ids, target_group_arn=None):
    """Deploy service using Fargate launch type"""
    
    ecs = boto3.client('ecs')
    
    service_config = {
        'cluster': cluster_name,
        'serviceName': service_name,
        'taskDefinition': task_definition_arn,
        'desiredCount': 2,
        'launchType': 'FARGATE',
        'networkConfiguration': {
            'awsvpcConfiguration': {
                'subnets': subnet_ids,
                'securityGroups': security_group_ids,
                'assignPublicIp': 'ENABLED'  # For internet access
            }
        },
        'deploymentConfiguration': {
            'maximumPercent': 200,
            'minimumHealthyPercent': 50,
            'deploymentCircuitBreaker': {
                'enable': True,
                'rollback': True
            }
        },
        'enableExecuteCommand': True,  # Enable ECS Exec for debugging
        'enableLogging': True,
        'tags': [
            {'key': 'LaunchType', 'value': 'Fargate'},
            {'key': 'Environment', 'value': 'Production'}
        ]
    }
    
    # Add load balancer configuration if provided
    if target_group_arn:
        service_config['loadBalancers'] = [
            {
                'targetGroupArn': target_group_arn,
                'containerName': 'web-app',  # Must match container name
                'containerPort': 80
            }
        ]
        service_config['healthCheckGracePeriodSeconds'] = 300
    
    try:
        response = ecs.create_service(**service_config)
        service_arn = response['service']['serviceArn']
        
        print(f"🚀 Fargate service deployed successfully!")
        print(f"Service ARN: {service_arn}")
        print(f"Launch Type: Fargate (Serverless)")
        print(f"Tasks: {service_config['desiredCount']}")
        
        return service_arn
        
    except Exception as e:
        print(f"❌ Error deploying Fargate service: {e}")
        return None

def run_fargate_task(cluster_name, task_definition_arn, subnet_ids, security_group_ids):
    """Run one-time task on Fargate (great for batch jobs)"""
    
    ecs = boto3.client('ecs')
    
    try:
        response = ecs.run_task(
            cluster=cluster_name,
            taskDefinition=task_definition_arn,
            launchType='FARGATE',
            networkConfiguration={
                'awsvpcConfiguration': {
                    'subnets': subnet_ids,
                    'securityGroups': security_group_ids,
                    'assignPublicIp': 'ENABLED'
                }
            },
            count=1,
            enableExecuteCommand=True,
            tags=[
                {'key': 'TaskType', 'value': 'Batch'},
                {'key': 'LaunchType', 'value': 'Fargate'}
            ]
        )
        
        task_arn = response['tasks'][0]['taskArn']
        task_id = task_arn.split('/')[-1]
        
        print(f"⚡ Fargate task started!")
        print(f"Task ARN: {task_arn}")
        print(f"Task ID: {task_id}")
        print("💡 Use 'aws ecs execute-command' to access the running container")
        
        return task_arn
        
    except Exception as e:
        print(f"❌ Error running Fargate task: {e}")
        return None

def scale_fargate_service(cluster_name, service_name, desired_count):
    """Scale Fargate service up or down"""
    
    ecs = boto3.client('ecs')
    
    try:
        response = ecs.update_service(
            cluster=cluster_name,
            service=service_name,
            desiredCount=desired_count
        )
        
        print(f"📈 Scaling Fargate service to {desired_count} tasks")
        print(f"Service: {service_name}")
        print(f"Previous count: {response['service']['runningCount']}")
        print(f"Target count: {desired_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error scaling service: {e}")
        return False

def monitor_fargate_costs(cluster_name, service_name, days=7):
    """Monitor Fargate costs and usage"""
    
    ce = boto3.client('ce')  # Cost Explorer
    cloudwatch = boto3.client('cloudwatch')
    
    from datetime import datetime, timedelta
    
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days)
    
    try:
        # Get cost data
        cost_response = ce.get_cost_and_usage(
            TimePeriod={
                'Start': start_date.strftime('%Y-%m-%d'),
                'End': end_date.strftime('%Y-%m-%d')
            },
            Granularity='DAILY',
            Metrics=['BlendedCost'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'SERVICE'}
            ],
            Filter={
                'Dimensions': {
                    'Key': 'SERVICE',
                    'Values': ['Amazon Elastic Container Service']
                }
            }
        )
        
        total_cost = 0
        for result in cost_response['ResultsByTime']:
            for group in result['Groups']:
                if 'Fargate' in group['Keys'][0]:
                    daily_cost = float(group['Metrics']['BlendedCost']['Amount'])
                    total_cost += daily_cost
        
        print(f"💰 FARGATE COST ANALYSIS ({days} days)")
        print(f"Total Cost: ${total_cost:.2f}")
        print(f"Average Daily Cost: ${total_cost/days:.2f}")
        print(f"Projected Monthly Cost: ${(total_cost/days)*30:.2f}")
        
        # Get CloudWatch metrics for resource utilization
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        cpu_metrics = cloudwatch.get_metric_statistics(
            Namespace='AWS/ECS',
            MetricName='CPUUtilization',
            Dimensions=[
                {'Name': 'ServiceName', 'Value': service_name},
                {'Name': 'ClusterName', 'Value': cluster_name}
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=3600,
            Statistics=['Average']
        )
        
        if cpu_metrics['Datapoints']:
            avg_cpu = sum([dp['Average'] for dp in cpu_metrics['Datapoints']]) / len(cpu_metrics['Datapoints'])
            print(f"📊 Average CPU Utilization: {avg_cpu:.2f}%")
            
            if avg_cpu < 20:
                print("💡 Recommendation: Consider smaller task size to reduce costs")
            elif avg_cpu > 80:
                print("⚠️ Recommendation: Consider larger task size or more tasks")
        
        return total_cost
        
    except Exception as e:
        print(f"❌ Error monitoring costs: {e}")
        return None

# Example: Deploy complete web application on Fargate
def deploy_web_app_on_fargate():
    """Complete example: Deploy web application using Fargate"""
    
    # Define containers for the application
    containers = [
        {
            'name': 'web-app',
            'image': 'nginx:latest',
            'port': 80,
            'environment': {
                'ENV': 'production',
                'REGION': 'us-east-1'
            },
            'healthCheck': {
                'command': ['CMD-SHELL', 'curl -f http://localhost/ || exit 1'],
                'interval': 30,
                'timeout': 5,
                'retries': 3,
                'startPeriod': 60
            }
        }
    ]
    
    # Step 1: Create task definition
    task_def_arn = create_fargate_task_definition('web-app-fargate', containers)
    
    if not task_def_arn:
        return False
    
    # Step 2: Deploy service
    service_arn = deploy_fargate_service(
        cluster_name='fargate-cluster',
        service_name='web-app-service',
        task_definition_arn=task_def_arn,
        subnet_ids=['subnet-12345678', 'subnet-87654321'],
        security_group_ids=['sg-12345678']
    )
    
    if not service_arn:
        return False
    
    print("🎉 Web application successfully deployed on Fargate!")
    print("💡 Benefits achieved:")
    print("  ✅ No server management required")
    print("  ✅ Automatic scaling capabilities") 
    print("  ✅ Pay only for actual usage")
    print("  ✅ High availability across AZs")
    
    return True

# Run example deployment
if __name__ == "__main__":
    success = deploy_web_app_on_fargate()
    if success:
        print("✅ Fargate deployment completed successfully!")
        
        # Monitor costs
        monitor_fargate_costs('fargate-cluster', 'web-app-service')
    ''', language='python')
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
    st.markdown("# 📦 AWS Container Services")
    st.markdown("""<div class="info-box">
                Master AWS container orchestration services including Amazon ECS, Amazon EKS, and AWS Fargate to deploy, manage, and scale containerized applications with different levels of control and abstraction.
                </div>""", unsafe_allow_html=True)
    
    # Service comparison overview
    st.markdown("### 🎯 Container Services Comparison")
    common.mermaid(create_container_comparison_mermaid(), height=300)
    
    # Service selection guide
    st.markdown("### 🤔 Which Container Service Should You Choose?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### Choose **Amazon ECS** when:
        - You want **simple container orchestration**
        - Prefer **AWS-native** solutions
        - Need **quick deployment** with minimal learning curve
        - Want **tight integration** with AWS services
        - Team has **limited Kubernetes experience**
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### Choose **Amazon EKS** when:
        - You need **Kubernetes compatibility**
        - Have **existing K8s workloads** to migrate
        - Want **multi-cloud portability**
        - Need **rich ecosystem** of Kubernetes tools
        - Team has **Kubernetes expertise**
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### Choose **AWS Fargate** when:
        - You want **serverless containers**
        - Don't want to **manage infrastructure**
        - Have **variable workloads**
        - Need **quick scaling** up and down
        - Want to **focus on applications** only
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        "📦 Amazon ECS", 
        "☸️ Amazon EKS", 
        "🚀 AWS Fargate"
    ])
    
    with tab1:
        amazon_ecs_tab()
    
    with tab2:
        amazon_eks_tab()
    
    with tab3:
        aws_fargate_tab()
    
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
