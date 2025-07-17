import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import utils.common as common
import utils.authenticate as authenticate
import json
from datetime import datetime, timedelta
import random

# Page configuration
st.set_page_config(
    page_title="AWS X-Ray Monitoring Hub",
    page_icon="🔍",
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
    'warning': '#FF6B35',
    'error': '#FF6B6B',
    'fault': '#E74C3C'
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
        
        .error-box {{
            background: linear-gradient(135deg, {AWS_COLORS['error']} 0%, {AWS_COLORS['fault']} 100%);
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
        
        .trace-segment {{
            background: white;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid {AWS_COLORS['success']};
            margin: 10px 0;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }}
        
        .error-segment {{
            background: white;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid {AWS_COLORS['error']};
            margin: 10px 0;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }}
        
        .fault-segment {{
            background: white;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid {AWS_COLORS['fault']};
            margin: 10px 0;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
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
            - 🔍 AWS X-Ray - Introduction to distributed tracing
            - 🧩 Key Concepts - Traces, segments, subsegments, and annotations
            - ⚠️ Errors, Faults & Exceptions - Error tracking and categorization
            
            **Learning Objectives:**
            - Understand distributed application tracing
            - Learn X-Ray core concepts and terminology
            - Master error tracking and debugging techniques
            - Practice with interactive examples and trace analysis
            """)

def create_xray_overview_mermaid():
    """Create mermaid diagram for X-Ray overview"""
    return """
    graph TB
        A[👤 User Request] --> B[🌐 Application Load Balancer]
        B --> C[💻 EC2 Instance - Web App]
        C --> D[🗃️ DynamoDB Table]
        C --> E[📦 S3 Bucket]
        C --> F[🔄 Lambda Function]
        F --> G[📊 RDS Database]
        
        X[🔍 AWS X-Ray] -.-> B
        X -.-> C
        X -.-> D
        X -.-> E  
        X -.-> F
        X -.-> G
        
        style A fill:#4B9EDB,stroke:#232F3E,color:#fff
        style X fill:#FF9900,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#4B9EDB,stroke:#232F3E,color:#fff
        style E fill:#FF6B35,stroke:#232F3E,color:#fff
        style F fill:#232F3E,stroke:#FF9900,color:#fff
        style G fill:#3FB34F,stroke:#232F3E,color:#fff
    """

def create_trace_timeline_mermaid():
    """Create mermaid diagram for trace timeline"""
    return """
    gantt
        title X-Ray Trace Timeline
        dateFormat X
        axisFormat %L ms
        
        section Request Flow
        Load Balancer    :0, 5
        Web Application  :2, 45
        DynamoDB Query   :10, 25
        S3 File Upload   :15, 30
        Lambda Function  :35, 15
        Database Query   :38, 12
        
        section Response
        Response Assembly :45, 5
        Client Response   :48, 2
    """

def create_segment_subsegment_mermaid():
    """Create diagram showing segments and subsegments"""
    return """
    graph TD
        T[🎯 Trace: User Purchase Request] --> S1[📦 Segment: Web Application]
        
        S1 --> SS1[🔍 Subsegment: User Authentication]
        S1 --> SS2[🔍 Subsegment: Product Validation] 
        S1 --> SS3[🔍 Subsegment: Payment Processing]
        S1 --> SS4[🔍 Subsegment: Inventory Update]
        
        SS1 --> SSS1[📊 SQL: User Lookup]
        SS2 --> SSS2[🗃️ DynamoDB: Product Info]
        SS3 --> SSS3[💳 HTTP: Payment Gateway]
        SS4 --> SSS4[🔄 Lambda: Inventory Service]
        
        T --> S2[📦 Segment: Lambda Function]
        S2 --> SS5[🔍 Subsegment: Database Update]
        S2 --> SS6[🔍 Subsegment: Email Notification]
        
        style T fill:#FF9900,stroke:#232F3E,color:#fff
        style S1 fill:#4B9EDB,stroke:#232F3E,color:#fff
        style S2 fill:#4B9EDB,stroke:#232F3E,color:#fff
        style SS1 fill:#3FB34F,stroke:#232F3E,color:#fff
        style SS2 fill:#3FB34F,stroke:#232F3E,color:#fff
        style SS3 fill:#3FB34F,stroke:#232F3E,color:#fff
        style SS4 fill:#3FB34F,stroke:#232F3E,color:#fff
        style SS5 fill:#3FB34F,stroke:#232F3E,color:#fff
        style SS6 fill:#3FB34F,stroke:#232F3E,color:#fff
    """

def create_error_classification_mermaid():
    """Create diagram for error classification"""
    return """
    graph TD
        A[📊 HTTP Response Codes] --> B[4xx Client Errors]
        A --> C[5xx Server Errors]
        A --> D[429 Throttling]
        
        B --> E[🚫 Error - Client Issues]
        C --> F[⚠️ Fault - Server Issues]
        D --> G[🔄 Throttle - Rate Limiting]
        
        E --> E1[400 Bad Request]
        E --> E2[401 Unauthorized]
        E --> E3[403 Forbidden]
        E --> E4[404 Not Found]
        
        F --> F1[500 Internal Server Error]
        F --> F2[502 Bad Gateway]
        F --> F3[503 Service Unavailable]
        F --> F4[504 Gateway Timeout]
        
        G --> G1[429 Too Many Requests]
        
        style A fill:#FF9900,stroke:#232F3E,color:#fff
        style E fill:#FF6B35,stroke:#232F3E,color:#fff
        style F fill:#E74C3C,stroke:#232F3E,color:#fff
        style G fill:#F39C12,stroke:#232F3E,color:#fff
    """

def aws_xray_tab():
    """Content for AWS X-Ray tab"""
    st.markdown("## 🔍 AWS X-Ray")
    st.markdown("*Distributed tracing service for analyzing and debugging distributed applications*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 What is AWS X-Ray?
    **AWS X-Ray** is a service that collects data about requests that your application serves, and provides tools 
    that you can use to view, filter, and gain insights into that data to identify issues and opportunities for optimization.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # X-Ray Benefits
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🔍\n**Trace Requests**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🐛\n**Debug Issues**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### ⚡\n**Optimize Performance**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 📊\n**Service Map**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # X-Ray Architecture Overview
    st.markdown("### 🏗️ X-Ray Architecture Overview")
    common.mermaid(create_xray_overview_mermaid(), height=300)
    
    # Interactive Application Scenario
    st.markdown("### 🎮 Interactive Application Tracing Scenario")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📱 Application Configuration")
        app_type = st.selectbox("Application Type:", [
            "E-commerce Website", "REST API Service", "Microservices App", 
            "Mobile Backend", "Data Processing Pipeline"
        ])
        
        complexity = st.slider("Application Complexity:", 1, 10, 5)
        expected_traffic = st.selectbox("Expected Traffic:", [
            "Low (< 1K requests/day)", "Medium (1K-100K requests/day)", 
            "High (100K-1M requests/day)", "Very High (> 1M requests/day)"
        ])
    
    with col2:
        st.markdown("### 🔧 X-Ray Configuration")
        sampling_rate = st.slider("Sampling Rate (%):", 1, 100, 10)
        trace_retention = st.selectbox("Trace Retention:", [
            "30 days (default)", "Custom (up to 30 days)"
        ])
        
        enable_insights = st.checkbox("Enable X-Ray Insights", value=True)
        enable_analytics = st.checkbox("Enable X-Ray Analytics", value=False)
    
    if st.button("🚀 Enable X-Ray Tracing", use_container_width=True):
        # Simulate X-Ray setup
        estimated_traces = {
            "Low": 100,
            "Medium": 10000, 
            "High": 100000,
            "Very High": 1000000
        }
        
        daily_traces = estimated_traces.get(expected_traffic.split()[0], 1000)
        sampled_traces = int(daily_traces * (sampling_rate / 100))
        monthly_cost = sampled_traces * 30 * 0.000005  # $5 per million traces
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ X-Ray Tracing Enabled!
        
        **Configuration Summary:**
        - **Application**: {app_type}
        - **Complexity Level**: {complexity}/10
        - **Sampling Rate**: {sampling_rate}%
        - **Daily Traces**: {daily_traces:,} → {sampled_traces:,} sampled
        
        **Features Enabled:**
        - **Insights**: {'✅ Yes' if enable_insights else '❌ No'}
        - **Analytics**: {'✅ Yes' if enable_analytics else '❌ No'}
        - **Retention**: {trace_retention}
        
        💰 **Estimated Monthly Cost**: ${monthly_cost:.2f}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # X-Ray Benefits and Use Cases
    st.markdown("### ✨ X-Ray Benefits & Use Cases")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔍 Debugging & Troubleshooting
        - **End-to-end request tracing**
        - Identify bottlenecks and latency
        - Root cause analysis
        - **Performance optimization**
        
        **Perfect for:**
        - Complex microservices
        - Intermittent issues
        - Performance problems
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📊 Application Insights
        - **Service dependency mapping**
        - Response time analysis
        - Error rate monitoring
        - **Traffic pattern analysis**
        
        **Perfect for:**
        - Understanding architecture
        - Capacity planning
        - SLA monitoring
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🛠️ Development & Operations
        - **Code-level visibility**
        - Integration testing
        - Deployment validation
        - **Production monitoring**
        
        **Perfect for:**
        - DevOps teams
        - Performance testing
        - Production support
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Supported Services
    st.markdown("### 🛠️ AWS Services with X-Ray Integration")
    
    services_data = {
        'Service Category': ['Compute', 'Compute', 'Storage', 'Database', 'Integration', 'Analytics'],
        'AWS Service': ['Amazon EC2', 'AWS Lambda', 'Amazon S3', 'Amazon DynamoDB', 'Amazon API Gateway', 'Amazon Kinesis'],
        'Integration Type': ['SDK/Agent', 'Built-in', 'SDK', 'Built-in', 'Built-in', 'SDK'],
        'Tracing Capability': ['Full', 'Full', 'Basic', 'Full', 'Full', 'Basic'],
        'Common Use Cases': [
            'Web applications, APIs',
            'Serverless functions', 
            'File operations tracking',
            'Database performance',
            'API request tracing',
            'Stream processing'
        ]
    }
    
    df_services = pd.DataFrame(services_data)
    st.dataframe(df_services, use_container_width=True)
    
    # Sample Trace Visualization
    st.markdown("### 📈 Sample Trace Timeline")
    
    # Create a sample trace timeline
    trace_data = {
        'Service': ['ALB', 'EC2 Web App', 'DynamoDB', 'S3', 'Lambda', 'RDS'],
        'Start_Time': [0, 5, 15, 20, 35, 40],
        'Duration': [5, 40, 10, 15, 10, 8],
        'Status': ['Success', 'Success', 'Success', 'Success', 'Success', 'Success']
    }
    
    df_trace = pd.DataFrame(trace_data)
    df_trace['End_Time'] = df_trace['Start_Time'] + df_trace['Duration']
    
    fig = px.timeline(df_trace, x_start='Start_Time', x_end='End_Time', y='Service', 
                      color='Status', title='Sample E-commerce Request Trace',
                      color_discrete_map={'Success': AWS_COLORS['success'], 'Error': AWS_COLORS['error']})
    
    fig.update_yaxes(categoryorder="array", categoryarray=df_trace['Service'].tolist()[::-1])
    fig.update_layout(height=300, xaxis_title="Time (milliseconds)")
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Getting Started Steps
    st.markdown("### 🚀 Getting Started with X-Ray")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📋 Setup Steps
        
        1. **Install X-Ray SDK** in your application
        2. **Configure sampling rules** for trace collection
        3. **Add instrumentation** to your code
        4. **Deploy X-Ray daemon** (for EC2/ECS)
        5. **Enable tracing** in AWS services
        6. **Set IAM permissions** for X-Ray
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔧 Best Practices
        
        - **Use appropriate sampling rates** (1-10% for production)
        - **Add meaningful annotations** and metadata
        - **Implement proper error handling**
        - **Monitor costs** with trace volumes
        - **Use service maps** for architecture understanding
        - **Set up alerts** for anomalies
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Basic X-Ray Implementation")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Basic X-Ray integration with Python Flask application
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
from aws_xray_sdk.flask.middleware import XRayMiddleware
from flask import Flask
import boto3
import requests

# Initialize Flask app
app = Flask(__name__)

# Configure X-Ray
xray_recorder.configure(
    context_missing='LOG_ERROR',
    plugins=('EC2Plugin', 'ECSPlugin'),
    daemon_address='127.0.0.1:2000',  # X-Ray daemon address
    sampling=True
)

# Enable X-Ray middleware for Flask
XRayMiddleware(app, xray_recorder)

# Patch AWS SDK calls for automatic tracing
patch_all()

# Initialize AWS clients (automatically traced)
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

@app.route('/api/users/<user_id>')
@xray_recorder.capture('get_user_profile')
def get_user_profile(user_id):
    """Get user profile with X-Ray tracing"""
    
    # Add custom annotation for filtering
    xray_recorder.put_annotation('user_id', user_id)
    xray_recorder.put_annotation('operation', 'get_user_profile')
    
    # Add metadata for additional context
    xray_recorder.put_metadata('request_info', {
        'endpoint': '/api/users',
        'method': 'GET',
        'user_agent': request.headers.get('User-Agent', 'Unknown')
    })
    
    try:
        # Database query (automatically traced)
        with xray_recorder.in_subsegment('database_query'):
            table = dynamodb.Table('Users')
            response = table.get_item(Key={'user_id': user_id})
            
            if 'Item' not in response:
                xray_recorder.put_annotation('user_found', False)
                return {'error': 'User not found'}, 404
            
            user_data = response['Item']
            xray_recorder.put_annotation('user_found', True)
        
        # S3 operation for profile image (automatically traced)
        with xray_recorder.in_subsegment('s3_profile_image'):
            try:
                profile_image_url = s3.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': 'user-profiles', 'Key': f'{user_id}/avatar.jpg'},
                    ExpiresIn=3600
                )
                user_data['profile_image_url'] = profile_image_url
                
            except Exception as e:
                # Log error but don't fail the request
                xray_recorder.put_metadata('s3_error', str(e))
                user_data['profile_image_url'] = None
        
        # External API call with manual subsegment
        with xray_recorder.in_subsegment('external_api_call') as subsegment:
            try:
                # Add subsegment metadata
                subsegment.put_metadata('api_endpoint', 'https://api.external-service.com')
                
                response = requests.get(
                    f'https://api.external-service.com/users/{user_id}/preferences',
                    timeout=2.0
                )
                
                if response.status_code == 200:
                    user_data['preferences'] = response.json()
                    subsegment.put_annotation('api_success', True)
                else:
                    subsegment.put_annotation('api_success', False)
                    subsegment.put_annotation('api_status_code', response.status_code)
                    
            except requests.exceptions.Timeout:
                # Handle timeout gracefully
                subsegment.add_exception(Exception('API timeout'))
                subsegment.put_annotation('api_timeout', True)
                user_data['preferences'] = {}
            
            except Exception as e:
                # Record exception in X-Ray
                subsegment.add_exception(e)
                user_data['preferences'] = {}
        
        # Add final annotations
        xray_recorder.put_annotation('response_size', len(str(user_data)))
        xray_recorder.put_annotation('success', True)
        
        return user_data
        
    except Exception as e:
        # Record error details
        xray_recorder.put_annotation('success', False)
        xray_recorder.put_annotation('error_type', type(e).__name__)
        
        # Add exception to current segment
        xray_recorder.current_segment().add_exception(e)
        
        return {'error': 'Internal server error'}, 500

@app.route('/api/health')
@xray_recorder.capture('health_check')
def health_check():
    """Simple health check endpoint"""
    
    xray_recorder.put_annotation('endpoint', 'health_check')
    
    # Check dependencies
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'checks': {}
    }
    
    # Check DynamoDB connectivity
    with xray_recorder.in_subsegment('dynamodb_health_check'):
        try:
            dynamodb.meta.client.describe_table(TableName='Users')
            health_status['checks']['dynamodb'] = 'healthy'
            xray_recorder.put_annotation('dynamodb_healthy', True)
        except Exception as e:
            health_status['checks']['dynamodb'] = 'unhealthy'
            health_status['status'] = 'degraded'
            xray_recorder.put_annotation('dynamodb_healthy', False)
    
    # Check S3 connectivity  
    with xray_recorder.in_subsegment('s3_health_check'):
        try:
            s3.head_bucket(Bucket='user-profiles')
            health_status['checks']['s3'] = 'healthy'
            xray_recorder.put_annotation('s3_healthy', True)
        except Exception as e:
            health_status['checks']['s3'] = 'unhealthy'
            health_status['status'] = 'degraded'
            xray_recorder.put_annotation('s3_healthy', False)
    
    xray_recorder.put_annotation('overall_health', health_status['status'])
    
    return health_status

# Custom X-Ray middleware for additional context
@app.before_request
def before_request():
    """Add request context to X-Ray traces"""
    segment = xray_recorder.current_segment()
    if segment:
        segment.put_annotation('request_path', request.path)
        segment.put_annotation('request_method', request.method)
        segment.put_metadata('request_headers', dict(request.headers))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def xray_key_concepts_tab():
    """Content for AWS X-Ray Key Concepts tab"""
    st.markdown("## 🧩 AWS X-Ray - Key Concepts")
    st.markdown("*Understanding traces, segments, subsegments, and service maps for effective distributed tracing*")
    
    # Key concept overview
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Core X-Ray Concepts
    X-Ray uses a hierarchical data model to represent distributed requests, providing detailed insights 
    into how your application processes requests and interacts with downstream resources.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Concept Hierarchy Visualization
    st.markdown("### 🏗️ X-Ray Data Model Hierarchy")
    common.mermaid(create_segment_subsegment_mermaid(), height=400)
    
    # Interactive Concept Explorer
    st.markdown("### 🔍 Interactive Concept Explorer")
    
    concepts = {
        "Trace": {
            "definition": "A trace ID tracks the path of a request through your application",
            "characteristics": [
                "End-to-end view of a request",
                "Unique identifier across all services", 
                "Contains one or more segments",
                "Shows complete request journey"
            ],
            "example": "A user purchasing an item - from web request to database update",
            "duration": "Entire request lifecycle"
        },
        "Segment": {
            "definition": "A segment represents work done by a single service component",
            "characteristics": [
                "Service-level granularity",
                "Contains timing information",
                "Includes service name and version",
                "Can contain multiple subsegments"
            ],
            "example": "Web application processing, Lambda function execution",
            "duration": "Time spent in one service/component"
        },
        "Subsegment": {
            "definition": "A subsegment provides more granular timing information about a segment",
            "characteristics": [
                "Function or operation level detail",
                "Shows specific work within a segment",
                "Can be nested for complex operations",
                "Provides detailed performance metrics"
            ],
            "example": "Database query, HTTP API call, file operation",
            "duration": "Time for specific operation"
        },
        "Annotation": {
            "definition": "Annotations are indexed key-value pairs for filtering and grouping traces",
            "characteristics": [
                "Searchable and filterable",
                "Limited to simple data types",
                "Used for trace queries",
                "Maximum 50 annotations per trace"
            ],
            "example": "user_id=12345, error_type=timeout, api_version=v2",
            "duration": "N/A - metadata only"
        },
        "Metadata": {
            "definition": "Metadata provides additional context but is not indexed for searching",
            "characteristics": [
                "Rich data structures allowed",
                "Not searchable via X-Ray console",
                "Useful for debugging context",
                "No limits on data types"
            ],
            "example": "Request headers, response bodies, configuration details",
            "duration": "N/A - contextual data only"
        }
    }
    
    selected_concept = st.selectbox("Select a concept to explore:", list(concepts.keys()))
    
    if selected_concept:
        concept_data = concepts[selected_concept]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown(f"""
            ### 📖 {selected_concept} Definition
            
            {concept_data['definition']}
            
            **Duration Scope:** {concept_data['duration']}
            
            **Real-world Example:**
            {concept_data['example']}
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="concept-card">', unsafe_allow_html=True)
            st.markdown(f"""
            ### ✨ Key Characteristics
            """)
            for char in concept_data['characteristics']:
                st.markdown(f"- {char}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Trace Builder
    st.markdown("### 🛠️ Interactive Trace Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Scenario Configuration")
        scenario_type = st.selectbox("Application Scenario:", [
            "E-commerce Purchase", "User Authentication", "File Upload Process",
            "API Data Aggregation", "Batch Data Processing"
        ])
        
        include_errors = st.checkbox("Include Error Scenarios", value=False)
        trace_complexity = st.slider("Trace Complexity (1-10):", 1, 10, 5)
    
    with col2:
        st.markdown("### ⚙️ Tracing Options")
        enable_subsegments = st.checkbox("Show Subsegments", value=True)
        include_annotations = st.checkbox("Add Annotations", value=True)
        include_metadata = st.checkbox("Include Metadata", value=False)
    
    if st.button("🔍 Generate Sample Trace", use_container_width=True):
        # Generate sample trace data based on selections
        if scenario_type == "E-commerce Purchase":
            services = ["Web App", "Auth Service", "Product Service", "Payment Gateway", "Inventory Service", "Notification Service"]
            base_latencies = [45, 12, 18, 120, 25, 8]
        elif scenario_type == "User Authentication":
            services = ["API Gateway", "Lambda Auth", "DynamoDB", "Cognito"]
            base_latencies = [5, 15, 8, 12]
        else:
            services = ["Load Balancer", "Web Server", "Database", "Cache", "External API"]
            base_latencies = [3, 25, 15, 2, 85]
        
        # Apply complexity factor
        latencies = [int(latency * (1 + trace_complexity * 0.1)) for latency in base_latencies]
        
        # Create trace visualization
        cumulative_time = 0
        trace_segments = []
        
        for i, (service, latency) in enumerate(zip(services, latencies)):
            status = "Error" if include_errors and i == len(services) - 2 else "Success"
            
            trace_segments.append({
                'Service': service,
                'Start': cumulative_time,
                'Duration': latency,
                'Status': status,
                'End': cumulative_time + latency
            })
            
            if i < len(services) - 1:  # Don't add gap after last service
                cumulative_time += latency + random.randint(1, 5)  # Small gap between services
        
        df_trace = pd.DataFrame(trace_segments)
        
        # Create timeline chart
        fig = px.timeline(df_trace, x_start='Start', x_end='End', y='Service', 
                         color='Status', title=f'Generated Trace: {scenario_type}',
                         color_discrete_map={'Success': AWS_COLORS['success'], 'Error': AWS_COLORS['error']})
        
        fig.update_yaxes(categoryorder="array", categoryarray=df_trace['Service'].tolist()[::-1])
        fig.update_layout(height=300, xaxis_title="Time (milliseconds)")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show trace details
        total_time = df_trace['End'].max()
        error_count = len(df_trace[df_trace['Status'] == 'Error'])
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 📊 Trace Analysis Results
        
        **Trace Summary:**
        - **Total Duration**: {total_time:.0f}ms
        - **Services Involved**: {len(services)}
        - **Error Count**: {error_count}
        - **Success Rate**: {((len(services) - error_count) / len(services) * 100):.1f}%
        
        **Performance Insights:**
        - **Slowest Service**: {df_trace.loc[df_trace['Duration'].idxmax(), 'Service']} ({df_trace['Duration'].max()}ms)
        - **Critical Path**: {' → '.join(services)}
        - **Bottleneck Impact**: {(df_trace['Duration'].max() / total_time * 100):.1f}% of total time
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show annotations and metadata if enabled
        if include_annotations:
            st.markdown("### 🏷️ Sample Annotations")
            annotations = {
                'user_id': '12345',
                'request_type': scenario_type.lower().replace(' ', '_'),
                'api_version': 'v2.1',
                'region': 'us-east-1',
                'error_present': str(error_count > 0).lower()
            }
            
            for key, value in annotations.items():
                st.code(f'xray_recorder.put_annotation("{key}", "{value}")')
        
        if include_metadata:
            st.markdown("### 📋 Sample Metadata")
            metadata = {
                'request_headers': {'user-agent': 'Mozilla/5.0', 'content-type': 'application/json'},
                'response_size': f'{random.randint(100, 5000)} bytes',
                'cache_status': random.choice(['HIT', 'MISS', 'REFRESH']),
                'database_query_count': random.randint(1, 8)
            }
            
            st.code(f'xray_recorder.put_metadata("request_context", {json.dumps(metadata, indent=2)})')
    
    # Service Map Explanation
    st.markdown("### 🗺️ Service Maps")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📊 What are Service Maps?
        
        **Service Maps** provide a visual representation of your application's architecture:
        
        - **Nodes** represent services/resources
        - **Edges** show request/response flows  
        - **Colors** indicate health status
        - **Numbers** show response times and throughput
        
        **Benefits:**
        - Understand application dependencies
        - Identify performance bottlenecks
        - Visualize error propagation
        - Monitor service health
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 Service Map Use Cases
        
        **Architecture Understanding:**
        - New team member onboarding
        - System documentation
        - Dependency analysis
        
        **Operations & Monitoring:**
        - Health status overview
        - Performance monitoring  
        - Incident response
        
        **Development & Planning:**
        - Impact analysis for changes
        - Capacity planning
        - Service decomposition decisions
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Best Practices
    st.markdown("### 💡 X-Ray Best Practices")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🏷️ Annotations Best Practices
        
        **Do:**
        - Use for filtering and grouping
        - Keep values simple (string, number, boolean)
        - Include business-relevant data
        - Use consistent naming conventions
        
        **Don't:**
        - Exceed 50 annotations per trace
        - Include high-cardinality values
        - Store large data structures
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📋 Metadata Best Practices
        
        **Do:**
        - Use for rich debugging context
        - Include request/response data
        - Add configuration details
        - Store complex data structures
        
        **Don't:**
        - Include sensitive information
        - Store excessive amounts of data
        - Depend on metadata for filtering
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🚀 Performance Best Practices
        
        **Do:**
        - Use appropriate sampling rates
        - Implement async tracing
        - Cache segment creation
        - Monitor X-Ray overhead
        
        **Don't:**
        - Trace every request in production
        - Create excessive subsegments
        - Block on X-Ray operations
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Advanced X-Ray Concepts")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Advanced X-Ray concepts: Annotations, Metadata, and Custom Segments
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core.models import subsegment
import json
import time
import boto3

@xray_recorder.capture('advanced_trace_example')
def process_user_order(order_data):
    """
    Comprehensive example showing X-Ray concepts in action
    """
    
    # Add annotations for filtering and grouping traces
    xray_recorder.put_annotation('user_id', order_data['user_id'])
    xray_recorder.put_annotation('order_type', order_data['order_type'])
    xray_recorder.put_annotation('payment_method', order_data['payment_method'])
    xray_recorder.put_annotation('order_value', order_data['total_amount'])
    xray_recorder.put_annotation('api_version', '2.1')
    
    # Add metadata for debugging context (not searchable but rich data)
    xray_recorder.put_metadata('order_details', {
        'items': order_data['items'],
        'shipping_address': order_data['shipping_address'],
        'timestamp': time.time(),
        'request_source': 'web_frontend'
    })
    
    try:
        # Custom subsegment for user validation
        with xray_recorder.in_subsegment('user_validation') as subsegment:
            # Add subsegment-specific annotations
            subsegment.put_annotation('validation_type', 'user_auth')
            
            # Simulate user validation logic
            user_valid = validate_user(order_data['user_id'])
            
            if user_valid:
                subsegment.put_annotation('validation_result', 'success')
                subsegment.put_metadata('user_info', {
                    'membership_level': 'premium',
                    'account_age_days': 365,
                    'previous_orders': 12
                })
            else:
                subsegment.put_annotation('validation_result', 'failed')
                subsegment.put_annotation('failure_reason', 'invalid_user')
                raise ValueError("Invalid user")
        
        # Inventory check with detailed subsegments
        with xray_recorder.in_subsegment('inventory_management') as inventory_segment:
            inventory_segment.put_annotation('operation', 'inventory_check')
            
            # Check each item in the order
            for item in order_data['items']:
                with xray_recorder.in_subsegment(f'check_item_{item["sku"]}') as item_segment:
                    item_segment.put_annotation('sku', item['sku'])
                    item_segment.put_annotation('quantity_requested', item['quantity'])
                    
                    # Simulate inventory check
                    available_quantity = check_inventory(item['sku'])
                    item_segment.put_annotation('quantity_available', available_quantity)
                    
                    if available_quantity >= item['quantity']:
                        item_segment.put_annotation('inventory_status', 'sufficient')
                        
                        # Reserve inventory
                        reserve_inventory(item['sku'], item['quantity'])
                        item_segment.put_annotation('reservation_id', f"RES_{int(time.time())}")
                        
                    else:
                        item_segment.put_annotation('inventory_status', 'insufficient')
                        item_segment.put_annotation('shortage', item['quantity'] - available_quantity)
                        
                        # Add exception to subsegment
                        shortage_error = Exception(f"Insufficient inventory for {item['sku']}")
                        item_segment.add_exception(shortage_error)
                        raise shortage_error
            
            inventory_segment.put_annotation('all_items_available', True)
        
        # Payment processing with external service tracing
        with xray_recorder.in_subsegment('payment_processing') as payment_segment:
            payment_segment.put_annotation('payment_gateway', 'stripe')
            payment_segment.put_annotation('amount', order_data['total_amount'])
            payment_segment.put_annotation('currency', 'USD')
            
            # Add payment metadata
            payment_segment.put_metadata('payment_details', {
                'card_type': order_data.get('card_type', 'unknown'),
                'last_four': order_data.get('card_last_four', 'xxxx'),
                'billing_zip': order_data.get('billing_zip', 'unknown')
            })
            
            try:
                # Simulate payment processing
                payment_result = process_payment(order_data)
                
                payment_segment.put_annotation('payment_status', 'success')
                payment_segment.put_annotation('transaction_id', payment_result['transaction_id'])
                payment_segment.put_metadata('payment_response', payment_result)
                
            except PaymentException as e:
                payment_segment.put_annotation('payment_status', 'failed')
                payment_segment.put_annotation('failure_reason', str(e))
                payment_segment.add_exception(e)
                raise
        
        # Database operations for order creation
        with xray_recorder.in_subsegment('order_persistence') as db_segment:
            db_segment.put_annotation('operation', 'create_order')
            db_segment.put_annotation('table_name', 'Orders')
            
            # Create order record
            dynamodb = boto3.resource('dynamodb')
            orders_table = dynamodb.Table('Orders')
            
            order_record = {
                'order_id': f"ORD_{int(time.time())}",
                'user_id': order_data['user_id'],
                'items': order_data['items'],
                'total_amount': order_data['total_amount'],
                'status': 'confirmed',
                'created_at': int(time.time())
            }
            
            # Put item with automatic DynamoDB tracing
            orders_table.put_item(Item=order_record)
            
            db_segment.put_annotation('order_id', order_record['order_id'])
            db_segment.put_annotation('items_count', len(order_data['items']))
            db_segment.put_metadata('order_record', order_record)
        
        # Notification subsegment
        with xray_recorder.in_subsegment('send_confirmation') as notification_segment:
            notification_segment.put_annotation('notification_type', 'email')
            notification_segment.put_annotation('recipient', order_data['user_email'])
            
            # Send confirmation email (Lambda function call)
            lambda_client = boto3.client('lambda')
            
            notification_payload = {
                'order_id': order_record['order_id'],
                'user_email': order_data['user_email'],
                'order_total': order_data['total_amount']
            }
            
            lambda_response = lambda_client.invoke(
                FunctionName='send-order-confirmation',
                InvocationType='Event',  # Async
                Payload=json.dumps(notification_payload)
            )
            
            notification_segment.put_annotation('lambda_invoked', True)
            notification_segment.put_annotation('invocation_type', 'async')
            notification_segment.put_metadata('lambda_payload', notification_payload)
        
        # Final success annotations
        xray_recorder.put_annotation('order_processing_result', 'success')
        xray_recorder.put_annotation('processing_time_bucket', categorize_processing_time(time.time()))
        
        return {
            'status': 'success',
            'order_id': order_record['order_id'],
            'message': 'Order processed successfully'
        }
        
    except Exception as e:
        # Add error annotations and metadata
        xray_recorder.put_annotation('order_processing_result', 'error')
        xray_recorder.put_annotation('error_type', type(e).__name__)
        xray_recorder.put_annotation('error_stage', get_current_stage())
        
        # Add exception to current segment
        xray_recorder.current_segment().add_exception(e)
        
        # Add error metadata for debugging
        xray_recorder.put_metadata('error_context', {
            'order_data': order_data,
            'error_message': str(e),
            'timestamp': time.time()
        })
        
        # Re-raise for upstream handling
        raise

def validate_user(user_id):
    """Simulate user validation"""
    # Add some processing delay
    time.sleep(0.01)
    return user_id != 'invalid_user'

def check_inventory(sku):
    """Simulate inventory check"""
    time.sleep(0.005)
    return np.random.randint(0, 100)

def reserve_inventory(sku, quantity):
    """Simulate inventory reservation"""
    time.sleep(0.003)
    return True

def process_payment(order_data):
    """Simulate payment processing"""
    time.sleep(0.1)  # Simulate network call
    
    if order_data['payment_method'] == 'invalid_card':
        raise PaymentException("Invalid payment method")
    
    return {
        'transaction_id': f"TXN_{int(time.time())}",
        'status': 'approved',
        'amount_charged': order_data['total_amount']
    }

def categorize_processing_time(current_time):
    """Categorize processing time for analysis"""
    # This would use the actual start time
    processing_time = 0.5  # Simulated
    
    if processing_time < 0.1:
        return 'fast'
    elif processing_time < 0.5:
        return 'normal'
    else:
        return 'slow'

def get_current_stage():
    """Get current processing stage for error context"""
    # This would determine the current stage based on execution context
    return 'payment_processing'

class PaymentException(Exception):
    pass

# Example usage
if __name__ == "__main__":
    sample_order = {
        'user_id': 'user_12345',
        'user_email': 'customer@example.com',
        'order_type': 'regular',
        'payment_method': 'credit_card',
        'total_amount': 89.99,
        'items': [
            {'sku': 'PROD_001', 'quantity': 2, 'price': 29.99},
            {'sku': 'PROD_002', 'quantity': 1, 'price': 29.99}
        ],
        'shipping_address': {
            'street': '123 Main St',
            'city': 'Seattle',
            'state': 'WA',
            'zip': '98101'
        }
    }
    
    result = process_user_order(sample_order)
    print(f"Order processing result: {result}")
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def xray_errors_tab():
    """Content for AWS X-Ray Errors, Faults, and Exceptions tab"""
    st.markdown("## ⚠️ AWS X-Ray - Errors, Faults, and Exceptions")
    st.markdown("*Understanding and categorizing different types of errors for effective debugging*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Error Classification in X-Ray
    AWS X-Ray tracks errors that occur in your application code and errors returned by downstream services. 
    Understanding the different error categories helps you quickly identify and resolve issues in distributed applications.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Error Classification Diagram
    st.markdown("### 🏗️ Error Classification Hierarchy")
    common.mermaid(create_error_classification_mermaid(), height=350)
    
    # Error Types Overview
    st.markdown("### 📊 Error Types Overview")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="error-box">', unsafe_allow_html=True)
        st.markdown("""
        ### 🚫 Client Errors (4xx)
        **Status Code Range:** 400-499
        
        **What it means:**
        - Client made an invalid request
        - Authentication/authorization issues
        - Resource not found
        - Malformed request data
        
        **Common Examples:**
        - 400 Bad Request
        - 401 Unauthorized  
        - 403 Forbidden
        - 404 Not Found
        - 422 Unprocessable Entity
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="fault-segment">', unsafe_allow_html=True)
        st.markdown("""
        ### ⚠️ Server Faults (5xx)
        **Status Code Range:** 500-599
        
        **What it means:**
        - Server failed to process valid request
        - Internal application errors
        - Downstream service failures
        - Infrastructure issues
        
        **Common Examples:**
        - 500 Internal Server Error
        - 502 Bad Gateway
        - 503 Service Unavailable
        - 504 Gateway Timeout
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔄 Throttling Errors (429)
        **Status Code:** 429 Too Many Requests
        
        **What it means:**
        - Rate limiting in effect
        - Too many requests from client
        - Service capacity protection
        - Temporary restriction
        
        **Common Scenarios:**
        - API rate limits exceeded
        - DynamoDB throttling
        - Lambda concurrency limits
        - Custom rate limiting
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Error Simulator
    st.markdown("### 🎮 Interactive Error Analysis Simulator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔧 Error Scenario Configuration")
        error_scenario = st.selectbox("Select Error Scenario:", [
            "Database Connection Failure",
            "Invalid User Input", 
            "API Rate Limiting",
            "Downstream Service Timeout",
            "Authentication Failure",
            "Resource Not Found",
            "Payment Processing Error"
        ])
        
        error_frequency = st.slider("Error Rate (%):", 1, 50, 5)
        simulate_duration = st.selectbox("Simulation Duration:", [
            "1 hour", "6 hours", "24 hours", "1 week"
        ])
    
    with col2:
        st.markdown("### 📊 Application Context")
        app_type = st.selectbox("Application Type:", [
            "E-commerce Website", "REST API", "Mobile Backend", "Data Pipeline"
        ])
        
        traffic_volume = st.selectbox("Traffic Volume:", [
            "Low (< 1K req/hour)", "Medium (1K-10K req/hour)", 
            "High (10K-100K req/hour)", "Very High (> 100K req/hour)"
        ])
    
    if st.button("🚀 Simulate Error Analysis", use_container_width=True):
        # Generate error analysis based on scenario
        error_mappings = {
            "Database Connection Failure": {
                "primary_type": "Fault", "status_code": 503, "avg_duration": 5000,
                "impact": "High", "urgency": "Critical"
            },
            "Invalid User Input": {
                "primary_type": "Error", "status_code": 400, "avg_duration": 50,
                "impact": "Low", "urgency": "Low"
            },
            "API Rate Limiting": {
                "primary_type": "Throttle", "status_code": 429, "avg_duration": 100,
                "impact": "Medium", "urgency": "Medium"
            },
            "Downstream Service Timeout": {
                "primary_type": "Fault", "status_code": 504, "avg_duration": 30000,
                "impact": "High", "urgency": "High"
            },
            "Authentication Failure": {
                "primary_type": "Error", "status_code": 401, "avg_duration": 25,
                "impact": "Medium", "urgency": "Medium"
            },
            "Resource Not Found": {
                "primary_type": "Error", "status_code": 404, "avg_duration": 10,
                "impact": "Low", "urgency": "Low"
            },
            "Payment Processing Error": {
                "primary_type": "Fault", "status_code": 502, "avg_duration": 2000,
                "impact": "Critical", "urgency": "Critical"
            }
        }
        
        error_data = error_mappings[error_scenario]
        
        # Calculate impact metrics
        traffic_multipliers = {
            "Low": 500, "Medium": 5000, "High": 50000, "Very High": 500000
        }
        
        hourly_requests = traffic_multipliers[traffic_volume.split()[0]]
        affected_requests = int(hourly_requests * (error_frequency / 100))
        
        # Determine cost impact
        error_cost_impact = {
            "Low": 0.1, "Medium": 0.5, "High": 2.0, "Critical": 10.0
        }
        
        daily_cost_impact = error_cost_impact[error_data["impact"]] * 24
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 📊 Error Analysis Results
        
        **Error Classification:**
        - **Type**: {error_data['primary_type']} ({error_data['status_code']})
        - **Scenario**: {error_scenario}
        - **Average Duration**: {error_data['avg_duration']}ms
        - **Business Impact**: {error_data['impact']}
        - **Response Urgency**: {error_data['urgency']}
        
        **Impact Metrics:**
        - **Affected Requests/Hour**: {affected_requests:,}
        - **Error Rate**: {error_frequency}%
        - **Estimated Daily Cost Impact**: ${daily_cost_impact:.2f}
        
        **Recommended Actions:**
        - Set up X-Ray error alerts for {error_data['status_code']} responses
        - Monitor error trends in X-Ray service map
        - Implement retry logic for transient failures
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Generate sample error timeline
        hours = list(range(24))
        base_errors = [affected_requests] * 24
        
        # Add some variation to make it realistic
        error_counts = [int(base + np.random.normal(0, base * 0.2)) for base in base_errors]
        error_counts = [max(0, count) for count in error_counts]  # Ensure non-negative
        
        df_errors = pd.DataFrame({
            'Hour': hours,
            'Error_Count': error_counts,
            'Error_Type': [error_data['primary_type']] * 24
        })
        
        fig = px.line(df_errors, x='Hour', y='Error_Count', 
                     title=f'24-Hour Error Timeline: {error_scenario}',
                     color='Error_Type', 
                     color_discrete_map={
                         'Error': AWS_COLORS['error'],
                         'Fault': AWS_COLORS['fault'], 
                         'Throttle': AWS_COLORS['warning']
                     })
        
        fig.update_layout(height=300, xaxis_title="Hour of Day", yaxis_title="Error Count")
        st.plotly_chart(fig, use_container_width=True)
    
    # Exception Handling in X-Ray
    st.markdown("### 🔍 Exception Details in X-Ray")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📋 Exception Information Captured
        
        When exceptions occur, X-Ray records:
        
        - **Exception type** and class name
        - **Error message** and description  
        - **Stack trace** (if available)
        - **Line numbers** and file locations
        - **Timestamp** of occurrence
        - **Service context** where it happened
        
        This information helps developers quickly locate and fix issues.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 Best Practices for Exception Handling
        
        **In Application Code:**
        - Use try-catch blocks appropriately
        - Add meaningful error messages
        - Include relevant context in exceptions
        - Don't suppress important errors
        
        **In X-Ray Integration:**
        - Let SDK capture exceptions automatically
        - Add custom annotations to error context
        - Use subsegments for granular error tracking
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Error Monitoring Dashboard
    st.markdown("### 📊 Sample Error Monitoring Dashboard")
    
    # Create sample error data for visualization
    error_types = ['4xx Errors', '5xx Faults', '429 Throttling']
    error_counts = [150, 45, 25]
    colors = [AWS_COLORS['error'], AWS_COLORS['fault'], AWS_COLORS['warning']]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Error distribution pie chart
        fig_pie = px.pie(values=error_counts, names=error_types, 
                        title='Error Distribution by Type',
                        color_discrete_sequence=colors)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Error trends over time
        time_periods = ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00']
        error_trends = {
            '4xx Errors': [20, 15, 35, 45, 30, 25],
            '5xx Faults': [8, 5, 12, 15, 10, 8], 
            '429 Throttling': [3, 2, 8, 12, 5, 3]
        }
        
        fig_trends = go.Figure()
        for error_type, counts in error_trends.items():
            color = colors[error_types.index(error_type)]
            fig_trends.add_trace(go.Scatter(
                x=time_periods, y=counts, name=error_type,
                line=dict(color=color, width=3)
            ))
        
        fig_trends.update_layout(
            title='Error Trends Throughout Day',
            xaxis_title='Time', yaxis_title='Error Count',
            height=300
        )
        st.plotly_chart(fig_trends, use_container_width=True)
    
    # Common Error Patterns
    st.markdown("### 🔍 Common Error Patterns & Solutions")
    
    error_patterns = {
        'Pattern': [
            'Cascading Failures', 'Timeout Errors', 'Authentication Spikes',
            'Resource Exhaustion', 'Rate Limit Breaches', 'Data Validation Errors'
        ],
        'X-Ray Signature': [
            'Multiple 5xx faults across services',
            '504 errors with long durations', 
            'Sudden 401/403 error increase',
            '503 errors during peak traffic',
            '429 errors in specific time windows',
            '400 errors with consistent patterns'
        ],
        'Root Cause': [
            'One service failure triggers others',
            'Network latency or service overload',
            'Auth service issues or token expiry',
            'Memory/CPU limits reached',
            'Traffic exceeds configured limits', 
            'Invalid input data or API changes'
        ],
        'Solution Strategy': [
            'Implement circuit breakers',
            'Add retry logic with backoff',
            'Monitor auth service health',
            'Scale resources or optimize code',
            'Adjust rate limits or implement queuing',
            'Validate input and improve error messages'
        ]
    }
    
    df_patterns = pd.DataFrame(error_patterns)
    st.dataframe(df_patterns, use_container_width=True)
    
    # Alerting and Monitoring
    st.markdown("### 🚨 Error Alerting & Monitoring Strategy")
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Recommended Alerting Thresholds
    
    **Critical Alerts (Immediate Response):**
    - Error rate > 5% for any service
    - Fault rate > 1% for critical services  
    - Response time > 5 seconds for user-facing APIs
    - Any 5xx error rate > 2%
    
    **Warning Alerts (Monitor Closely):**
    - Error rate > 2% for non-critical services
    - Throttling rate > 1%
    - Response time degradation > 50%
    - Unusual error pattern changes
    
    **Best Practices:**
    - Set different thresholds for different services
    - Use time-based windows (5min, 15min, 1hour)
    - Consider business hours vs off-hours
    - Implement escalation policies
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Advanced Error Handling with X-Ray")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Advanced error handling and exception tracking with X-Ray
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core.exceptions import SegmentNotFoundException
import boto3
import time
import traceback
from functools import wraps
from enum import Enum

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    CLIENT_ERROR = "client_error"      # 4xx
    SERVER_FAULT = "server_fault"      # 5xx  
    THROTTLING = "throttling"          # 429
    TIMEOUT = "timeout"                # Custom
    VALIDATION = "validation"          # Custom

def enhanced_error_tracking(error_category=None, severity=ErrorSeverity.MEDIUM):
    """
    Decorator for enhanced error tracking with X-Ray
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            segment_name = f"{func.__name__}_operation"
            
            try:
                with xray_recorder.in_subsegment(segment_name) as subsegment:
                    # Add operation metadata
                    subsegment.put_annotation('operation_name', func.__name__)
                    subsegment.put_annotation('error_category', error_category.value if error_category else 'unknown')
                    subsegment.put_annotation('severity_level', severity.value)
                    
                    start_time = time.time()
                    result = func(*args, **kwargs)
                    end_time = time.time()
                    
                    # Track successful operations
                    subsegment.put_annotation('operation_result', 'success')
                    subsegment.put_annotation('execution_time_ms', int((end_time - start_time) * 1000))
                    
                    return result
                    
            except Exception as e:
                # Enhanced error tracking
                track_error_with_xray(e, func.__name__, error_category, severity, args, kwargs)
                raise
                
        return wrapper
    return decorator

def track_error_with_xray(exception, function_name, error_category, severity, args=None, kwargs=None):
    """
    Comprehensive error tracking with X-Ray annotations and metadata
    """
    try:
        current_segment = xray_recorder.current_segment()
        
        # Basic error annotations
        current_segment.put_annotation('error_occurred', True)
        current_segment.put_annotation('error_type', type(exception).__name__)
        current_segment.put_annotation('error_message', str(exception)[:100])  # Truncate long messages
        current_segment.put_annotation('function_name', function_name)
        current_segment.put_annotation('severity', severity.value)
        
        if error_category:
            current_segment.put_annotation('error_category', error_category.value)
        
        # Categorize by HTTP status code if applicable
        if hasattr(exception, 'response'):
            status_code = exception.response.get('ResponseMetadata', {}).get('HTTPStatusCode')
            if status_code:
                current_segment.put_annotation('http_status_code', status_code)
                current_segment.put_annotation('xray_error_category', categorize_http_error(status_code))
        
        # Add detailed metadata for debugging
        error_metadata = {
            'exception_class': type(exception).__name__,
            'exception_message': str(exception),
            'stack_trace': traceback.format_exc(),
            'function_args_count': len(args) if args else 0,
            'function_kwargs_keys': list(kwargs.keys()) if kwargs else [],
            'timestamp': time.time(),
            'severity_level': severity.value
        }
        
        # Add AWS-specific error details if available
        if hasattr(exception, 'response'):
            aws_error_details = {
                'error_code': exception.response.get('Error', {}).get('Code'),
                'error_message': exception.response.get('Error', {}).get('Message'),
                'request_id': exception.response.get('ResponseMetadata', {}).get('RequestId'),
                'retry_attempts': exception.response.get('ResponseMetadata', {}).get('RetryAttempts', 0)
            }
            error_metadata['aws_error_details'] = aws_error_details
        
        current_segment.put_metadata('error_details', error_metadata)
        
        # Add the exception to the segment for X-Ray console display
        current_segment.add_exception(exception)
        
    except SegmentNotFoundException:
        # If no active segment, create a custom one for error tracking
        with xray_recorder.in_segment('error_tracking'):
            xray_recorder.current_segment().put_annotation('standalone_error', True)
            xray_recorder.current_segment().add_exception(exception)

def categorize_http_error(status_code):
    """Categorize HTTP errors for X-Ray"""
    if 400 <= status_code < 500:
        if status_code == 429:
            return 'throttle'
        else:
            return 'error'
    elif 500 <= status_code < 600:
        return 'fault'
    else:
        return 'unknown'

# Example usage with different error scenarios

@enhanced_error_tracking(error_category=ErrorCategory.SERVER_FAULT, severity=ErrorSeverity.HIGH)
def database_operation_with_retry(table_name, item_data, max_retries=3):
    """
    Database operation with retry logic and comprehensive error tracking
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    for attempt in range(max_retries + 1):
        try:
            with xray_recorder.in_subsegment(f'dynamodb_attempt_{attempt + 1}') as subsegment:
                subsegment.put_annotation('attempt_number', attempt + 1)
                subsegment.put_annotation('max_retries', max_retries)
                subsegment.put_annotation('table_name', table_name)
                
                # Attempt the database operation
                response = table.put_item(Item=item_data)
                
                subsegment.put_annotation('operation_result', 'success')
                subsegment.put_annotation('consumed_capacity', 
                    response.get('ConsumedCapacity', {}).get('CapacityUnits', 0))
                
                return response
                
        except Exception as e:
            with xray_recorder.in_subsegment('retry_handling') as retry_subsegment:
                retry_subsegment.put_annotation('retry_attempt', attempt + 1)
                retry_subsegment.put_annotation('error_type', type(e).__name__)
                
                if attempt < max_retries:
                    # Exponential backoff
                    wait_time = (2 ** attempt) * 0.1
                    retry_subsegment.put_annotation('backoff_time_seconds', wait_time)
                    retry_subsegment.put_annotation('will_retry', True)
                    
                    time.sleep(wait_time)
                    continue
                else:
                    retry_subsegment.put_annotation('will_retry', False)
                    retry_subsegment.put_annotation('final_failure', True)
                    
                    # Enhanced error context for final failure
                    xray_recorder.put_annotation('retry_exhausted', True)
                    xray_recorder.put_annotation('total_attempts', max_retries + 1)
                    
                    raise

@enhanced_error_tracking(error_category=ErrorCategory.CLIENT_ERROR, severity=ErrorSeverity.LOW)
def validate_user_input(user_data):
    """
    Input validation with detailed error tracking
    """
    validation_errors = []
    
    with xray_recorder.in_subsegment('input_validation') as validation_segment:
        validation_segment.put_annotation('validation_started', True)
        
        # Email validation
        if 'email' not in user_data or '@' not in user_data['email']:
            validation_errors.append('Invalid email format')
            validation_segment.put_annotation('email_valid', False)
        else:
            validation_segment.put_annotation('email_valid', True)
        
        # Age validation  
        if 'age' not in user_data or not isinstance(user_data['age'], int) or user_data['age'] < 0:
            validation_errors.append('Invalid age')
            validation_segment.put_annotation('age_valid', False)
        else:
            validation_segment.put_annotation('age_valid', True)
        
        # Required fields
        required_fields = ['name', 'email', 'age']
        missing_fields = [field for field in required_fields if field not in user_data]
        
        validation_segment.put_annotation('missing_fields_count', len(missing_fields))
        validation_segment.put_annotation('total_errors', len(validation_errors))
        
        if validation_errors or missing_fields:
            validation_segment.put_annotation('validation_result', 'failed')
            
            error_details = {
                'validation_errors': validation_errors,
                'missing_fields': missing_fields,
                'provided_fields': list(user_data.keys())
            }
            
            validation_segment.put_metadata('validation_failure_details', error_details)
            
            # Create custom validation exception
            error_message = f"Validation failed: {', '.join(validation_errors + [f'Missing: {f}' for f in missing_fields])}"
            raise ValueError(error_message)
        
        validation_segment.put_annotation('validation_result', 'passed')
        return True

@enhanced_error_tracking(error_category=ErrorCategory.TIMEOUT, severity=ErrorSeverity.HIGH)
def external_api_call_with_timeout(api_url, timeout_seconds=5):
    """
    External API call with timeout handling
    """
    import requests
    
    with xray_recorder.in_subsegment('external_api_request') as api_segment:
        api_segment.put_annotation('api_url', api_url)
        api_segment.put_annotation('timeout_seconds', timeout_seconds)
        
        try:
            start_time = time.time()
            
            response = requests.get(api_url, timeout=timeout_seconds)
            
            end_time = time.time()
            response_time = int((end_time - start_time) * 1000)
            
            api_segment.put_annotation('response_time_ms', response_time)
            api_segment.put_annotation('status_code', response.status_code)
            api_segment.put_annotation('api_call_result', 'success')
            
            if response.status_code >= 400:
                api_segment.put_annotation('http_error', True)
                
                # Create HTTP error with status code
                http_error = requests.HTTPError(f"HTTP {response.status_code}: {response.reason}")
                http_error.response = {'ResponseMetadata': {'HTTPStatusCode': response.status_code}}
                raise http_error
            
            return response.json()
            
        except requests.exceptions.Timeout as e:
            api_segment.put_annotation('timeout_occurred', True)
            api_segment.put_annotation('api_call_result', 'timeout')
            raise
            
        except requests.exceptions.RequestException as e:
            api_segment.put_annotation('request_exception', True)
            api_segment.put_annotation('api_call_result', 'request_error')
            raise

# Example usage and error monitoring
def main_application_handler(event):
    """
    Main application handler with comprehensive error tracking
    """
    try:
        with xray_recorder.in_segment('main_request_handler'):
            xray_recorder.put_annotation('handler_name', 'main_application_handler')
            xray_recorder.put_annotation('event_type', event.get('type', 'unknown'))
            
            # Process user data
            user_data = event.get('user_data', {})
            validate_user_input(user_data)
            
            # Store in database  
            database_operation_with_retry('Users', user_data)
            
            # Call external service
            external_data = external_api_call_with_timeout('https://api.example.com/data')
            
            xray_recorder.put_annotation('request_processed_successfully', True)
            
            return {
                'statusCode': 200,
                'body': 'Request processed successfully'
            }
            
    except ValueError as e:
        # Client error - validation failure
        xray_recorder.put_annotation('error_type', 'validation_error')
        return {
            'statusCode': 400,
            'body': f'Validation error: {str(e)}'
        }
        
    except Exception as e:
        # Server fault - unexpected error
        xray_recorder.put_annotation('error_type', 'server_error')
        xray_recorder.put_annotation('unexpected_error', True)
        
        return {
            'statusCode': 500,
            'body': 'Internal server error'
        }

# Example test calls
if __name__ == "__main__":
    # Test successful case
    success_event = {
        'type': 'user_registration',
        'user_data': {
            'name': 'John Doe',
            'email': 'john@example.com', 
            'age': 30
        }
    }
    
    result = main_application_handler(success_event)
    print(f"Success result: {result}")
    
    # Test validation error
    error_event = {
        'type': 'user_registration',
        'user_data': {
            'name': 'Jane Doe'
            # Missing email and age
        }
    }
    
    result = main_application_handler(error_event)
    print(f"Error result: {result}")
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
    st.markdown("""
    # 🔍 AWS X-Ray Monitoring Hub
    
    """)
    st.markdown("""<div class="info-box">
                Master distributed tracing with AWS X-Ray to analyze, debug, and optimize your applications. 
                Learn core concepts, error handling, and best practices for effective application monitoring and troubleshooting.
                </div>""", unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        "🔍 AWS X-Ray", 
        "🧩 Key Concepts", 
        "⚠️ Errors, Faults & Exceptions"
    ])
    
    with tab1:
        aws_xray_tab()
    
    with tab2:
        xray_key_concepts_tab()
    
    with tab3:
        xray_errors_tab()
    
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
