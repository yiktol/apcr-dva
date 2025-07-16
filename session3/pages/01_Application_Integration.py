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

# Page configuration
st.set_page_config(
    page_title="AWS Development with AWS Services",
    page_icon="🔧",
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
        
        .service-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            border: 2px solid {AWS_COLORS['light_blue']};
            margin: 15px 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
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
            - 📨 Amazon Simple Queue Service (SQS) - Message queuing for distributed systems
            - 📢 Amazon Simple Notification Service (SNS) - Pub/sub messaging service
            - 📅 Amazon EventBridge - Event-driven architecture service
            - 🚀 AWS AppSync - GraphQL API service for real-time applications
            
            **Learning Objectives:**
            - Master AWS messaging and event-driven services
            - Understand application integration patterns
            - Learn to build decoupled, scalable architectures
            - Practice with interactive examples and code samples
            """)

def create_messaging_overview_mermaid():
    """Create mermaid diagram for AWS messaging services overview"""
    return """
    graph TB
        subgraph "Event Stores"
            A[Message Queue<br/>Amazon SQS]
            B[Stream<br/>Amazon Kinesis<br/>Data Streams]
        end
        
        subgraph "Event Routers"
            C[Topic<br/>Amazon SNS]
            D[Bus<br/>Amazon EventBridge]
        end
        
        A --> E[Pull-based<br/>Messages]
        B --> F[Real-time<br/>Streaming]
        C --> G[Push-based<br/>Fan-out]
        D --> H[Event-driven<br/>Architecture]
        
        style A fill:#FF9900,stroke:#232F3E,color:#fff
        style B fill:#4B9EDB,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_sqs_workflow_mermaid():
    """Create mermaid diagram for SQS workflow"""
    return """
    graph LR
        A[📱 Producer] --> B[📨 SQS Queue]
        B --> C[👤 Consumer 1]
        B --> D[👤 Consumer 2]
        B --> E[👤 Consumer 3]
        
        F[⚡ Lambda Trigger] --> B
        B --> G[🔄 Auto Scaling Group]
        
        H[💀 Dead Letter Queue] --> B
        B --> I[☁️ CloudWatch Metrics]
        
        style A fill:#4B9EDB,stroke:#232F3E,color:#fff
        style B fill:#FF9900,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#3FB34F,stroke:#232F3E,color:#fff
        style E fill:#3FB34F,stroke:#232F3E,color:#fff
        style H fill:#FF6B35,stroke:#232F3E,color:#fff
    """

def create_sns_fanout_mermaid():
    """Create mermaid diagram for SNS fanout pattern"""
    return """
    graph TD
        A[📱 Publisher] --> B[📢 SNS Topic<br/>Order Notifications]
        
        B --> C[📨 SQS Queue<br/>Order Processing]
        B --> D[📨 SQS Queue<br/>Inventory Update]
        B --> E[📧 Email<br/>Customer Notification]
        B --> F[⚡ Lambda<br/>Analytics]
        B --> G[📱 Mobile Push<br/>App Notification]
        
        C --> H[🖥️ EC2 Instance<br/>Fulfillment]
        D --> I[🗄️ Database<br/>Inventory System]
        
        style A fill:#4B9EDB,stroke:#232F3E,color:#fff
        style B fill:#FF9900,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#3FB34F,stroke:#232F3E,color:#fff
        style E fill:#FF6B35,stroke:#232F3E,color:#fff
        style F fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_eventbridge_architecture_mermaid():
    """Create mermaid diagram for EventBridge architecture"""
    return """
    graph TB
        subgraph "Event Sources"
            A[🗄️ AWS Services]
            B[📱 Custom Applications]
            C[🔗 SaaS Partners]
        end
        
        A --> D[📅 EventBridge<br/>Custom Bus]
        B --> D
        C --> D
        
        D --> E{Event Rules<br/>& Filters}
        
        E --> F[⚡ Lambda Function]
        E --> G[📨 SQS Queue]
        E --> H[🗄️ DynamoDB]
        E --> I[📧 SNS Topic]
        E --> J[🔗 API Destination]
        
        style D fill:#FF9900,stroke:#232F3E,color:#fff
        style E fill:#4B9EDB,stroke:#232F3E,color:#fff
        style F fill:#232F3E,stroke:#FF9900,color:#fff
        style G fill:#3FB34F,stroke:#232F3E,color:#fff
    """

def create_appsync_architecture_mermaid():
    """Create mermaid diagram for AppSync architecture"""
    return """
    graph TB
        A[📱 Mobile App] --> B[🚀 AWS AppSync<br/>GraphQL API]
        C[🌐 Web App] --> B
        D[🖥️ Desktop App] --> B
        
        B --> E{GraphQL<br/>Resolvers}
        
        E --> F[🗄️ DynamoDB]
        E --> G[⚡ Lambda]
        E --> H[🔍 OpenSearch]
        E --> I[🗃️ RDS]
        
        B --> J[📡 Real-time<br/>Subscriptions]
        J --> K[📱 Live Updates]
        
        L[🔐 Amazon Cognito] --> B
        
        style B fill:#FF9900,stroke:#232F3E,color:#fff
        style E fill:#4B9EDB,stroke:#232F3E,color:#fff
        style J fill:#3FB34F,stroke:#232F3E,color:#fff
        style L fill:#232F3E,stroke:#FF9900,color:#fff
    """

def sqs_tab():
    """Content for Amazon SQS tab"""
    st.markdown("## 📨 Amazon Simple Queue Service (SQS)")
    st.markdown("*Fully managed message queuing for microservices, distributed systems, and serverless applications*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Amazon SQS** is a fully managed message queuing service that enables you to decouple and scale microservices, 
    distributed systems, and serverless applications. SQS eliminates the complexity and overhead associated with 
    managing and operating message-oriented middleware.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # SQS Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 256KB\n**Max Message Size**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 14 Days\n**Max Retention**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 3000\n**TPS Standard**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 300\n**TPS FIFO**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # SQS Workflow
    st.markdown("### 🔄 SQS Message Flow")
    common.mermaid(create_sqs_workflow_mermaid(), height=500)
    
    # Interactive Queue Configuration
    st.markdown("### 🛠️ Interactive SQS Queue Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Queue Settings")
        queue_type = st.selectbox("Queue Type:", ["Standard Queue", "FIFO Queue"])
        queue_name = st.text_input("Queue Name:", "my-application-queue")
        
        visibility_timeout = st.slider("Visibility Timeout (seconds):", 0, 900, 30)
        message_retention = st.slider("Message Retention (days):", 1, 14, 4)
        
        max_receive_count = st.slider("Max Receive Count (DLQ):", 1, 1000, 5)
    
    with col2:
        st.markdown("### ⚙️ Advanced Settings")
        delay_seconds = st.slider("Delivery Delay (seconds):", 0, 900, 0)
        receive_wait_time = st.slider("Receive Message Wait Time (seconds):", 0, 20, 0)
        
        content_based_dedup = False
        if queue_type == "FIFO Queue":
            content_based_dedup = st.checkbox("Content-Based Deduplication", value=False)
        
        encryption = st.checkbox("Server-Side Encryption (SSE)", value=True)
    
    if st.button("🚀 Create SQS Queue", use_container_width=True):
        # Calculate estimated costs and characteristics
        monthly_requests = 1000000  # 1M requests
        standard_cost = (monthly_requests / 1000000) * 0.40  # $0.40 per million
        fifo_cost = (monthly_requests / 1000000) * 0.50  # $0.50 per million
        
        estimated_cost = fifo_cost if queue_type == "FIFO Queue" else standard_cost
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ SQS Queue Configuration Complete!
        
        **Queue Details:**
        - **Name**: {queue_name}{'.' + 'fifo' if queue_type == 'FIFO Queue' else ''}
        - **Type**: {queue_type}
        - **Visibility Timeout**: {visibility_timeout} seconds
        - **Message Retention**: {message_retention} days
        - **DLQ Threshold**: {max_receive_count} failures
        
        **Performance Characteristics:**
        - **Throughput**: {'300 TPS' if queue_type == 'FIFO Queue' else '3,000+ TPS'}
        - **Ordering**: {'Guaranteed FIFO' if queue_type == 'FIFO Queue' else 'Best-effort ordering'}
        - **Deduplication**: {'✅ Enabled' if content_based_dedup else '❌ Disabled'}
        - **Encryption**: {'✅ SSE Enabled' if encryption else '❌ Disabled'}
        
        💰 **Estimated Cost**: ${estimated_cost:.2f}/month (1M requests)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Queue Types Comparison
    st.markdown("### ⚖️ Standard vs FIFO Queues")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📊 Standard Queues
        
        **Characteristics:**
        - **Unlimited throughput** - nearly unlimited TPS
        - **At-least-once delivery** - messages delivered at least once
        - **Best-effort ordering** - messages generally delivered in order
        - **Duplicate messages** - occasional duplicates possible
        
        **Best For:**
        - High-throughput applications
        - Processing tasks where duplicates are acceptable
        - Batch processing workloads
        - **Use Case**: Credit card validation requests
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 FIFO Queues
        
        **Characteristics:**
        - **Limited throughput** - up to 300 TPS
        - **Exactly-once processing** - no duplicate messages
        - **First-in-first-out delivery** - strict ordering
        - **Message deduplication** - automatic duplicate detection
        
        **Best For:**
        - Order-critical applications
        - Financial transactions
        - Inventory management
        - **Use Case**: Product price modifications
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Best Practices
    st.markdown("### 💡 SQS Best Practices")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ⏱️ Visibility Timeout Best Practices
        
        **Key Principle**: Set visibility timeout based on processing time
        
        - **Processing time 10s** → Set timeout to 15+ seconds
        - **Too short** → Duplicate processing of messages
        - **Too long** → Delayed retry on failures
        - **Dynamic adjustment** → Use ChangeMessageVisibility API
        
        **Example**: Web request processing takes 5 seconds, set timeout to 30 seconds for safety margin.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 💀 Dead Letter Queue Strategy
        
        **Key Principle**: Capture problematic messages for analysis
        
        - **Max receive count** → 3-5 attempts recommended
        - **Separate DLQ** → Create dedicated queue for failed messages
        - **Monitoring** → Set CloudWatch alarms on DLQ depth
        - **Analysis** → Review failed messages for patterns
        
        **Benefit**: Prevents poison pill messages from blocking processing.
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # SQS with Lambda Integration
    st.markdown("### ⚡ SQS with AWS Lambda Integration")
    
    lambda_integration_data = {
        'Integration Type': ['Event Source Mapping', 'Standard Queue', 'FIFO Queue'],
        'Polling Method': ['Long Polling', 'Automatic', 'Automatic'],
        'Batch Size': ['1-10 messages', '1-10 messages', '1-10 messages'],
        'Concurrency': ['Up to 1,000', 'Up to 1,000', 'Sequential processing'],
        'Use Case': ['Real-time processing', 'High throughput jobs', 'Ordered processing']
    }
    
    df_lambda = pd.DataFrame(lambda_integration_data)
    st.dataframe(df_lambda, use_container_width=True)
    
    # Performance Monitoring
    st.markdown("### 📊 SQS Performance Monitoring")
    
    # Simulate queue metrics
    time_range = pd.date_range(start='2025-07-14', end='2025-07-14 23:59', freq='H')
    np.random.seed(42)
    
    metrics_data = {
        'Time': time_range,
        'Messages Sent': np.random.poisson(100, len(time_range)),
        'Messages Received': np.random.poisson(95, len(time_range)),
        'Approximate Number of Messages': np.random.randint(10, 50, len(time_range)),
        'Number of Messages Deleted': np.random.poisson(90, len(time_range))
    }
    
    df_metrics = pd.DataFrame(metrics_data)
    
    fig = px.line(df_metrics, x='Time', y=['Messages Sent', 'Messages Received', 'Number of Messages Deleted'],
                  title='SQS Queue Metrics Over Time',
                  color_discrete_sequence=[AWS_COLORS['primary'], AWS_COLORS['light_blue'], AWS_COLORS['success']])
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Complete SQS Implementation")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Complete SQS implementation with best practices
import boto3
import json
import time
from datetime import datetime
from botocore.exceptions import ClientError

def create_sqs_queue_with_dlq(queue_name, is_fifo=False):
    """Create SQS queue with Dead Letter Queue configuration"""
    sqs = boto3.client('sqs')
    
    try:
        # Create Dead Letter Queue first
        dlq_name = f"{queue_name}-dlq"
        if is_fifo:
            dlq_name += ".fifo"
            
        dlq_attributes = {
            'MessageRetentionPeriod': '1209600',  # 14 days
        }
        
        if is_fifo:
            dlq_attributes.update({
                'FifoQueue': 'true',
                'ContentBasedDeduplication': 'true'
            })
        
        dlq_response = sqs.create_queue(
            QueueName=dlq_name,
            Attributes=dlq_attributes
        )
        dlq_url = dlq_response['QueueUrl']
        
        # Get DLQ ARN
        dlq_attrs = sqs.get_queue_attributes(
            QueueUrl=dlq_url,
            AttributeNames=['QueueArn']
        )
        dlq_arn = dlq_attrs['Attributes']['QueueArn']
        
        # Create main queue with DLQ configuration
        main_queue_name = queue_name
        if is_fifo:
            main_queue_name += ".fifo"
            
        queue_attributes = {
            'VisibilityTimeoutSeconds': '30',
            'MessageRetentionPeriod': '345600',  # 4 days
            'DelaySeconds': '0',
            'ReceiveMessageWaitTimeSeconds': '20',  # Long polling
            'RedrivePolicy': json.dumps({
                'deadLetterTargetArn': dlq_arn,
                'maxReceiveCount': 3
            })
        }
        
        if is_fifo:
            queue_attributes.update({
                'FifoQueue': 'true',
                'ContentBasedDeduplication': 'true'
            })
        
        main_response = sqs.create_queue(
            QueueName=main_queue_name,
            Attributes=queue_attributes
        )
        
        main_queue_url = main_response['QueueUrl']
        
        print(f"✅ Created queue: {main_queue_name}")
        print(f"✅ Created DLQ: {dlq_name}")
        print(f"Queue URL: {main_queue_url}")
        
        return main_queue_url, dlq_url
        
    except ClientError as e:
        print(f"❌ Error creating queue: {e}")
        return None, None

def send_message_with_attributes(queue_url, message_body, message_attributes=None, group_id=None):
    """Send message to SQS queue with optional attributes"""
    sqs = boto3.client('sqs')
    
    message_params = {
        'QueueUrl': queue_url,
        'MessageBody': message_body
    }
    
    # Add message attributes if provided
    if message_attributes:
        formatted_attributes = {}
        for key, value in message_attributes.items():
            if isinstance(value, str):
                formatted_attributes[key] = {
                    'StringValue': value,
                    'DataType': 'String'
                }
            elif isinstance(value, (int, float)):
                formatted_attributes[key] = {
                    'StringValue': str(value),
                    'DataType': 'Number'
                }
        
        message_params['MessageAttributes'] = formatted_attributes
    
    # Add FIFO-specific parameters
    if group_id:
        message_params['MessageGroupId'] = group_id
        # Generate deduplication ID based on content
        import hashlib
        content_hash = hashlib.md5(message_body.encode()).hexdigest()
        message_params['MessageDeduplicationId'] = content_hash
    
    try:
        response = sqs.send_message(**message_params)
        print(f"✅ Message sent: {response['MessageId']}")
        return response['MessageId']
        
    except ClientError as e:
        print(f"❌ Error sending message: {e}")
        return None

def process_messages_batch(queue_url, processor_function, max_messages=10):
    """Process messages from SQS queue in batches"""
    sqs = boto3.client('sqs')
    
    try:
        while True:
            # Receive messages with long polling
            response = sqs.receive_message(
                QueueUrl=queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=20,  # Long polling
                MessageAttributeNames=['All'],
                AttributeNames=['All']
            )
            
            messages = response.get('Messages', [])
            
            if not messages:
                print("No messages available")
                break
            
            print(f"📨 Processing {len(messages)} messages...")
            
            # Process messages
            successful_deletes = []
            failed_messages = []
            
            for message in messages:
                try:
                    # Process the message
                    result = processor_function(message)
                    
                    if result:
                        # Mark for deletion if processing successful
                        successful_deletes.append({
                            'Id': message['MessageId'],
                            'ReceiptHandle': message['ReceiptHandle']
                        })
                    else:
                        failed_messages.append(message['MessageId'])
                        
                except Exception as e:
                    print(f"❌ Error processing message {message['MessageId']}: {e}")
                    failed_messages.append(message['MessageId'])
            
            # Batch delete successful messages
            if successful_deletes:
                try:
                    delete_response = sqs.delete_message_batch(
                        QueueUrl=queue_url,
                        Entries=successful_deletes
                    )
                    
                    print(f"✅ Deleted {len(successful_deletes)} messages successfully")
                    
                    if 'Failed' in delete_response:
                        print(f"⚠️ Failed to delete {len(delete_response['Failed'])} messages")
                        
                except ClientError as e:
                    print(f"❌ Error deleting messages: {e}")
            
            if failed_messages:
                print(f"⚠️ Failed to process {len(failed_messages)} messages")
            
            # Continue processing if there might be more messages
            if len(messages) < max_messages:
                break
                
    except KeyboardInterrupt:
        print("🛑 Processing stopped by user")
    except ClientError as e:
        print(f"❌ Error receiving messages: {e}")

def example_message_processor(message):
    """Example message processor function"""
    try:
        # Parse message body
        message_body = json.loads(message['Body'])
        
        print(f"Processing order: {message_body.get('order_id', 'unknown')}")
        
        # Simulate processing time
        time.sleep(0.5)
        
        # Extract message attributes
        attributes = message.get('MessageAttributes', {})
        priority = attributes.get('Priority', {}).get('StringValue', 'normal')
        
        print(f"Order priority: {priority}")
        
        # Simulate random failures for testing DLQ
        import random
        if random.random() < 0.1:  # 10% failure rate
            raise Exception("Simulated processing error")
        
        return True  # Success
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        return False  # Failure - message will be retried

def monitor_queue_metrics(queue_url):
    """Monitor SQS queue metrics using CloudWatch"""
    cloudwatch = boto3.client('cloudwatch')
    sqs = boto3.client('sqs')
    
    # Extract queue name from URL
    queue_name = queue_url.split('/')[-1]
    
    try:
        from datetime import timedelta
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        
        metrics_to_check = [
            'NumberOfMessagesSent',
            'NumberOfMessagesReceived', 
            'NumberOfMessagesDeleted',
            'ApproximateNumberOfVisibleMessages'
        ]
        
        print(f"📊 Queue Metrics for {queue_name}:")
        print("-" * 50)
        
        for metric_name in metrics_to_check:
            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/SQS',
                MetricName=metric_name,
                Dimensions=[
                    {'Name': 'QueueName', 'Value': queue_name}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,  # 5 minutes
                Statistics=['Sum', 'Average']
            )
            
            if response['Datapoints']:
                latest = max(response['Datapoints'], key=lambda x: x['Timestamp'])
                value = latest.get('Sum', latest.get('Average', 0))
                print(f"{metric_name}: {value}")
            else:
                print(f"{metric_name}: No data")
        
        # Get current queue attributes
        attrs = sqs.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['All']
        )
        
        attributes = attrs['Attributes']
        print(f"\nCurrent Queue State:")
        print(f"Visible Messages: {attributes.get('ApproximateNumberOfMessages', 0)}")
        print(f"In Flight Messages: {attributes.get('ApproximateNumberOfMessagesNotVisible', 0)}")
        print(f"DLQ Messages: {attributes.get('ApproximateNumberOfMessagesDelayed', 0)}")
        
    except ClientError as e:
        print(f"❌ Error getting metrics: {e}")

# Example usage
def main_sqs_example():
    # Create queue with DLQ
    queue_url, dlq_url = create_sqs_queue_with_dlq('order-processing', is_fifo=False)
    
    if queue_url:
        # Send test messages
        for i in range(5):
            order_data = {
                'order_id': f'ORD-{i+1:03d}',
                'customer_id': f'CUST-{i+1}',
                'total_amount': round(50 + i * 10.5, 2),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            message_attrs = {
                'Priority': 'high' if i < 2 else 'normal',
                'CustomerTier': 'premium' if i % 2 == 0 else 'standard'
            }
            
            send_message_with_attributes(
                queue_url, 
                json.dumps(order_data),
                message_attrs
            )
        
        print(f"\n🔄 Starting message processing...")
        
        # Process messages
        process_messages_batch(queue_url, example_message_processor)
        
        # Monitor metrics
        monitor_queue_metrics(queue_url)

# Run the example
if __name__ == "__main__":
    main_sqs_example()
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def sns_tab():
    """Content for Amazon SNS tab"""
    st.markdown("## 📢 Amazon Simple Notification Service (SNS)")
    st.markdown("*Fully managed pub/sub messaging, SMS, email, and mobile push notifications*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Amazon SNS** is a managed service that provides message delivery from publishers to subscribers (producers and consumers). 
    Publishers communicate asynchronously with subscribers by sending messages to a topic, which is a logical access point 
    and communication channel.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # SNS Benefits
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### ∞\n**Unlimited Throughput**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 256KB\n**Max Message Size**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 100M\n**Subscribers per Topic**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 99.9%\n**SLA Availability**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # SNS Fanout Pattern
    st.markdown("### 🌟 SNS Fanout Pattern")
    common.mermaid(create_sns_fanout_mermaid(), height=500)
    
    # Interactive SNS Topic Configuration
    st.markdown("### 🛠️ Interactive SNS Topic Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Topic Settings")
        topic_name = st.text_input("Topic Name:", "order-notifications")
        topic_type = st.selectbox("Topic Type:", ["Standard Topic", "FIFO Topic"])
        
        display_name = st.text_input("Display Name:", "Order Notification System")
        delivery_policy = st.selectbox("Delivery Policy:", [
            "Immediate Delivery", "Retry with Backoff", "Custom Retry Policy"
        ])
    
    with col2:
        st.markdown("### 🔧 Subscription Settings")
        subscription_types = st.multiselect("Subscription Types:", [
            "Email", "SMS", "HTTP/HTTPS", "SQS", "Lambda", "Mobile Push", "Kinesis Data Firehose"
        ], default=["Email", "SQS", "Lambda"])
        
        message_filtering = st.checkbox("Enable Message Filtering", value=True)
        encryption = st.checkbox("Server-Side Encryption", value=True)
    
    # Advanced Configuration
    st.markdown("### ⚙️ Advanced Topic Configuration")
    
    col3, col4 = st.columns(2)
    
    with col3:
        content_based_dedup = False
        if topic_type == "FIFO Topic":
            content_based_dedup = st.checkbox("Content-Based Deduplication", value=True)
        
        dead_letter_queue = st.checkbox("Configure Dead Letter Queue", value=True)
    
    with col4:
        delivery_status_logging = st.multiselect("Delivery Status Logging:", [
            "Lambda", "SQS", "HTTP/HTTPS", "SMS", "Email"
        ])
    
    if st.button("🚀 Create SNS Topic and Subscriptions", use_container_width=True):
        # Calculate estimated costs
        monthly_publishes = 1000000  # 1M publishes
        monthly_notifications = len(subscription_types) * monthly_publishes
        
        # SNS pricing (simplified)
        publish_cost = (monthly_publishes / 1000000) * 0.50  # $0.50 per million
        notification_cost = (monthly_notifications / 1000000) * 0.50
        sms_cost = 0.75 * (monthly_publishes / 1000) if "SMS" in subscription_types else 0
        
        total_cost = publish_cost + notification_cost + sms_cost
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ SNS Topic Configuration Complete!
        
        **Topic Details:**
        - **Name**: {topic_name}
        - **Type**: {topic_type}
        - **Display Name**: {display_name}
        - **ARN**: arn:aws:sns:us-east-1:123456789012:{topic_name}
        
        **Subscriptions Configured:**
        {chr(10).join([f"  - {sub_type}" for sub_type in subscription_types])}
        
        **Features Enabled:**
        - **Message Filtering**: {'✅ Enabled' if message_filtering else '❌ Disabled'}
        - **Encryption**: {'✅ SSE Enabled' if encryption else '❌ Disabled'}
        - **DLQ**: {'✅ Configured' if dead_letter_queue else '❌ Not configured'}
        - **Delivery Logging**: {'✅ ' + ', '.join(delivery_status_logging) if delivery_status_logging else '❌ Disabled'}
        
        💰 **Estimated Monthly Cost**: ${total_cost:.2f} (1M messages)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # SNS Benefits Deep Dive
    st.markdown("### ✨ Key SNS Benefits")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🚀 Simplify & Reduce Costs
        - **Message filtering** - subscribers get only relevant messages
        - **Message batching** - up to 10 messages per API call
        - **Reduced complexity** - no message broker management
        - **Pay-per-use** - no fixed costs
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 Ensure Accuracy
        - **Message ordering** with FIFO topics
        - **Message deduplication** prevents duplicates
        - **Exactly-once delivery** for FIFO topics
        - **Delivery status tracking** for all protocols
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🛡️ Increase Security
        - **Message encryption** with 256-bit AES-GCM
        - **VPC endpoints** via AWS PrivateLink
        - **Access control** with IAM policies
        - **Message privacy** with encryption at rest/transit
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Message Filtering Demo
    st.markdown("### 🔍 Interactive Message Filtering Demo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📝 Message Attributes")
        location = st.selectbox("Location:", ["us-west", "us-east", "eu-west", "eu-east"])
        order_type = st.selectbox("Order Type:", ["premium", "standard", "express"])
        amount = st.slider("Order Amount ($):", 0, 1000, 100)
        customer_tier = st.selectbox("Customer Tier:", ["gold", "silver", "bronze"])
    
    with col2:
        st.markdown("### 🎯 Filter Policies")
        
        # Sample filter policies
        filter_policies = {
            "US Orders Queue": {
                "location": ["us-west", "us-east"]
            },
            "EU Orders Queue": {
                "location": ["eu-west", "eu-east"]  
            },
            "Premium Orders Queue": {
                "order_type": ["premium", "express"],
                "amount": [{"numeric": [">", 200]}]
            },
            "VIP Customers Queue": {
                "customer_tier": ["gold"]
            }
        }
        
        for queue_name, policy in filter_policies.items():
            st.code(f"{queue_name}:\n{json.dumps(policy, indent=2)}", language="json")
    
    if st.button("🧪 Test Message Filtering", use_container_width=True):
        # Test message against filter policies
        test_message = {
            "location": location,
            "order_type": order_type,
            "amount": amount,
            "customer_tier": customer_tier
        }
        
        matching_queues = []
        
        # Check each filter policy
        for queue_name, policy in filter_policies.items():
            match = True
            
            for attr, conditions in policy.items():
                if attr == "amount":
                    # Handle numeric conditions
                    for condition in conditions:
                        if isinstance(condition, dict) and "numeric" in condition:
                            operator, threshold = condition["numeric"]
                            if operator == ">" and amount <= threshold:
                                match = False
                                break
                else:
                    # Handle string/list conditions
                    if test_message[attr] not in conditions:
                        match = False
                        break
            
            if match:
                matching_queues.append(queue_name)
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 🎯 Message Filtering Results
        
        **Test Message:**
        ```json
        {json.dumps(test_message, indent=2)}
        ```
        
        **Matching Subscriptions:**
        {chr(10).join([f"✅ {queue}" for queue in matching_queues]) if matching_queues else "❌ No matching subscriptions"}
        
        **Filter Efficiency**: {len(matching_queues)}/4 subscriptions matched
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # SNS Subscription Types
    st.markdown("### 📡 SNS Subscription Types & Use Cases")
    
    subscription_data = {
        'Subscription Type': ['Email', 'SMS', 'HTTP/HTTPS', 'SQS', 'Lambda', 'Mobile Push', 'Kinesis Data Firehose'],
        'Delivery Method': ['SMTP', 'SMS Gateway', 'HTTP POST', 'Queue Message', 'Function Invoke', 'Push Service', 'Data Stream'],
        'Use Case': [
            'Admin notifications',
            'User alerts & OTP',
            'Webhook integration', 
            'Async processing',
            'Event processing',
            'App notifications',
            'Data analytics'
        ],
        'Cost (per 1M)': ['$2.00', '$0.75', '$0.60', '$0.50', '$0.20', '$0.50', '$0.50'],
        'Max Message Size': ['256KB', '1600 chars', '256KB', '256KB', '256KB', '4KB', '256KB']
    }
    
    df_subscriptions = pd.DataFrame(subscription_data)
    st.dataframe(df_subscriptions, use_container_width=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Complete SNS Implementation")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Complete SNS implementation with filtering and multiple subscription types
import boto3
import json
from datetime import datetime
from botocore.exceptions import ClientError

def create_sns_topic_with_subscriptions(topic_name, is_fifo=False):
    """Create SNS topic with multiple subscription types and filtering"""
    sns = boto3.client('sns')
    sqs = boto3.client('sqs')
    
    try:
        # Create SNS topic
        topic_attributes = {}
        
        if is_fifo:
            topic_name += '.fifo'
            topic_attributes.update({
                'FifoTopic': 'true',
                'ContentBasedDeduplication': 'true'
            })
        
        # Add encryption
        topic_attributes['KmsMasterKeyId'] = 'alias/aws/sns'
        
        response = sns.create_topic(
            Name=topic_name,
            Attributes=topic_attributes
        )
        
        topic_arn = response['TopicArn']
        print(f"✅ Created topic: {topic_arn}")
        
        # Set display name
        sns.set_topic_attributes(
            TopicArn=topic_arn,
            AttributeName='DisplayName',
            AttributeValue='Order Processing Notifications'
        )
        
        # Create SQS queues for different message types
        queue_configs = [
            {
                'name': 'us-orders-queue',
                'filter_policy': {
                    'location': ['us-west', 'us-east']
                }
            },
            {
                'name': 'eu-orders-queue', 
                'filter_policy': {
                    'location': ['eu-west', 'eu-east']
                }
            },
            {
                'name': 'premium-orders-queue',
                'filter_policy': {
                    'order_type': ['premium', 'express'],
                    'amount': [{'numeric': ['>', 200]}]
                }
            }
        ]
        
        # Create queues and subscriptions
        subscriptions = []
        
        for queue_config in queue_configs:
            # Create SQS queue
            queue_response = sqs.create_queue(
                QueueName=queue_config['name'],
                Attributes={
                    'MessageRetentionPeriod': '1209600',  # 14 days
                    'ReceiveMessageWaitTimeSeconds': '20'  # Long polling
                }
            )
            
            queue_url = queue_response['QueueUrl']
            
            # Get queue ARN
            queue_attrs = sqs.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=['QueueArn']
            )
            queue_arn = queue_attrs['Attributes']['QueueArn']
            
            # Allow SNS to send messages to SQS
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "sns.amazonaws.com"},
                        "Action": "sqs:SendMessage",
                        "Resource": queue_arn,
                        "Condition": {
                            "ArnEquals": {
                                "aws:SourceArn": topic_arn
                            }
                        }
                    }
                ]
            }
            
            sqs.set_queue_attributes(
                QueueUrl=queue_url,
                Attributes={
                    'Policy': json.dumps(policy)
                }
            )
            
            # Subscribe queue to SNS topic
            sub_response = sns.subscribe(
                TopicArn=topic_arn,
                Protocol='sqs',
                Endpoint=queue_arn
            )
            
            subscription_arn = sub_response['SubscriptionArn']
            
            # Apply message filter policy
            sns.set_subscription_attributes(
                SubscriptionArn=subscription_arn,
                AttributeName='FilterPolicy',
                AttributeValue=json.dumps(queue_config['filter_policy'])
            )
            
            subscriptions.append({
                'queue_name': queue_config['name'],
                'queue_url': queue_url,
                'subscription_arn': subscription_arn,
                'filter_policy': queue_config['filter_policy']
            })
            
            print(f"✅ Created subscription for {queue_config['name']}")
        
        return topic_arn, subscriptions
        
    except ClientError as e:
        print(f"❌ Error creating topic: {e}")
        return None, []

def publish_message_with_attributes(topic_arn, message, attributes, group_id=None):
    """Publish message to SNS topic with attributes for filtering"""
    sns = boto3.client('sns')
    
    try:
        # Format message attributes for SNS
        message_attributes = {}
        for key, value in attributes.items():
            if isinstance(value, str):
                message_attributes[key] = {
                    'DataType': 'String',
                    'StringValue': value
                }
            elif isinstance(value, (int, float)):
                message_attributes[key] = {
                    'DataType': 'Number',
                    'StringValue': str(value)
                }
        
        publish_params = {
            'TopicArn': topic_arn,
            'Message': json.dumps(message) if isinstance(message, dict) else message,
            'MessageAttributes': message_attributes
        }
        
        # Add FIFO-specific parameters
        if group_id:
            publish_params['MessageGroupId'] = group_id
            
            # Generate deduplication ID
            import hashlib
            content = json.dumps(message, sort_keys=True)
            dedup_id = hashlib.md5(content.encode()).hexdigest()
            publish_params['MessageDeduplicationId'] = dedup_id
        
        # Add subject for email subscriptions
        if 'order_id' in (message if isinstance(message, dict) else {}):
            order_data = message if isinstance(message, dict) else {}
            publish_params['Subject'] = f"Order Update: {order_data.get('order_id', 'Unknown')}"
        
        response = sns.publish(**publish_params)
        
        print(f"✅ Published message: {response['MessageId']}")
        return response['MessageId']
        
    except ClientError as e:
        print(f"❌ Error publishing message: {e}")
        return None

def monitor_topic_metrics(topic_arn):
    """Monitor SNS topic metrics"""
    cloudwatch = boto3.client('cloudwatch')
    
    # Extract topic name from ARN
    topic_name = topic_arn.split(':')[-1]
    
    try:
        from datetime import timedelta
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        
        metrics = [
            'NumberOfMessagesPublished',
            'NumberOfNotificationsDelivered',
            'NumberOfNotificationsFailed'
        ]
        
        print(f"📊 SNS Topic Metrics for {topic_name}:")
        print("-" * 50)
        
        for metric_name in metrics:
            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/SNS',
                MetricName=metric_name,
                Dimensions=[
                    {'Name': 'TopicName', 'Value': topic_name}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Sum']
            )
            
            if response['Datapoints']:
                total = sum([dp['Sum'] for dp in response['Datapoints']])
                print(f"{metric_name}: {total}")
            else:
                print(f"{metric_name}: No data")
        
        # Get subscription counts
        sns = boto3.client('sns')
        subscriptions = sns.list_subscriptions_by_topic(TopicArn=topic_arn)
        
        print(f"\nSubscription Summary:")
        sub_counts = {}
        for sub in subscriptions['Subscriptions']:
            protocol = sub['Protocol']
            sub_counts[protocol] = sub_counts.get(protocol, 0) + 1
        
        for protocol, count in sub_counts.items():
            print(f"{protocol.upper()}: {count} subscriptions")
            
    except ClientError as e:
        print(f"❌ Error getting metrics: {e}")

def process_orders_example():
    """Example: E-commerce order processing with SNS"""
    
    # Create topic and subscriptions
    topic_arn, subscriptions = create_sns_topic_with_subscriptions('order-notifications')
    
    if not topic_arn:
        return
    
    # Sample orders to publish
    sample_orders = [
        {
            'order': {
                'order_id': 'ORD-001',
                'customer_id': 'CUST-12345',
                'total': 299.99,
                'status': 'confirmed',
                'timestamp': datetime.utcnow().isoformat()
            },
            'attributes': {
                'location': 'us-west',
                'order_type': 'premium',
                'amount': 299.99,
                'customer_tier': 'gold'
            }
        },
        {
            'order': {
                'order_id': 'ORD-002', 
                'customer_id': 'CUST-67890',
                'total': 49.99,
                'status': 'confirmed',
                'timestamp': datetime.utcnow().isoformat()
            },
            'attributes': {
                'location': 'eu-west',
                'order_type': 'standard',
                'amount': 49.99,
                'customer_tier': 'silver'
            }
        },
        {
            'order': {
                'order_id': 'ORD-003',
                'customer_id': 'CUST-11111',
                'total': 599.99,
                'status': 'confirmed', 
                'timestamp': datetime.utcnow().isoformat()
            },
            'attributes': {
                'location': 'us-east',
                'order_type': 'express',
                'amount': 599.99,
                'customer_tier': 'gold'
            }
        }
    ]
    
    # Publish orders
    print("📤 Publishing order notifications...")
    for order_data in sample_orders:
        message_id = publish_message_with_attributes(
            topic_arn,
            order_data['order'],
            order_data['attributes']
        )
        
        if message_id:
            print(f"   Order {order_data['order']['order_id']} published")
    
    print("\n⏳ Waiting for message processing...")
    import time
    time.sleep(5)
    
    # Check messages in queues
    print("\n📥 Checking message distribution:")
    sqs = boto3.client('sqs')
    
    for subscription in subscriptions:
        try:
            response = sqs.get_queue_attributes(
                QueueUrl=subscription['queue_url'],
                AttributeNames=['ApproximateNumberOfMessages']
            )
            
            message_count = response['Attributes']['ApproximateNumberOfMessages']
            print(f"   {subscription['queue_name']}: {message_count} messages")
            
        except ClientError as e:
            print(f"   ❌ Error checking {subscription['queue_name']}: {e}")
    
    # Monitor metrics
    print()
    monitor_topic_metrics(topic_arn)

# Run the example
if __name__ == "__main__":
    process_orders_example()
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def eventbridge_tab():
    """Content for Amazon EventBridge tab"""
    st.markdown("## 📅 Amazon EventBridge")
    st.markdown("*Serverless event bus for building event-driven applications at scale*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Amazon EventBridge** (formerly CloudWatch Events) is a serverless event bus that makes it easier to build 
    event-driven applications at scale. EventBridge works with other AWS services to process events or invoke 
    an AWS resource as the target of a rule.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # EventBridge Features
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 90+\n**AWS Services**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 30+\n**SaaS Partners**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 300\n**Rules per Bus**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 5\n**Targets per Rule**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # EventBridge Architecture
    st.markdown("### 🏗️ EventBridge Architecture")
    common.mermaid(create_eventbridge_architecture_mermaid(), height=600)
    
    # Interactive Event Rule Builder
    st.markdown("### 🛠️ Interactive Event Rule Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Event Source Configuration")
        event_bus = st.selectbox("Event Bus:", [
            "default (AWS Services)", "custom-application-bus", "partner-event-bus"
        ])
        
        event_source = st.selectbox("Event Source:", [
            "AWS EC2", "AWS S3", "AWS Lambda", "Custom Application", "Stripe", "Shopify"
        ])
        
        event_pattern_type = st.selectbox("Event Pattern Type:", [
            "State Change", "Scheduled Event", "API Call", "Custom Event"
        ])
    
    with col2:
        st.markdown("### 🎯 Event Pattern")
        
        if event_source == "AWS EC2":
            detail_type = st.selectbox("Detail Type:", [
                "EC2 Instance State-change Notification",
                "EBS Volume Notification",
                "EBS Snapshot Notification"
            ])
            
            if "Instance State-change" in detail_type:
                state_filter = st.multiselect("Instance States:", [
                    "pending", "running", "stopping", "stopped", "terminated"
                ], default=["stopped", "terminated"])
        
        elif event_source == "AWS S3":
            detail_type = st.selectbox("Detail Type:", [
                "Object Created", "Object Deleted", "Object Restore Completed"
            ])
            
            bucket_name = st.text_input("Bucket Name:", "my-application-bucket")
            object_prefix = st.text_input("Object Prefix (optional):", "uploads/")
        
        elif event_source == "Custom Application":
            detail_type = st.text_input("Custom Detail Type:", "user-signup")
            custom_source = st.text_input("Custom Source:", "myapp.users")
    
    # Event Targets Configuration
    st.markdown("### 🎯 Event Targets Configuration")
    
    col3, col4 = st.columns(2)
    
    with col3:
        target_types = st.multiselect("Target Types:", [
            "Lambda Function", "SQS Queue", "SNS Topic", "Step Functions", 
            "ECS Task", "Systems Manager", "API Gateway"
        ], default=["Lambda Function", "SQS Queue"])
    
    with col4:
        dlq_enabled = st.checkbox("Enable Dead Letter Queue", value=True)
        retry_policy = st.selectbox("Retry Policy:", [
            "Default (24 hours, exponential backoff)",
            "Custom Retry Configuration", 
            "No Retries"
        ])
    
    # Advanced Event Pattern
    st.markdown("### 🔧 Advanced Event Pattern Configuration")
    
    with st.expander("Event Pattern JSON", expanded=False):
        if event_source == "AWS EC2" and "Instance State-change" in detail_type:
            event_pattern = {
                "source": ["aws.ec2"],
                "detail-type": ["EC2 Instance State-change Notification"],
                "detail": {
                    "state": state_filter
                }
            }
        elif event_source == "AWS S3":
            event_pattern = {
                "source": ["aws.s3"],
                "detail-type": [detail_type],
                "detail": {
                    "bucket": {"name": [bucket_name]},
                    "object": {"key": [{"prefix": object_prefix}]} if object_prefix else {}
                }
            }
        else:
            event_pattern = {
                "source": [custom_source if event_source == "Custom Application" else f"aws.{event_source.lower()}"],
                "detail-type": [detail_type]
            }
        
        st.code(json.dumps(event_pattern, indent=2), language="json")
    
    if st.button("🚀 Create EventBridge Rule", use_container_width=True):
        # Calculate estimated costs
        monthly_events = 1000000  # 1M events
        custom_bus_cost = 1.00 if "custom" in event_bus else 0  # $1 per million custom events
        targets_cost = len(target_types) * 0.20  # $0.20 per million invocations per target
        
        total_cost = custom_bus_cost + targets_cost
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ EventBridge Rule Created Successfully!
        
        **Rule Configuration:**
        - **Event Bus**: {event_bus}
        - **Event Source**: {event_source}
        - **Event Pattern**: {detail_type}
        - **Rule Name**: {event_source.lower().replace(' ', '-')}-{detail_type.lower().replace(' ', '-')}-rule
        
        **Targets Configured:**
        {chr(10).join([f"  - {target}" for target in target_types])}
        
        **Features:**
        - **Dead Letter Queue**: {'✅ Enabled' if dlq_enabled else '❌ Disabled'}
        - **Retry Policy**: {retry_policy}
        - **Event Filtering**: ✅ Pattern-based filtering
        
        💰 **Estimated Monthly Cost**: ${total_cost:.2f} (1M events)
        ⚡ **Latency**: < 5 seconds end-to-end
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # EventBridge Use Cases
    st.markdown("### 🌟 Common EventBridge Use Cases")
    
    use_cases_data = {
        'Use Case': [
            'Application Integration',
            'Microservices Orchestration', 
            'Data Pipeline Automation',
            'Security Monitoring',
            'Customer Experience',
            'DevOps Automation'
        ],
        'Event Source': [
            'Custom Applications',
            'AWS Services',
            'S3, DynamoDB, Kinesis',
            'CloudTrail, GuardDuty',
            'SaaS Partners',
            'CodePipeline, CodeBuild'
        ],
        'Common Targets': [
            'Lambda, SQS, Step Functions',
            'ECS, Lambda, SNS',
            'Lambda, Step Functions, Glue',
            'SNS, Lambda, Security Hub',
            'SNS, SES, Lambda',
            'Lambda, SNS, Step Functions'
        ],
        'Business Value': [
            'Loose coupling, scalability',
            'Event-driven architecture',
            'Automated data processing',
            'Real-time threat response',
            'Personalized experiences',
            'Automated deployments'
        ]
    }
    
    df_use_cases = pd.DataFrame(use_cases_data)
    st.dataframe(df_use_cases, use_container_width=True)
    
    # EventBridge Patterns
    st.markdown("### 🎨 EventBridge Design Patterns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔄 Event Replication Pattern
        
        **Use Case**: Replicate events across regions or accounts
        
        **Implementation**:
        - Source account publishes to custom bus
        - Cross-account/region rule forwards events
        - Target account processes events locally
        
        **Benefits**:
        - Disaster recovery
        - Multi-region processing
        - Account isolation
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🌊 Event Enrichment Pattern
        
        **Use Case**: Add context to events before processing
        
        **Implementation**:
        - Lambda function receives event
        - Enriches with additional data (DynamoDB, API)
        - Publishes enriched event to EventBridge
        
        **Benefits**:
        - Simplified downstream processing
        - Centralized enrichment logic
        - Event standardization
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Event Filtering Examples
    st.markdown("### 🔍 Advanced Event Filtering Examples")
    
    filtering_examples = {
        'Filter Type': ['Exact Match', 'Prefix Match', 'Numeric Range', 'Exists Check', 'Complex Logic'],
        'JSON Pattern': [
            '{"account": ["123456789012"]}',
            '{"detail": {"bucket": {"name": [{"prefix": "images-"}]}}}',
            '{"detail": {"temperature": [{"numeric": [">", 25, "<=", 100]}]}}',
            '{"detail": {"error": [{"exists": true}]}}',
            '{"$or": [{"account": ["123"]}, {"source": ["myapp"]}]}'
        ],
        'Use Case': [
            'Account-specific processing',
            'Bucket prefix filtering',
            'Temperature monitoring',
            'Error event detection', 
            'Multiple condition matching'
        ]
    }
    
    df_filtering = pd.DataFrame(filtering_examples)
    st.dataframe(df_filtering, use_container_width=True)
    
    # Real-time Event Simulator
    st.markdown("### 🎮 Real-time Event Processing Simulator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Event Generation")
        event_rate = st.slider("Events per second:", 1, 100, 10)
        event_types = st.multiselect("Event Types:", [
            "user-signup", "order-placed", "payment-processed", "inventory-low", "error-occurred"
        ], default=["user-signup", "order-placed"])
    
    with col2:
        st.markdown("### ⚙️ Processing Configuration")
        target_lambda = st.checkbox("Process with Lambda", value=True)
        store_in_sqs = st.checkbox("Store in SQS", value=True)
        alert_on_error = st.checkbox("SNS alerts for errors", value=True)
    
    if st.button("▶️ Start Event Simulation", use_container_width=True):
        # Simulate event processing metrics
        processing_time = np.random.uniform(10, 100, len(event_types))
        success_rate = np.random.uniform(95, 99.9, len(event_types))
        
        simulation_data = {
            'Event Type': event_types,
            'Processing Time (ms)': [f"{t:.1f}" for t in processing_time],
            'Success Rate (%)': [f"{s:.1f}" for s in success_rate],
            'Throughput (TPS)': [f"{event_rate * s/100:.1f}" for s in success_rate]
        }
        
        df_simulation = pd.DataFrame(simulation_data)
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 🎯 Event Processing Simulation Results
        
        **Configuration:**
        - **Event Rate**: {event_rate} events/second
        - **Active Targets**: {sum([target_lambda, store_in_sqs, alert_on_error])}
        - **Event Types**: {len(event_types)}
        
        **Performance Metrics:**
        """)
        st.dataframe(df_simulation, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Complete EventBridge Implementation")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Complete EventBridge implementation with custom bus and multiple targets
import boto3
import json
from datetime import datetime
from botocore.exceptions import ClientError

def create_custom_event_bus_with_rules(bus_name, rules_config):
    """Create custom EventBridge bus with rules and targets"""
    eventbridge = boto3.client('events')
    
    try:
        # Create custom event bus
        bus_response = eventbridge.create_event_bus(
            Name=bus_name,
            Tags=[
                {'Key': 'Environment', 'Value': 'Production'},
                {'Key': 'Application', 'Value': 'OrderProcessing'}
            ]
        )
        
        bus_arn = bus_response['EventBusArn']
        print(f"✅ Created event bus: {bus_name}")
        print(f"Bus ARN: {bus_arn}")
        
        created_rules = []
        
        # Create rules for the bus
        for rule_config in rules_config:
            rule_name = rule_config['name']
            
            # Create the rule
            rule_response = eventbridge.put_rule(
                Name=rule_name,
                EventPattern=json.dumps(rule_config['event_pattern']),
                State='ENABLED',
                Description=rule_config.get('description', 'EventBridge rule'),
                EventBusName=bus_name
            )
            
            rule_arn = rule_response['RuleArn']
            print(f"✅ Created rule: {rule_name}")
            
            # Add targets to the rule
            targets = []
            target_id = 1
            
            for target_config in rule_config['targets']:
                target = {
                    'Id': str(target_id),
                    'Arn': target_config['arn']
                }
                
                # Add specific configurations based on target type
                if 'lambda' in target_config['arn']:
                    # Lambda target configuration
                    target['DeadLetterConfig'] = {
                        'Arn': target_config.get('dlq_arn')
                    } if target_config.get('dlq_arn') else {}
                    
                elif 'sqs' in target_config['arn']:
                    # SQS target configuration
                    target['SqsParameters'] = {
                        'MessageGroupId': target_config.get('message_group_id', 'default')
                    } if target_config.get('message_group_id') else {}
                
                elif 'states' in target_config['arn']:
                    # Step Functions target
                    target['RoleArn'] = target_config.get('role_arn')
                    target['Input'] = json.dumps(target_config.get('input', {}))
                
                # Add retry policy
                target['RetryPolicy'] = {
                    'MaximumRetryAttempts': target_config.get('max_retry', 3),
                    'MaximumEventAge': target_config.get('max_age_seconds', 3600)
                }
                
                targets.append(target)
                target_id += 1
            
            # Add targets to rule
            if targets:
                eventbridge.put_targets(
                    Rule=rule_name,
                    EventBusName=bus_name,
                    Targets=targets
                )
                print(f"   Added {len(targets)} targets to {rule_name}")
            
            created_rules.append({
                'name': rule_name,
                'arn': rule_arn,
                'targets_count': len(targets)
            })
        
        return bus_arn, created_rules
        
    except ClientError as e:
        print(f"❌ Error creating event bus: {e}")
        return None, []

def publish_custom_event(event_bus_name, source, detail_type, detail, resources=None):
    """Publish custom event to EventBridge"""
    eventbridge = boto3.client('events')
    
    try:
        entries = [{
            'Source': source,
            'DetailType': detail_type,
            'Detail': json.dumps(detail) if isinstance(detail, dict) else detail,
            'EventBusName': event_bus_name,
            'Time': datetime.utcnow()
        }]
        
        if resources:
            entries[0]['Resources'] = resources
        
        response = eventbridge.put_events(Entries=entries)
        
        if response['FailedEntryCount'] == 0:
            print(f"✅ Published event: {detail_type}")
            return response['Entries'][0]['EventId']
        else:
            print(f"❌ Failed to publish event: {response['Entries'][0].get('ErrorMessage')}")
            return None
            
    except ClientError as e:
        print(f"❌ Error publishing event: {e}")
        return None

def create_lambda_target_with_permissions(function_name, event_bus_arn, rule_name):
    """Create Lambda function and grant EventBridge permissions"""
    lambda_client = boto3.client('lambda')
    
    try:
        # Create Lambda function (simplified example)
        function_code = """
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Process EventBridge events"""
    
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Extract event details
    source = event.get('source', 'unknown')
    detail_type = event.get('detail-type', 'unknown')
    detail = event.get('detail', {})
    
    # Process based on event type
    if detail_type == 'Order Placed':
        return process_order(detail)
    elif detail_type == 'User Signup':
        return process_user_signup(detail)
    elif detail_type == 'Inventory Low':
        return process_inventory_alert(detail)
    else:
        logger.warning(f"Unknown event type: {detail_type}")
        return {"status": "ignored", "reason": "unknown event type"}

def process_order(order_detail):
    """Process order placement events"""
    order_id = order_detail.get('order_id')
    customer_id = order_detail.get('customer_id')
    total = order_detail.get('total', 0)
    
    logger.info(f"Processing order {order_id} for customer {customer_id}, total: ${total}")
    
    # Simulate order processing logic
    if total > 1000:
        # High-value order processing
        logger.info(f"High-value order {order_id} flagged for review")
        return {"status": "review_required", "order_id": order_id}
    else:
        # Standard order processing
        logger.info(f"Order {order_id} processed successfully")
        return {"status": "processed", "order_id": order_id}

def process_user_signup(user_detail):
    """Process user signup events"""
    user_id = user_detail.get('user_id')
    email = user_detail.get('email')
    
    logger.info(f"Processing signup for user {user_id}: {email}")
    
    # Simulate user onboarding
    return {"status": "onboarding_started", "user_id": user_id}

def process_inventory_alert(inventory_detail):
    """Process inventory low alerts"""
    product_id = inventory_detail.get('product_id')
    current_stock = inventory_detail.get('current_stock', 0)
    
    logger.info(f"Low inventory alert for product {product_id}: {current_stock} units")
    
    # Simulate inventory management
    if current_stock == 0:
        return {"status": "out_of_stock", "action": "disable_product"}
    else:
        return {"status": "low_stock", "action": "reorder_triggered"}
        """
        
        # Package the code (in real implementation, you'd zip this)
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime='python3.9',
            Role='arn:aws:iam::123456789012:role/lambda-execution-role',  # Replace with actual role
            Handler='lambda_function.lambda_handler',
            Code={'ZipFile': function_code.encode()},
            Description='EventBridge event processor',
            Timeout=30,
            MemorySize=128,
            Tags={
                'Application': 'EventProcessing',
                'Environment': 'Production'
            }
        )
        
        function_arn = response['FunctionArn']
        print(f"✅ Created Lambda function: {function_name}")
        
        # Add permission for EventBridge to invoke Lambda
        try:
            lambda_client.add_permission(
                FunctionName=function_name,
                StatementId=f"eventbridge-{rule_name}",
                Action='lambda:InvokeFunction',
                Principal='events.amazonaws.com',
                SourceArn=f"{event_bus_arn.replace(':event-bus/', ':rule/')}/{rule_name}"
            )
            print(f"✅ Added EventBridge permission to {function_name}")
            
        except ClientError as perm_error:
            if 'ResourceConflictException' not in str(perm_error):
                raise perm_error
            print(f"⚠️ Permission already exists for {function_name}")
        
        return function_arn
        
    except ClientError as e:
        print(f"❌ Error creating Lambda function: {e}")
        return None

def monitor_eventbridge_metrics(event_bus_name, rule_names):
    """Monitor EventBridge metrics"""
    cloudwatch = boto3.client('cloudwatch')
    
    try:
        from datetime import timedelta
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=1)
        
        print(f"📊 EventBridge Metrics for {event_bus_name}:")
        print("-" * 60)
        
        # Custom event bus metrics
        custom_bus_metrics = [
            'Invocations',
            'SuccessfulInvocations', 
            'FailedInvocations'
        ]
        
        for metric_name in custom_bus_metrics:
            response = cloudwatch.get_metric_statistics(
                Namespace='AWS/Events',
                MetricName=metric_name,
                Dimensions=[
                    {'Name': 'EventBusName', 'Value': event_bus_name}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Sum']
            )
            
            if response['Datapoints']:
                total = sum([dp['Sum'] for dp in response['Datapoints']])
                print(f"Bus {metric_name}: {total}")
            else:
                print(f"Bus {metric_name}: No data")
        
        # Rule-specific metrics
        print(f"\nRule-specific metrics:")
        for rule_name in rule_names:
            rule_metrics = cloudwatch.get_metric_statistics(
                Namespace='AWS/Events',
                MetricName='MatchedEvents',
                Dimensions=[
                    {'Name': 'RuleName', 'Value': rule_name},
                    {'Name': 'EventBusName', 'Value': event_bus_name}
                ],
                StartTime=start_time,
                EndTime=end_time,
                Period=300,
                Statistics=['Sum']
            )
            
            if rule_metrics['Datapoints']:
                matched = sum([dp['Sum'] for dp in rule_metrics['Datapoints']])
                print(f"  {rule_name}: {matched} matched events")
            else:
                print(f"  {rule_name}: No matches")
                
    except ClientError as e:
        print(f"❌ Error getting metrics: {e}")

def main_eventbridge_example():
    """Main example: E-commerce event-driven architecture"""
    
    # Define event bus and rules configuration
    bus_name = 'ecommerce-events'
    
    # Create Lambda function first
    lambda_arn = create_lambda_target_with_permissions(
        'ecommerce-event-processor',
        f'arn:aws:events:us-east-1:123456789012:event-bus/{bus_name}',
        'order-processing-rule'
    )
    
    if not lambda_arn:
        return
    
    # Define rules configuration
    rules_config = [
        {
            'name': 'order-processing-rule',
            'description': 'Process order-related events',
            'event_pattern': {
                'source': ['ecommerce.orders'],
                'detail-type': ['Order Placed', 'Order Cancelled', 'Order Shipped']
            },
            'targets': [
                {
                    'arn': lambda_arn,
                    'max_retry': 3,
                    'max_age_seconds': 3600
                }
            ]
        },
        {
            'name': 'user-events-rule',
            'description': 'Process user-related events',
            'event_pattern': {
                'source': ['ecommerce.users'],
                'detail-type': ['User Signup', 'User Login', 'Profile Updated']
            },
            'targets': [
                {
                    'arn': lambda_arn,
                    'max_retry': 2,
                    'max_age_seconds': 1800
                }
            ]
        },
        {
            'name': 'inventory-alerts-rule',
            'description': 'Process inventory alerts',
            'event_pattern': {
                'source': ['ecommerce.inventory'],
                'detail-type': ['Inventory Low', 'Out of Stock'],
                'detail': {
                    'current_stock': [{'numeric': ['<', 10]}]
                }
            },
            'targets': [
                {
                    'arn': lambda_arn,
                    'max_retry': 1,
                    'max_age_seconds': 900
                }
            ]
        }
    ]
    
    # Create event bus and rules
    bus_arn, created_rules = create_custom_event_bus_with_rules(bus_name, rules_config)
    
    if not bus_arn:
        return
    
    # Publish sample events
    sample_events = [
        {
            'source': 'ecommerce.orders',
            'detail_type': 'Order Placed',
            'detail': {
                'order_id': 'ORD-12345',
                'customer_id': 'CUST-67890',
                'total': 299.99,
                'items': [
                    {'product_id': 'PROD-001', 'quantity': 2, 'price': 149.99}
                ],
                'timestamp': datetime.utcnow().isoformat()
            }
        },
        {
            'source': 'ecommerce.users',
            'detail_type': 'User Signup',
            'detail': {
                'user_id': 'USER-11111',
                'email': 'john.doe@example.com',
                'signup_method': 'web',
                'timestamp': datetime.utcnow().isoformat()
            }
        },
        {
            'source': 'ecommerce.inventory',
            'detail_type': 'Inventory Low',
            'detail': {
                'product_id': 'PROD-001',
                'current_stock': 5,
                'threshold': 10,
                'warehouse': 'US-EAST-1',
                'timestamp': datetime.utcnow().isoformat()
            }
        }
    ]
    
    print(f"\n📤 Publishing sample events...")
    for event in sample_events:
        event_id = publish_custom_event(
            bus_name,
            event['source'],
            event['detail_type'], 
            event['detail']
        )
        
        if event_id:
            print(f"   {event['detail_type']} event published: {event_id}")
    
    print(f"\n⏳ Waiting for event processing...")
    import time
    time.sleep(10)
    
    # Monitor metrics
    rule_names = [rule['name'] for rule in created_rules]
    monitor_eventbridge_metrics(bus_name, rule_names)

# Run the example
if __name__ == "__main__":
    main_eventbridge_example()
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def appsync_tab():
    """Content for AWS AppSync tab"""
    st.markdown("## 🚀 AWS AppSync")
    st.markdown("*Serverless GraphQL and Pub/Sub APIs that simplify application development*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **AWS AppSync** creates serverless GraphQL and Pub/Sub APIs that simplify application development through a 
    single endpoint to securely query, update, or publish data. AppSync supports iOS, Android, and JavaScript 
    with real-time subscriptions and offline capabilities.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # AppSync Features
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### GraphQL\n**Single Endpoint**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### Real-time\n**Subscriptions**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### Offline\n**Sync Support**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### Multi\n**Data Sources**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # AppSync Architecture
    st.markdown("### 🏗️ AppSync Architecture")
    common.mermaid(create_appsync_architecture_mermaid(), height=550)
    
    # Interactive AppSync API Builder
    st.markdown("### 🛠️ Interactive AppSync API Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 API Configuration")
        api_name = st.text_input("API Name:", "blog-api")
        api_type = st.selectbox("API Type:", ["GraphQL API", "Real-time API", "Merged API"])
        
        authentication = st.multiselect("Authentication Methods:", [
            "API Key", "Amazon Cognito User Pool", "AWS IAM", "OpenID Connect"
        ], default=["API Key", "Amazon Cognito User Pool"])
        
        realtime_enabled = st.checkbox("Enable Real-time Subscriptions", value=True)
    
    with col2:
        st.markdown("### 🗄️ Data Sources")
        data_sources = st.multiselect("Data Sources:", [
            "Amazon DynamoDB", "AWS Lambda", "Amazon OpenSearch", 
            "Amazon RDS", "HTTP Endpoint", "Local Resolver"
        ], default=["Amazon DynamoDB", "AWS Lambda"])
        
        caching_enabled = st.checkbox("Enable Caching", value=True)
        
        if caching_enabled:
            cache_behavior = st.selectbox("Cache Behavior:", [
                "Per-resolver caching", "Full request caching", "Custom caching"
            ])
    
    # Schema Design
    st.markdown("### 📐 GraphQL Schema Design")
    
    schema_type = st.selectbox("Schema Template:", [
        "Blog/Content Management", "E-commerce", "Social Media", "IoT Data", "Custom Schema"
    ])
    
    if schema_type == "Blog/Content Management":
        sample_schema = '''
type Post {
    id: ID!
    title: String!
    content: String!
    author: User!
    createdAt: String!
    updatedAt: String!
    published: Boolean!
    tags: [String!]
    comments: [Comment!]
}

type User {
    id: ID!
    username: String!
    email: String!
    posts: [Post!]
    profile: UserProfile
}

type Comment {
    id: ID!
    content: String!
    author: User!
    post: Post!
    createdAt: String!
}

type UserProfile {
    bio: String
    avatar: String
    website: String
}

type Query {
    getPosts(limit: Int, nextToken: String): PostConnection
    getPost(id: ID!): Post
    getUserPosts(userId: ID!): [Post!]
    searchPosts(keyword: String!): [Post!]
}

type Mutation {
    createPost(input: CreatePostInput!): Post!
    updatePost(id: ID!, input: UpdatePostInput!): Post!
    deletePost(id: ID!): Boolean!
    createComment(input: CreateCommentInput!): Comment!
}

type Subscription {
    onCreatePost: Post
        @aws_subscribe(mutations: ["createPost"])
    onUpdatePost(id: ID!): Post
        @aws_subscribe(mutations: ["updatePost"])
    onCreateComment(postId: ID!): Comment
        @aws_subscribe(mutations: ["createComment"])
}

type PostConnection {
    items: [Post!]
    nextToken: String
}

input CreatePostInput {
    title: String!
    content: String!
    published: Boolean = false
    tags: [String!]
}

input UpdatePostInput {
    title: String
    content: String
    published: Boolean
    tags: [String!]
}

input CreateCommentInput {
    content: String!
    postId: ID!
}
        '''
    elif schema_type == "E-commerce":
        sample_schema = '''
type Product {
    id: ID!
    name: String!
    description: String!
    price: Float!
    category: Category!
    inventory: Int!
    images: [String!]
    reviews: [Review!]
    createdAt: String!
}

type Category {
    id: ID!
    name: String!
    products: [Product!]
}

type Order {
    id: ID!
    user: User!
    items: [OrderItem!]!
    total: Float!
    status: OrderStatus!
    createdAt: String!
    shippingAddress: Address!
}

type OrderItem {
    product: Product!
    quantity: Int!
    price: Float!
}

enum OrderStatus {
    PENDING
    CONFIRMED
    SHIPPED
    DELIVERED
    CANCELLED
}

type User {
    id: ID!
    email: String!
    orders: [Order!]
    cart: Cart
}

type Cart {
    items: [CartItem!]
    total: Float!
}

type CartItem {
    product: Product!
    quantity: Int!
}

type Query {
    getProducts(category: ID, limit: Int): [Product!]
    getProduct(id: ID!): Product
    getOrders(userId: ID!): [Order!]
    getOrder(id: ID!): Order
}

type Mutation {
    addToCart(productId: ID!, quantity: Int!): Cart!
    removeFromCart(productId: ID!): Cart!
    createOrder(input: CreateOrderInput!): Order!
    updateOrderStatus(orderId: ID!, status: OrderStatus!): Order!
}

type Subscription {
    onOrderStatusChange(userId: ID!): Order
        @aws_subscribe(mutations: ["updateOrderStatus"])
    onInventoryUpdate(productId: ID!): Product
        @aws_subscribe(mutations: ["updateInventory"])
}
        '''
    else:
        sample_schema = "# Define your custom GraphQL schema here"
    
    with st.expander("GraphQL Schema", expanded=True):
        st.code(sample_schema, language="graphql")
    
    # Resolver Configuration
    st.markdown("### ⚙️ Resolver Configuration")
    
    col3, col4 = st.columns(2)
    
    with col3:
        resolver_type = st.selectbox("Resolver Type:", [
            "Direct Lambda Resolver", "VTL Template Resolver", "JavaScript Resolver", "Pipeline Resolver"
        ])
        
        conflict_resolution = st.selectbox("Conflict Resolution:", [
            "Auto Merge", "Optimistic Concurrency", "Lambda", "None"
        ])
    
    with col4:
        error_handling = st.selectbox("Error Handling:", [
            "Propagate All Errors", "Suppress Errors", "Custom Error Handler"
        ])
        
        request_timeout = st.slider("Request Timeout (seconds):", 1, 30, 30)
    
    if st.button("🚀 Create AppSync API", use_container_width=True):
        # Calculate estimated costs
        monthly_requests = 1000000  # 1M requests
        monthly_realtime = 100000   # 100K real-time connections
        monthly_cache_requests = 500000 if caching_enabled else 0
        
        # AppSync pricing (simplified)
        query_cost = (monthly_requests / 1000000) * 4.00  # $4 per million
        realtime_cost = (monthly_realtime / 1000000) * 2.00 if realtime_enabled else 0
        cache_cost = (monthly_cache_requests / 1000000) * 0.25 if caching_enabled else 0
        
        total_cost = query_cost + realtime_cost + cache_cost
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ AppSync API Created Successfully!
        
        **API Configuration:**
        - **Name**: {api_name}
        - **Type**: {api_type}
        - **GraphQL Endpoint**: https://{api_name.lower().replace(' ', '')}.appsync-api.us-east-1.amazonaws.com/graphql
        - **Real-time Endpoint**: wss://{api_name.lower().replace(' ', '')}.appsync-realtime-api.us-east-1.amazonaws.com/graphql
        
        **Authentication:**
        {chr(10).join([f"  - {auth_method}" for auth_method in authentication])}
        
        **Data Sources:**
        {chr(10).join([f"  - {ds}" for ds in data_sources])}
        
        **Features:**
        - **Real-time Subscriptions**: {'✅ Enabled' if realtime_enabled else '❌ Disabled'}
        - **Caching**: {'✅ ' + cache_behavior if caching_enabled else '❌ Disabled'}
        - **Conflict Resolution**: {conflict_resolution}
        - **Request Timeout**: {request_timeout}s
        
        💰 **Estimated Monthly Cost**: ${total_cost:.2f} (1M requests)
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # AppSync vs REST API Comparison
    st.markdown("### ⚖️ GraphQL (AppSync) vs REST API Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🚀 GraphQL with AppSync
        
        **Advantages:**
        - **Single endpoint** for all operations
        - **Flexible queries** - fetch exactly what you need
        - **Real-time subscriptions** built-in
        - **Type-safe** with schema validation
        - **Automatic caching** and optimization
        - **Offline sync** capabilities
        
        **Best For:**
        - Mobile applications
        - Real-time features
        - Complex data relationships
        - Rapid frontend development
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🌐 REST API with API Gateway
        
        **Advantages:**
        - **Widely adopted** standard
        - **Simple caching** strategies
        - **HTTP status codes** for errors
        - **Easy to test** with standard tools
        - **Mature ecosystem** of tools
        - **Stateless** architecture
        
        **Best For:**
        - Public APIs
        - Simple CRUD operations
        - Legacy system integration
        - Microservices architecture
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Real-time Features Deep Dive
    st.markdown("### ⚡ Real-time Subscriptions in AppSync")
    
    subscription_examples = {
        'Use Case': [
            'Live Chat', 'Real-time Comments', 'Live Dashboard', 'IoT Sensor Data', 'Collaborative Editing'
        ],
        'Subscription Pattern': [
            'onMessageSent(roomId: ID!)',
            'onCommentAdded(postId: ID!)', 
            'onMetricUpdate(dashboardId: ID!)',
            'onSensorReading(deviceId: ID!)',
            'onDocumentChanged(docId: ID!)'
        ],
        'Update Frequency': [
            'High (100+ per minute)',
            'Medium (10-50 per minute)',
            'Low (1-10 per minute)', 
            'Very High (1000+ per minute)',
            'Medium (keystroke-based)'
        ],
        'Connection Management': [
            'Per chat room',
            'Per blog post',
            'Per user dashboard',
            'Per device type',
            'Per document'
        ]
    }
    
    df_subscriptions = pd.DataFrame(subscription_examples)
    st.dataframe(df_subscriptions, use_container_width=True)
    
    # Performance Optimization
    st.markdown("### 🎯 AppSync Performance Optimization")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🚄 Query Optimization
        - **DataLoader pattern** to batch requests
        - **Field-level caching** for expensive operations
        - **Query complexity analysis** to prevent abuse
        - **Pagination** for large datasets
        - **Query whitelisting** for production
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 💾 Caching Strategy
        - **Full request caching** for read-heavy APIs
        - **Per-resolver caching** for mixed workloads
        - **TTL-based invalidation** for data freshness
        - **Cache key customization** for multi-tenant apps
        - **Cache warming** for predictable patterns
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📊 Monitoring & Alerts
        - **Request latency** tracking
        - **Error rate** monitoring
        - **Cache hit ratio** optimization
        - **Subscription connection** counts
        - **Resolver performance** analysis
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Complete AppSync Implementation")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Complete AppSync implementation with DynamoDB integration
import boto3
import json
from datetime import datetime
from botocore.exceptions import ClientError

def create_appsync_api_with_dynamodb(api_name, schema_definition):
    """Create AppSync API with DynamoDB data source"""
    appsync = boto3.client('appsync')
    dynamodb = boto3.resource('dynamodb')
    iam = boto3.client('iam')
    
    try:
        # Create AppSync API
        api_response = appsync.create_graphql_api(
            name=api_name,
            authenticationType='API_KEY',
            additionalAuthenticationProviders=[
                {
                    'authenticationType': 'AMAZON_COGNITO_USER_POOLS',
                    'userPoolConfig': {
                        'userPoolId': 'us-east-1_example123',  # Replace with actual user pool
                        'awsRegion': 'us-east-1'
                    }
                }
            ],
            logConfig={
                'fieldLogLevel': 'ALL',
                'cloudWatchLogsRoleArn': 'arn:aws:iam::123456789012:role/AppSyncServiceRole'
            },
            xrayEnabled=True,
            tags={
                'Environment': 'Production',
                'Application': 'BlogAPI'
            }
        )
        
        api_id = api_response['graphqlApi']['apiId']
        api_endpoint = api_response['graphqlApi']['uris']['GRAPHQL']
        
        print(f"✅ Created AppSync API: {api_name}")
        print(f"API ID: {api_id}")
        print(f"GraphQL Endpoint: {api_endpoint}")
        
        # Create API Key
        api_key_response = appsync.create_api_key(
            apiId=api_id,
            description=f"API Key for {api_name}",
            expires=int((datetime.utcnow().timestamp() + 365*24*3600))  # 1 year
        )
        
        api_key = api_key_response['apiKey']['id']
        print(f"✅ Created API Key: {api_key}")
        
        # Update GraphQL Schema
        schema_response = appsync.start_schema_creation(
            apiId=api_id,
            definition=schema_definition.encode('utf-8')
        )
        
        print(f"✅ Schema update started")
        
        # Create DynamoDB tables
        table_configs = [
            {
                'TableName': 'Posts',
                'KeySchema': [
                    {'AttributeName': 'id', 'KeyType': 'HASH'}
                ],
                'AttributeDefinitions': [
                    {'AttributeName': 'id', 'AttributeType': 'S'},
                    {'AttributeName': 'userId', 'AttributeType': 'S'},
                    {'AttributeName': 'createdAt', 'AttributeType': 'S'}
                ],
                'GlobalSecondaryIndexes': [
                    {
                        'IndexName': 'UserPostsIndex',
                        'KeySchema': [
                            {'AttributeName': 'userId', 'KeyType': 'HASH'},
                            {'AttributeName': 'createdAt', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'},
                        'BillingMode': 'PAY_PER_REQUEST'
                    }
                ],
                'BillingMode': 'PAY_PER_REQUEST'
            },
            {
                'TableName': 'Users',
                'KeySchema': [
                    {'AttributeName': 'id', 'KeyType': 'HASH'}
                ],
                'AttributeDefinitions': [
                    {'AttributeName': 'id', 'AttributeType': 'S'},
                    {'AttributeName': 'username', 'AttributeType': 'S'}
                ],
                'GlobalSecondaryIndexes': [
                    {
                        'IndexName': 'UsernameIndex',
                        'KeySchema': [
                            {'AttributeName': 'username', 'KeyType': 'HASH'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'},
                        'BillingMode': 'PAY_PER_REQUEST'
                    }
                ],
                'BillingMode': 'PAY_PER_REQUEST'
            },
            {
                'TableName': 'Comments',
                'KeySchema': [
                    {'AttributeName': 'id', 'KeyType': 'HASH'}
                ],
                'AttributeDefinitions': [
                    {'AttributeName': 'id', 'AttributeType': 'S'},
                    {'AttributeName': 'postId', 'AttributeType': 'S'},
                    {'AttributeName': 'createdAt', 'AttributeType': 'S'}
                ],
                'GlobalSecondaryIndexes': [
                    {
                        'IndexName': 'PostCommentsIndex',
                        'KeySchema': [
                            {'AttributeName': 'postId', 'KeyType': 'HASH'},
                            {'AttributeName': 'createdAt', 'KeyType': 'RANGE'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'},
                        'BillingMode': 'PAY_PER_REQUEST'
                    }
                ],
                'BillingMode': 'PAY_PER_REQUEST'
            }
        ]
        
        created_tables = []
        for table_config in table_configs:
            try:
                table = dynamodb.create_table(**table_config)
                created_tables.append(table_config['TableName'])
                print(f"✅ Created DynamoDB table: {table_config['TableName']}")
                
                # Wait for table to be active
                table.wait_until_exists()
                
            except ClientError as e:
                if 'ResourceInUseException' in str(e):
                    print(f"⚠️ Table {table_config['TableName']} already exists")
                    created_tables.append(table_config['TableName'])
                else:
                    raise e
        
        # Create IAM role for AppSync to access DynamoDB
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "appsync.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        dynamodb_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "dynamodb:GetItem",
                        "dynamodb:PutItem",
                        "dynamodb:UpdateItem",
                        "dynamodb:DeleteItem",
                        "dynamodb:Query",
                        "dynamodb:Scan"
                    ],
                    "Resource": [
                        f"arn:aws:dynamodb:us-east-1:123456789012:table/{table_name}*"
                        for table_name in created_tables
                    ]
                }
            ]
        }
        
        role_name = f"{api_name}-DynamoDBRole"
        
        try:
            role_response = iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description=f"AppSync DynamoDB access role for {api_name}"
            )
            
            role_arn = role_response['Role']['Arn']
            
            # Attach policy to role
            iam.put_role_policy(
                RoleName=role_name,
                PolicyName='DynamoDBAccess',
                PolicyDocument=json.dumps(dynamodb_policy)
            )
            
            print(f"✅ Created IAM role: {role_name}")
            
        except ClientError as e:
            if 'EntityAlreadyExists' in str(e):
                print(f"⚠️ Role {role_name} already exists")
                role_arn = f"arn:aws:iam::123456789012:role/{role_name}"
            else:
                raise e
        
        # Create Data Sources
        data_sources = []
        for table_name in created_tables:
            try:
                ds_response = appsync.create_data_source(
                    apiId=api_id,
                    name=f"{table_name}DataSource",
                    type='AMAZON_DYNAMODB',
                    serviceRoleArn=role_arn,
                    dynamodbConfig={
                        'tableName': table_name,
                        'awsRegion': 'us-east-1'
                    }
                )
                
                data_sources.append({
                    'name': f"{table_name}DataSource",
                    'table': table_name
                })
                
                print(f"✅ Created data source for {table_name}")
                
            except ClientError as e:
                print(f"❌ Error creating data source for {table_name}: {e}")
        
        return {
            'api_id': api_id,
            'api_endpoint': api_endpoint,
            'api_key': api_key,
            'data_sources': data_sources,
            'tables': created_tables
        }
        
    except ClientError as e:
        print(f"❌ Error creating AppSync API: {e}")
        return None

def create_appsync_resolvers(api_id, data_sources):
    """Create GraphQL resolvers for AppSync API"""
    appsync = boto3.client('appsync')
    
    # Resolver configurations
    resolvers_config = [
        {
            'typeName': 'Query',
            'fieldName': 'getPosts',
            'dataSourceName': 'PostsDataSource',
            'requestTemplate': """
            {
                "version": "2017-02-28",
                "operation": "Scan",
                "limit": $util.defaultIfNull($ctx.args.limit, 20),
                "nextToken": $util.toJson($util.defaultIfNullOrEmpty($ctx.args.nextToken, null))
            }
            """,
            'responseTemplate': """
            {
                "items": $util.toJson($ctx.result.items),
                "nextToken": $util.toJson($ctx.result.nextToken)
            }
            """
        },
        {
            'typeName': 'Query',
            'fieldName': 'getPost',
            'dataSourceName': 'PostsDataSource',
            'requestTemplate': """
            {
                "version": "2017-02-28",
                "operation": "GetItem",
                "key": {
                    "id": $util.dynamodb.toDynamoDBJson($ctx.args.id)
                }
            }
            """,
            'responseTemplate': '$util.toJson($ctx.result)'
        },
        {
            'typeName': 'Mutation',
            'fieldName': 'createPost',
            'dataSourceName': 'PostsDataSource',
            'requestTemplate': """
            #set($input = $ctx.args.input)
            {
                "version": "2017-02-28",
                "operation": "PutItem",
                "key": {
                    "id": $util.dynamodb.toDynamoDBJson($util.autoId())
                },
                "attributeValues": {
                    "title": $util.dynamodb.toDynamoDBJson($input.title),
                    "content": $util.dynamodb.toDynamoDBJson($input.content),
                    "userId": $util.dynamodb.toDynamoDBJson($ctx.identity.sub),
                    "published": $util.dynamodb.toDynamoDBJson($util.defaultIfNull($input.published, false)),
                    "createdAt": $util.dynamodb.toDynamoDBJson($util.time.nowISO8601()),
                    "updatedAt": $util.dynamodb.toDynamoDBJson($util.time.nowISO8601()),
                    "tags": $util.dynamodb.toDynamoDBJson($util.defaultIfNull($input.tags, []))
                }
            }
            """,
            'responseTemplate': '$util.toJson($ctx.result)'
        },
        {
            'typeName': 'Mutation',
            'fieldName': 'updatePost',
            'dataSourceName': 'PostsDataSource',
            'requestTemplate': """
            #set($input = $ctx.args.input)
            {
                "version": "2017-02-28",
                "operation": "UpdateItem",
                "key": {
                    "id": $util.dynamodb.toDynamoDBJson($ctx.args.id)
                },
                "update": {
                    "expression": "SET #updatedAt = :updatedAt",
                    "expressionNames": {
                        "#updatedAt": "updatedAt"
                    },
                    "expressionValues": {
                        ":updatedAt": $util.dynamodb.toDynamoDBJson($util.time.nowISO8601())
                    }
                }
            }
            #if($input.title)
                #set($expression = "$expression, title = :title")
                $util.qr($expression.expressionValues.put(":title", $util.dynamodb.toDynamoDBJson($input.title)))
            #end
            #if($input.content)
                #set($expression = "$expression, content = :content")
                $util.qr($expression.expressionValues.put(":content", $util.dynamodb.toDynamoDBJson($input.content)))
            #end
            """,
            'responseTemplate': '$util.toJson($ctx.result)'
        }
    ]
    
    created_resolvers = []
    
    for resolver_config in resolvers_config:
        try:
            resolver_response = appsync.create_resolver(
                apiId=api_id,
                typeName=resolver_config['typeName'],
                fieldName=resolver_config['fieldName'],
                dataSourceName=resolver_config['dataSourceName'],
                requestMappingTemplate=resolver_config['requestTemplate'],
                responseMappingTemplate=resolver_config['responseTemplate']
            )
            
            created_resolvers.append({
                'type': resolver_config['typeName'],
                'field': resolver_config['fieldName']
            })
            
            print(f"✅ Created resolver: {resolver_config['typeName']}.{resolver_config['fieldName']}")
            
        except ClientError as e:
            print(f"❌ Error creating resolver {resolver_config['fieldName']}: {e}")
    
    return created_resolvers

def test_appsync_api(api_endpoint, api_key):
    """Test AppSync API with sample queries"""
    import requests
    
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key
    }
    
    # Test queries
    test_queries = [
        {
            'name': 'Create Post',
            'query': """
            mutation CreatePost($input: CreatePostInput!) {
                createPost(input: $input) {
                    id
                    title
                    content
                    createdAt
                    published
                }
            }
            """,
            'variables': {
                'input': {
                    'title': 'My First Blog Post',
                    'content': 'This is the content of my first blog post created via GraphQL!',
                    'published': True,
                    'tags': ['graphql', 'appsync', 'aws']
                }
            }
        },
        {
            'name': 'Get Posts',
            'query': """
            query GetPosts($limit: Int) {
                getPosts(limit: $limit) {
                    items {
                        id
                        title
                        content
                        createdAt
                        published
                        tags
                    }
                    nextToken
                }
            }
            """,
            'variables': {
                'limit': 10
            }
        }
    ]
    
    print(f"\n🧪 Testing AppSync API...")
    
    for test in test_queries:
        try:
            response = requests.post(
                api_endpoint,
                headers=headers,
                json={
                    'query': test['query'],
                    'variables': test['variables']
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if 'errors' in result:
                    print(f"❌ {test['name']}: {result['errors']}")
                else:
                    print(f"✅ {test['name']}: Success")
                    print(f"   Data: {json.dumps(result['data'], indent=2)}")
            else:
                print(f"❌ {test['name']}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {test['name']}: {e}")

def main_appsync_example():
    """Main example: Blog API with AppSync"""
    
    # GraphQL Schema for blog API
    blog_schema = """
    type Post {
        id: ID!
        title: String!
        content: String!
        userId: String!
        createdAt: String!
        updatedAt: String!
        published: Boolean!
        tags: [String!]
    }
    
    type Query {
        getPosts(limit: Int, nextToken: String): PostConnection
        getPost(id: ID!): Post
    }
    
    type Mutation {
        createPost(input: CreatePostInput!): Post!
        updatePost(id: ID!, input: UpdatePostInput!): Post!
        deletePost(id: ID!): Boolean!
    }
    
    type Subscription {
        onCreatePost: Post
            @aws_subscribe(mutations: ["createPost"])
        onUpdatePost(id: ID!): Post
            @aws_subscribe(mutations: ["updatePost"])
    }
    
    type PostConnection {
        items: [Post!]
        nextToken: String
    }
    
    input CreatePostInput {
        title: String!
        content: String!
        published: Boolean = false
        tags: [String!]
    }
    
    input UpdatePostInput {
        title: String
        content: String
        published: Boolean
        tags: [String!]
    }
    """
    
    # Create AppSync API
    api_config = create_appsync_api_with_dynamodb('BlogAPI', blog_schema)
    
    if not api_config:
        return
    
    print(f"\n⏳ Waiting for schema deployment...")
    import time
    time.sleep(30)  # Wait for schema to be deployed
    
    # Create resolvers
    resolvers = create_appsync_resolvers(api_config['api_id'], api_config['data_sources'])
    
    print(f"\n📊 API Summary:")
    print(f"API ID: {api_config['api_id']}")
    print(f"GraphQL Endpoint: {api_config['api_endpoint']}")
    print(f"Created Tables: {', '.join(api_config['tables'])}")
    print(f"Created Resolvers: {len(resolvers)}")
    
    # Test the API
    test_appsync_api(api_config['api_endpoint'], api_config['api_key'])

# Run the example
if __name__ == "__main__":
    main_appsync_example()
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
    st.markdown("# 🔧 Development with AWS Services")
    st.markdown("*Application Integration Services for Modern Applications*")
    
    st.markdown("""<div class="info-box">
                Master AWS application integration services including SQS, SNS, EventBridge, and AppSync to build scalable, 
                event-driven architectures with decoupled microservices, real-time capabilities, and robust messaging patterns.
                </div>""", unsafe_allow_html=True)
    
    # Messaging Services Overview
    st.markdown("### 📊 AWS Messaging Services Overview")
    common.mermaid(create_messaging_overview_mermaid(), height=350)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📨 Amazon SQS", 
        "📢 Amazon SNS", 
        "📅 Amazon EventBridge",
        "🚀 AWS AppSync"
    ])
    
    with tab1:
        sqs_tab()
    
    with tab2:
        sns_tab()
    
    with tab3:
        eventbridge_tab()
    
    with tab4:
        appsync_tab()
    
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
