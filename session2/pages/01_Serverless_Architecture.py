
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
    page_title="AWS Development with Services Hub",
    page_icon="⚡",
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
        
        .architecture-box {{
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
            - 🏗️ Server-Based vs Serverless Architecture - Compare traditional and modern approaches
            - 🌐 Amazon API Gateway - REST/HTTP/WebSocket APIs at scale
            - ⚡ AWS Lambda - Serverless compute service
            - 🗃️ Amazon DynamoDB - NoSQL database for high-performance apps
            - 🔄 AWS Step Functions - Visual workflow orchestration
            
            **Learning Objectives:**
            - Understand different architectural patterns
            - Learn about serverless microservices
            - Explore AWS managed services
            - Practice with interactive examples and code
            """)

def create_serverless_architecture_mermaid():
    """Create mermaid diagram for serverless architecture"""
    return """
    graph LR
        A[👤 Customer] --> B[🌐 Amazon API Gateway]
        B --> C[⚡ AWS Lambda]
        C --> D[🗃️ Amazon DynamoDB]
        
        B --> E[⚡ Lambda Function 2]
        E --> F[📧 Amazon SNS]
        
        C --> G[📋 AWS Step Functions]
        G --> H[⚡ Lambda Function 3]
        H --> I[📦 Amazon S3]
        
        style A fill:#4B9EDB,stroke:#232F3E,color:#fff
        style B fill:#FF9900,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#232F3E,stroke:#FF9900,color:#fff
        style E fill:#3FB34F,stroke:#232F3E,color:#fff
        style F fill:#FF6B35,stroke:#232F3E,color:#fff
        style G fill:#4B9EDB,stroke:#232F3E,color:#fff
        style H fill:#3FB34F,stroke:#232F3E,color:#fff
        style I fill:#FF9900,stroke:#232F3E,color:#fff
    """

def create_server_based_architecture_mermaid():
    """Create mermaid diagram for server-based architecture"""
    return """
    graph TB
        A[👤 Users] --> B[🌐 Load Balancer]
        B --> C[💻 EC2 Instance 1]
        B --> D[💻 EC2 Instance 2]
        B --> E[💻 EC2 Instance 3]
        
        C --> F[🗄️ Amazon RDS<br/>MySQL Database]
        D --> F
        E --> F
        
        F --> G[🗄️ RDS Read Replica]
        
        subgraph VPC[🏠 Virtual Private Cloud]
            C
            D
            E
            F
            G
        end
        
        style A fill:#4B9EDB,stroke:#232F3E,color:#fff
        style B fill:#FF9900,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#3FB34F,stroke:#232F3E,color:#fff
        style E fill:#3FB34F,stroke:#232F3E,color:#fff
        style F fill:#232F3E,stroke:#FF9900,color:#fff
        style G fill:#FF6B35,stroke:#232F3E,color:#fff
    """

def create_api_gateway_flow_mermaid():
    """Create mermaid diagram for API Gateway flow"""
    return """
    graph LR
        A[📱 Client Request] --> B{🌐 API Gateway}
        B --> C[🔐 Authentication]
        C --> D[📊 Request Validation]
        D --> E[⚡ Lambda Integration]
        E --> F[📋 Response Transformation]
        F --> G[📊 Logging & Monitoring]
        G --> H[📱 Client Response]
        
        B --> I[🔄 Caching Layer]
        I --> E
        
        style A fill:#4B9EDB,stroke:#232F3E,color:#fff
        style B fill:#FF9900,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#FF6B35,stroke:#232F3E,color:#fff
        style E fill:#232F3E,stroke:#FF9900,color:#fff
        style F fill:#4B9EDB,stroke:#232F3E,color:#fff
        style G fill:#3FB34F,stroke:#232F3E,color:#fff
        style H fill:#4B9EDB,stroke:#232F3E,color:#fff
        style I fill:#FF9900,stroke:#232F3E,color:#fff
    """

def create_lambda_execution_models_mermaid():
    """Create mermaid diagram for Lambda execution models"""
    return """
    graph TB
        A[🎯 Lambda Invocation Models] --> B[🔄 Synchronous]
        A --> C[📡 Asynchronous]
        A --> D[🌊 Stream-based]
        
        B --> E[⚡ Immediate Execution]
        B --> F[🔙 Direct Response]
        B --> G[📱 API Gateway<br/>Application Load Balancer]
        
        C --> H[📋 Event Queue]
        C --> I[⏳ Background Processing]
        C --> J[📧 SNS, S3 Events<br/>CloudWatch Events]
        
        D --> K[📊 Polling Service]
        D --> L[🔄 Batch Processing]
        D --> M[🌊 Kinesis, DynamoDB Streams<br/>SQS Queues]
        
        style A fill:#FF9900,stroke:#232F3E,color:#fff
        style B fill:#3FB34F,stroke:#232F3E,color:#fff
        style C fill:#4B9EDB,stroke:#232F3E,color:#fff
        style D fill:#FF6B35,stroke:#232F3E,color:#fff
        style E fill:#232F3E,stroke:#FF9900,color:#fff
        style F fill:#232F3E,stroke:#FF9900,color:#fff
        style G fill:#232F3E,stroke:#FF9900,color:#fff
        style H fill:#232F3E,stroke:#FF9900,color:#fff
        style I fill:#232F3E,stroke:#FF9900,color:#fff
        style J fill:#232F3E,stroke:#FF9900,color:#fff
        style K fill:#232F3E,stroke:#FF9900,color:#fff
        style L fill:#232F3E,stroke:#FF9900,color:#fff
        style M fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_dynamodb_architecture_mermaid():
    """Create mermaid diagram for DynamoDB architecture"""
    return """
    graph TB
        A[🏗️ DynamoDB Table] --> B[🔑 Primary Key]
        A --> C[📊 Items & Attributes]
        A --> D[📍 Secondary Indexes]
        
        B --> E[🆔 Partition Key]
        B --> F[🔄 Sort Key<br/>Optional]
        
        D --> G[📍 Global Secondary Index<br/>GSI]
        D --> H[📍 Local Secondary Index<br/>LSI]
        
        A --> I[🌊 DynamoDB Streams]
        I --> J[⚡ Lambda Triggers]
        I --> K[📊 Change Data Capture]
        
        A --> L[⏰ Time to Live TTL]
        L --> M[🗑️ Automatic Item Deletion]
        
        A --> N[⚡ Capacity Modes]
        N --> O[📊 Provisioned<br/>Predictable Traffic]
        N --> P[🔄 On-Demand<br/>Variable Traffic]
        
        style A fill:#FF9900,stroke:#232F3E,color:#fff
        style B fill:#3FB34F,stroke:#232F3E,color:#fff
        style C fill:#4B9EDB,stroke:#232F3E,color:#fff
        style D fill:#FF6B35,stroke:#232F3E,color:#fff
        style E fill:#232F3E,stroke:#FF9900,color:#fff
        style F fill:#232F3E,stroke:#FF9900,color:#fff
        style G fill:#232F3E,stroke:#FF9900,color:#fff
        style H fill:#232F3E,stroke:#FF9900,color:#fff
        style I fill:#4B9EDB,stroke:#232F3E,color:#fff
        style J fill:#3FB34F,stroke:#232F3E,color:#fff
        style K fill:#FF6B35,stroke:#232F3E,color:#fff
        style L fill:#4B9EDB,stroke:#232F3E,color:#fff
        style M fill:#FF6B35,stroke:#232F3E,color:#fff
        style N fill:#3FB34F,stroke:#232F3E,color:#fff
        style O fill:#232F3E,stroke:#FF9900,color:#fff
        style P fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_step_functions_workflow_mermaid():
    """Create mermaid diagram for Step Functions workflow"""
    return """
    graph TD
        A[▶️ Start] --> B{📋 Credit Check}
        B -->|✅ Approved| C[💳 Process Payment]
        B -->|❌ Denied| D[📧 Send Rejection Email]
        
        C --> E{💰 Payment Success?}
        E -->|✅ Success| F[📦 Ship Product]
        E -->|❌ Failed| G[🔄 Retry Payment]
        
        G --> H{🔄 Retry Count < 3?}
        H -->|✅ Yes| C
        H -->|❌ No| I[📧 Payment Failed Email]
        
        F --> J[📧 Shipping Confirmation]
        J --> K[⏳ Wait 7 Days]
        K --> L[📊 Request Review]
        L --> M[🏁 End]
        
        D --> M
        I --> M
        
        style A fill:#3FB34F,stroke:#232F3E,color:#fff
        style B fill:#FF9900,stroke:#232F3E,color:#fff
        style C fill:#4B9EDB,stroke:#232F3E,color:#fff
        style D fill:#FF6B35,stroke:#232F3E,color:#fff
        style E fill:#FF9900,stroke:#232F3E,color:#fff
        style F fill:#3FB34F,stroke:#232F3E,color:#fff
        style G fill:#4B9EDB,stroke:#232F3E,color:#fff
        style H fill:#FF9900,stroke:#232F3E,color:#fff
        style I fill:#FF6B35,stroke:#232F3E,color:#fff
        style J fill:#3FB34F,stroke:#232F3E,color:#fff
        style K fill:#232F3E,stroke:#FF9900,color:#fff
        style L fill:#4B9EDB,stroke:#232F3E,color:#fff
        style M fill:#3FB34F,stroke:#232F3E,color:#fff
    """

def architecture_comparison_tab():
    """Content for Server-Based vs Serverless Architecture tab"""
    st.markdown("## 🏗️ Server-Based vs Serverless Architecture")
    st.markdown("*Compare traditional server-based architecture with modern serverless patterns*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Architecture Patterns** define how application components interact and scale. Server-based architectures 
    provide control and predictability, while serverless architectures offer automatic scaling and reduced operational overhead.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Architecture comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🖥️ Server-Based Architecture")
        common.mermaid(create_server_based_architecture_mermaid(), height=400)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        **Components:**
        - **Amazon EC2**: Virtual servers running your application
        - **Amazon RDS**: Managed relational database
        - **Load Balancer**: Distributes traffic across instances
        - **VPC**: Isolated network environment
        
        **Characteristics:**
        - ✅ Full control over server configuration
        - ✅ Predictable performance and costs
        - ✅ Suitable for legacy applications
        - ❌ Manual scaling and maintenance required
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### ⚡ Serverless Architecture")
        common.mermaid(create_serverless_architecture_mermaid(), height=200)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        **Components:**
        - **API Gateway**: Managed API endpoints
        - **AWS Lambda**: Event-driven compute functions
        - **DynamoDB**: NoSQL database with auto-scaling
        - **Step Functions**: Workflow orchestration
        
        **Characteristics:**
        - ✅ Automatic scaling and high availability
        - ✅ Pay only for what you use
        - ✅ No server management required
        - ❌ Vendor lock-in and cold start latency
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Architecture Builder
    st.markdown("### 🛠️ Interactive Architecture Builder")
    
    architecture_type = st.selectbox("Choose Architecture Pattern:", [
        "RESTful Microservices (Serverless)",
        "Traditional Web Application (Server-based)",
        "Hybrid Architecture (Best of Both)"
    ])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        expected_traffic = st.selectbox("Expected Traffic:", [
            "Low (< 1,000 requests/day)",
            "Medium (1,000 - 100,000 requests/day)", 
            "High (> 100,000 requests/day)"
        ])
    
    with col2:
        performance_priority = st.selectbox("Performance Priority:", [
            "Cost Optimization", "Consistent Performance", "Maximum Scalability"
        ])
    
    with col3:
        team_expertise = st.selectbox("Team Expertise:", [
            "Cloud Native", "Traditional IT", "Mixed Skills"
        ])
    
    if st.button("🚀 Generate Architecture Recommendation", use_container_width=True):
        # Simple recommendation logic
        if "Serverless" in architecture_type and "Low" in expected_traffic:
            recommendation = "Serverless"
            cost_estimate = "$5-50/month"
            scaling = "Automatic (0 to millions)"
            maintenance = "Minimal"
        elif "Server-based" in architecture_type or "High" in expected_traffic:
            recommendation = "Server-based"
            cost_estimate = "$100-1000/month"
            scaling = "Manual/Auto Scaling Groups"
            maintenance = "Regular updates required"
        else:
            recommendation = "Hybrid"
            cost_estimate = "$50-500/month"
            scaling = "Mixed approach"
            maintenance = "Moderate"
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 🎯 Architecture Recommendation: {recommendation}
        
        **Analysis Results:**
        - **Estimated Cost**: {cost_estimate}
        - **Scaling Strategy**: {scaling}
        - **Maintenance Effort**: {maintenance}
        - **Best For**: {architecture_type}
        
        **Key Benefits:**
        - Optimized for your traffic pattern: {expected_traffic}
        - Aligned with priority: {performance_priority}
        - Matches team skills: {team_expertise}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed comparison table
    st.markdown("### ⚖️ Detailed Architecture Comparison")
    
    comparison_data = {
        'Aspect': [
            'Infrastructure Management', 'Scaling', 'Cost Model', 'Performance', 
            'Development Speed', 'Vendor Lock-in', 'Monitoring', 'Security'
        ],
        'Server-Based': [
            'Manual setup & maintenance', 'Manual/ASG configuration', 'Fixed costs (instances running 24/7)', 
            'Consistent, predictable', 'Slower (infrastructure setup)', 'Low (standard APIs)', 
            'CloudWatch + custom tools', 'Full control, more complexity'
        ],
        'Serverless': [
            'Fully managed by AWS', 'Automatic, instant', 'Pay-per-use (execution time)', 
            'Variable (cold starts)', 'Faster (focus on business logic)', 'Higher (AWS-specific services)', 
            'Built-in monitoring', 'Shared responsibility model'
        ],
        'Best For': [
            'Complex enterprise apps', 'Predictable workloads', 'Steady traffic patterns',
            'Latency-sensitive apps', 'Legacy system migrations', 'Multi-cloud strategy',
            'Detailed system insights', 'Compliance-heavy industries'
        ]
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True)
    
    # Code Examples
    st.markdown("### 💻 Code Examples")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🖥️ Server-Based: EC2 + RDS Setup")
        st.markdown('<div class="code-container">', unsafe_allow_html=True)
        st.code('''
# Server-based architecture with EC2 and RDS
import boto3

def setup_server_based_architecture():
    ec2 = boto3.client('ec2')
    rds = boto3.client('rds')
    
    # Create VPC
    vpc = ec2.create_vpc(CidrBlock='10.0.0.0/16')
    vpc_id = vpc['Vpc']['VpcId']
    
    # Create subnets
    subnet1 = ec2.create_subnet(
        VpcId=vpc_id,
        CidrBlock='10.0.1.0/24',
        AvailabilityZone='us-west-2a'
    )
    
    subnet2 = ec2.create_subnet(
        VpcId=vpc_id,
        CidrBlock='10.0.2.0/24',
        AvailabilityZone='us-west-2b'
    )
    
    # Launch EC2 instances
    response = ec2.run_instances(
        ImageId='ami-0c02fb55956c7d316',  # Amazon Linux 2
        MinCount=2,
        MaxCount=2,
        InstanceType='t3.micro',
        SubnetId=subnet1['Subnet']['SubnetId'],
        UserData="""#!/bin/bash
        yum update -y
        yum install -y httpd php mysql
        systemctl start httpd
        systemctl enable httpd
        """
    )
    
    # Create RDS MySQL instance
    db_instance = rds.create_db_instance(
        DBInstanceIdentifier='webapp-db',
        DBInstanceClass='db.t3.micro',
        Engine='mysql',
        MasterUsername='admin',
        MasterUserPassword='SecurePassword123!',
        AllocatedStorage=20,
        VpcSecurityGroupIds=['sg-12345678'],
        DBSubnetGroupName='default-vpc-subnet-group'
    )
    
    return {
        'vpc_id': vpc_id,
        'instances': [i['InstanceId'] for i in response['Instances']],
        'db_instance': db_instance['DBInstance']['DBInstanceIdentifier']
    }

# Deploy server-based architecture
architecture = setup_server_based_architecture()
print(f"Deployed: {architecture}")
        ''', language='python')
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### ⚡ Serverless: Lambda + DynamoDB")
        st.markdown('<div class="code-container">', unsafe_allow_html=True)
        st.code('''
# Serverless architecture with Lambda and DynamoDB
import boto3
import json

def setup_serverless_architecture():
    lambda_client = boto3.client('lambda')
    dynamodb = boto3.client('dynamodb')
    apigateway = boto3.client('apigateway')
    
    # Create DynamoDB table
    table = dynamodb.create_table(
        TableName='UserProfiles',
        KeySchema=[
            {'AttributeName': 'userId', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'userId', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    
    # Create Lambda function
    lambda_code = """
import json
import boto3
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('UserProfiles')

def lambda_handler(event, context):
    http_method = event['httpMethod']
    
    if http_method == 'GET':
        # Get user profile
        user_id = event['pathParameters']['userId']
        response = table.get_item(Key={'userId': user_id})
        return {
            'statusCode': 200,
            'body': json.dumps(response.get('Item', {}))
        }
    
    elif http_method == 'POST':
        # Create user profile
        user_data = json.loads(event['body'])
        table.put_item(Item=user_data)
        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'User created'})
        }
    """
    
    # Deploy Lambda function
    function = lambda_client.create_function(
        FunctionName='UserProfileAPI',
        Runtime='python3.9',
        Role='arn:aws:iam::123456789012:role/LambdaRole',
        Handler='index.lambda_handler',
        Code={'ZipFile': lambda_code.encode()},
        Environment={
            'Variables': {'TABLE_NAME': 'UserProfiles'}
        }
    )
    
    return {
        'table_name': 'UserProfiles',
        'function_name': function['FunctionName'],
        'function_arn': function['FunctionArn']
    }

# Deploy serverless architecture 
serverless = setup_serverless_architecture()
print(f"Deployed: {serverless}")
        ''', language='python')
        st.markdown('</div>', unsafe_allow_html=True)

def api_gateway_tab():
    """Content for Amazon API Gateway tab"""
    st.markdown("## 🌐 Amazon API Gateway")
    st.markdown("*Create, publish, maintain, monitor, and secure REST, HTTP, and WebSocket APIs at any scale*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Amazon API Gateway** is a fully managed service that makes it easy for developers to create, publish, maintain, 
    monitor, and secure APIs at any scale. It acts as a "front door" for applications to access data, business logic, 
    or functionality from backend services.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # API Gateway Flow
    st.markdown("### 🔄 API Gateway Request Flow")
    common.mermaid(create_api_gateway_flow_mermaid(), height=200)
    
    # API Types comparison
    st.markdown("### 🔧 API Types Comparison")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🌐 REST APIs
        **Features:**
        - Complete API management features
        - Request/response transformation
        - Authentication & authorization
        - Caching and throttling
        
        **Best For:**
        - Full-featured API management
        - Enterprise applications
        - Complex integrations
        
        **Pricing:** Higher cost, more features
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚡ HTTP APIs
        **Features:**
        - Lower latency & cost
        - Built-in CORS support
        - JWT authorization
        - Basic request routing
        
        **Best For:**
        - Simple proxy integration
        - Cost-sensitive applications
        - Modern microservices
        
        **Pricing:** 70% cost reduction vs REST
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔄 WebSocket APIs
        **Features:**
        - Persistent connections
        - Bidirectional communication
        - Real-time data transfer
        - Connection management
        
        **Best For:**
        - Chat applications
        - Real-time dashboards
        - Gaming applications
        
        **Pricing:** Pay per connection/message
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive API Builder
    st.markdown("### 🛠️ Interactive API Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⚙️ API Configuration")
        api_type = st.selectbox("API Type:", ["REST API", "HTTP API", "WebSocket API"])
        api_name = st.text_input("API Name:", "my-serverless-api")
        
        endpoint_type = st.selectbox("Endpoint Type:", [
            "Edge-optimized (Global)", 
            "Regional (Same region clients)", 
            "Private (VPC only)"
        ])
        
        enable_cors = st.checkbox("Enable CORS", value=True)
        enable_caching = st.checkbox("Enable Caching", value=False)
    
    with col2:
        st.markdown("#### 🔒 Security & Authorization")
        auth_type = st.selectbox("Authorization:", [
            "None", "AWS IAM", "Cognito User Pools", "Lambda Authorizer", "API Keys"
        ])
        
        throttling = st.checkbox("Enable Throttling", value=True)
        if throttling:
            rate_limit = st.slider("Rate Limit (requests/second):", 10, 10000, 1000)
            burst_limit = st.slider("Burst Limit:", 20, 5000, 2000)
    
    # Resource and Method Configuration
    st.markdown("#### 🛣️ Routes and Methods")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        resource_path = st.text_input("Resource Path:", "/users/{userId}")
        http_method = st.selectbox("HTTP Method:", ["GET", "POST", "PUT", "DELETE", "PATCH"])
    
    with col2:
        integration_type = st.selectbox("Integration Type:", [
            "Lambda Function", "HTTP Endpoint", "AWS Service", "Mock Integration"
        ])
        
        if integration_type == "Lambda Function":
            lambda_function = st.text_input("Lambda Function:", "arn:aws:lambda:us-east-1:123456789012:function:userAPI")
    
    with col3:
        response_model = st.selectbox("Response Model:", [
            "Default", "Custom JSON Schema", "Proxy Integration"
        ])
        
        enable_validation = st.checkbox("Request Validation", value=True)
    
    if st.button("🚀 Generate API Configuration", use_container_width=True):
        # Generate API configuration
        config = {
            "api_name": api_name,
            "api_type": api_type,
            "endpoint_type": endpoint_type,
            "cors_enabled": enable_cors,
            "caching_enabled": enable_caching,
            "authorization": auth_type,
            "throttling": throttling
        }
        
        if throttling:
            config["rate_limit"] = rate_limit
            config["burst_limit"] = burst_limit
        
        estimated_cost = 3.50 if "REST" in api_type else 1.00  # Per million requests
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ API Configuration Generated!
        
        **API Details:**
        - **Name**: {api_name}
        - **Type**: {api_type}
        - **Endpoint**: {endpoint_type}
        - **Authorization**: {auth_type}
        - **Resource**: {resource_path}
        - **Method**: {http_method}
        
        **Features Enabled:**
        - CORS: {'✅' if enable_cors else '❌'}
        - Caching: {'✅' if enable_caching else '❌'}
        - Throttling: {'✅' if throttling else '❌'}
        - Request Validation: {'✅' if enable_validation else '❌'}
        
        **Estimated Cost**: ${estimated_cost}/million requests
        **Integration**: {integration_type}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Endpoint Types Explanation  
    st.markdown("### 📍 API Gateway Endpoint Types")
    
    endpoint_data = {
        'Endpoint Type': ['Edge-Optimized', 'Regional', 'Private'],
        'Best For': [
            'Global users, geographically distributed',
            'Clients in same region as API',
            'Internal applications, VPC access only'
        ],
        'Performance': [
            'Cached at CloudFront edge locations',
            'Lower latency for regional clients',
            'Lowest latency for VPC clients'
        ],
        'Use Cases': [
            'Public APIs, mobile apps, web frontends',
            'Regional microservices, B2B APIs',
            'Internal services, enterprise apps'
        ],
        'Cost Impact': ['Higher (CloudFront costs)', 'Standard', 'Lower (no CloudFront)']
    }
    
    df_endpoints = pd.DataFrame(endpoint_data)
    st.dataframe(df_endpoints, use_container_width=True)
    
    # Stage Management
    st.markdown("### 🏗️ Deployment Stages")
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Stage Variables & Environment Management
    
    **Stage Variables** allow you to configure different environments (dev, staging, prod) with:
    - Different **Lambda function versions**
    - Different **backend endpoints**
    - Different **configuration values**
    - Different **caching and throttling** settings
    
    **Example:** Use `${stageVariables.lambdaAlias}` to point to different Lambda aliases per stage.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Examples
    st.markdown("### 💻 Code Examples")
    
    tab1, tab2 = st.tabs(["🛠️ API Creation", "🔧 Lambda Integration"])
    
    with tab1:
        st.markdown('<div class="code-container">', unsafe_allow_html=True)
        st.code('''
# Create and deploy API Gateway with multiple resources
import boto3
import json

def create_rest_api():
    apigateway = boto3.client('apigateway')
    
    # Create REST API
    api = apigateway.create_rest_api(
        name='UserManagementAPI',
        description='RESTful API for user management',
        endpointConfiguration={
            'types': ['REGIONAL']
        },
        policy=json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "execute-api:Invoke",
                    "Resource": "*"
                }
            ]
        })
    )
    
    api_id = api['id']
    print(f"Created API: {api_id}")
    
    # Get root resource
    resources = apigateway.get_resources(restApiId=api_id)
    root_id = None
    for resource in resources['items']:
        if resource['path'] == '/':
            root_id = resource['id']
            break
    
    # Create /users resource
    users_resource = apigateway.create_resource(
        restApiId=api_id,
        parentId=root_id,
        pathPart='users'
    )
    
    users_resource_id = users_resource['id']
    
    # Create /users/{userId} resource  
    user_resource = apigateway.create_resource(
        restApiId=api_id,
        parentId=users_resource_id,
        pathPart='{userId}'
    )
    
    user_resource_id = user_resource['id']
    
    # Create GET method for /users/{userId}
    apigateway.put_method(
        restApiId=api_id,
        resourceId=user_resource_id,
        httpMethod='GET',
        authorizationType='NONE',
        requestParameters={
            'method.request.path.userId': True
        }
    )
    
    # Create Lambda integration
    lambda_arn = 'arn:aws:lambda:us-east-1:123456789012:function:getUserProfile'
    
    apigateway.put_integration(
        restApiId=api_id,
        resourceId=user_resource_id,
        httpMethod='GET',
        type='AWS_PROXY',
        integrationHttpMethod='POST',
        uri=f'arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/{lambda_arn}/invocations'
    )
    
    # Deploy API to stage
    deployment = apigateway.create_deployment(
        restApiId=api_id,
        stageName='prod',
        stageDescription='Production deployment',
        description='Initial deployment'
    )
    
    # Configure stage variables
    apigateway.update_stage(
        restApiId=api_id,
        stageName='prod',
        patchOps=[
            {
                'op': 'replace',
                'path': '/variables/lambdaAlias',
                'value': 'PROD'
            },
            {
                'op': 'replace', 
                'path': '/throttle/rateLimit',
                'value': '1000'
            },
            {
                'op': 'replace',
                'path': '/throttle/burstLimit', 
                'value': '2000'
            }
        ]
    )
    
    api_url = f"https://{api_id}.execute-api.us-east-1.amazonaws.com/prod"
    print(f"API deployed at: {api_url}")
    
    return {
        'api_id': api_id,
        'api_url': api_url,
        'stage': 'prod'
    }

# Create and deploy the API
api_details = create_rest_api()
        ''', language='python')
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="code-container">', unsafe_allow_html=True)
        st.code('''
# Lambda function optimized for API Gateway integration
import json
import boto3
from decimal import Decimal

def lambda_handler(event, context):
    """
    API Gateway Lambda Proxy Integration Handler
    """
    
    # Parse the incoming request
    http_method = event['httpMethod']
    resource_path = event['resource']
    path_parameters = event.get('pathParameters', {})
    query_parameters = event.get('queryStringParameters', {})
    headers = event.get('headers', {})
    body = event.get('body')
    
    # CORS headers for all responses
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }
    
    try:
        # Route based on HTTP method and resource
        if http_method == 'OPTIONS':
            # Handle CORS preflight
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': ''
            }
        
        elif http_method == 'GET' and resource_path == '/users/{userId}':
            # Get single user
            user_id = path_parameters['userId']
            user_data = get_user_from_db(user_id)
            
            if user_data:
                return {
                    'statusCode': 200,
                    'headers': {**cors_headers, 'Content-Type': 'application/json'},
                    'body': json.dumps(user_data, cls=DecimalEncoder)
                }
            else:
                return {
                    'statusCode': 404,
                    'headers': cors_headers,
                    'body': json.dumps({'error': 'User not found'})
                }
        
        elif http_method == 'POST' and resource_path == '/users':
            # Create new user
            if body:
                user_data = json.loads(body)
                result = create_user_in_db(user_data)
                
                return {
                    'statusCode': 201,
                    'headers': {**cors_headers, 'Content-Type': 'application/json'},
                    'body': json.dumps({
                        'message': 'User created successfully',
                        'userId': result['userId']
                    })
                }
            else:
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'error': 'Request body is required'})
                }
        
        elif http_method == 'PUT' and resource_path == '/users/{userId}':
            # Update existing user
            user_id = path_parameters['userId']
            if body:
                update_data = json.loads(body)
                result = update_user_in_db(user_id, update_data)
                
                return {
                    'statusCode': 200,
                    'headers': {**cors_headers, 'Content-Type': 'application/json'},
                    'body': json.dumps({
                        'message': 'User updated successfully',
                        'userId': user_id
                    })
                }
            else:
                return {
                    'statusCode': 400,
                    'headers': cors_headers,
                    'body': json.dumps({'error': 'Request body is required'})
                }
        
        else:
            # Method not allowed
            return {
                'statusCode': 405,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Method not allowed'})
            }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Internal server error'})
        }

def get_user_from_db(user_id):
    """Get user from DynamoDB"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Users')
    
    try:
        response = table.get_item(Key={'userId': user_id})
        return response.get('Item')
    except Exception as e:
        print(f"Database error: {e}")
        return None

def create_user_in_db(user_data):
    """Create user in DynamoDB"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Users')
    
    import uuid
    user_id = str(uuid.uuid4())
    user_data['userId'] = user_id
    
    table.put_item(Item=user_data)
    return {'userId': user_id}

def update_user_in_db(user_id, update_data):
    """Update user in DynamoDB"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Users')
    
    # Build update expression
    update_expression = "SET "
    expression_values = {}
    
    for key, value in update_data.items():
        if key != 'userId':  # Don't update the primary key
            update_expression += f"{key} = :{key}, "
            expression_values[f":{key}"] = value
    
    update_expression = update_expression.rstrip(', ')
    
    table.update_item(
        Key={'userId': user_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values
    )
    
    return {'userId': user_id}

class DecimalEncoder(json.JSONEncoder):
    """Helper class to handle Decimal types from DynamoDB"""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)
        ''', language='python')
        st.markdown('</div>', unsafe_allow_html=True)

def lambda_tab():
    """Content for AWS Lambda tab"""
    st.markdown("## ⚡ AWS Lambda")
    st.markdown("*Serverless compute service that lets you run code without provisioning or managing servers*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **AWS Lambda** is a serverless compute service that runs your code in response to events and automatically 
    manages the underlying compute resources. You pay only for the compute time you consume - no charge when 
    your code is not running.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Lambda execution models
    st.markdown("### 🔄 Lambda Execution Models")
    common.mermaid(create_lambda_execution_models_mermaid(), height=200)
    
    # Key Lambda concepts
    st.markdown("### 🧩 Key Lambda Concepts")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 Function
        - Your code packaged as a deployment package
        - **Handler**: Entry point for Lambda execution
        - **Runtime**: Language-specific environment
        - **Environment variables**: Configuration settings
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔄 Trigger
        - Resource that invokes your function
        - **Event sources**: S3, API Gateway, DynamoDB
        - **Scheduled events**: CloudWatch Events/EventBridge
        - **Manual invocation**: AWS CLI, SDK, Console
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📦 Event
        - JSON document with request data
        - **Structure varies** by event source
        - Contains metadata about the trigger
        - **Context object**: Runtime information
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📚 Layer
        - Shared libraries and dependencies
        - **Reusable across functions**
        - Reduces deployment package size
        - **Version management** for dependencies
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚡ Concurrency
        - Number of simultaneous executions
        - **Default limit**: 1,000 concurrent executions
        - **Reserved concurrency**: Guarantee capacity
        - **Provisioned concurrency**: Pre-warm functions
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 Destination
        - Where Lambda sends event records
        - **Success destinations**: SQS, SNS, Lambda, EventBridge
        - **Failure destinations**: DLQ for error handling
        - **Async invocations only**
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Lambda Function Builder
    st.markdown("### 🛠️ Interactive Lambda Function Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⚙️ Function Configuration")
        function_name = st.text_input("Function Name:", "my-serverless-function")
        runtime = st.selectbox("Runtime:", [
            "python3.9", "python3.8", "nodejs18.x", "nodejs16.x", 
            "java11", "dotnet6", "go1.x", "ruby2.7"
        ])
        
        memory_size = st.slider("Memory (MB):", 128, 10240, 512)
        timeout = st.slider("Timeout (seconds):", 1, 900, 30)
        
        # Calculate CPU allocation based on memory
        cpu_allocation = memory_size / 1769  # 1 vCPU at 1769 MB
        st.info(f"💻 **Allocated vCPU**: {cpu_allocation:.2f}")
    
    with col2:
        st.markdown("#### 🔌 Event Source")
        event_source = st.selectbox("Trigger Source:", [
            "API Gateway", "S3 Bucket", "DynamoDB Stream", "CloudWatch Events",
            "SQS Queue", "SNS Topic", "Kinesis Stream", "Manual Invocation"
        ])
        
        invocation_type = st.selectbox("Invocation Type:", [
            "Synchronous (Real-time response)",
            "Asynchronous (Background processing)", 
            "Stream-based (Batch processing)"
        ])
        
        enable_dlq = st.checkbox("Enable Dead Letter Queue", value=False)
        enable_monitoring = st.checkbox("Enhanced Monitoring", value=True)
    
    # Environment Variables
    st.markdown("#### 🌍 Environment Variables")
    col1, col2 = st.columns(2)
    
    with col1:
        env_vars = st.text_area("Environment Variables (JSON format):", 
                               '{\n  "TABLE_NAME": "MyDynamoTable",\n  "API_URL": "https://api.example.com",\n  "LOG_LEVEL": "INFO"\n}')
    
    with col2:
        # VPC Configuration
        enable_vpc = st.checkbox("Enable VPC Configuration", value=False)
        if enable_vpc:
            vpc_id = st.text_input("VPC ID:", "vpc-12345678")
            subnet_ids = st.text_input("Subnet IDs (comma-separated):", "subnet-12345678,subnet-87654321")
            security_groups = st.text_input("Security Group IDs:", "sg-12345678")
    
    if st.button("🚀 Generate Lambda Function", use_container_width=True):
        # Calculate estimated cost
        monthly_invocations = 1000000  # 1M invocations
        avg_duration = timeout / 2  # Assume average duration is half of timeout
        
        compute_cost = monthly_invocations * (avg_duration / 1000) * (memory_size / 1024) * 0.0000166667
        request_cost = monthly_invocations * 0.0000002
        total_cost = compute_cost + request_cost
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ Lambda Function Configuration Generated!
        
        **Function Details:**
        - **Name**: {function_name}
        - **Runtime**: {runtime}
        - **Memory**: {memory_size} MB ({cpu_allocation:.2f} vCPU)
        - **Timeout**: {timeout} seconds
        - **Trigger**: {event_source}
        - **Invocation**: {invocation_type}
        
        **Features:**
        - Dead Letter Queue: {'✅' if enable_dlq else '❌'}
        - Enhanced Monitoring: {'✅' if enable_monitoring else '❌'}
        - VPC Configuration: {'✅' if enable_vpc else '❌'}
        
        **Cost Estimate (1M invocations/month):**
        - Compute: ${compute_cost:.4f}
        - Requests: ${request_cost:.4f}
        - **Total**: ${total_cost:.4f}/month
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Memory vs Performance Analysis
    st.markdown("### 📊 Memory vs Performance Analysis")
    
    performance_data = {
        'Memory (MB)': [128, 256, 512, 1024, 1536, 3008],
        'vCPU Allocation': [0.07, 0.14, 0.29, 0.58, 0.87, 1.70],
        'Typical Duration (ms)': [5000, 2500, 1250, 625, 420, 300],
        'Cost per Invocation ($)': [0.0000208, 0.0000417, 0.0000834, 0.0001668, 0.0002501, 0.0005001],
        'Cost per Duration ($)': [0.0000042, 0.0000104, 0.0000104, 0.0000104, 0.0000105, 0.0000150]
    }
    
    df_performance = pd.DataFrame(performance_data)
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Duration vs Memory', 'Cost vs Memory'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    fig.add_trace(
        go.Scatter(x=df_performance['Memory (MB)'], y=df_performance['Typical Duration (ms)'], 
                  name='Duration', line=dict(color=AWS_COLORS['primary'], width=3)),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df_performance['Memory (MB)'], y=df_performance['Cost per Duration ($)'], 
                  name='Cost per Duration', line=dict(color=AWS_COLORS['light_blue'], width=3)),
        row=1, col=2
    )
    
    fig.update_layout(height=400, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)
    
    # Best Practices
    st.markdown("### 💡 Lambda Best Practices")
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Performance Optimization
    
    **Memory Configuration:**
    - Start with **512 MB** for most functions
    - **Monitor CloudWatch metrics** to optimize
    - More memory = more CPU = potentially lower cost per execution
    
    **Cold Start Mitigation:**
    - Use **Provisioned Concurrency** for latency-sensitive functions
    - **Keep functions warm** with scheduled events if needed
    - **Minimize deployment package** size and dependencies
    
    **Timeout Best Practices:**
    - Set timeout slightly higher than expected execution time
    - **API Gateway timeout is 29 seconds** - plan accordingly
    - Use **Step Functions** for long-running workflows
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Examples
    st.markdown("### 💻 Code Examples")
    
    tab1, tab2, tab3 = st.tabs(["🐍 Python Handler", "🔄 Event Processing", "⚡ Optimized Function"])
    
    with tab1:
        st.markdown('<div class="code-container">', unsafe_allow_html=True)
        st.code('''
# Basic Lambda function handler patterns
import json
import boto3
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """
    Basic Lambda handler with error handling and logging
    """
    # Log the incoming event (be careful with sensitive data)
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Extract information from the event
        event_source = context.invoked_function_arn.split(':')[3]  # Get service name
        
        # Different handling based on event source
        if 'Records' in event:
            # S3, SNS, SQS, DynamoDB events
            return process_records(event['Records'])
        
        elif 'httpMethod' in event:
            # API Gateway event
            return process_api_request(event, context)
        
        elif 'source' in event and event['source'] == 'aws.events':
            # CloudWatch Events / EventBridge
            return process_scheduled_event(event, context)
        
        else:
            # Direct invocation or custom event
            return process_custom_event(event, context)
    
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        
        # For API Gateway, return proper HTTP error response
        if 'httpMethod' in event:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Internal server error'})
            }
        
        # For other event sources, re-raise the exception
        raise

def process_records(records):
    """Process records from S3, SQS, SNS, DynamoDB"""
    results = []
    
    for record in records:
        event_source = record.get('eventSource', record.get('EventSource', ''))
        
        if 's3' in event_source.lower():
            # Process S3 event
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            logger.info(f"Processing S3 object: s3://{bucket}/{key}")
            
            # Your S3 processing logic here
            result = process_s3_object(bucket, key)
            results.append(result)
        
        elif 'sqs' in event_source.lower():
            # Process SQS message
            message_body = record['body']
            logger.info(f"Processing SQS message: {message_body}")
            
            # Your SQS processing logic here
            result = process_sqs_message(message_body)
            results.append(result)
        
        elif 'dynamodb' in event_source.lower():
            # Process DynamoDB stream record
            event_name = record['eventName']  # INSERT, MODIFY, REMOVE
            logger.info(f"Processing DynamoDB {event_name} event")
            
            # Your DynamoDB processing logic here
            result = process_dynamodb_record(record)
            results.append(result)
    
    return {
        'statusCode': 200,
        'processedRecords': len(results),
        'results': results
    }

def process_api_request(event, context):
    """Process API Gateway request"""
    http_method = event['httpMethod']
    resource_path = event['resource']
    
    # Add CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
        'Content-Type': 'application/json'
    }
    
    if http_method == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}
    
    # Route to appropriate handler
    if http_method == 'GET':
        return handle_get_request(event, headers)
    elif http_method == 'POST':
        return handle_post_request(event, headers)
    else:
        return {
            'statusCode': 405,
            'headers': headers,
            'body': json.dumps({'error': 'Method not allowed'})
        }

def handle_get_request(event, headers):
    """Handle GET requests"""
    # Extract path parameters and query string
    path_params = event.get('pathParameters', {}) or {}
    query_params = event.get('queryStringParameters', {}) or {}
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'message': 'GET request processed',
            'pathParameters': path_params,
            'queryParameters': query_params,
            'timestamp': datetime.utcnow().isoformat()
        })
    }

def handle_post_request(event, headers):
    """Handle POST requests"""
    try:
        # Parse request body
        body = json.loads(event['body']) if event.get('body') else {}
        
        # Your POST processing logic here
        result = {
            'message': 'POST request processed',
            'receivedData': body,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return {
            'statusCode': 201,
            'headers': headers,
            'body': json.dumps(result)
        }
    
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }

def process_s3_object(bucket, key):
    """Process S3 object"""
    s3 = boto3.client('s3')
    
    # Example: Get object metadata
    response = s3.head_object(Bucket=bucket, Key=key)
    return {
        'bucket': bucket,
        'key': key,
        'size': response['ContentLength'],
        'lastModified': response['LastModified'].isoformat()
    }

def process_sqs_message(message_body):
    """Process SQS message"""
    # Parse message if it's JSON
    try:
        message_data = json.loads(message_body)
        return {'status': 'processed', 'messageData': message_data}
    except json.JSONDecodeError:
        return {'status': 'processed', 'messageText': message_body}

def process_dynamodb_record(record):
    """Process DynamoDB stream record"""
    return {
        'eventName': record['eventName'],
        'dynamodb': record['dynamodb'],
        'processed': True
    }

def process_scheduled_event(event, context):
    """Process CloudWatch/EventBridge scheduled event"""
    return {
        'message': 'Scheduled event processed',
        'detail': event.get('detail', {}),
        'timestamp': datetime.utcnow().isoformat()
    }

def process_custom_event(event, context):
    """Process custom/direct invocation event"""
    return {
        'message': 'Custom event processed',
        'event': event,
        'context': {
            'functionName': context.function_name,
            'functionVersion': context.function_version,
            'remainingTimeMs': context.get_remaining_time_in_millis()
        }
    }
        ''', language='python')
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="code-container">', unsafe_allow_html=True)
        st.code('''
# Advanced event processing patterns
import json
import boto3
from typing import Dict, List, Any
import asyncio
import concurrent.futures

def lambda_handler(event, context):
    """
    Advanced event processing with batch operations and error handling
    """
    
    # Determine processing strategy based on event size
    if 'Records' in event:
        record_count = len(event['Records'])
        
        if record_count > 10:
            # Use parallel processing for large batches
            return process_batch_parallel(event['Records'], context)
        else:
            # Use sequential processing for small batches
            return process_batch_sequential(event['Records'], context)
    
    return process_single_event(event, context)

def process_batch_sequential(records: List[Dict], context) -> Dict:
    """Process records sequentially"""
    results = []
    errors = []
    
    for i, record in enumerate(records):
        try:
            result = process_single_record(record)
            results.append(result)
            
            # Check remaining execution time
            if context.get_remaining_time_in_millis() < 5000:  # 5 seconds buffer
                logger.warning("Approaching timeout, stopping processing")
                break
                
        except Exception as e:
            error_info = {
                'recordIndex': i,
                'error': str(e),
                'record': record
            }
            errors.append(error_info)
            logger.error(f"Error processing record {i}: {e}")
    
    return {
        'batchItemFailures': [{'itemIdentifier': err['recordIndex']} for err in errors],
        'successCount': len(results),
        'errorCount': len(errors),
        'results': results
    }

def process_batch_parallel(records: List[Dict], context) -> Dict:
    """Process records in parallel using ThreadPoolExecutor"""
    max_workers = min(10, len(records))  # Limit concurrent workers
    results = []
    errors = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_record = {
            executor.submit(process_single_record, record): i 
            for i, record in enumerate(records)
        }
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_record):
            record_index = future_to_record[future]
            
            try:
                result = future.result(timeout=30)  # 30 second timeout per task
                results.append(result)
                
            except Exception as e:
                error_info = {
                    'recordIndex': record_index,
                    'error': str(e),
                    'record': records[record_index]
                }
                errors.append(error_info)
                logger.error(f"Error processing record {record_index}: {e}")
            
            # Check remaining execution time
            if context.get_remaining_time_in_millis() < 10000:  # 10 seconds buffer
                logger.warning("Approaching timeout, cancelling remaining tasks")
                for f in future_to_record:
                    f.cancel()
                break
    
    return {
        'batchItemFailures': [{'itemIdentifier': err['recordIndex']} for err in errors],
        'successCount': len(results),
        'errorCount': len(errors),
        'results': results,
        'processingMode': 'parallel'
    }

def process_single_record(record: Dict) -> Dict:
    """Process a single record with retry logic"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Determine record type and process accordingly
            if 's3' in record.get('eventSource', '').lower():
                return process_s3_record(record)
            
            elif 'sqs' in record.get('eventSource', '').lower():
                return process_sqs_record(record)
            
            elif 'dynamodb' in record.get('eventSource', '').lower():
                return process_dynamodb_stream_record(record)
            
            else:
                return process_generic_record(record)
        
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise e
            
            # Exponential backoff
            import time
            time.sleep(2 ** retry_count)
            logger.warning(f"Retrying record processing, attempt {retry_count}")

def process_s3_record(record: Dict) -> Dict:
    """Process S3 event record"""
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    event_name = record['eventName']
    
    s3 = boto3.client('s3')
    
    if event_name.startswith('ObjectCreated'):
        # Handle object creation
        return handle_s3_object_created(s3, bucket, key)
    
    elif event_name.startswith('ObjectRemoved'):
        # Handle object deletion
        return handle_s3_object_removed(bucket, key)
    
    else:
        return {'status': 'ignored', 'eventName': event_name}

def handle_s3_object_created(s3, bucket: str, key: str) -> Dict:
    """Handle S3 object creation"""
    try:
        # Get object metadata
        response = s3.head_object(Bucket=bucket, Key=key)
        content_type = response.get('ContentType', '')
        size = response['ContentLength']
        
        # Process based on content type
        if content_type.startswith('image/'):
            return process_image_file(s3, bucket, key, size)
        
        elif content_type == 'application/json':
            return process_json_file(s3, bucket, key, size)
        
        elif content_type.startswith('text/'):
            return process_text_file(s3, bucket, key, size)
        
        else:
            return {
                'status': 'processed',
                'contentType': content_type,
                'size': size,
                'action': 'metadata_extracted'
            }
    
    except Exception as e:
        raise Exception(f"Failed to process S3 object {bucket}/{key}: {e}")

def process_image_file(s3, bucket: str, key: str, size: int) -> Dict:
    """Process image file"""
    # Example: Create thumbnail or extract metadata
    return {
        'status': 'processed',
        'fileType': 'image',
        'size': size,
        'action': 'thumbnail_created'
    }

def process_json_file(s3, bucket: str, key: str, size: int) -> Dict:
    """Process JSON file"""
    try:
        # Read and parse JSON file
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read().decode('utf-8')
        data = json.loads(content)
        
        # Process JSON data
        return {
            'status': 'processed',
            'fileType': 'json',
            'size': size,
            'recordCount': len(data) if isinstance(data, list) else 1,
            'action': 'json_parsed_and_processed'
        }
    
    except json.JSONDecodeError:
        raise Exception(f"Invalid JSON in file {bucket}/{key}")

def process_sqs_record(record: Dict) -> Dict:
    """Process SQS record"""
    message_id = record['messageId']
    body = record['body']
    
    try:
        # Try to parse as JSON
        message_data = json.loads(body)
        
        # Process based on message type
        message_type = message_data.get('type', 'unknown')
        
        if message_type == 'user_signup':
            return handle_user_signup(message_data)
        
        elif message_type == 'order_placed':
            return handle_order_placed(message_data)
        
        else:
            return handle_generic_message(message_data)
    
    except json.JSONDecodeError:
        # Handle as plain text message
        return {
            'status': 'processed',
            'messageId': message_id,
            'messageType': 'plain_text',
            'action': 'text_message_processed'
        }

def handle_user_signup(message_data: Dict) -> Dict:
    """Handle user signup message"""
    user_id = message_data.get('userId')
    email = message_data.get('email')
    
    # Send welcome email, create user profile, etc.
    return {
        'status': 'processed',
        'messageType': 'user_signup',
        'userId': user_id,
        'action': 'welcome_email_sent'
    }

def handle_order_placed(message_data: Dict) -> Dict:
    """Handle order placed message"""
    order_id = message_data.get('orderId')
    user_id = message_data.get('userId')
    
    # Process order, update inventory, send notifications
    return {
        'status': 'processed',
        'messageType': 'order_placed',
        'orderId': order_id,
        'action': 'order_processing_initiated'
    }
        ''', language='python')
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="code-container">', unsafe_allow_html=True)
        st.code('''
# Performance-optimized Lambda function
import json
import boto3
import os
from functools import lru_cache
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

# Initialize clients outside handler for connection reuse
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# Cache table references
@lru_cache(maxsize=32)
def get_table(table_name: str):
    """Get DynamoDB table with caching"""
    return dynamodb.Table(table_name)

# Global variables for caching
USER_TABLE = None
CONFIG_CACHE = {}

def lambda_handler(event, context):
    """
    Optimized Lambda handler with performance best practices
    """
    global USER_TABLE, CONFIG_CACHE
    
    # Initialize resources on cold start
    if USER_TABLE is None:
        USER_TABLE = get_table(os.environ['USER_TABLE_NAME'])
        load_configuration()
    
    try:
        # Process event efficiently
        if 'Records' in event:
            return process_batch_optimized(event['Records'])
        else:
            return process_single_event_optimized(event, context)
    
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return create_error_response(str(e))

def load_configuration():
    """Load configuration on cold start"""
    global CONFIG_CACHE
    
    try:
        # Load config from S3, Parameter Store, or environment
        config_bucket = os.environ.get('CONFIG_BUCKET')
        if config_bucket:
            response = s3.get_object(Bucket=config_bucket, Key='config.json')
            CONFIG_CACHE = json.loads(response['Body'].read().decode('utf-8'))
        else:
            # Use environment variables as fallback
            CONFIG_CACHE = {
                'api_timeout': int(os.environ.get('API_TIMEOUT', '30')),
                'batch_size': int(os.environ.get('BATCH_SIZE', '25')),
                'retry_attempts': int(os.environ.get('RETRY_ATTEMPTS', '3'))
            }
        
        logger.info("Configuration loaded successfully")
    
    except Exception as e:
        logger.warning(f"Failed to load configuration: {e}")
        CONFIG_CACHE = {}  # Use defaults

def process_batch_optimized(records):
    """Optimized batch processing"""
    batch_size = CONFIG_CACHE.get('batch_size', 25)
    
    # Process in optimal batch sizes
    all_results = []
    all_errors = []
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        
        try:
            batch_results = process_batch_with_db_optimization(batch)
            all_results.extend(batch_results.get('results', []))
            all_errors.extend(batch_results.get('errors', []))
        
        except Exception as e:
            logger.error(f"Batch processing error: {e}")
            all_errors.append({'batch_index': i, 'error': str(e)})
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'processed': len(all_results),
            'errors': len(all_errors),
            'batchItemFailures': [{'itemIdentifier': err.get('id')} for err in all_errors]
        })
    }

def process_batch_with_db_optimization(batch):
    """Process batch with database optimization"""
    results = []
    errors = []
    
    # Collect all keys for batch get operation
    keys_to_fetch = []
    write_requests = []
    
    for record in batch:
        try:
            # Extract key for batch operations
            if 'dynamodb' in record.get('eventSource', ''):
                # DynamoDB stream record
                if record['eventName'] in ['INSERT', 'MODIFY']:
                    # Prepare for batch write
                    item_data = parse_dynamodb_record(record)
                    write_requests.append({
                        'PutRequest': {'Item': item_data}
                    })
            else:
                # Regular record processing
                result = process_single_record_fast(record)
                results.append(result)
        
        except Exception as e:
            errors.append({'record': record, 'error': str(e)})
    
    # Execute batch operations if any
    if write_requests:
        try:
            execute_batch_write(write_requests)
        except Exception as e:
            logger.error(f"Batch write error: {e}")
            errors.append({'operation': 'batch_write', 'error': str(e)})
    
    return {'results': results, 'errors': errors}

def execute_batch_write(write_requests):
    """Execute batch write with retry logic"""
    dynamodb_client = boto3.client('dynamodb')
    table_name = os.environ['USER_TABLE_NAME']
    
    # Split into chunks of 25 (DynamoDB limit)
    chunk_size = 25
    for i in range(0, len(write_requests), chunk_size):
        chunk = write_requests[i:i + chunk_size]
        
        request_items = {table_name: chunk}
        
        # Retry logic for unprocessed items
        max_retries = 3
        retry_count = 0
        
        while request_items and retry_count < max_retries:
            try:
                response = dynamodb_client.batch_write_item(
                    RequestItems=request_items
                )
                
                # Handle unprocessed items
                request_items = response.get('UnprocessedItems', {})
                
                if request_items:
                    retry_count += 1
                    # Exponential backoff
                    import time
                    time.sleep(2 ** retry_count)
                
            except Exception as e:
                retry_count += 1
                if retry_count >= max_retries:
                    raise e
                
                import time
                time.sleep(2 ** retry_count)

def process_single_record_fast(record):
    """Fast single record processing"""
    event_source = record.get('eventSource', '')
    
    if 's3' in event_source:
        return process_s3_optimized(record)
    elif 'sqs' in event_source:
        return process_sqs_optimized(record)
    else:
        return {'status': 'processed', 'type': 'unknown'}

def process_s3_optimized(record):
    """Optimized S3 processing"""
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    
    # Use head_object instead of get_object for metadata only
    try:
        response = s3.head_object(Bucket=bucket, Key=key)
        
        return {
            'status': 'processed',
            'bucket': bucket,
            'key': key,
            'size': response['ContentLength'],
            'contentType': response.get('ContentType', 'unknown')
        }
    
    except Exception as e:
        raise Exception(f"S3 processing failed: {e}")

def process_sqs_optimized(record):
    """Optimized SQS processing"""
    message_id = record['messageId']
    receipt_handle = record['receiptHandle']
    
    try:
        body = json.loads(record['body'])
        
        # Fast processing based on message type
        message_type = body.get('type', 'default')
        
        if message_type in CONFIG_CACHE.get('high_priority_types', []):
            return process_high_priority_message(body)
        else:
            return process_standard_message(body)
    
    except json.JSONDecodeError:
        return {'status': 'processed', 'type': 'text', 'message_id': message_id}

def process_high_priority_message(message_data):
    """Process high priority messages"""
    # Implement high-priority logic
    return {
        'status': 'processed',
        'priority': 'high',
        'type': message_data.get('type'),
        'processing_time': 'fast'
    }

def process_standard_message(message_data):
    """Process standard messages"""
    return {
        'status': 'processed',
        'priority': 'standard',
        'type': message_data.get('type')
    }

def parse_dynamodb_record(record):
    """Parse DynamoDB stream record efficiently"""
    if record['eventName'] == 'INSERT':
        return record['dynamodb']['NewImage']
    elif record['eventName'] == 'MODIFY':
        return record['dynamodb']['NewImage']
    elif record['eventName'] == 'REMOVE':
        return record['dynamodb']['OldImage']
    else:
        return {}

def create_error_response(error_message):
    """Create standardized error response"""
    return {
        'statusCode': 500,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'error': 'Internal server error',
            'message': error_message,
            'timestamp': datetime.utcnow().isoformat()
        })
    }

# Performance monitoring decorator
def monitor_performance(func):
    """Decorator to monitor function performance"""
    import time
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        logger.info(f"{func.__name__} executed in {execution_time:.2f}ms")
        
        return result
    
    return wrapper

# Use the decorator on critical functions
@monitor_performance
def critical_business_logic(data):
    """Critical business logic with performance monitoring"""
    # Your critical code here
    pass
        ''', language='python')
        st.markdown('</div>', unsafe_allow_html=True)

def dynamodb_tab():
    """Content for Amazon DynamoDB tab"""
    st.markdown("## 🗃️ Amazon DynamoDB")
    st.markdown("*Fully managed, serverless, key-value NoSQL database designed to run high-performance applications at any scale*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Amazon DynamoDB** is a fully managed NoSQL database service that provides fast and predictable performance 
    with seamless scalability. It's designed for applications that need consistent, single-digit millisecond latency 
    at any scale.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # DynamoDB Architecture
    st.markdown("### 🏗️ DynamoDB Architecture & Components")
    common.mermaid(create_dynamodb_architecture_mermaid(), height=200)
    
    # Core Components
    st.markdown("### 🧩 Core Components Deep Dive")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔑 Primary Key
        **Partition Key (Required):**
        - Determines which partition stores the item
        - Must be unique if no sort key
        - Examples: userId, productId, email
        
        **Sort Key (Optional):**
        - Sorts items within the same partition
        - Enables range queries
        - Examples: timestamp, version, category
        
        **Composite Key:** Partition Key + Sort Key
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📊 Items & Attributes
        **Item:** Collection of attributes (max 400KB)
        
        **Attribute Types:**
        - **Scalar:** String, Number, Binary, Boolean, Null
        - **Document:** List, Map
        - **Set:** String Set, Number Set, Binary Set
        
        **Schemaless:** No predefined schema required
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📍 Secondary Indexes
        **Global Secondary Index (GSI):**
        - Different partition key and sort key
        - Queries across all partitions
        - Own provisioned throughput
        - Eventually consistent reads
        
        **Local Secondary Index (LSI):**
        - Same partition key, different sort key
        - Query within same partition
        - Shares table's throughput
        - Strongly consistent reads available
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🌊 DynamoDB Streams
        **Capture data modification events:**
        - KEYS_ONLY: Only key attributes
        - NEW_IMAGE: Entire item after modification
        - OLD_IMAGE: Entire item before modification
        - NEW_AND_OLD_IMAGES: Both new and old
        
        **Use Cases:** Real-time analytics, replication, triggers
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Table Builder
    st.markdown("### 🛠️ Interactive DynamoDB Table Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏗️ Table Configuration")
        table_name = st.text_input("Table Name:", "UserProfiles")
        
        # Primary Key Configuration
        st.markdown("**Primary Key:**")
        partition_key = st.text_input("Partition Key Name:", "userId")
        partition_key_type = st.selectbox("Partition Key Type:", ["String", "Number", "Binary"])
        
        use_sort_key = st.checkbox("Enable Sort Key", value=False)
        if use_sort_key:
            sort_key = st.text_input("Sort Key Name:", "timestamp")
            sort_key_type = st.selectbox("Sort Key Type:", ["String", "Number", "Binary"])
    
    with col2:
        st.markdown("#### ⚡ Capacity Configuration")
        capacity_mode = st.selectbox("Capacity Mode:", [
            "On-Demand (Pay per request)",
            "Provisioned (Predictable workload)"
        ])
        
        if "Provisioned" in capacity_mode:
            read_capacity = st.slider("Read Capacity Units (RCU):", 1, 1000, 5)
            write_capacity = st.slider("Write Capacity Units (WCU):", 1, 1000, 5)
            
            st.info(f"""
            **Capacity Calculations:**
            - 1 RCU = 4KB strongly consistent read/sec
            - 1 WCU = 1KB write/sec
            - **Estimated Cost**: ${(read_capacity * 0.00013 + write_capacity * 0.00065) * 24 * 30:.2f}/month
            """)
    
    # Additional Features
    st.markdown("#### 🔧 Additional Features")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        enable_streams = st.checkbox("Enable DynamoDB Streams", value=False)
        if enable_streams:
            stream_view_type = st.selectbox("Stream View Type:", [
                "KEYS_ONLY", "NEW_IMAGE", "OLD_IMAGE", "NEW_AND_OLD_IMAGES"
            ])
    
    with col2:
        enable_ttl = st.checkbox("Enable Time to Live (TTL)", value=False)
        if enable_ttl:
            ttl_attribute = st.text_input("TTL Attribute Name:", "expiresAt")
    
    with col3:
        enable_encryption = st.checkbox("Enable Encryption at Rest", value=True)
        if enable_encryption:
            encryption_type = st.selectbox("Encryption Type:", [
                "AWS Managed Key", "Customer Managed Key"
            ])
    
    # Global Secondary Index Configuration
    st.markdown("#### 📍 Global Secondary Index (Optional)")
    enable_gsi = st.checkbox("Add Global Secondary Index", value=False)
    
    if enable_gsi:
        col1, col2 = st.columns(2)
        with col1:
            gsi_name = st.text_input("GSI Name:", "email-index")
            gsi_partition_key = st.text_input("GSI Partition Key:", "email")
        
        with col2:
            gsi_sort_key = st.text_input("GSI Sort Key (Optional):", "createdAt")
            if "Provisioned" in capacity_mode:
                gsi_read_capacity = st.slider("GSI Read Capacity:", 1, 1000, 5)
                gsi_write_capacity = st.slider("GSI Write Capacity:", 1, 1000, 5)
    
    if st.button("🚀 Generate DynamoDB Table Configuration", use_container_width=True):
        # Generate table configuration
        table_config = {
            "TableName": table_name,
            "KeySchema": [
                {"AttributeName": partition_key, "KeyType": "HASH"}
            ],
            "AttributeDefinitions": [
                {"AttributeName": partition_key, "AttributeType": partition_key_type[0]}
            ]
        }
        
        if use_sort_key:
            table_config["KeySchema"].append({"AttributeName": sort_key, "KeyType": "RANGE"})
            table_config["AttributeDefinitions"].append({"AttributeName": sort_key, "AttributeType": sort_key_type[0]})
        
        # Calculate estimated cost
        if "On-Demand" in capacity_mode:
            estimated_cost = "~$1.25 per million read requests, $1.25 per million write requests"
        else:
            monthly_cost = (read_capacity * 0.00013 + write_capacity * 0.00065) * 24 * 30
            estimated_cost = f"${monthly_cost:.2f}/month"
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ DynamoDB Table Configuration Generated!
        
        **Table Details:**
        - **Name**: {table_name}
        - **Partition Key**: {partition_key} ({partition_key_type})
        {f"- **Sort Key**: {sort_key} ({sort_key_type})" if use_sort_key else ""}
        - **Capacity Mode**: {capacity_mode}
        {f"- **RCU/WCU**: {read_capacity}/{write_capacity}" if "Provisioned" in capacity_mode else ""}
        
        **Features Enabled:**
        - DynamoDB Streams: {'✅ ' + stream_view_type if enable_streams else '❌'}
        - Time to Live: {'✅ ' + ttl_attribute if enable_ttl else '❌'}
        - Encryption: {'✅ ' + encryption_type if enable_encryption else '❌'}
        {f"- Global Secondary Index: ✅ {gsi_name}" if enable_gsi else ""}
        
        **Estimated Cost**: {estimated_cost}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Capacity Modes Comparison
    st.markdown("### ⚖️ Capacity Modes Comparison")
    
    capacity_data = {
        'Feature': ['Pricing Model', 'Scaling', 'Performance', 'Use Case', 'Cost Predictability'],
        'Provisioned Mode': [
            'Fixed hourly rate based on provisioned capacity',
            'Manual scaling or Auto Scaling',
            'Consistent performance, predictable latency',
            'Predictable traffic patterns, cost optimization',
            'High - fixed monthly costs'
        ],
        'On-Demand Mode': [
            'Pay-per-request pricing',
            'Automatic scaling (instant)',
            'Variable performance, handles traffic spikes',
            'Unpredictable traffic, new applications',
            'Low - costs vary with usage'
        ]
    }
    
    df_capacity = pd.DataFrame(capacity_data)
    st.dataframe(df_capacity, use_container_width=True)
    
    # DynamoDB vs RDS Comparison  
    st.markdown("### 🗄️ DynamoDB vs Amazon RDS Comparison")
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 When to Choose DynamoDB vs RDS
    
    **Choose DynamoDB when:**
    - You need **single-digit millisecond** latency
    - Your application has **unpredictable scaling** requirements
    - You want **zero database administration**
    - Your data access patterns are **known and simple**
    - You're building **serverless applications**
    
    **Choose RDS when:**
    - You need **complex queries and joins**
    - You have **existing SQL applications**
    - You need **ACID transactions across multiple tables**
    - Your team has **strong SQL expertise**
    - You need **complex reporting and analytics**
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Examples
    st.markdown("### 💻 Code Examples")
    
    tab1, tab2, tab3 = st.tabs(["🏗️ Table Operations", "📊 Query & Scan", "🌊 DynamoDB Streams"])
    
    with tab1:
        st.markdown('<div class="code-container">', unsafe_allow_html=True)
        st.code('''
# DynamoDB table operations and CRUD operations
import boto3
import json
from decimal import Decimal
from datetime import datetime, timedelta
import uuid

# Initialize DynamoDB clients
dynamodb = boto3.resource('dynamodb')
dynamodb_client = boto3.client('dynamodb')

def create_user_table():
    """Create a user table with GSI and streams"""
    
    try:
        table = dynamodb.create_table(
            TableName='UserProfiles',
            KeySchema=[
                {'AttributeName': 'userId', 'KeyType': 'HASH'},  # Partition key
                {'AttributeName': 'createdAt', 'KeyType': 'RANGE'}  # Sort key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'userId', 'AttributeType': 'S'},
                {'AttributeName': 'createdAt', 'AttributeType': 'S'},
                {'AttributeName': 'email', 'AttributeType': 'S'},
                {'AttributeName': 'status', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'email-index',
                    'KeySchema': [
                        {'AttributeName': 'email', 'KeyType': 'HASH'}
                    ],
                    'Projection': {'ProjectionType': 'ALL'},
                    'BillingMode': 'PAY_PER_REQUEST'
                },
                {
                    'IndexName': 'status-index', 
                    'KeySchema': [
                        {'AttributeName': 'status', 'KeyType': 'HASH'},
                        {'AttributeName': 'createdAt', 'KeyType': 'RANGE'}
                    ],
                    'Projection': {
                        'ProjectionType': 'INCLUDE',
                        'NonKeyAttributes': ['userId', 'email', 'name']
                    },
                    'BillingMode': 'PAY_PER_REQUEST'
                }
            ],
            StreamSpecification={
                'StreamEnabled': True,
                'StreamViewType': 'NEW_AND_OLD_IMAGES'
            },
            BillingMode='PAY_PER_REQUEST',
            Tags=[
                {'Key': 'Environment', 'Value': 'Production'},
                {'Key': 'Application', 'Value': 'UserManagement'}
            ]
        )
        
        # Wait for table to be created
        table.wait_until_exists()
        print(f"✅ Table {table.table_name} created successfully")
        
        # Enable TTL
        dynamodb_client.update_time_to_live(
            TableName='UserProfiles',
            TimeToLiveSpecification={
                'AttributeName': 'expiresAt',
                'Enabled': True
            }
        )
        
        return table
    
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return None

def create_user(user_data):
    """Create a new user with proper data types"""
    table = dynamodb.Table('UserProfiles')
    
    # Generate unique user ID
    user_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    
    # Prepare item with TTL (expires in 30 days)
    expires_at = int((datetime.utcnow() + timedelta(days=30)).timestamp())
    
    item = {
        'userId': user_id,
        'createdAt': created_at,
        'email': user_data['email'],
        'name': user_data['name'],
        'status': user_data.get('status', 'active'),
        'profile': {
            'age': user_data.get('age', 0),
            'location': user_data.get('location', ''),
            'interests': user_data.get('interests', [])
        },
        'metadata': {
            'loginCount': 0,
            'lastLogin': None,
            'preferences': user_data.get('preferences', {})
        },
        'expiresAt': expires_at  # TTL attribute
    }
    
    try:
        # Use condition expression to prevent overwrites
        response = table.put_item(
            Item=item,
            ConditionExpression='attribute_not_exists(userId)',
            ReturnValues='ALL_OLD'
        )
        
        print(f"✅ User created: {user_id}")
        return {'userId': user_id, 'status': 'created'}
    
    except dynamodb_client.exceptions.ConditionalCheckFailedException:
        print(f"❌ User already exists: {user_id}")
        return {'error': 'User already exists'}
    
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return {'error': str(e)}

def get_user(user_id, created_at=None):
    """Get user with optional consistent read"""
    table = dynamodb.Table('UserProfiles')
    
    try:
        if created_at:
            # Get specific version with sort key
            response = table.get_item(
                Key={
                    'userId': user_id,
                    'createdAt': created_at
                },
                ConsistentRead=True  # Strong consistency
            )
        else:
            # Query for latest version
            response = table.query(
                KeyConditionExpression='userId = :uid',
                ExpressionAttributeValues={':uid': user_id},
                ScanIndexForward=False,  # Descending order (latest first)
                Limit=1
            )
            
            if response['Items']:
                return response['Items'][0]
            else:
                return None
        
        return response.get('Item')
    
    except Exception as e:
        print(f"❌ Error getting user: {e}")
        return None

def update_user(user_id, created_at, update_data):
    """Update user with atomic operations"""
    table = dynamodb.Table('UserProfiles')
    
    # Build update expression dynamically
    update_expression = "SET "
    expression_values = {}
    expression_names = {}
    
    for key, value in update_data.items():
        if key not in ['userId', 'createdAt']:  # Don't update primary key
            if isinstance(value, dict):
                # Handle nested attributes
                for nested_key, nested_value in value.items():
                    attr_name = f"#{key}__{nested_key}"
                    attr_value = f":{key}_{nested_key}"
                    
                    expression_names[attr_name] = f"{key}.{nested_key}"
                    expression_values[attr_value] = nested_value
                    update_expression += f"{attr_name} = {attr_value}, "
            else:
                attr_name = f"#{key}"
                attr_value = f":{key}"
                
                expression_names[attr_name] = key
                expression_values[attr_value] = value
                update_expression += f"{attr_name} = {attr_value}, "
    
    # Add timestamp for last modified
    expression_names['#lastModified'] = 'lastModified'
    expression_values[':lastModified'] = datetime.utcnow().isoformat()
    update_expression += "#lastModified = :lastModified"
    
    try:
        response = table.update_item(
            Key={
                'userId': user_id,
                'createdAt': created_at
            },
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_names,
            ExpressionAttributeValues=expression_values,
            ConditionExpression='attribute_exists(userId)',  # Ensure item exists
            ReturnValues='ALL_NEW'
        )
        
        print(f"✅ User updated: {user_id}")
        return response['Attributes']
    
    except dynamodb_client.exceptions.ConditionalCheckFailedException:
        print(f"❌ User not found: {user_id}")
        return {'error': 'User not found'}
    
    except Exception as e:
        print(f"❌ Error updating user: {e}")
        return {'error': str(e)}

def delete_user(user_id, created_at):
    """Delete user with condition"""
    table = dynamodb.Table('UserProfiles')
    
    try:
        response = table.delete_item(
            Key={
                'userId': user_id,
                'createdAt': created_at
            },
            ConditionExpression='attribute_exists(userId)',
            ReturnValues='ALL_OLD'
        )
        
        print(f"✅ User deleted: {user_id}")
        return response.get('Attributes')
    
    except dynamodb_client.exceptions.ConditionalCheckFailedException:
        print(f"❌ User not found: {user_id}")
        return {'error': 'User not found'}
    
    except Exception as e:
        print(f"❌ Error deleting user: {e}")
        return {'error': str(e)}

def batch_operations_example():
    """Example of batch read and write operations"""
    
    # Batch write - up to 25 items
    with dynamodb.Table('UserProfiles').batch_writer() as batch:
        for i in range(10):
            batch.put_item(Item={
                'userId': f'batch-user-{i}',
                'createdAt': datetime.utcnow().isoformat(),
                'email': f'user{i}@example.com',
                'name': f'Batch User {i}',
                'status': 'active'
            })
    
    print("✅ Batch write completed")
    
    # Batch read
    response = dynamodb_client.batch_get_item(
        RequestItems={
            'UserProfiles': {
                'Keys': [
                    {'userId': {'S': 'batch-user-0'}, 'createdAt': {'S': '2023-01-01T00:00:00'}},
                    {'userId': {'S': 'batch-user-1'}, 'createdAt': {'S': '2023-01-01T00:00:00'}}
                ]
            }
        }
    )
    
    print(f"✅ Batch read returned {len(response['Responses']['UserProfiles'])} items")

# Example usage
if __name__ == "__main__":
    # Create table
    table = create_user_table()
    
    if table:
        # Create users
        user_data = {
            'email': 'john.doe@example.com',
            'name': 'John Doe',
            'age': 30,
            'location': 'New York',
            'interests': ['technology', 'music'],
            'preferences': {'theme': 'dark', 'notifications': True}
        }
        
        result = create_user(user_data)
        print(f"Create result: {result}")
        
        # Batch operations
        batch_operations_example()
        ''', language='python')
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="code-container">', unsafe_allow_html=True)
        st.code('''
# DynamoDB Query and Scan operations with best practices
import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal
import json

dynamodb = boto3.resource('dynamodb')

def query_users_by_status(status, limit=20):
    """Query users by status using GSI"""
    table = dynamodb.Table('UserProfiles')
    
    try:
        response = table.query(
            IndexName='status-index',
            KeyConditionExpression=Key('status').eq(status),
            ScanIndexForward=False,  # Descending order by sort key
            Limit=limit,
            ProjectionExpression='userId, email, #name, createdAt, #status',
            ExpressionAttributeNames={
                '#name': 'name',  # 'name' is a reserved word
                '#status': 'status'
            }
        )
        
        users = response['Items']
        
        # Handle pagination
        last_evaluated_key = response.get('LastEvaluatedKey')
        
        print(f"✅ Found {len(users)} users with status '{status}'")
        
        return {
            'users': users,
            'lastEvaluatedKey': last_evaluated_key,
            'count': len(users)
        }
    
    except Exception as e:
        print(f"❌ Error querying users: {e}")
        return {'error': str(e)}

def query_user_by_email(email):
    """Query user by email using GSI"""
    table = dynamodb.Table('UserProfiles')
    
    try:
        response = table.query(
            IndexName='email-index',
            KeyConditionExpression=Key('email').eq(email),
            Select='ALL_ATTRIBUTES'
        )
        
        if response['Items']:
            return response['Items'][0]  # Should be unique
        else:
            return None
    
    except Exception as e:
        print(f"❌ Error querying user by email: {e}")
        return None

def query_users_created_in_date_range(start_date, end_date, user_id=None):
    """Query users created within a date range"""
    table = dynamodb.Table('UserProfiles')
    
    try:
        if user_id:
            # Query specific user's versions within date range
            response = table.query(
                KeyConditionExpression=Key('userId').eq(user_id) & 
                                     Key('createdAt').between(start_date, end_date),
                ScanIndexForward=True  # Ascending order by date
            )
        else:
            # Use GSI to query by date range (requires GSI on createdAt)
            response = table.scan(
                FilterExpression=Attr('createdAt').between(start_date, end_date),
                ProjectionExpression='userId, email, #name, createdAt',
                ExpressionAttributeNames={'#name': 'name'}
            )
        
        return response['Items']
    
    except Exception as e:
        print(f"❌ Error querying users by date range: {e}")
        return []

def paginated_scan_with_filter():
    """Perform paginated scan with filters"""
    table = dynamodb.Table('UserProfiles')
    
    all_items = []
    last_evaluated_key = None
    scan_count = 0
    
    try:
        while True:
            scan_count += 1
            print(f"Performing scan #{scan_count}")
            
            scan_kwargs = {
                'FilterExpression': Attr('profile.age').gte(18) & Attr('status').eq('active'),
                'ProjectionExpression': 'userId, email, #name, profile.age, #status',
                'ExpressionAttributeNames': {
                    '#name': 'name',
                    '#status': 'status'
                },
                'Limit': 100  # Process in chunks of 100
            }
            
            if last_evaluated_key:
                scan_kwargs['ExclusiveStartKey'] = last_evaluated_key
            
            response = table.scan(**scan_kwargs)
            
            items = response['Items']
            all_items.extend(items)
            
            print(f"  Found {len(items)} items in this scan")
            
            last_evaluated_key = response.get('LastEvaluatedKey')
            if not last_evaluated_key:
                break  # No more items to scan
        
        print(f"✅ Total items found: {len(all_items)} across {scan_count} scans")
        return all_items
    
    except Exception as e:
        print(f"❌ Error during paginated scan: {e}")
        return []

def query_with_sort_key_conditions():
    """Advanced query with sort key conditions"""
    table = dynamodb.Table('UserProfiles')
    
    # Get user's recent activities (last 30 days)
    from datetime import datetime, timedelta
    
    thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
    user_id = 'specific-user-id'
    
    try:
        # Query with begins_with condition
        response = table.query(
            KeyConditionExpression=Key('userId').eq(user_id) & 
                                 Key('createdAt').gte(thirty_days_ago),
            ScanIndexForward=False,  # Get latest first
            Limit=50
        )
        
        recent_items = response['Items']
        
        # Query with specific sort key pattern
        response2 = table.query(
            KeyConditionExpression=Key('userId').eq(user_id) & 
                                 Key('createdAt').begins_with('2023-07'),  # July 2023
            ScanIndexForward=True
        )
        
        july_items = response2['Items']
        
        return {
            'recent_items': recent_items,
            'july_items': july_items
        }
    
    except Exception as e:
        print(f"❌ Error in advanced query: {e}")
        return {}

def count_items_efficiently():
    """Count items efficiently using query/scan with Select"""
    table = dynamodb.Table('UserProfiles')
    
    try:
        # Count active users using GSI
        response = table.query(
            IndexName='status-index',
            KeyConditionExpression=Key('status').eq('active'),
            Select='COUNT'  # Only return count, not items
        )
        
        active_count = response['Count']
        
        # Count all users in table
        response = table.scan(Select='COUNT')
        total_count = response['Count']
        
        # Handle pagination for accurate count
        while 'LastEvaluatedKey' in response:
            response = table.scan(
                Select='COUNT',
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            total_count += response['Count']
        
        print(f"✅ Active users: {active_count}, Total users: {total_count}")
        
        return {
            'active_users': active_count,
            'total_users': total_count,
            'inactive_users': total_count - active_count
        }
    
    except Exception as e:
        print(f"❌ Error counting items: {e}")
        return {}

def search_users_by_multiple_criteria():
    """Search users with multiple filter conditions"""
    table = dynamodb.Table('UserProfiles')
    
    try:
        # Complex filter expression
        filter_expression = (
            Attr('status').eq('active') &
            Attr('profile.age').between(25, 40) &
            Attr('profile.location').contains('New York') &
            Attr('metadata.loginCount').gte(5)
        )
        
        response = table.scan(
            FilterExpression=filter_expression,
            ProjectionExpression='userId, email, #name, profile, metadata.loginCount',
            ExpressionAttributeNames={'#name': 'name'}
        )
        
        users = response['Items']
        
        # Continue pagination if needed
        while 'LastEvaluatedKey' in response:
            response = table.scan(
                FilterExpression=filter_expression,
                ProjectionExpression='userId, email, #name, profile, metadata.loginCount',
                ExpressionAttributeNames={'#name': 'name'},
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            users.extend(response['Items'])
        
        print(f"✅ Found {len(users)} users matching criteria")
        return users
    
    except Exception as e:
        print(f"❌ Error searching users: {e}")
        return []

def efficient_large_data_processing():
    """Process large datasets efficiently with parallel scanning"""
    import concurrent.futures
    import threading
    
    table = dynamodb.Table('UserProfiles')
    
    def scan_segment(segment, total_segments):
        """Scan a specific segment of the table"""
        items = []
        last_evaluated_key = None
        
        try:
            while True:
                scan_kwargs = {
                    'Segment': segment,
                    'TotalSegments': total_segments,
                    'FilterExpression': Attr('status').eq('active'),
                    'ProjectionExpression': 'userId, email, profile.age'
                }
                
                if last_evaluated_key:
                    scan_kwargs['ExclusiveStartKey'] = last_evaluated_key
                
                response = table.scan(**scan_kwargs)
                items.extend(response['Items'])
                
                last_evaluated_key = response.get('LastEvaluatedKey')
                if not last_evaluated_key:
                    break
            
            print(f"Segment {segment}: {len(items)} items")
            return items
        
        except Exception as e:
            print(f"Error in segment {segment}: {e}")
            return []
    
    # Use parallel scanning for large tables
    total_segments = 4  # Adjust based on table size and RCU capacity
    all_items = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=total_segments) as executor:
        futures = [
            executor.submit(scan_segment, segment, total_segments)
            for segment in range(total_segments)
        ]
        
        for future in concurrent.futures.as_completed(futures):
            segment_items = future.result()
            all_items.extend(segment_items)
    
    print(f"✅ Parallel scan completed: {len(all_items)} total items")
    return all_items

# Example usage and best practices
def demo_query_patterns():
    """Demonstrate various query patterns"""
    print("🔍 DynamoDB Query and Scan Patterns Demo")
    print("=" * 50)
    
    # 1. Efficient queries using GSI
    print("\n1. Query by status (using GSI):")
    active_users = query_users_by_status('active', limit=10)
    
    # 2. Point lookup by email
    print("\n2. Query by email (using GSI):")
    user = query_user_by_email('john.doe@example.com')
    
    # 3. Range query with date
    print("\n3. Date range query:")
    recent_users = query_users_created_in_date_range(
        '2023-07-01T00:00:00',
        '2023-07-31T23:59:59'
    )
    
    # 4. Filtered scan with pagination
    print("\n4. Filtered scan with pagination:")
    adult_active_users = paginated_scan_with_filter()
    
    # 5. Count operations
    print("\n5. Count items efficiently:")
    counts = count_items_efficiently()
    
    # 6. Complex search
    print("\n6. Multi-criteria search:")
    targeted_users = search_users_by_multiple_criteria()
    
    # 7. Large data processing
    print("\n7. Parallel processing for large datasets:")
    all_active_users = efficient_large_data_processing()

if __name__ == "__main__":
    demo_query_patterns()
        ''', language='python')
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="code-container">', unsafe_allow_html=True)
        st.code('''
# DynamoDB Streams processing with Lambda
import json
import boto3
from decimal import Decimal
from datetime import datetime

def lambda_handler(event, context):
    """
    Process DynamoDB Streams with different event types
    """
    
    # Process each record in the stream
    processed_records = []
    
    for record in event['Records']:
        try:
            result = process_stream_record(record)
            processed_records.append(result)
            
        except Exception as e:
            print(f"Error processing record: {e}")
            # In production, you might want to send to DLQ
            continue
    
    return {
        'statusCode': 200,
        'processedRecords': len(processed_records),
        'results': processed_records
    }

def process_stream_record(record):
    """Process individual DynamoDB stream record"""
    
    event_name = record['eventName']  # INSERT, MODIFY, REMOVE
    event_source = record['eventSource']  # aws:dynamodb
    
    # Extract DynamoDB data
    dynamodb_data = record['dynamodb']
    
    print(f"Processing {event_name} event from {event_source}")
    
    if event_name == 'INSERT':
        return handle_insert_event(dynamodb_data)
    
    elif event_name == 'MODIFY':
        return handle_modify_event(dynamodb_data)
    
    elif event_name == 'REMOVE':
        return handle_remove_event(dynamodb_data)
    
    else:
        print(f"Unknown event type: {event_name}")
        return {'status': 'ignored', 'eventName': event_name}

def handle_insert_event(dynamodb_data):
    """Handle new item insertion"""
    
    # Get the new item
    new_image = dynamodb_data['NewImage']
    keys = dynamodb_data['Keys']
    
    # Convert DynamoDB format to Python format
    new_item = deserialize_dynamodb_item(new_image)
    
    print(f"New item created: {new_item.get('userId', 'unknown')}")
    
    # Example actions for new user
    if 'email' in new_item:
        send_welcome_email(new_item['email'], new_item.get('name', 'User'))
    
    # Update analytics
    update_user_analytics('user_created', new_item)
    
    # Sync to search index
    sync_to_elasticsearch(new_item, action='index')
    
    return {
        'status': 'processed',
        'action': 'insert',
        'userId': new_item.get('userId'),
        'operations': ['welcome_email', 'analytics', 'search_sync']
    }

def handle_modify_event(dynamodb_data):
    """Handle item modification"""
    
    old_image = dynamodb_data.get('OldImage', {})
    new_image = dynamodb_data['NewImage']
    keys = dynamodb_data['Keys']
    
    # Convert to Python format
    old_item = deserialize_dynamodb_item(old_image) if old_image else {}
    new_item = deserialize_dynamodb_item(new_image)
    
    user_id = new_item.get('userId', 'unknown')
    print(f"Item modified: {user_id}")
    
    # Detect specific changes
    changes = detect_changes(old_item, new_item)
    operations = []
    
    # Handle status changes
    if 'status' in changes:
        old_status = changes['status']['old']
        new_status = changes['status']['new']
        
        handle_status_change(user_id, old_status, new_status)
        operations.append('status_change')
    
    # Handle email changes
    if 'email' in changes:
        handle_email_change(user_id, changes['email']['old'], changes['email']['new'])
        operations.append('email_update')
    
    # Handle profile updates
    if 'profile' in changes:
        handle_profile_update(user_id, changes['profile'])
        operations.append('profile_update')
    
    # Update search index
    sync_to_elasticsearch(new_item, action='update')
    operations.append('search_sync')
    
    # Update analytics
    update_user_analytics('user_modified', new_item, changes)
    operations.append('analytics')
    
    return {
        'status': 'processed',
        'action': 'modify',
        'userId': user_id,
        'changes': list(changes.keys()),
        'operations': operations
    }

def handle_remove_event(dynamodb_data):
    """Handle item deletion"""
    
    old_image = dynamodb_data.get('OldImage', {})
    keys = dynamodb_data['Keys']
    
    # Get the deleted item data
    deleted_item = deserialize_dynamodb_item(old_image) if old_image else {}
    user_id = deleted_item.get('userId', 'unknown')
    
    print(f"Item deleted: {user_id}")
    
    # Archive user data
    archive_user_data(deleted_item)
    
    # Remove from search index
    sync_to_elasticsearch({'userId': user_id}, action='delete')
    
    # Update analytics
    update_user_analytics('user_deleted', deleted_item)
    
    # Send deletion confirmation email
    if 'email' in deleted_item:
        send_deletion_confirmation(deleted_item['email'])
    
    return {
        'status': 'processed',
        'action': 'remove',
        'userId': user_id,
        'operations': ['archive', 'search_remove', 'analytics', 'confirmation_email']
    }

def deserialize_dynamodb_item(item):
    """Convert DynamoDB format to Python objects"""
    if not item:
        return {}
    
    result = {}
    
    for key, value in item.items():
        if 'S' in value:  # String
            result[key] = value['S']
        elif 'N' in value:  # Number
            result[key] = Decimal(value['N'])
        elif 'B' in value:  # Binary
            result[key] = value['B']
        elif 'BOOL' in value:  # Boolean
            result[key] = value['BOOL']
        elif 'NULL' in value:  # Null
            result[key] = None
        elif 'L' in value:  # List
            result[key] = [deserialize_dynamodb_item({'item': item_val})['item'] for item_val in value['L']]
        elif 'M' in value:  # Map
            result[key] = deserialize_dynamodb_item(value['M'])
        elif 'SS' in value:  # String Set
            result[key] = set(value['SS'])
        elif 'NS' in value:  # Number Set
            result[key] = set(Decimal(n) for n in value['NS'])
        elif 'BS' in value:  # Binary Set
            result[key] = set(value['BS'])
    
    return result

def detect_changes(old_item, new_item):
    """Detect changes between old and new items"""
    changes = {}
    
    # Check all keys in new item
    for key, new_value in new_item.items():
        old_value = old_item.get(key)
        
        if old_value != new_value:
            changes[key] = {
                'old': old_value,
                'new': new_value
            }
    
    # Check for removed keys
    for key in old_item:
        if key not in new_item:
            changes[key] = {
                'old': old_item[key],
                'new': None
            }
    
    return changes

def handle_status_change(user_id, old_status, new_status):
    """Handle user status changes"""
    print(f"Status change for {user_id}: {old_status} -> {new_status}")
    
    # Send to SNS for different status changes
    sns = boto3.client('sns')
    topic_arn = 'arn:aws:sns:us-east-1:123456789012:user-status-changes'
    
    message = {
        'userId': user_id,
        'oldStatus': old_status,
        'newStatus': new_status,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    sns.publish(
        TopicArn=topic_arn,
        Message=json.dumps(message),
        Subject=f'User Status Change: {user_id}'
    )

def handle_email_change(user_id, old_email, new_email):
    """Handle email address changes"""
    print(f"Email change for {user_id}: {old_email} -> {new_email}")
    
    # Send verification email to new address
    ses = boto3.client('ses')
    
    try:
        ses.send_email(
            Source='noreply@example.com',
            Destination={'ToAddresses': [new_email]},
            Message={
                'Subject': {'Data': 'Email Address Changed'},
                'Body': {
                    'Text': {
                        'Data': f'Your email address has been updated to {new_email}. '
                               f'If this was not you, please contact support.'
                    }
                }
            }
        )
    except Exception as e:
        print(f"Failed to send email notification: {e}")

def handle_profile_update(user_id, profile_changes):
    """Handle profile updates"""
    print(f"Profile updated for {user_id}: {profile_changes}")
    
    # Trigger recommendations update if interests changed
    if 'interests' in profile_changes:
        trigger_recommendations_update(user_id, profile_changes['interests']['new'])

def sync_to_elasticsearch(item, action='index'):
    """Sync data to Elasticsearch for search"""
    # This would integrate with Amazon OpenSearch Service
    print(f"Syncing to search index: {action} - {item.get('userId', 'unknown')}")
    
    # In a real implementation, you would:
    # 1. Transform the data for search
    # 2. Send to OpenSearch/Elasticsearch
    # 3. Handle any sync errors

def update_user_analytics(event_type, item_data, changes=None):
    """Update analytics data"""
    # Send analytics data to Kinesis or CloudWatch
    cloudwatch = boto3.client('cloudwatch')
    
    try:
        cloudwatch.put_metric_data(
            Namespace='UserAnalytics',
            MetricData=[
                {
                    'MetricName': 'UserEvents',
                    'Dimensions': [
                        {'Name': 'EventType', 'Value': event_type}
                    ],
                    'Value': 1,
                    'Unit': 'Count'
                }
            ]
        )
    except Exception as e:
        print(f"Failed to send analytics: {e}")

def send_welcome_email(email, name='User'):
    """Send welcome email to new users"""
    print(f"Sending welcome email to {email}")
    # Implementation would use SES to send email

def send_deletion_confirmation(email):
    """Send deletion confirmation email"""
    print(f"Sending deletion confirmation to {email}")
    # Implementation would use SES to send email

def archive_user_data(user_data):
    """Archive deleted user data"""
    # Store in S3 for compliance/audit purposes
    s3 = boto3.client('s3')
    
    try:
        archive_key = f"deleted-users/{user_data.get('userId', 'unknown')}/{datetime.utcnow().isoformat()}.json"
        
        s3.put_object(
            Bucket='user-data-archive',
            Key=archive_key,
            Body=json.dumps(user_data, default=str, indent=2),
            ContentType='application/json'
        )
        
        print(f"User data archived: {archive_key}")
    except Exception as e:
        print(f"Failed to archive user data: {e}")

def trigger_recommendations_update(user_id, interests):
    """Trigger recommendations engine update"""
    # Send to SQS queue for processing by recommendations service
    sqs = boto3.client('sqs')
    
    try:
        message = {
            'userId': user_id,
            'interests': interests,
            'timestamp': datetime.utcnow().isoformat(),
            'action': 'update_recommendations'
        }
        
        sqs.send_message(
            QueueUrl='https://sqs.us-east-1.amazonaws.com/123456789012/recommendations-queue',
            MessageBody=json.dumps(message)
        )
    except Exception as e:
        print(f"Failed to trigger recommendations update: {e}")

# Example stream record processing
def example_stream_processing():
    """Example of processing different stream record types"""
    
    # Example INSERT record
    insert_record = {
        'eventName': 'INSERT',
        'eventSource': 'aws:dynamodb',
        'dynamodb': {
            'Keys': {
                'userId': {'S': 'user-123'},
                'createdAt': {'S': '2023-07-15T10:00:00Z'}
            },
            'NewImage': {
                'userId': {'S': 'user-123'},
                'createdAt': {'S': '2023-07-15T10:00:00Z'},
                'email': {'S': 'user@example.com'},
                'name': {'S': 'John Doe'},
                'status': {'S': 'active'},
                'profile': {
                    'M': {
                        'age': {'N': '30'},
                        'location': {'S': 'New York'}
                    }
                }
            }
        }
    }
    
    # Process the record
    result = process_stream_record(insert_record)
    print(f"Insert processing result: {result}")

if __name__ == "__main__":
    example_stream_processing()
        ''', language='python')
        st.markdown('</div>', unsafe_allow_html=True)

def step_functions_tab():
    """Content for AWS Step Functions tab"""
    st.markdown("## 🔄 AWS Step Functions")
    st.markdown("*Serverless visual workflow service that orchestrates AWS services using state machines*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **AWS Step Functions** lets you coordinate multiple AWS services into serverless workflows. You can design and run 
    workflows that stitch together services such as Lambda, Fargate, and SageMaker into feature-rich applications.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Step Functions Workflow Example
    st.markdown("### 🔄 Credit Card Application Workflow")
    common.mermaid(create_step_functions_workflow_mermaid(), height=1000)
    
    # Workflow Types
    st.markdown("### ⚙️ Step Functions Workflow Types")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚡ Express Workflows
        **Characteristics:**
        - **High-volume**, short-duration workflows
        - **At-least-once** execution model
        - Duration up to **5 minutes**
        - Up to **100,000 executions/second**
        
        **Pricing:** Pay per execution
        
        **Best For:**
        - IoT data ingestion
        - Real-time data processing
        - Mobile/web backends
        - Microservices orchestration
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 Standard Workflows
        **Characteristics:**
        - **Long-running** workflows
        - **Exactly-once** execution model
        - Duration up to **1 year**
        - Up to **2,000 executions/second**
        
        **Pricing:** Pay per state transition
        
        **Best For:**
        - Business processes
        - ETL jobs
        - Complex orchestration
        - Human approval workflows
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # State Types
    st.markdown("### 🧩 State Types in Step Functions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 Task States
        - **Lambda functions**
        - **AWS services** (SNS, SQS, DynamoDB)
        - **Activities** (external workers)
        - **Container tasks** (ECS, Fargate)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔄 Flow Control
        - **Choice**: Conditional branching
        - **Parallel**: Execute in parallel
        - **Map**: Process array items
        - **Wait**: Delay execution
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎬 Control States
        - **Pass**: Pass input to output
        - **Succeed**: Successful termination
        - **Fail**: Failure termination
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔄 Error Handling
        - **Retry**: Automatic retries
        - **Catch**: Error handling
        - **TimeoutSeconds**: Task timeout
        - **HeartbeatSeconds**: Activity heartbeat
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📊 Data Processing
        - **InputPath**: Filter input
        - **OutputPath**: Filter output
        - **ResultPath**: Where to put result
        - **Parameters**: Transform input
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔄 Advanced Features
        - **Callbacks**: Wait for external response
        - **Nested workflows**: Step Function to Step Function
        - **Local testing**: Step Functions Local
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Workflow Builder
    st.markdown("### 🛠️ Interactive Workflow Builder")
    
    workflow_type = st.selectbox("Workflow Type:", [
        "E-commerce Order Processing",
        "Image Processing Pipeline", 
        "Data ETL Pipeline",
        "User Approval Workflow",
        "Custom Workflow"
    ])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⚙️ Workflow Configuration")
        if workflow_type == "E-commerce Order Processing":
            steps = ["Validate Order", "Process Payment", "Update Inventory", "Ship Product", "Send Confirmation"]
            error_handling = ["Payment Retry Logic", "Inventory Check", "Shipping Fallback"]
        elif workflow_type == "Image Processing Pipeline":
            steps = ["Upload to S3", "Thumbnail Generation", "Metadata Extraction", "Content Moderation", "Store Results"]
            error_handling = ["Retry Failed Processing", "Invalid Image Handling", "Moderation Failure"]
        elif workflow_type == "Data ETL Pipeline":
            steps = ["Extract from Sources", "Transform Data", "Validate Quality", "Load to Warehouse", "Send Notifications"]
            error_handling = ["Source Connection Retry", "Validation Failures", "Load Rollback"]
        else:
            steps = ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"]
            error_handling = ["Retry Logic", "Error Notifications", "Fallback Handling"]
        
        max_duration = st.selectbox("Max Duration:", [
            "5 minutes (Express)", "1 hour", "1 day", "1 week", "1 year (Standard)"
        ])
        
        enable_parallel = st.checkbox("Enable Parallel Processing", value=True)
        enable_human_approval = st.checkbox("Include Human Approval Step", value=False)
    
    with col2:
        st.markdown("#### 🔧 Advanced Settings")
        retry_attempts = st.slider("Max Retry Attempts:", 0, 10, 3)
        timeout_seconds = st.slider("Task Timeout (seconds):", 30, 3600, 300)
        
        error_notification = st.checkbox("Error Notifications", value=True)
        execution_logging = st.selectbox("Logging Level:", ["OFF", "ALL", "ERROR", "FATAL"])
        
        integration_services = st.multiselect("AWS Services to Integrate:", [
            "Lambda", "DynamoDB", "S3", "SNS", "SQS", "ECS", "Batch", "Glue"
        ], default=["Lambda", "DynamoDB"])
    
    if st.button("🚀 Generate Step Functions Workflow", use_container_width=True):
        # Calculate estimated cost
        if "Express" in max_duration:
            estimated_cost = "$0.000025 per execution"
            execution_model = "At-least-once"
        else:
            estimated_cost = "$0.025 per 1,000 state transitions"
            execution_model = "Exactly-once"
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ Step Functions Workflow Generated!
        
        **Workflow Details:**
        - **Type**: {workflow_type}
        - **Max Duration**: {max_duration}
        - **Execution Model**: {execution_model}
        - **Steps**: {len(steps)} total steps
        
        **Configuration:**
        - **Retry Attempts**: {retry_attempts}
        - **Task Timeout**: {timeout_seconds} seconds
        - **Parallel Processing**: {'✅' if enable_parallel else '❌'}
        - **Human Approval**: {'✅' if enable_human_approval else '❌'}
        
        **Integrations:**
        - **AWS Services**: {', '.join(integration_services)}
        - **Error Notifications**: {'✅' if error_notification else '❌'}
        - **Logging**: {execution_logging}
        
        **Estimated Cost**: {estimated_cost}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show workflow steps
        st.markdown("#### 📋 Workflow Steps:")
        for i, step in enumerate(steps, 1):
            st.markdown(f"{i}. **{step}**")
    
    # Use Cases and Patterns
    st.markdown("### 🌟 Common Use Cases & Patterns")
    
    use_cases_data = {
        'Use Case': [
            'Order Processing', 'Data Processing Pipeline', 'Image/Video Processing',
            'Human Approval Workflow', 'Batch Job Orchestration', 'Microservices Coordination'
        ],
        'Workflow Type': [
            'Standard', 'Express/Standard', 'Express',
            'Standard', 'Standard', 'Express'
        ],
        'Key Services': [
            'Lambda, DynamoDB, SNS, SQS',
            'Lambda, Glue, S3, Athena',
            'Lambda, S3, Rekognition, MediaConvert',
            'Lambda, SNS, SES',
            'Batch, ECS, Lambda, CloudWatch',
            'Lambda, API Gateway, DynamoDB'
        ],
        'Duration': [
            'Minutes to Hours', 'Hours to Days', 'Minutes',
            'Days to Weeks', 'Hours to Days', 'Seconds to Minutes'
        ]
    }
    
    df_use_cases = pd.DataFrame(use_cases_data)
    st.dataframe(df_use_cases, use_container_width=True)
    
    # Best Practices
    st.markdown("### 💡 Step Functions Best Practices")
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Design Best Practices
    
    **Error Handling:**
    - Always implement **Retry** and **Catch** blocks
    - Use **exponential backoff** for retries
    - Set appropriate **TimeoutSeconds** for each task
    - Design for **idempotency** in your Lambda functions
    
    **Performance & Cost:**
    - Use **Express Workflows** for high-volume, short-duration tasks
    - **Minimize state transitions** in Standard Workflows
    - Use **Parallel** states to reduce overall execution time
    - **Pass only necessary data** between states
    
    **Monitoring & Debugging:**
    - Enable **CloudWatch Logs** for debugging
    - Use **Step Functions Visual Debugging**
    - Implement **comprehensive logging** in Lambda functions
    - Set up **CloudWatch Alarms** for failed executions
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Examples
    st.markdown("### 💻 Code Examples")
    
    tab1, tab2, tab3 = st.tabs(["🏗️ State Machine Definition", "⚡ Lambda Integration", "🔧 Advanced Patterns"])
    
    with tab1:
        st.markdown('<div class="code-container">', unsafe_allow_html=True)
        st.code('''
# Step Functions State Machine Definition (Amazon States Language)
{
  "Comment": "E-commerce Order Processing Workflow",
  "StartAt": "ValidateOrder",
  "States": {
    "ValidateOrder": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789012:function:ValidateOrder",
      "Parameters": {
        "orderId.$": "$.orderId",
        "customerId.$": "$.customerId",
        "items.$": "$.items"
      },
      "ResultPath": "$.validation",
      "Next": "IsValidOrder",
      "Retry": [
        {
          "ErrorEquals": ["Lambda.ServiceException", "Lambda.AWSLambdaException"],
          "IntervalSeconds": 2,
          "MaxAttempts": 3,
          "BackoffRate": 2.0
        }
      ],
      "Catch": [
        {
          "ErrorEquals": ["States.ALL"],
          "Next": "OrderValidationFailed",
          "ResultPath": "$.error"
        }
      ],
      "TimeoutSeconds": 30
    },
    
    "IsValidOrder": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.validation.isValid",
          "BooleanEquals": true,
          "Next": "ProcessPayment"
        }
      ],
      "Default": "OrderValidationFailed"
    },
    
    "ProcessPayment": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789012:function:ProcessPayment",
      "Parameters": {
        "orderId.$": "$.orderId",
        "paymentMethod.$": "$.paymentMethod",
        "amount.$": "$.validation.totalAmount"
      },
      "ResultPath": "$.payment",
      "Next": "IsPaymentSuccessful",
      "Retry": [
        {
          "ErrorEquals": ["PaymentProcessor.TemporaryFailure"],
          "IntervalSeconds": 5,
          "MaxAttempts": 3,
          "BackoffRate": 2.0
        }
      ],
      "Catch": [
        {
          "ErrorEquals": ["PaymentProcessor.InsufficientFunds"],
          "Next": "PaymentFailed",
          "ResultPath": "$.error"
        },
        {
          "ErrorEquals": ["States.ALL"],
          "Next": "PaymentError",
          "ResultPath": "$.error"
        }
      ],
      "TimeoutSeconds": 60
    },
    
    "IsPaymentSuccessful": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.payment.status",
          "StringEquals": "SUCCESS",
          "Next": "ParallelProcessing"
        }
      ],
      "Default": "PaymentFailed"
    },
    
    "ParallelProcessing": {
      "Type": "Parallel",
      "Comment": "Process inventory and shipping in parallel",
      "Branches": [
        {
          "StartAt": "UpdateInventory",
          "States": {
            "UpdateInventory": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:us-east-1:123456789012:function:UpdateInventory",
              "Parameters": {
                "orderId.$": "$.orderId",
                "items.$": "$.items"
              },
              "End": true,
              "Retry": [
                {
                  "ErrorEquals": ["States.ALL"],
                  "IntervalSeconds": 1,
                  "MaxAttempts": 3,
                  "BackoffRate": 2.0
                }
              ]
            }
          }
        },
        {
          "StartAt": "CreateShippingLabel",
          "States": {
            "CreateShippingLabel": {
              "Type": "Task",
              "Resource": "arn:aws:lambda:us-east-1:123456789012:function:CreateShippingLabel",
              "Parameters": {
                "orderId.$": "$.orderId",
                "shippingAddress.$": "$.shippingAddress"
              },
              "End": true,
              "Retry": [
                {
                  "ErrorEquals": ["States.ALL"],
                  "IntervalSeconds": 1,
                  "MaxAttempts": 3,
                  "BackoffRate": 2.0
                }
              ]
            }
          }
        }
      ],
      "ResultPath": "$.parallelResults",
      "Next": "WaitForShipping",
      "Catch": [
        {
          "ErrorEquals": ["States.ALL"],
          "Next": "ProcessingError",
          "ResultPath": "$.error"
        }
      ]
    },
    
    "WaitForShipping": {
      "Type": "Wait",
      "Comment": "Wait 24 hours before checking shipping status",
      "Seconds": 86400,
      "Next": "CheckShippingStatus"
    },
    
    "CheckShippingStatus": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:us-east-1:123456789012:function:CheckShippingStatus",
      "Parameters": {
        "orderId.$": "$.orderId"
      },
      "ResultPath": "$.shipping",
      "Next": "IsShipped",
      "TimeoutSeconds": 30
    },
    
    "IsShipped": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.shipping.status",
          "StringEquals": "SHIPPED",
          "Next": "SendConfirmationEmail"
        },
        {
          "Variable": "$.shipping.status",
          "StringEquals": "PENDING",
          "Next": "WaitForShipping"
        }
      ],
      "Default": "ShippingError"
    },
    
    "SendConfirmationEmail": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sns:publish",
      "Parameters": {
        "TopicArn": "arn:aws:sns:us-east-1:123456789012:order-confirmations",
        "Message": {
          "orderId.$": "$.orderId",
          "status": "SHIPPED",
          "trackingNumber.$": "$.shipping.trackingNumber"
        }
      },
      "Next": "OrderCompleted"
    },
    
    "OrderCompleted": {
      "Type": "Succeed",
      "Comment": "Order processing completed successfully"
    },
    
    "OrderValidationFailed": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sns:publish",
      "Parameters": {
        "TopicArn": "arn:aws:sns:us-east-1:123456789012:order-errors",
        "Message": {
          "orderId.$": "$.orderId",
          "error": "Order validation failed",
          "details.$": "$.error"
        }
      },
      "Next": "OrderFailed"
    },
    
    "PaymentFailed": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sns:publish",
      "Parameters": {
        "TopicArn": "arn:aws:sns:us-east-1:123456789012:payment-failures",
        "Message": {
          "orderId.$": "$.orderId",
          "error": "Payment processing failed",
          "details.$": "$.error"
        }
      },
      "Next": "OrderFailed"
    },
    
    "PaymentError": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sns:publish",
      "Parameters": {
        "TopicArn": "arn:aws:sns:us-east-1:123456789012:payment-errors",
        "Message": {
          "orderId.$": "$.orderId",
          "error": "Payment processing error",
          "details.$": "$.error"
        }
      },
      "Next": "OrderFailed"
    },
    
    "ProcessingError": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sns:publish",
      "Parameters": {
        "TopicArn": "arn:aws:sns:us-east-1:123456789012:processing-errors",
        "Message": {
          "orderId.$": "$.orderId",
          "error": "Order processing error",
          "details.$": "$.error"
        }
      },
      "Next": "OrderFailed"
    },
    
    "ShippingError": {
      "Type": "Task",
      "Resource": "arn:aws:states:::sns:publish",
      "Parameters": {
        "TopicArn": "arn:aws:sns:us-east-1:123456789012:shipping-errors",
        "Message": {
          "orderId.$": "$.orderId",
          "error": "Shipping processing error"
        }
      },
      "Next": "OrderFailed"
    },
    
    "OrderFailed": {
      "Type": "Fail",
      "Comment": "Order processing failed"
    }
  }
}
        ''', language='json')
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="code-container">', unsafe_allow_html=True)
        st.code('''
# Lambda functions for Step Functions integration
import json
import boto3
from decimal import Decimal
import uuid
from datetime import datetime

def validate_order_handler(event, context):
    """Validate order details"""
    
    order_id = event['orderId']
    customer_id = event['customerId']
    items = event['items']
    
    print(f"Validating order {order_id} for customer {customer_id}")
    
    try:
        # Basic validation
        if not order_id or not customer_id or not items:
            return {
                'isValid': False,
                'error': 'Missing required order information'
            }
        
        # Validate items
        total_amount = Decimal('0')
        validated_items = []
        
        for item in items:
            if not all(key in item for key in ['productId', 'quantity', 'price']):
                return {
                    'isValid': False,
                    'error': f'Invalid item data: {item}'
                }
            
            quantity = Decimal(str(item['quantity']))
            price = Decimal(str(item['price']))
            item_total = quantity * price
            total_amount += item_total
            
            validated_items.append({
                'productId': item['productId'],
                'quantity': quantity,
                'price': price,
                'total': item_total
            })
        
        # Check inventory availability
        inventory_available = check_inventory_availability(validated_items)
        
        if not inventory_available:
            return {
                'isValid': False,
                'error': 'Insufficient inventory for order'
            }
        
        return {
            'isValid': True,
            'totalAmount': total_amount,
            'validatedItems': validated_items,
            'validationTimestamp': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        print(f"Error validating order: {e}")
        raise Exception(f"Order validation failed: {str(e)}")

def process_payment_handler(event, context):
    """Process payment for the order"""
    
    order_id = event['orderId']
    payment_method = event['paymentMethod']
    amount = Decimal(str(event['amount']))
    
    print(f"Processing payment for order {order_id}: ${amount}")
    
    try:
        # Simulate payment processing
        payment_id = str(uuid.uuid4())
        
        # Mock payment gateway call
        payment_result = call_payment_gateway(payment_method, amount)
        
        if payment_result['success']:
            # Store payment record
            store_payment_record(order_id, payment_id, amount, 'SUCCESS')
            
            return {
                'status': 'SUCCESS',
                'paymentId': payment_id,
                'amount': amount,
                'transactionId': payment_result['transactionId'],
                'timestamp': datetime.utcnow().isoformat()
            }
        else:
            # Store failed payment record
            store_payment_record(order_id, payment_id, amount, 'FAILED')
            
            return {
                'status': 'FAILED',
                'paymentId': payment_id,
                'error': payment_result['error'],
                'timestamp': datetime.utcnow().isoformat()
            }
    
    except Exception as e:
        print(f"Error processing payment: {e}")
        # For Step Functions, we can raise specific error types
        if 'insufficient funds' in str(e).lower():
            raise PaymentInsufficientFundsError(str(e))
        else:
            raise PaymentProcessorError(str(e))

def update_inventory_handler(event, context):
    """Update inventory after successful payment"""
    
    order_id = event['orderId']
    items = event['items']
    
    print(f"Updating inventory for order {order_id}")
    
    dynamodb = boto3.resource('dynamodb')
    inventory_table = dynamodb.Table('Inventory')
    
    try:
        # Use transaction to update all items atomically
        with inventory_table.batch_writer() as batch:
            for item in items:
                product_id = item['productId']
                quantity = int(item['quantity'])
                
                # Decrease inventory count
                response = inventory_table.update_item(
                    Key={'productId': product_id},
                    UpdateExpression='SET availableQuantity = availableQuantity - :qty, lastUpdated = :timestamp',
                    ExpressionAttributeValues={
                        ':qty': quantity,
                        ':timestamp': datetime.utcnow().isoformat()
                    },
                    ConditionExpression='availableQuantity >= :qty',
                    ReturnValues='UPDATED_NEW'
                )
                
                print(f"Updated inventory for {product_id}: -{quantity}")
        
        return {
            'status': 'SUCCESS',
            'orderId': order_id,
            'updatedItems': len(items),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        print(f"Error updating inventory: {e}")
        raise Exception(f"Inventory update failed: {str(e)}")

def create_shipping_label_handler(event, context):
    """Create shipping label"""
    
    order_id = event['orderId']
    shipping_address = event['shippingAddress']
    
    print(f"Creating shipping label for order {order_id}")
    
    try:
        # Generate tracking number
        tracking_number = f"TRK{uuid.uuid4().hex[:10].upper()}"
        
        # Call shipping service API
        shipping_result = call_shipping_service(order_id, shipping_address, tracking_number)
        
        if shipping_result['success']:
            # Store shipping record
            store_shipping_record(order_id, tracking_number, shipping_address)
            
            return {
                'status': 'SUCCESS',
                'trackingNumber': tracking_number,
                'shippingLabelUrl': shipping_result['labelUrl'],
                'estimatedDelivery': shipping_result['estimatedDelivery'],
                'timestamp': datetime.utcnow().isoformat()
            }
        else:
            raise Exception(f"Shipping label creation failed: {shipping_result['error']}")
    
    except Exception as e:
        print(f"Error creating shipping label: {e}")
        raise Exception(f"Shipping label creation failed: {str(e)}")

def check_shipping_status_handler(event, context):
    """Check shipping status"""
    
    order_id = event['orderId']
    
    print(f"Checking shipping status for order {order_id}")
    
    try:
        # Get shipping record
        dynamodb = boto3.resource('dynamodb')
        shipping_table = dynamodb.Table('ShippingRecords')
        
        response = shipping_table.get_item(
            Key={'orderId': order_id}
        )
        
        if 'Item' not in response:
            return {
                'status': 'NOT_FOUND',
                'error': 'Shipping record not found'
            }
        
        shipping_record = response['Item']
        tracking_number = shipping_record['trackingNumber']
        
        # Check with shipping carrier
        carrier_status = check_carrier_status(tracking_number)
        
        # Update shipping record
        shipping_table.update_item(
            Key={'orderId': order_id},
            UpdateExpression='SET #status = :status, lastChecked = :timestamp',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': carrier_status['status'],
                ':timestamp': datetime.utcnow().isoformat()
            }
        )
        
        return {
            'status': carrier_status['status'],
            'trackingNumber': tracking_number,
            'location': carrier_status.get('location'),
            'estimatedDelivery': carrier_status.get('estimatedDelivery'),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        print(f"Error checking shipping status: {e}")
        raise Exception(f"Shipping status check failed: {str(e)}")

# Helper functions
def check_inventory_availability(items):
    """Check if all items are available in inventory"""
    dynamodb = boto3.resource('dynamodb')
    inventory_table = dynamodb.Table('Inventory')
    
    for item in items:
        response = inventory_table.get_item(
            Key={'productId': item['productId']}
        )
        
        if 'Item' not in response:
            return False
        
        available_qty = response['Item']['availableQuantity']
        if available_qty < item['quantity']:
            return False
    
    return True

def call_payment_gateway(payment_method, amount):
    """Mock payment gateway call"""
    # In real implementation, this would call actual payment processor
    if amount > 10000:  # Mock: amounts over $10,000 fail
        return {
            'success': False,
            'error': 'Amount exceeds daily limit'
        }
    
    return {
        'success': True,
        'transactionId': f"TXN{uuid.uuid4().hex[:8].upper()}"
    }

def store_payment_record(order_id, payment_id, amount, status):
    """Store payment record in database"""
    dynamodb = boto3.resource('dynamodb')
    payments_table = dynamodb.Table('PaymentRecords')
    
    payments_table.put_item(
        Item={
            'paymentId': payment_id,
            'orderId': order_id,
            'amount': amount,
            'status': status,
            'timestamp': datetime.utcnow().isoformat()
        }
    )

def call_shipping_service(order_id, address, tracking_number):
    """Mock shipping service call"""
    # In real implementation, this would call actual shipping API
    return {
        'success': True,
        'labelUrl': f"https://shipping.example.com/labels/{tracking_number}.pdf",
        'estimatedDelivery': '2023-07-20'
    }

def store_shipping_record(order_id, tracking_number, address):
    """Store shipping record in database"""
    dynamodb = boto3.resource('dynamodb')
    shipping_table = dynamodb.Table('ShippingRecords')
    
    shipping_table.put_item(
        Item={
            'orderId': order_id,
            'trackingNumber': tracking_number,
            'address': address,
            'status': 'LABEL_CREATED',
            'timestamp': datetime.utcnow().isoformat()
        }
    )

def check_carrier_status(tracking_number):
    """Mock carrier status check"""
    # In real implementation, this would call carrier API
    import random
    
    statuses = ['LABEL_CREATED', 'PICKED_UP', 'IN_TRANSIT', 'SHIPPED', 'DELIVERED']
    return {
        'status': random.choice(statuses),
        'location': 'Distribution Center',
        'estimatedDelivery': '2023-07-22'
    }

# Custom exception classes for Step Functions error handling
class PaymentInsufficientFundsError(Exception):
    pass

class PaymentProcessorError(Exception):
    pass
        ''', language='python')
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<div class="code-container">', unsafe_allow_html=True)
        st.code('''
# Advanced Step Functions patterns and integrations
import boto3
import json
from datetime import datetime

def create_advanced_workflow():
    """Create Step Functions workflow with advanced patterns"""
    
    stepfunctions = boto3.client('stepfunctions')
    
    # Advanced workflow with Map state, Callback pattern, and nested workflows
    advanced_definition = {
        "Comment": "Advanced data processing workflow with Map state",
        "StartAt": "PreprocessData",
        "States": {
            "PreprocessData": {
                "Type": "Task",
                "Resource": "arn:aws:lambda:us-east-1:123456789012:function:PreprocessData",
                "Next": "ProcessBatchItems",
                "ResultPath": "$.preprocessing"
            },
            
            "ProcessBatchItems": {
                "Type": "Map",
                "Comment": "Process each item in the batch",
                "ItemsPath": "$.preprocessing.items",
                "MaxConcurrency": 5,
                "Parameters": {
                    "item.$": "$$.Map.Item.Value",
                    "batchId.$": "$.batchId"
                },
                "Iterator": {
                    "StartAt": "ProcessSingleItem",
                    "States": {
                        "ProcessSingleItem": {
                            "Type": "Task",
                            "Resource": "arn:aws:lambda:us-east-1:123456789012:function:ProcessItem",
                            "Retry": [
                                {
                                    "ErrorEquals": ["States.TaskFailed"],
                                    "IntervalSeconds": 2,
                                    "MaxAttempts": 3,
                                    "BackoffRate": 2.0
                                }
                            ],
                            "Next": "ItemProcessed"
                        },
                        "ItemProcessed": {
                            "Type": "Succeed"
                        }
                    }
                },
                "ResultPath": "$.processedItems",
                "Next": "WaitForApproval"
            },
            
            "WaitForApproval": {
                "Type": "Task",
                "Resource": "arn:aws:states:::lambda:invoke.waitForTaskToken",
                "Parameters": {
                    "FunctionName": "arn:aws:lambda:us-east-1:123456789012:function:RequestApproval",
                    "Payload": {
                        "batchId.$": "$.batchId",
                        "processedCount.$": "States.ArrayLength($.processedItems)",
                        "taskToken.$": "$$.Task.Token"
                    }
                },
                "TimeoutSeconds": 3600,
                "Next": "CheckApprovalResult",
                "Catch": [
                    {
                        "ErrorEquals": ["States.Timeout"],
                        "Next": "ApprovalTimeout"
                    }
                ]
            },
            
            "CheckApprovalResult": {
                "Type": "Choice",
                "Choices": [
                    {
                        "Variable": "$.approvalResult.approved",
                        "BooleanEquals": true,
                        "Next": "ExecuteNestedWorkflow"
                    }
                ],
                "Default": "ApprovalRejected"
            },
            
            "ExecuteNestedWorkflow": {
                "Type": "Task",
                "Resource": "arn:aws:states:::states:startExecution.sync",
                "Parameters": {
                    "StateMachineArn": "arn:aws:states:us-east-1:123456789012:stateMachine:DataValidationWorkflow",
                    "Input": {
                        "batchId.$": "$.batchId",
                        "processedItems.$": "$.processedItems"
                    }
                },
                "ResultPath": "$.validationResult",
                "Next": "FinalizeProcessing",
                "Catch": [
                    {
                        "ErrorEquals": ["States.ExecutionFailed"],
                        "Next": "ValidationFailed",
                        "ResultPath": "$.error"
                    }
                ]
            },
            
            "FinalizeProcessing": {
                "Type": "Parallel",
                "Comment": "Finalize processing in parallel",
                "Branches": [
                    {
                        "StartAt": "UpdateDatabase",
                        "States": {
                            "UpdateDatabase": {
                                "Type": "Task",
                                "Resource": "arn:aws:states:::dynamodb:putItem",
                                "Parameters": {
                                    "TableName": "ProcessingResults",
                                    "Item": {
                                        "batchId": {"S.$": "$.batchId"},
                                        "status": {"S": "COMPLETED"},
                                        "processedCount": {"N.$": "States.Format('{}', States.ArrayLength($.processedItems))"},
                                        "completedAt": {"S.$": "$$.State.EnteredTime"}
                                    }
                                },
                                "End": true
                            }
                        }
                    },
                    {
                        "StartAt": "SendNotification",
                        "States": {
                            "SendNotification": {
                                "Type": "Task",
                                "Resource": "arn:aws:states:::sns:publish",
                                "Parameters": {
                                    "TopicArn": "arn:aws:sns:us-east-1:123456789012:processing-complete",
                                    "Message": {
                                        "batchId.$": "$.batchId",
                                        "status": "Processing completed successfully",
                                        "processedCount.$": "States.ArrayLength($.processedItems)",
                                        "completedAt.$": "$$.State.EnteredTime"
                                    }
                                },
                                "End": true
                            }
                        }
                    }
                ],
                "Next": "ProcessingCompleted"
            },
            
            "ProcessingCompleted": {
                "Type": "Succeed",
                "Comment": "Processing completed successfully"
            },
            
            "ApprovalTimeout": {
                "Type": "Task",
                "Resource": "arn:aws:states:::sns:publish",
                "Parameters": {
                    "TopicArn": "arn:aws:sns:us-east-1:123456789012:approval-timeout",
                    "Message": "Approval request timed out",
                    "Subject": "Workflow Approval Timeout"
                },
                "Next": "ProcessingFailed"
            },
            
            "ApprovalRejected": {
                "Type": "Task",
                "Resource": "arn:aws:states:::sns:publish",
                "Parameters": {
                    "TopicArn": "arn:aws:sns:us-east-1:123456789012:approval-rejected",
                    "Message": "Processing request was rejected",
                    "Subject": "Workflow Approval Rejected"
                },
                "Next": "ProcessingFailed"
            },
            
            "ValidationFailed": {
                "Type": "Task",
                "Resource": "arn:aws:states:::sns:publish",
                "Parameters": {
                    "TopicArn": "arn:aws:sns:us-east-1:123456789012:validation-failed",
                    "Message.$": "$.error",
                    "Subject": "Data Validation Failed"
                },
                "Next": "ProcessingFailed"
            },
            
            "ProcessingFailed": {
                "Type": "Fail",
                "Comment": "Processing failed"
            }
        }
    }
    
    try:
        response = stepfunctions.create_state_machine(
            name='AdvancedDataProcessingWorkflow',
            definition=json.dumps(advanced_definition),
            roleArn='arn:aws:iam::123456789012:role/StepFunctionsExecutionRole',
            type='STANDARD',
            tags=[
                {'key': 'Environment', 'value': 'Production'},
                {'key': 'Application', 'value': 'DataProcessing'}
            ]
        )
        
        print(f"✅ Created state machine: {response['stateMachineArn']}")
        return response['stateMachineArn']
    
    except Exception as e:
        print(f"❌ Error creating state machine: {e}")
        return None

def request_approval_handler(event, context):
    """Lambda function that requests approval and waits for callback"""
    
    batch_id = event['batchId']
    processed_count = event['processedCount']
    task_token = event['taskToken']
    
    print(f"Requesting approval for batch {batch_id} with {processed_count} items")
    
    # Store task token for later callback
    dynamodb = boto3.resource('dynamodb')
    approvals_table = dynamodb.Table('PendingApprovals')
    
    approvals_table.put_item(
        Item={
            'batchId': batch_id,
            'taskToken': task_token,
            'processedCount': processed_count,
            'requestedAt': datetime.utcnow().isoformat(),
            'status': 'PENDING'
        }
    )
    
    # Send approval request email
    ses = boto3.client('ses')
    
    approval_url = f"https://approval.example.com/approve?batchId={batch_id}"
    
    email_body = f"""
    A batch processing job requires your approval:
    
    Batch ID: {batch_id}
    Processed Items: {processed_count}
    
    Please review and approve or reject:
    {approval_url}
    """
    
    try:
        ses.send_email(
            Source='approval@example.com',
            Destination={'ToAddresses': ['approver@example.com']},
            Message={
                'Subject': {'Data': f'Approval Required: Batch {batch_id}'},
                'Body': {'Text': {'Data': email_body}}
            }
        )
        
        print(f"✅ Approval request sent for batch {batch_id}")
        
        # Don't return anything - Step Functions will wait for callback
        
    except Exception as e:
        print(f"❌ Error sending approval request: {e}")
        # Send failure callback
        stepfunctions = boto3.client('stepfunctions')
        stepfunctions.send_task_failure(
            taskToken=task_token,
            error='ApprovalRequestFailed',
            cause=str(e)
        )

def process_approval_response(event, context):
    """API Gateway handler for approval responses"""
    
    # This would be called by approval web interface
    batch_id = event['pathParameters']['batchId']
    approval_decision = json.loads(event['body'])
    
    approved = approval_decision['approved']
    reason = approval_decision.get('reason', '')
    
    print(f"Processing approval response for batch {batch_id}: {approved}")
    
    # Get task token
    dynamodb = boto3.resource('dynamodb')
    approvals_table = dynamodb.Table('PendingApprovals')
    
    try:
        response = approvals_table.get_item(Key={'batchId': batch_id})
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Approval request not found'})
            }
        
        approval_record = response['Item']
        task_token = approval_record['taskToken']
        
        # Send callback to Step Functions
        stepfunctions = boto3.client('stepfunctions')
        
        if approved:
            stepfunctions.send_task_success(
                taskToken=task_token,
                output=json.dumps({
                    'approvalResult': {
                        'approved': True,
                        'approvedBy': approval_decision.get('approvedBy', 'unknown'),
                        'approvedAt': datetime.utcnow().isoformat(),
                        'reason': reason
                    }
                })
            )
        else:
            stepfunctions.send_task_success(
                taskToken=task_token,
                output=json.dumps({
                    'approvalResult': {
                        'approved': False,
                        'rejectedBy': approval_decision.get('rejectedBy', 'unknown'),
                        'rejectedAt': datetime.utcnow().isoformat(),
                        'reason': reason
                    }
                })
            )
        
        # Update approval record
        approvals_table.update_item(
            Key={'batchId': batch_id},
            UpdateExpression='SET #status = :status, respondedAt = :timestamp',
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={
                ':status': 'APPROVED' if approved else 'REJECTED',
                ':timestamp': datetime.utcnow().isoformat()
            }
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Approval {"granted" if approved else "rejected"} for batch {batch_id}'
            })
        }
    
    except Exception as e:
        print(f"❌ Error processing approval response: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def start_workflow_execution():
    """Start the advanced workflow execution"""
    
    stepfunctions = boto3.client('stepfunctions')
    
    # Input data for the workflow
    input_data = {
        "batchId": f"batch-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
        "items": [
            {"id": "item-1", "data": "sample data 1"},
            {"id": "item-2", "data": "sample data 2"},
            {"id": "item-3", "data": "sample data 3"},
            {"id": "item-4", "data": "sample data 4"},
            {"id": "item-5", "data": "sample data 5"}
        ]
    }
    
    try:
        response = stepfunctions.start_execution(
            stateMachineArn='arn:aws:states:us-east-1:123456789012:stateMachine:AdvancedDataProcessingWorkflow',
            name=f"execution-{input_data['batchId']}",
            input=json.dumps(input_data)
        )
        
        execution_arn = response['executionArn']
        print(f"✅ Started workflow execution: {execution_arn}")
        
        return execution_arn
    
    except Exception as e:
        print(f"❌ Error starting workflow execution: {e}")
        return None

def monitor_workflow_execution(execution_arn):
    """Monitor workflow execution status"""
    
    stepfunctions = boto3.client('stepfunctions')
    
    try:
        response = stepfunctions.describe_execution(executionArn=execution_arn)
        
        status = response['status']
        started_at = response['startDate']
        
        print(f"Execution Status: {status}")
        print(f"Started At: {started_at}")
        
        if status in ['SUCCEEDED', 'FAILED', 'TIMED_OUT', 'ABORTED']:
            stopped_at = response.get('stopDate')
            print(f"Stopped At: {stopped_at}")
            
            if 'output' in response:
                output = json.loads(response['output'])
                print(f"Output: {json.dumps(output, indent=2)}")
        
        return response
    
    except Exception as e:
        print(f"❌ Error monitoring execution: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Create the advanced workflow
    state_machine_arn = create_advanced_workflow()
    
    if state_machine_arn:
        # Start execution
        execution_arn = start_workflow_execution()
        
        if execution_arn:
            # Monitor execution
            monitor_workflow_execution(execution_arn)
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
    # ⚡ AWS Development with Services
    
    """)
    st.markdown("""<div class="info-box">
                Master AWS serverless and server-based architectures through hands-on exploration of API Gateway, Lambda, DynamoDB, and Step Functions. Learn to build scalable, cost-effective applications using modern cloud-native patterns and best practices.
                </div>""", unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏗️ Server-Based vs Serverless", 
        "🌐 Amazon API Gateway", 
        "⚡ AWS Lambda",
        "🗃️ Amazon DynamoDB",
        "🔄 AWS Step Functions"
    ])
    
    with tab1:
        architecture_comparison_tab()
    
    with tab2:
        api_gateway_tab()
    
    with tab3:
        lambda_tab()
    
    with tab4:
        dynamodb_tab()
        
    with tab5:
        step_functions_tab()
    
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
