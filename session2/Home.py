
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import utils.common as common
import utils.authenticate as authenticate

# Page configuration
st.set_page_config(
    page_title="AWS Developer Associate - Session 2",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

common.initialize_session_state()

with st.sidebar:
    common.render_sidebar()

def main():
    # Custom CSS for AWS styling
    st.markdown("""
    <style>
    /* AWS Color Scheme */
    :root {
        --aws-orange: #FF9900;
        --aws-blue: #232F3E;
        --aws-light-blue: #4B9CD3;
        --aws-gray: #879196;
        --aws-white: #FFFFFF;
    }

    .main-header {
        background: linear-gradient(135deg, #232F3E 0%, #4B9CD3 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
    }

    .service-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border-left: 6px solid #FF9900;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }

    .service-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }

    .architecture-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e3f2fd 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1.5rem 0;
        border: 2px solid #4B9CD3;
    }

    .comparison-card {
        background: #e8f5e8;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #4caf50;
        margin: 1rem 0;
    }

    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #f39c12;
    }

    .info-highlight {
        background: linear-gradient(135deg, #E6F2FF 0%, #CCE7FF 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #00A1C9;
        margin: 1rem 0;
    }

    .code-example {
        background: #2d3748;
        color: #e2e8f0;
        padding: 1rem;
        border-radius: 8px;
        font-family: 'Courier New', monospace;
        margin: 1rem 0;
    }

    .training-progress {
        background: linear-gradient(135deg, #FF9900 0%, #FFB84D 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }

    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }

    .stat-card {
        background: linear-gradient(135deg, #232F3E 0%, #4B9CD3 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
    }

    .footer {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #232F3E 0%, #4B9CD3 100%);
        color: white;
        margin-top: 3rem;
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar Navigation
    with st.sidebar:
        st.markdown("## 📚 Session 2 Navigation")
        
        section = st.selectbox(
            "Choose a section:",
            [
                "🏠 Overview",
                "🏗️ Server vs Serverless Architecture",
                "🌐 Amazon API Gateway",
                "⚡ AWS Lambda",
                "🗄️ Amazon DynamoDB",
                "🔄 AWS Step Functions",
                "📊 Database Offerings",
                "📨 Messaging & Decoupling",
                "✅ Progress Check"
            ]
        )
        
        st.markdown("---")
        st.markdown("### 📖 Week 2 Progress")
        progress = st.progress(0.65)
        st.markdown("**65% Complete**")
        
        st.markdown("### 🎯 Quick Stats")
        st.metric("Services Covered", "8", "2")
        st.metric("Architecture Patterns", "3", "1")
        st.metric("Hands-on Labs", "2", "1")

    # Main Content
    if section == "🏠 Overview":
        render_overview()
    elif section == "🏗️ Server vs Serverless Architecture":
        render_architecture_comparison()
    elif section == "🌐 Amazon API Gateway":
        render_api_gateway()
    elif section == "⚡ AWS Lambda":
        render_lambda()
    elif section == "🗄️ Amazon DynamoDB":
        render_dynamodb()
    elif section == "🔄 AWS Step Functions":
        render_step_functions()
    elif section == "📊 Database Offerings":
        render_database_offerings()
    elif section == "📨 Messaging & Decoupling":
        render_messaging()
    elif section == "✅ Progress Check":
        render_progress_check()

def render_overview():
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>AWS Partner Certification Readiness</h1>
        <h2>Developer - Associate Session 2</h2>
        <h3>Development with AWS Services</h3>
    </div>
    """, unsafe_allow_html=True)

    # Today's Focus
    st.markdown("## 🎯 Today's Focus: Development with AWS Services")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="info-highlight">
            <h3>🚀 What You'll Learn Today</h3>
            <p>In this session, we'll dive deep into AWS services that are essential for application development, 
            focusing on serverless architectures, database services, and application integration patterns.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="training-progress">
            <h4>Session 2 of 6</h4>
            <div style="font-size: 2rem;">⚡</div>
            <p>Development Focus</p>
        </div>
        """, unsafe_allow_html=True)

    # Service Categories
    st.markdown("### 🛠️ AWS Services We'll Cover")
    
    categories = [
        {
            "title": "Compute",
            "icon": "⚡",
            "services": ["AWS Lambda"],
            "color": "#FF9900"
        },
        {
            "title": "Database", 
            "icon": "🗄️",
            "services": ["Amazon DynamoDB", "Amazon RDS"],
            "color": "#4B9CD3"
        },
        {
            "title": "Networking",
            "icon": "🌐", 
            "services": ["Amazon API Gateway"],
            "color": "#52C41A"
        },
        {
            "title": "Integration",
            "icon": "🔄",
            "services": ["Amazon SNS", "Amazon SQS", "AWS Step Functions"],
            "color": "#722ED1"
        }
    ]
    
    cols = st.columns(4)
    for i, category in enumerate(categories):
        with cols[i]:
            st.markdown(f"""
            <div class="service-card" style="border-left-color: {category['color']}">
                <div style="text-align: center; font-size: 2rem;">{category['icon']}</div>
                <h4 style="text-align: center; margin: 1rem 0;">{category['title']}</h4>
                <ul>
                {"".join([f"<li>{service}</li>" for service in category['services']])}
                </ul>
            </div>
            """, unsafe_allow_html=True)

    # Week 2 Training Curriculum
    st.markdown("## 📚 Week 2 Digital Training Curriculum")
    
    training_modules = [
        {"name": "AWS Database Offerings", "type": "Core", "duration": "45 min"},
        {"name": "Amazon ElastiCache Getting Started", "type": "Core", "duration": "30 min"},
        {"name": "Getting into the Serverless Mindset", "type": "Core", "duration": "60 min"},
        {"name": "Amazon DynamoDB for Serverless Architectures", "type": "Core", "duration": "90 min"},
        {"name": "AWS Cloud Quest: Serverless Developer", "type": "Optional", "duration": "2 hours"},
        {"name": "Working with Amazon ECS Lab", "type": "Optional", "duration": "90 min"}
    ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Required Courses")
        for module in training_modules:
            if module["type"] == "Core":
                st.markdown(f"""
                <div class="comparison-card">
                    <strong>{module['name']}</strong><br>
                    <small>Duration: {module['duration']}</small>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Optional Courses")
        for module in training_modules:
            if module["type"] == "Optional":
                st.markdown(f"""
                <div class="warning-box">
                    <strong>{module['name']}</strong><br>
                    <small>Duration: {module['duration']}</small>
                </div>
                """, unsafe_allow_html=True)

def render_architecture_comparison():
    st.markdown("# 🏗️ Server-Based vs Serverless Architectures")
    
    # Architecture Comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="architecture-section">
            <h3>🖥️ Server-Based Architecture</h3>
            <ul>
                <li><strong>Amazon EC2:</strong> Virtual servers running your application</li>
                <li><strong>Amazon RDS:</strong> Managed relational database service</li>
                <li><strong>VPC:</strong> Virtual private cloud for networking</li>
                <li><strong>Scaling:</strong> Manual or auto-scaling groups</li>
            </ul>
            <div class="warning-box">
                <strong>Best for:</strong> Applications requiring persistent connections, 
                complex server-side processing, or specific runtime environments.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="architecture-section">
            <h3>⚡ Serverless Architecture</h3>
            <ul>
                <li><strong>AWS Lambda:</strong> Function-as-a-Service compute</li>
                <li><strong>Amazon DynamoDB:</strong> NoSQL database</li>
                <li><strong>API Gateway:</strong> RESTful API management</li>
                <li><strong>Scaling:</strong> Automatic and instant</li>
            </ul>
            <div class="info-highlight">
                <strong>Best for:</strong> Event-driven applications, microservices,
                APIs, and applications with variable traffic patterns.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Example Application Architecture
    st.markdown("### 🏗️ Serverless Microservices Example")
    
    st.markdown("""
    <div class="info-highlight">
        <h4>📱 To-Do List Web Application</h4>
        <p>A simple serverless application that enables users to create, update, view, and delete items:</p>
        <ul>
            <li><strong>AWS Lambda + API Gateway:</strong> Business logic and API endpoints</li>
            <li><strong>Amazon DynamoDB:</strong> Data persistence and storage</li>
            <li><strong>AWS Amplify Console:</strong> Static content hosting</li>
            <li><strong>Amazon Cognito:</strong> User authentication (implied)</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Architecture Benefits Comparison
    st.markdown("### ⚖️ Architecture Comparison")
    
    comparison_data = {
        "Aspect": ["Cost Model", "Scaling", "Maintenance", "Performance", "Complexity"],
        "Server-Based": [
            "Pay for provisioned capacity",
            "Manual/Auto Scaling Groups", 
            "OS patches, updates, monitoring",
            "Consistent, predictable",
            "Higher operational complexity"
        ],
        "Serverless": [
            "Pay per request/execution",
            "Automatic, instant scaling",
            "Fully managed by AWS",
            "Variable, cold start latency", 
            "Focus on business logic"
        ]
    }
    
    df = pd.DataFrame(comparison_data)
    st.dataframe(df, use_container_width=True)

def render_api_gateway():
    st.markdown("# 🌐 Amazon API Gateway")
    
    st.markdown("""
    <div class="info-highlight">
        <h3>What is Amazon API Gateway?</h3>
        <p>Amazon API Gateway is an AWS service for creating, publishing, maintaining, monitoring, 
        and securing REST, HTTP, and WebSocket APIs at any scale.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # API Types
    st.markdown("## 🔧 API Types")
    
    api_types = [
        {
            "type": "REST APIs",
            "description": "Full-featured APIs with resources and methods",
            "use_case": "Complex APIs with advanced features like request/response transformation",
            "icon": "🔄"
        },
        {
            "type": "HTTP APIs", 
            "description": "Lower latency and cost than REST APIs",
            "use_case": "Simple proxy to Lambda functions or HTTP endpoints",
            "icon": "⚡"
        },
        {
            "type": "WebSocket APIs",
            "description": "Bidirectional communication between client and server", 
            "use_case": "Chat applications, real-time dashboards, notifications",
            "icon": "💬"
        }
    ]
    
    for api in api_types:
        st.markdown(f"""
        <div class="service-card">
            <div style="display: flex; align-items: center;">
                <div style="font-size: 2rem; margin-right: 1rem;">{api['icon']}</div>
                <div>
                    <h4>{api['type']}</h4>
                    <p><strong>Description:</strong> {api['description']}</p>
                    <p><strong>Use Case:</strong> {api['use_case']}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Endpoint Types
    st.markdown("## 🌍 API Gateway Endpoint Types")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="comparison-card">
            <h4>🌐 Edge-Optimized</h4>
            <p><strong>Best for:</strong> Geographically distributed clients</p>
            <p><strong>How it works:</strong> Requests routed to nearest CloudFront POP</p>
            <p><strong>Default:</strong> Yes, for REST APIs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="comparison-card">
            <h4>🗺️ Regional</h4>
            <p><strong>Best for:</strong> Clients in the same region</p>
            <p><strong>How it works:</strong> Direct connection to API Gateway in region</p>
            <p><strong>Benefits:</strong> Lower latency for regional traffic</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="comparison-card">
            <h4>🔒 Private</h4>
            <p><strong>Best for:</strong> Internal VPC applications</p>
            <p><strong>How it works:</strong> Access only via VPC endpoint (ENI)</p>
            <p><strong>Security:</strong> Highest level of network isolation</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Deployment Stages
    st.markdown("## 🚀 Deployment Stages")
    
    st.markdown("""
    <div class="architecture-section">
        <h4>Managing Multiple Release Stages</h4>
        <p>API Gateway allows you to manage multiple deployment stages (alpha, beta, production) 
        for each API using stage variables.</p>
        
        <h5>💡 Example Use Cases:</h5>
        <ul>
            <li><strong>Backend Endpoints:</strong> Configure different backend hosts per stage</li>
            <li><strong>Lambda Functions:</strong> Point to different Lambda function versions</li>
            <li><strong>Configuration:</strong> Different timeout values, throttling limits</li>
        </ul>
        
        <div class="code-example">
# Example: Stage variables for different environments
Production stage: ${stageVariables.backend_host} = "api.example.com"
Beta stage: ${stageVariables.backend_host} = "beta.api.example.com"
Alpha stage: ${stageVariables.backend_host} = "alpha.api.example.com"
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_lambda():
    st.markdown("# ⚡ AWS Lambda")
    
    st.markdown("""
    <div class="info-highlight">
        <h3>AWS Lambda Overview</h3>
        <p>Serverless compute service that lets you run code without provisioning or managing servers, 
        creating workload-aware cluster scaling logic, maintaining event integrations, or managing runtimes.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Lambda Concepts
    st.markdown("## 🔧 Key Concepts")
    
    concepts = [
        {"term": "Function", "definition": "A resource that you can invoke to run your code in Lambda"},
        {"term": "Trigger", "definition": "A resource or configuration that invokes a Lambda function"},
        {"term": "Event", "definition": "A JSON-formatted document that contains data for processing"},
        {"term": "Runtime", "definition": "Language-specific environment that runs in an execution environment"},
        {"term": "Layer", "definition": "ZIP archive containing additional code, libraries, or configuration"},
        {"term": "Concurrency", "definition": "Number of requests your function serves simultaneously"},
        {"term": "Destination", "definition": "AWS resource where Lambda sends events from async invocations"}
    ]
    
    col1, col2 = st.columns(2)
    
    for i, concept in enumerate(concepts):
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            st.markdown(f"""
            <div class="comparison-card">
                <h5>{concept['term']}</h5>
                <p>{concept['definition']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Supported Runtimes
    st.markdown("## 💻 Supported Runtimes")
    
    runtimes = ["Node.js", "Python", "Ruby", "Go", ".NET", "Java", "Custom Runtime"]
    
    cols = st.columns(4)
    for i, runtime in enumerate(runtimes):
        with cols[i % 4]:
            st.markdown(f"""
            <div style="text-align: center; padding: 0.5rem; background: #f0f0f0; border-radius: 8px; margin: 0.25rem;">
                <strong>{runtime}</strong>
            </div>
            """, unsafe_allow_html=True)
    
    # Invocation Models
    st.markdown("## 🔄 Lambda Invocation Models")
    
    tab1, tab2, tab3 = st.tabs(["🔄 Synchronous", "📨 Asynchronous", "🌊 Stream-based"])
    
    with tab1:
        st.markdown("""
        <div class="architecture-section">
            <h4>Synchronous (Push) Invocations</h4>
            <p>Most straightforward way to invoke Lambda functions. Function executes immediately when you call the Lambda Invoke API.</p>
            
            <h5>Use Cases:</h5>
            <ul>
                <li>API Gateway requests</li>
                <li>Direct SDK calls</li>
                <li>CLI invocations</li>
            </ul>
            
            <h5>Characteristics:</h5>
            <ul>
                <li>✅ Immediate execution</li>
                <li>✅ Direct response handling</li>
                <li>✅ Error handling in real-time</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("""
        <div class="architecture-section">
            <h4>Asynchronous (Event) Invocations</h4>
            <p>Lambda service queues the request and processes it when resources are available.</p>
            
            <h5>Triggered by:</h5>
            <ul>
                <li>Amazon S3 events</li>
                <li>Amazon SNS notifications</li>
                <li>Amazon CloudWatch Events</li>
            </ul>
            
            <h5>Characteristics:</h5>
            <ul>
                <li>✅ Built-in retry logic</li>
                <li>✅ Dead Letter Queue support</li>
                <li>✅ Higher throughput</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("""
        <div class="architecture-section">
            <h4>Stream-based (Poll) Invocations</h4>
            <p>Lambda polls the stream and invokes your function with batches of records.</p>
            
            <h5>Supported Services:</h5>
            <ul>
                <li>Amazon Kinesis Data Streams</li>
                <li>Amazon DynamoDB Streams</li>
                <li>Amazon SQS</li>
            </ul>
            
            <h5>Characteristics:</h5>
            <ul>
                <li>✅ Batch processing</li>
                <li>✅ Automatic scaling</li>
                <li>✅ No server management</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Memory and Performance
    st.markdown("## ⚡ Memory and Performance Considerations")
    
    # Create performance visualization
    memory_sizes = [128, 256, 512, 1024, 2048, 3008]
    durations = [11.0, 6.2, 3.1, 1.6, 0.8, 0.5]  # Example durations
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=memory_sizes,
        y=durations,
        mode='lines+markers',
        name='Execution Duration',
        line=dict(color='#FF9900', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Lambda Performance vs Memory Configuration",
        xaxis_title="Memory (MB)",
        yaxis_title="Average Duration (seconds)",
        template="plotly_white",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div class="warning-box">
        <h5>💡 Performance Tips</h5>
        <ul>
            <li>Memory determines CPU allocation proportionally</li>
            <li>More memory = more CPU = potentially faster execution</li>
            <li>Monitor CloudWatch metrics to optimize memory settings</li>
            <li>Use AWS X-Ray to identify performance bottlenecks</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Timeout Best Practices
    st.markdown("## ⏰ Timeout Best Practices")
    
    st.markdown("""
    <div class="architecture-section">
        <h4>Preventing Lambda Timeouts</h4>
        
        <h5>🔧 Verify System Resources</h5>
        <p>Ensure your Lambda function has enough memory (which determines CPU and network bandwidth).</p>
        
        <h5>🔗 Check Service Integration Limits</h5>
        <p>While Lambda max timeout is 15 minutes, other AWS services may have different limits:</p>
        <ul>
            <li><strong>API Gateway:</strong> 30 seconds</li>
            <li><strong>ALB:</strong> 15 minutes</li>
            <li><strong>CloudFront:</strong> 30 seconds</li>
        </ul>
        
        <h5>⚡ Consider Provisioned Concurrency</h5>
        <p>Initializes runtime environments to eliminate cold starts for latency-sensitive applications.</p>
    </div>
    """, unsafe_allow_html=True)

def render_dynamodb():
    st.markdown("# 🗄️ Amazon DynamoDB")
    
    st.markdown("""
    <div class="info-highlight">
        <h3>Amazon DynamoDB Overview</h3>
        <p>Fully managed, serverless, key-value NoSQL database designed to run high-performance 
        applications at any scale with single-digit millisecond performance.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Core Components
    st.markdown("## 🔧 Core Components")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="service-card">
            <h4>📊 Table Structure</h4>
            <ul>
                <li><strong>Table:</strong> Collection of items</li>
                <li><strong>Item:</strong> Collection of attributes (max 400KB)</li>
                <li><strong>Attribute:</strong> Fundamental data element</li>
                <li><strong>Primary Key:</strong> Uniquely identifies each item</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="service-card">
            <h4>🔑 Key Types</h4>
            <ul>
                <li><strong>Partition Key:</strong> Simple primary key</li>
                <li><strong>Composite Key:</strong> Partition key + Sort key</li>
                <li><strong>Global Secondary Index:</strong> Alternate query patterns</li>
                <li><strong>Local Secondary Index:</strong> Additional sort key options</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Secondary Indexes
    st.markdown("## 🔍 Secondary Indexes")
    
    st.markdown("""
    <div class="architecture-section">
        <h4>Why Use Secondary Indexes?</h4>
        <p>DynamoDB provides fast access via primary key, but secondary indexes enable 
        efficient queries on non-key attributes.</p>
        
        <div class="warning-box">
            <h5>📝 Key Points:</h5>
            <ul>
                <li>Secondary indexes contain subset of attributes from table</li>
                <li>Support Query and Scan operations</li>
                <li>Each table can have multiple secondary indexes</li>
                <li>Enable flexible query patterns for your applications</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Capacity Modes
    st.markdown("## ⚡ Capacity Modes")
    
    tab1, tab2 = st.tabs(["📊 Provisioned Mode", "🔄 On-Demand Mode"])
    
    with tab1:
        st.markdown("""
        <div class="comparison-card">
            <h4>Provisioned Mode</h4>
            <p>Specify the number of reads and writes per second that you expect.</p>
            
            <h5>✅ Good Choice When:</h5>
            <ul>
                <li>You have predictable application traffic</li>
                <li>Traffic is consistent or ramps gradually</li>
                <li>You can forecast capacity requirements</li>
                <li>You want to control costs</li>
            </ul>
            
            <h5>💰 Cost Benefits:</h5>
            <ul>
                <li>Lower cost for consistent workloads</li>
                <li>Reserved capacity discounts available</li>
                <li>Auto Scaling available</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("""
        <div class="comparison-card">
            <h4>On-Demand Mode</h4>
            <p>Pay-per-request pricing model that automatically scales with your traffic.</p>
            
            <h5>✅ Good Choice When:</h5>
            <ul>
                <li>Creating new tables with unknown workloads</li>
                <li>You have unpredictable application traffic</li>
                <li>You prefer paying for only what you use</li>
                <li>You want zero capacity planning</li>
            </ul>
            
            <h5>🚀 Benefits:</h5>
            <ul>
                <li>Instant scaling to accommodate traffic</li>
                <li>No capacity planning required</li>
                <li>Pay only for requests you make</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # DynamoDB Streams
    st.markdown("## 🌊 DynamoDB Streams")
    
    st.markdown("""
    <div class="info-highlight">
        <h4>Real-time Data Streaming</h4>
        <p>DynamoDB Streams captures item-level changes in your table and allows you to 
        respond to these changes in near real-time.</p>
        
        <h5>🔄 Stream Records Include:</h5>
        <ul>
            <li><strong>KEYS_ONLY:</strong> Only key attributes of modified item</li>
            <li><strong>NEW_IMAGE:</strong> Entire item after modification</li>
            <li><strong>OLD_IMAGE:</strong> Entire item before modification</li>
            <li><strong>NEW_AND_OLD_IMAGES:</strong> Both new and old images</li>
        </ul>
        
        <h5>💡 Common Use Cases:</h5>
        <ul>
            <li>Real-time analytics</li>
            <li>Audit logs</li>
            <li>Data replication</li>
            <li>Triggering Lambda functions</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # TTL (Time to Live)
    st.markdown("## ⏰ Time to Live (TTL)")
    
    st.markdown("""
    <div class="architecture-section">
        <h4>Automatic Item Expiration</h4>
        <p>TTL allows you to automatically delete items from your table when they expire, 
        helping reduce storage costs.</p>
        
        <div class="code-example">
# Example: TTL attribute in Unix timestamp format
{
    "id": "user123",
    "name": "John Doe",
    "session_data": "...",
    "ttl": 1672531200  # Expires on Jan 1, 2023 00:00:00 UTC
}
        </div>
        
        <div class="warning-box">
            <h5>⚠️ TTL Considerations:</h5>
            <ul>
                <li>Items typically deleted within 48 hours of expiration</li>
                <li>No additional cost for TTL</li>
                <li>TTL attribute must be a Number data type</li>
                <li>Use Unix timestamp format</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # DynamoDB + S3 Pattern
    st.markdown("## 📦 DynamoDB + S3 Pattern")
    
    st.markdown("""
    <div class="service-card">
        <h4>Handling Large Items</h4>
        <p>DynamoDB has a 400KB item size limit. For larger objects, use this pattern:</p>
        
        <ol>
            <li><strong>Store large data in S3:</strong> Images, documents, large JSON objects</li>
            <li><strong>Store S3 object key in DynamoDB:</strong> Reference to the S3 object</li>
            <li><strong>Retrieve in application:</strong> Get metadata from DynamoDB, large data from S3</li>
        </ol>
        
        <div class="info-highlight">
            <h5>💡 Benefits of this pattern:</h5>
            <ul>
                <li>Cost-effective storage for large objects</li>
                <li>Fast access to metadata via DynamoDB</li>
                <li>Scalable architecture</li>
                <li>Reduced DynamoDB storage costs</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_step_functions():
    st.markdown("# 🔄 AWS Step Functions")
    
    st.markdown("""
    <div class="info-highlight">
        <h3>AWS Step Functions Overview</h3>
        <p>Fully managed service that makes it easier to coordinate the components of 
        distributed applications and microservices using visual workflows.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Credit Card Application Example
    st.markdown("## 💳 Example: Credit Card Application Workflow")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="architecture-section">
            <h4>Workflow Steps</h4>
            <ol>
                <li><strong>📝 Application Submitted</strong></li>
                <li><strong>🔍 Credit Check</strong></li>
                <li><strong>⚖️ Decision Logic</strong></li>
                <li><strong>✅ Approved Path</strong>
                    <ul>
                        <li>Account Creation</li>
                        <li>Card Production</li>
                        <li>Welcome Email</li>
                    </ul>
                </li>
                <li><strong>❌ Rejected Path</strong>
                    <ul>
                        <li>Rejection Email</li>
                        <li>Audit Log</li>
                    </ul>
                </li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="service-card">
            <h4>🔧 Step Functions Benefits</h4>
            <ul>
                <li><strong>Visual Workflows:</strong> See your application logic</li>
                <li><strong>Error Handling:</strong> Built-in retry and error handling</li>
                <li><strong>State Management:</strong> Automatic state transitions</li>
                <li><strong>Service Integration:</strong> Native AWS service integration</li>
                <li><strong>Monitoring:</strong> Built-in logging and monitoring</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # State Types
    st.markdown("## 🔄 Common State Types")
    
    states = [
        {
            "name": "Task",
            "icon": "⚙️",
            "description": "Performs work using an Activity, Lambda function, or AWS service",
            "example": "Invoke Lambda function to process credit application"
        },
        {
            "name": "Choice", 
            "icon": "🔀",
            "description": "Makes a choice between branches based on input",
            "example": "Route based on credit score (approved/rejected)"
        },
        {
            "name": "Parallel",
            "icon": "⚡",
            "description": "Executes multiple branches simultaneously",
            "example": "Send welcome email and create account in parallel"
        },
        {
            "name": "Wait",
            "icon": "⏸️", 
            "description": "Delays execution for a specified time",
            "example": "Wait for external credit bureau response"
        },
        {
            "name": "Pass",
            "icon": "➡️",
            "description": "Passes input to output without doing work",
            "example": "Transform data format between states"
        }
    ]
    
    for state in states:
        st.markdown(f"""
        <div class="comparison-card">
            <div style="display: flex; align-items: center;">
                <div style="font-size: 1.5rem; margin-right: 1rem;">{state['icon']}</div>
                <div>
                    <h5>{state['name']} State</h5>
                    <p><strong>Purpose:</strong> {state['description']}</p>
                    <p><strong>Example:</strong> {state['example']}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Use Cases
    st.markdown("## 💡 Common Use Cases")
    
    use_cases = [
        "Data Processing Pipelines",
        "Application Orchestration", 
        "IT Automation",
        "E-commerce Order Processing",
        "Media Processing Workflows",
        "Machine Learning Pipelines"
    ]
    
    cols = st.columns(3)
    for i, use_case in enumerate(use_cases):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background: #f0f8ff; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; text-align: center;">
                <strong>{use_case}</strong>
            </div>
            """, unsafe_allow_html=True)

def render_database_offerings():
    st.markdown("# 📊 AWS Database Offerings")
    
    # Database Categories
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="service-card">
            <h3>🗃️ Relational Databases</h3>
            <ul>
                <li><strong>Amazon RDS</strong>
                    <ul>
                        <li>MySQL, PostgreSQL, MariaDB</li>
                        <li>Oracle, SQL Server</li>
                        <li>Managed service, easy migration</li>
                    </ul>
                </li>
                <li><strong>Amazon Aurora</strong>
                    <ul>
                        <li>MySQL and PostgreSQL compatible</li>
                        <li>3-5x better performance</li>
                        <li>1/10th the cost of commercial databases</li>
                    </ul>
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="service-card">
            <h3>🔄 Non-Relational Databases</h3>
            <ul>
                <li><strong>Amazon DynamoDB</strong>
                    <ul>
                        <li>Key-value and document NoSQL</li>
                        <li>Serverless, automatic scaling</li>
                        <li>Single-digit millisecond latency</li>
                    </ul>
                </li>
                <li><strong>Amazon DocumentDB</strong>
                    <ul>
                        <li>MongoDB-compatible</li>
                        <li>Document database service</li>
                        <li>Fully managed</li>
                    </ul>
                </li>
                <li><strong>Amazon ElastiCache</strong>
                    <ul>
                        <li>Redis and Memcached compatible</li>
                        <li>In-memory caching</li>
                        <li>Microsecond latency</li>
                    </ul>
                </li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Migration Strategy
    st.markdown("## 🔄 Database Migration Strategy")
    
    st.markdown("""
    <div class="architecture-section">
        <h4>From Self-Managed to AWS Managed</h4>
        
        <h5>🎯 Target Customers</h5>
        <ul>
            <li>Currently self-managing databases on-premises or in EC2</li>
            <li>Want to reduce database admin burden</li>
            <li>Don't want to rearchitect applications</li>
            <li>Need better performance, availability, and security</li>
        </ul>
        
        <h5>📈 Benefits of Migration</h5>
        <ul>
            <li><strong>Reduced Operational Overhead:</strong> AWS handles patching, backups, scaling</li>
            <li><strong>Improved Performance:</strong> Optimized infrastructure and configurations</li>
            <li><strong>Better Availability:</strong> Multi-AZ deployments, automated failover</li>
            <li><strong>Enhanced Security:</strong> Encryption, VPC isolation, IAM integration</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # DynamoDB vs RDBMS Comparison
    st.markdown("## ⚖️ DynamoDB vs Relational Databases")
    
    comparison = {
        "Characteristic": [
            "Optimal Workloads",
            "Data Model", 
            "Query Language",
            "Scaling",
            "Performance",
            "Pricing Model"
        ],
        "Relational Database (RDBMS)": [
            "Ad hoc queries, data warehousing, OLAP",
            "Well-defined schema, normalized tables",
            "SQL with complex joins and aggregations", 
            "Vertical scaling (read replicas for reads)",
            "Consistent, good for complex queries",
            "Instance-based pricing"
        ],
        "Amazon DynamoDB": [
            "Web-scale apps, gaming, IoT, real-time",
            "Schemaless, key-value and document",
            "Simple queries, no joins",
            "Horizontal scaling, automatic",
            "Single-digit millisecond latency",
            "Pay-per-request or provisioned capacity"
        ]
    }
    
    df = pd.DataFrame(comparison)
    st.dataframe(df, use_container_width=True)
    
    # Amazon Aurora Highlights
    st.markdown("## ⭐ Amazon Aurora Highlights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="info-highlight">
            <h4>🚀 Performance</h4>
            <ul>
                <li><strong>5x faster</strong> than standard MySQL</li>
                <li><strong>3x faster</strong> than standard PostgreSQL</li>
                <li>Distributed, fault-tolerant storage</li>
                <li>Auto-scales up to 64TB per instance</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-highlight">
            <h4>🛡️ Availability & Reliability</h4>
            <ul>
                <li><strong>Up to 15</strong> low-latency read replicas</li>
                <li><strong>Point-in-time recovery</strong></li>
                <li><strong>Continuous backup</strong> to Amazon S3</li>
                <li><strong>Replication</strong> across 3 Availability Zones</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def render_messaging():
    st.markdown("# 📨 Decoupling and Messaging")
    
    st.markdown("""
    <div class="info-highlight">
        <h3>Why Decouple Applications?</h3>
        <p>Decoupling allows you to build resilient, scalable applications where components 
        can fail independently without affecting the entire system.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Message Channel Types
    st.markdown("## 📬 Message Channel Types")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="architecture-section">
            <h4>📬 Point-to-Point (Queue)</h4>
            <div style="text-align: center; font-size: 3rem; margin: 1rem;">📬</div>
            <p><strong>Amazon SQS</strong> - Simple Queue Service</p>
            <ul>
                <li>One sender, one receiver</li>
                <li>Messages consumed and deleted</li>
                <li>Ensures message delivery</li>
                <li>Decouples application components</li>
            </ul>
            
            <div class="comparison-card">
                <h5>🎯 Use Cases:</h5>
                <ul>
                    <li>Order processing systems</li>
                    <li>Background job queues</li>
                    <li>Microservice communication</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="architecture-section">
            <h4>📡 Publish-Subscribe (Topic)</h4>
            <div style="text-align: center; font-size: 3rem; margin: 1rem;">📡</div>
            <p><strong>Amazon SNS</strong> - Simple Notification Service</p>
            <ul>
                <li>One publisher, multiple subscribers</li>
                <li>Messages broadcasted to all subscribers</li>
                <li>Fan-out messaging pattern</li>
                <li>Multiple protocol support</li>
            </ul>
            
            <div class="comparison-card">
                <h5>🎯 Use Cases:</h5>
                <ul>
                    <li>Event notifications</li>
                    <li>Alert systems</li>
                    <li>Mobile push notifications</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Amazon SQS Deep Dive
    st.markdown("## 📬 Amazon Simple Queue Service (SQS)")
    
    st.markdown("""
    <div class="service-card">
        <h4>Key Features</h4>
        <ul>
            <li><strong>🔧 Fully Managed:</strong> No infrastructure to manage</li>
            <li><strong>📈 Scalable:</strong> Handles any volume of messages</li>
            <li><strong>🛡️ Reliable:</strong> Messages stored redundantly</li>
            <li><strong>🔒 Secure:</strong> Server-side encryption, access controls</li>
            <li><strong>💰 Cost-effective:</strong> Pay only for what you use</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Amazon SNS Deep Dive
    st.markdown("## 📡 Amazon Simple Notification Service (SNS)")
    
    sns_benefits = [
        {
            "title": "Message Filtering and Batching",
            "description": "Simplify architecture and reduce costs with targeted message delivery",
            "icon": "🔍"
        },
        {
            "title": "Message Ordering and Deduplication", 
            "description": "FIFO topics ensure ordered delivery and prevent duplicates",
            "icon": "📋"
        },
        {
            "title": "Event Capture and Fan-out",
            "description": "Native integration with 60+ AWS services for event-driven architectures",
            "icon": "🌟"
        },
        {
            "title": "Security and Privacy",
            "description": "Message encryption and VPC endpoints for secure communication",
            "icon": "🔒"
        },
        {
            "title": "Durability and Reliability",
            "description": "Message archiving, retry policies, and dead letter queues",
            "icon": "🛡️"
        },
        {
            "title": "Multi-Channel Notifications",
            "description": "SMS, email, and mobile push notifications to 200+ countries",
            "icon": "📱"
        }
    ]
    
    col1, col2 = st.columns(2)
    
    for i, benefit in enumerate(sns_benefits):
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            st.markdown(f"""
            <div class="comparison-card">
                <div style="display: flex; align-items: center;">
                    <div style="font-size: 1.5rem; margin-right: 1rem;">{benefit['icon']}</div>
                    <div>
                        <h5>{benefit['title']}</h5>
                        <p>{benefit['description']}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # SNS Fanout Pattern
    st.markdown("## 🌟 SNS Fanout Pattern Example")
    
    st.markdown("""
    <div class="architecture-section">
        <h4>📦 E-commerce Order Processing</h4>
        <p>When a new order is placed, multiple systems need to be notified simultaneously:</p>
        
        <div style="text-align: center; margin: 2rem 0;">
            <div style="font-size: 1.2rem; margin: 1rem;">
                📝 <strong>Order Placed</strong> → 📡 <strong>SNS Topic</strong> → 
            </div>
            <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
                <div style="background: #e8f5e8; padding: 1rem; border-radius: 8px;">
                    <strong>📬 SQS Queue</strong><br>
                    <small>Order Processing</small>
                </div>
                <div style="background: #e8f5e8; padding: 1rem; border-radius: 8px;">
                    <strong>📬 SQS Queue</strong><br>
                    <small>Inventory Management</small>
                </div>
                <div style="background: #e8f5e8; padding: 1rem; border-radius: 8px;">
                    <strong>⚡ Lambda Function</strong><br>
                    <small>Email Notification</small>
                </div>
                <div style="background: #e8f5e8; padding: 1rem; border-radius: 8px;">
                    <strong>📊 Kinesis</strong><br>
                    <small>Analytics Pipeline</small>
                </div>
            </div>
        </div>
        
        <div class="info-highlight">
            <h5>💡 Benefits of Fanout Pattern:</h5>
            <ul>
                <li><strong>Parallel Processing:</strong> Multiple systems process simultaneously</li>
                <li><strong>Loose Coupling:</strong> Systems operate independently</li>
                <li><strong>Reliability:</strong> Individual system failures don't affect others</li>
                <li><strong>Scalability:</strong> Easy to add new subscribers</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_progress_check():
    st.markdown("# ✅ Week 2 Progress Check")
    
    # Overall Progress
    st.markdown("## 📊 Your Learning Progress")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <h3>8/8</h3>
            <p>Services Covered</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <h3>3/3</h3>
            <p>Architecture Patterns</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <h3>2/6</h3>
            <p>Sessions Complete</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Knowledge Check Quiz
    st.markdown("## 🧠 Knowledge Check")
    
    # Quiz questions
    with st.expander("📝 Quick Quiz - Test Your Understanding", expanded=True):
        
        q1 = st.radio(
            "1. Which AWS service is best for building serverless REST APIs?",
            ["AWS Lambda", "Amazon API Gateway", "Amazon CloudFront", "Amazon Route 53"],
            key="q1"
        )
        
        q2 = st.radio(
            "2. What is the maximum item size in Amazon DynamoDB?",
            ["100KB", "400KB", "1MB", "4MB"],
            key="q2"
        )
        
        q3 = st.radio(
            "3. Which invocation type is used when API Gateway calls Lambda?",
            ["Asynchronous", "Synchronous", "Stream-based", "Batch"],
            key="q3"
        )
        
        q4 = st.radio(
            "4. What pattern does SNS use for message distribution?",
            ["Point-to-Point", "Publish-Subscribe", "Request-Response", "Peer-to-Peer"],
            key="q4"
        )
        
        if st.button("Check Answers"):
            answers = {
                "q1": "Amazon API Gateway",
                "q2": "400KB", 
                "q3": "Synchronous",
                "q4": "Publish-Subscribe"
            }
            
            score = 0
            user_answers = [q1, q2, q3, q4]
            correct_answers = list(answers.values())
            
            for i, (user_ans, correct_ans) in enumerate(zip(user_answers, correct_answers)):
                if user_ans == correct_ans:
                    score += 1
                    st.success(f"Question {i+1}: ✅ Correct!")
                else:
                    st.error(f"Question {i+1}: ❌ Incorrect. Correct answer: {correct_ans}")
            
            st.markdown(f"""
            <div class="info-highlight">
                <h4>📊 Your Score: {score}/4 ({score/4*100:.0f}%)</h4>
                <p>{"🎉 Excellent work!" if score >= 3 else "📚 Review the material and try again!"}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Action Items
    st.markdown("## 📋 Action Items for Week 3")
    
    action_items = [
        {
            "task": "Complete Week 2 Digital Training",
            "status": "🔄 In Progress",
            "priority": "High"
        },
        {
            "task": "Practice DynamoDB hands-on labs",
            "status": "📝 Planned", 
            "priority": "High"
        },
        {
            "task": "Review Lambda invocation patterns",
            "status": "📝 Planned",
            "priority": "Medium"
        },
        {
            "task": "Build a simple serverless API",
            "status": "💡 Suggested",
            "priority": "Medium"
        }
    ]
    
    for item in action_items:
        priority_color = "#ff4444" if item["priority"] == "High" else "#ffaa00"
        st.markdown(f"""
        <div class="comparison-card" style="border-left-color: {priority_color}">
            <div style="display: flex; justify-content: between; align-items: center;">
                <div>
                    <h5>{item['task']}</h5>
                    <p>Status: {item['status']} | Priority: {item['priority']}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Resources
    st.markdown("## 📚 Additional Resources")
    
    resources = [
        {
            "title": "AWS Lambda Developer Guide",
            "url": "https://docs.aws.amazon.com/lambda/",
            "type": "Documentation"
        },
        {
            "title": "DynamoDB Best Practices", 
            "url": "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html",
            "type": "Best Practices"
        },
        {
            "title": "API Gateway Workshop",
            "url": "https://aws.amazon.com/getting-started/hands-on/build-serverless-web-app-lambda-apigateway-s3-dynamodb-cognito/",
            "type": "Workshop"
        },
        {
            "title": "Serverless Application Lens",
            "url": "https://docs.aws.amazon.com/wellarchitected/latest/serverless-applications-lens/welcome.html", 
            "type": "Architecture Guide"
        }
    ]
    
    col1, col2 = st.columns(2)
    
    for i, resource in enumerate(resources):
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            st.markdown(f"""
            <div class="service-card">
                <h5>{resource['title']}</h5>
                <p><strong>Type:</strong> {resource['type']}</p>
                <a href="{resource['url']}" target="_blank" style="color: #FF9900;">📖 Read More</a>
            </div>
            """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="footer">
        <h3>🚀 Great Progress!</h3>
        <p>You've completed Session 2 covering essential development services on AWS.</p>
        <p><strong>Next Session:</strong> Security, Deployment, and Debugging</p>
        <p style="margin-top: 1rem; font-size: 0.9em;">
            Keep up the excellent work on your certification journey! 🎯
        </p>
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