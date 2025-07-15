
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import utils.common as common
import utils.authenticate as authenticate
import json
import time

# Page configuration
st.set_page_config(
    page_title="AWS Messaging Services Hub",
    page_icon="📨",
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
        
        .queue-simulator {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            border: 2px solid {AWS_COLORS['light_blue']};
            margin: 15px 0;
        }}
        
        .message-card {{
            background: linear-gradient(45deg, {AWS_COLORS['light_blue']} 0%, {AWS_COLORS['success']} 100%);
            padding: 15px;
            border-radius: 10px;
            color: white;
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
            - 🔄 Amazon Simple Queue Service (SQS) - Message queuing service
            - 📢 Amazon Simple Notification Service (SNS) - Pub/Sub messaging
            - 🌟 Common SNS Scenarios - Fanout pattern implementation
            - 📨 Message Channels - Point-to-point vs Publish-subscribe patterns
            
            **Learning Objectives:**
            - Understand AWS messaging services and patterns
            - Learn how to decouple applications using queues and topics
            - Explore fanout scenarios and message distribution
            - Practice with interactive message simulators and code examples
            """)

def create_sqs_architecture_mermaid():
    """Create mermaid diagram for SQS architecture"""
    return """
    graph LR
        A[Producer Application] --> B[SQS Queue]
        B --> C[Consumer Application 1]
        B --> D[Consumer Application 2]
        B --> E[Consumer Application 3]
        
        subgraph "SQS Features"
            F[Message Retention<br/>14 days max]
            G[Visibility Timeout<br/>Message processing]
            H[Dead Letter Queue<br/>Failed messages]
            I[Long Polling<br/>Reduce costs]
        end
        
        B --> F
        B --> G  
        B --> H
        B --> I
        
        style A fill:#4B9EDB,stroke:#232F3E,color:#fff
        style B fill:#FF9900,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#3FB34F,stroke:#232F3E,color:#fff
        style E fill:#3FB34F,stroke:#232F3E,color:#fff
        style F fill:#232F3E,stroke:#FF9900,color:#fff
        style G fill:#232F3E,stroke:#FF9900,color:#fff
        style H fill:#232F3E,stroke:#FF9900,color:#fff
        style I fill:#232F3E,stroke:#FF9900,color:#fff
    """

def create_sns_architecture_mermaid():
    """Create mermaid diagram for SNS architecture"""
    return """
    graph TD
        A[Publisher Application] --> B[SNS Topic]
        
        B --> C[SQS Queue 1]
        B --> D[SQS Queue 2] 
        B --> E[Lambda Function]
        B --> F[HTTP/HTTPS Endpoint]
        B --> G[Email Subscription]
        B --> H[SMS Subscription]
        
        C --> I[Consumer App 1]
        D --> J[Consumer App 2]
        E --> K[Serverless Processing]
        
        subgraph "SNS Features"
            L[Message Filtering<br/>Selective delivery]
            M[Message Encryption<br/>Security]
            N[DLQ Support<br/>Failed deliveries]
            O[Fanout Pattern<br/>1-to-many]
        end
        
        B --> L
        B --> M
        B --> N  
        B --> O
        
        style A fill:#4B9EDB,stroke:#232F3E,color:#fff
        style B fill:#FF9900,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#3FB34F,stroke:#232F3E,color:#fff
        style E fill:#232F3E,stroke:#FF9900,color:#fff
        style F fill:#4B9EDB,stroke:#232F3E,color:#fff
        style G fill:#4B9EDB,stroke:#232F3E,color:#fff
        style H fill:#4B9EDB,stroke:#232F3E,color:#fff
    """

def create_fanout_scenario_mermaid():
    """Create mermaid diagram for SNS fanout scenario"""
    return """
    graph TD
        A[E-commerce Order Placed] --> B[SNS Topic: OrderEvents]
        
        B --> C[SQS Queue: Order Processing]
        B --> D[SQS Queue: Inventory Management]  
        B --> E[SQS Queue: Analytics]
        B --> F[Lambda: Email Notification]
        B --> G[Lambda: SMS Alert]
        
        C --> H[EC2: Order Fulfillment]
        D --> I[EC2: Stock Updates]
        E --> J[Data Warehouse Analysis]
        
        style A fill:#FF9900,stroke:#232F3E,color:#fff
        style B fill:#4B9EDB,stroke:#232F3E,color:#fff
        style C fill:#3FB34F,stroke:#232F3E,color:#fff
        style D fill:#3FB34F,stroke:#232F3E,color:#fff
        style E fill:#3FB34F,stroke:#232F3E,color:#fff
        style F fill:#232F3E,stroke:#FF9900,color:#fff
        style G fill:#232F3E,stroke:#FF9900,color:#fff
        style H fill:#4B9EDB,stroke:#232F3E,color:#fff
        style I fill:#4B9EDB,stroke:#232F3E,color:#fff
        style J fill:#4B9EDB,stroke:#232F3E,color:#fff
    """

def create_message_channels_mermaid():
    """Create mermaid diagram comparing message channels"""
    return """
    graph TB
        subgraph "Point-to-Point (Queue)"
            A1[Sender] --> B1[SQS Queue]
            B1 --> C1[Receiver A]
            B1 --> C2[Receiver B] 
            B1 --> C3[Receiver C]
            
            note1[Only ONE receiver<br/>gets each message]
        end
        
        subgraph "Publish-Subscribe (Topic)"
            A2[Publisher] --> B2[SNS Topic]
            B2 --> C4[Subscriber A]
            B2 --> C5[Subscriber B]
            B2 --> C6[Subscriber C]
            
            note2[ALL subscribers<br/>get the message]
        end
        
        style A1 fill:#4B9EDB,stroke:#232F3E,color:#fff
        style B1 fill:#FF9900,stroke:#232F3E,color:#fff
        style C1 fill:#3FB34F,stroke:#232F3E,color:#fff
        style C2 fill:#3FB34F,stroke:#232F3E,color:#fff
        style C3 fill:#3FB34F,stroke:#232F3E,color:#fff
        
        style A2 fill:#4B9EDB,stroke:#232F3E,color:#fff
        style B2 fill:#FF9900,stroke:#232F3E,color:#fff
        style C4 fill:#3FB34F,stroke:#232F3E,color:#fff
        style C5 fill:#3FB34F,stroke:#232F3E,color:#fff
        style C6 fill:#3FB34F,stroke:#232F3E,color:#fff
        
        style note1 fill:#232F3E,stroke:#FF9900,color:#fff
        style note2 fill:#232F3E,stroke:#FF9900,color:#fff
    """

def sqs_tab():
    """Content for Amazon SQS tab"""
    st.markdown("## 🔄 Amazon Simple Queue Service (SQS)")
    st.markdown("*A fully managed message queue for microservices, distributed systems, and serverless applications*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Amazon SQS** eliminates the complexity and overhead associated with managing and operating message-oriented middleware, 
    enabling you to focus on differentiating work. Send, store, and receive messages between software components at any volume.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # SQS Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 14 Days\n**Message Retention**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 256 KB\n**Message Size**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 120,000\n**Messages/Second**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 99.9%\n**Availability SLA**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # SQS Architecture
    st.markdown("### 🏗️ SQS Architecture Overview")
    common.mermaid(create_sqs_architecture_mermaid(), height=400)
    
    # Interactive SQS Queue Simulator
    st.markdown("### 🎮 Interactive SQS Queue Simulator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Queue Configuration")
        queue_type = st.selectbox("Queue Type:", [
            "Standard Queue (High Throughput)",
            "FIFO Queue (Exactly-Once Processing)"
        ])
        
        visibility_timeout = st.slider("Visibility Timeout (seconds):", 1, 900, 30)
        message_retention = st.slider("Message Retention (days):", 1, 14, 4)
        receive_wait_time = st.slider("Long Polling Wait Time (seconds):", 0, 20, 0)
    
    with col2:
        st.markdown("### 📨 Message Properties")
        message_content = st.text_area("Message Body:", "Hello from SQS!", height=100)
        delay_seconds = st.slider("Delivery Delay (seconds):", 0, 900, 0)
        
        if queue_type == "FIFO Queue (Exactly-Once Processing)":
            group_id = st.text_input("Message Group ID:", "order-processing")
            dedup_id = st.text_input("Deduplication ID:", "msg-001")
    
    # Message sending simulation
    if st.button("📤 Send Message to Queue", use_container_width=True):
        if 'sqs_messages' not in st.session_state:
            st.session_state.sqs_messages = []
        
        message = {
            'id': f"msg-{len(st.session_state.sqs_messages) + 1:04d}",
            'body': message_content,
            'timestamp': time.time(),
            'visible_after': time.time() + delay_seconds,
            'queue_type': queue_type,
            'retention_until': time.time() + (message_retention * 86400)
        }
        
        if queue_type == "FIFO Queue (Exactly-Once Processing)":
            message['group_id'] = group_id
            message['dedup_id'] = dedup_id
        
        st.session_state.sqs_messages.append(message)
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ Message Sent Successfully!
        
        **Message Details:**
        - **Message ID**: {message['id']}
        - **Queue Type**: {queue_type}
        - **Delivery Delay**: {delay_seconds} seconds
        - **Retention Period**: {message_retention} days
        - **Visibility Timeout**: {visibility_timeout} seconds
        
        🎯 **Status**: Message queued for processing
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display queued messages
    if 'sqs_messages' in st.session_state and st.session_state.sqs_messages:
        st.markdown("### 📋 Messages in Queue")
        
        current_time = time.time()
        visible_messages = [msg for msg in st.session_state.sqs_messages if msg['visible_after'] <= current_time]
        delayed_messages = [msg for msg in st.session_state.sqs_messages if msg['visible_after'] > current_time]
        
        if visible_messages:
            st.markdown("**Available Messages:**")
            for msg in visible_messages[-5:]:  # Show last 5 messages
                st.markdown('<div class="message-card">', unsafe_allow_html=True)
                st.markdown(f"""
                **{msg['id']}** | {msg['queue_type']}<br>
                Body: {msg['body'][:50]}{'...' if len(msg['body']) > 50 else ''}
                """)
                st.markdown('</div>', unsafe_allow_html=True)
        
        if delayed_messages:
            st.markdown(f"**Delayed Messages**: {len(delayed_messages)} waiting for delivery")
    
    # SQS Queue Types Comparison
    st.markdown("### ⚖️ Standard vs FIFO Queues")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📈 Standard Queue
        
        **Characteristics:**
        - **Unlimited throughput** - nearly unlimited TPS
        - **At-least-once delivery** - messages delivered at least once
        - **Best-effort ordering** - messages generally delivered in order
        - **Duplicate messages** possible
        
        **Best For:**
        - High-throughput applications
        - Loose coupling between components
        - Applications that can handle duplicates
        - **Cost-effective** messaging
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 FIFO Queue
        
        **Characteristics:**  
        - **300 TPS limit** (3000 with batching)
        - **Exactly-once processing** - no duplicates
        - **First-in-first-out** delivery guaranteed
        - **Message groups** for parallel processing
        
        **Best For:**
        - Order-critical applications
        - Financial transactions
        - Command processing systems
        - **Data consistency** requirements
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # SQS Features Deep Dive
    st.markdown("### 🔧 SQS Key Features")
    
    features_data = {
        'Feature': [
            'Visibility Timeout', 'Message Retention', 'Long Polling', 
            'Dead Letter Queue', 'Message Attributes', 'Batch Operations'
        ],
        'Description': [
            'Hide messages during processing',
            'Store messages for up to 14 days',
            'Reduce polling costs and latency',
            'Handle failed message processing',
            'Add metadata to messages',
            'Send/receive up to 10 messages at once'
        ],
        'Use Case': [
            'Prevent duplicate processing',
            'Reliable message delivery',
            'Cost optimization',
            'Error handling and debugging',
            'Message routing and filtering',
            'Performance optimization'
        ],
        'Configuration': [
            '30 seconds (default)',
            '4 days (default, max 14)',
            '0-20 seconds wait time',
            'Separate DLQ after retries',
            'Up to 10 attributes per message',
            '1-10 messages per API call'
        ]
    }
    
    df_features = pd.DataFrame(features_data)
    st.dataframe(df_features, use_container_width=True)
    
    # Best Practices
    st.markdown("### 💡 SQS Best Practices")
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Design Principles
    
    **Message Processing:**
    - Make message processing **idempotent** - handle duplicates gracefully
    - Use **appropriate visibility timeout** - longer for complex processing
    - Implement **exponential backoff** for retries
    - Monitor and use **Dead Letter Queues** for failed messages
    
    **Performance Optimization:**
    - Use **long polling** to reduce costs and improve responsiveness  
    - Implement **batch operations** for better throughput
    - Consider **message grouping** for FIFO queues
    - Use **multiple consumers** to scale processing
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: SQS Message Processing")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Complete SQS message processing with error handling and best practices
import boto3
import json
import time
from botocore.exceptions import ClientError

class SQSMessageProcessor:
    def __init__(self, queue_url, region_name='us-east-1'):
        self.sqs = boto3.client('sqs', region_name=region_name)
        self.queue_url = queue_url
        
    def send_message(self, message_body, attributes=None, delay_seconds=0):
        """Send a message to SQS queue with attributes"""
        try:
            message_params = {
                'QueueUrl': self.queue_url,
                'MessageBody': json.dumps(message_body) if isinstance(message_body, dict) else message_body,
                'DelaySeconds': delay_seconds
            }
            
            # Add message attributes if provided
            if attributes:
                message_params['MessageAttributes'] = {}
                for key, value in attributes.items():
                    message_params['MessageAttributes'][key] = {
                        'StringValue': str(value),
                        'DataType': 'String'
                    }
            
            response = self.sqs.send_message(**message_params)
            
            print(f"✅ Message sent successfully!")
            print(f"Message ID: {response['MessageId']}")
            print(f"MD5 of Body: {response['MD5OfBody']}")
            
            return response['MessageId']
            
        except ClientError as e:
            print(f"❌ Error sending message: {e}")
            return None
    
    def send_batch_messages(self, messages):
        """Send multiple messages in a single API call (up to 10)"""
        try:
            entries = []
            for i, msg in enumerate(messages[:10]):  # Max 10 messages per batch
                entry = {
                    'Id': str(i),
                    'MessageBody': json.dumps(msg) if isinstance(msg, dict) else msg
                }
                entries.append(entry)
            
            response = self.sqs.send_message_batch(
                QueueUrl=self.queue_url,
                Entries=entries
            )
            
            successful = len(response.get('Successful', []))
            failed = len(response.get('Failed', []))
            
            print(f"📦 Batch send completed: {successful} successful, {failed} failed")
            
            return response
            
        except ClientError as e:
            print(f"❌ Error sending batch: {e}")
            return None
    
    def receive_messages(self, max_messages=1, wait_time_seconds=20):
        """Receive messages with long polling"""
        try:
            response = self.sqs.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=max_messages,
                WaitTimeSeconds=wait_time_seconds,  # Long polling
                MessageAttributeNames=['All'],
                AttributeNames=['ApproximateReceiveCount']
            )
            
            messages = response.get('Messages', [])
            print(f"📨 Received {len(messages)} message(s)")
            
            return messages
            
        except ClientError as e:
            print(f"❌ Error receiving messages: {e}")
            return []
    
    def process_message(self, message):
        """Process individual message with error handling"""
        receipt_handle = message['ReceiptHandle']
        message_body = message['Body']
        
        try:
            # Parse message body
            if message_body.startswith('{'):
                data = json.loads(message_body)
            else:
                data = message_body
            
            print(f"🔄 Processing message: {message.get('MessageId')}")
            print(f"Body: {data}")
            
            # Get message attributes
            attributes = message.get('MessageAttributes', {})
            for key, value in attributes.items():
                print(f"Attribute {key}: {value.get('StringValue')}")
            
            # Simulate processing work
            processing_time = 2  # seconds
            print(f"⏳ Processing for {processing_time} seconds...")
            time.sleep(processing_time)
            
            # Your business logic here
            result = self.business_logic(data)
            
            # Delete message after successful processing
            self.delete_message(receipt_handle)
            
            print(f"✅ Message processed successfully: {result}")
            return result
            
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in message body: {message_body}")
            self.handle_poison_message(receipt_handle)
            
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            # Don't delete message - let it become visible again for retry
            return None
    
    def business_logic(self, data):
        """Your custom business logic"""
        # Example: Process order data
        if isinstance(data, dict) and 'order_id' in data:
            order_id = data['order_id']
            # Simulate order processing
            return f"Order {order_id} processed successfully"
        else:
            return f"Generic data processed: {str(data)[:100]}"
    
    def delete_message(self, receipt_handle):
        """Delete processed message from queue"""
        try:
            self.sqs.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
            print("🗑️ Message deleted from queue")
            
        except ClientError as e:
            print(f"❌ Error deleting message: {e}")
    
    def handle_poison_message(self, receipt_handle):
        """Handle messages that can't be processed"""
        print("☠️ Handling poison message - moving to DLQ")
        # In practice, configure DLQ in queue settings
        self.delete_message(receipt_handle)
    
    def get_queue_attributes(self):
        """Get queue statistics and configuration"""
        try:
            response = self.sqs.get_queue_attributes(
                QueueUrl=self.queue_url,
                AttributeNames=['All']
            )
            
            attributes = response['Attributes']
            
            print("📊 Queue Statistics:")
            print(f"  Messages Available: {attributes.get('ApproximateNumberOfMessages', 0)}")
            print(f"  Messages In Flight: {attributes.get('ApproximateNumberOfMessagesNotVisible', 0)}")
            print(f"  Messages Delayed: {attributes.get('ApproximateNumberOfMessagesDelayed', 0)}")
            print(f"  Visibility Timeout: {attributes.get('VisibilityTimeout', 0)} seconds")
            print(f"  Message Retention: {attributes.get('MessageRetentionPeriod', 0)} seconds")
            
            return attributes
            
        except ClientError as e:
            print(f"❌ Error getting queue attributes: {e}")
            return {}

def continuous_message_processor(queue_url):
    """Continuously process messages from SQS queue"""
    processor = SQSMessageProcessor(queue_url)
    
    print("🚀 Starting continuous message processing...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            # Receive messages (long polling for 20 seconds)
            messages = processor.receive_messages(max_messages=10, wait_time_seconds=20)
            
            if not messages:
                print("⏸️ No messages received, continuing to poll...")
                continue
            
            # Process each message
            for message in messages:
                processor.process_message(message)
            
            # Brief pause between batches
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\\n🛑 Stopping message processor...")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

# Example usage
def main():
    queue_url = "https://sqs.us-east-1.amazonaws.com/123456789012/my-test-queue"
    processor = SQSMessageProcessor(queue_url)
    
    # Send sample messages
    sample_messages = [
        {"order_id": "ORD-001", "customer": "John Doe", "amount": 99.99},
        {"order_id": "ORD-002", "customer": "Jane Smith", "amount": 149.50},
        {"event": "user_signup", "user_id": "USR-123", "email": "user@example.com"}
    ]
    
    # Send individual message with attributes
    message_id = processor.send_message(
        sample_messages[0],
        attributes={
            'priority': 'high',
            'source': 'web-app',
            'timestamp': str(int(time.time()))
        },
        delay_seconds=5
    )
    
    # Send batch of messages
    processor.send_batch_messages(sample_messages)
    
    # Get queue statistics
    processor.get_queue_attributes()
    
    # Start continuous processing
    continuous_message_processor(queue_url)

if __name__ == "__main__":
    main()
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
    **Amazon SNS** is a fully managed messaging service for both application-to-application (A2A) and 
    application-to-person (A2P) communication. It provides topics for high-throughput, push-based, 
    many-to-many messaging between distributed systems, microservices, and event-driven serverless applications.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # SNS Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 300,000\n**Publishes/Second**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 12.5M\n**Subscriptions/Topic**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 256 KB\n**Message Size**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 99.9%\n**Availability SLA**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # SNS Architecture
    st.markdown("### 🏗️ SNS Architecture Overview")
    common.mermaid(create_sns_architecture_mermaid(), height=500)
    
    # Interactive SNS Topic Builder
    st.markdown("### 🛠️ Interactive SNS Topic Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Topic Settings")
        topic_name = st.text_input("Topic Name:", "OrderProcessingEvents")
        topic_type = st.selectbox("Topic Type:", [
            "Standard Topic (High Throughput)",
            "FIFO Topic (Ordered Messages)"
        ])
        
        display_name = st.text_input("Display Name:", "Order Processing Events")
        enable_encryption = st.checkbox("Enable Server-Side Encryption", value=True)
    
    with col2:
        st.markdown("### 🎯 Delivery Policy")
        delivery_retry = st.slider("HTTP Retry Attempts:", 1, 100, 3)
        min_delay_retry = st.slider("Min Delay Target (seconds):", 1, 300, 20)
        max_delay_retry = st.slider("Max Delay Target (seconds):", 1, 3600, 300)
        
        enable_dlq = st.checkbox("Enable Dead Letter Queue", value=True)
    
    # Subscription Configuration
    st.markdown("### 📮 Subscription Configuration")
    
    subscription_types = st.multiselect("Select Subscription Types:", [
        "Amazon SQS Queue", "AWS Lambda Function", "HTTP/HTTPS Endpoint",
        "Email Notification", "SMS Messages", "Mobile Push Notifications"
    ], default=["Amazon SQS Queue", "AWS Lambda Function"])
    
    # Message filtering
    st.markdown("### 🔍 Message Filtering")
    enable_filtering = st.checkbox("Enable Message Filtering", value=False)
    
    if enable_filtering:
        col3, col4 = st.columns(2)
        with col3:
            filter_attribute = st.text_input("Filter Attribute:", "event_type")
            filter_values = st.text_input("Filter Values (comma-separated):", "order_placed,payment_processed")
        
        with col4:
            numeric_filter = st.text_input("Numeric Range Filter (optional):", "price >= 100 AND price <= 500")
    
    if st.button("🚀 Create SNS Topic & Subscriptions", use_container_width=True):
        # Simulate topic creation
        topic_arn = f"arn:aws:sns:us-east-1:123456789012:{topic_name}"
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ SNS Topic Created Successfully!
        
        **Topic Details:**
        - **Topic Name**: {topic_name}
        - **Topic ARN**: {topic_arn}
        - **Type**: {topic_type}
        - **Display Name**: {display_name}
        - **Encryption**: {'✅ Enabled' if enable_encryption else '❌ Disabled'}
        
        **Delivery Configuration:**
        - **Retry Attempts**: {delivery_retry}
        - **Min Delay**: {min_delay_retry}s, **Max Delay**: {max_delay_retry}s
        - **Dead Letter Queue**: {'✅ Enabled' if enable_dlq else '❌ Disabled'}
        
        **Subscriptions Created:**
        {chr(10).join([f"- {sub}" for sub in subscription_types])}
        
        **Message Filtering**: {'✅ Enabled' if enable_filtering else '❌ Disabled'}
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # SNS Benefits Breakdown
    st.markdown("### ✨ SNS Key Benefits")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🚀 Simplify & Reduce Costs
        - **Message filtering** reduces unnecessary processing
        - **Message batching** up to 10 messages per API call
        - Pay only for messages published and delivered
        - **No upfront costs** or minimum fees
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### ✅ Ensure Accuracy
        - **Message ordering** with FIFO topics
        - **Message deduplication** prevents duplicates  
        - **Exactly-once processing** for critical workflows
        - **Delivery status logging** for auditing
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔒 Increase Security
        - **Message encryption** with AWS KMS
        - **VPC endpoints** for private communication
        - **Access control** with IAM policies
        - **Traffic privacy** with AWS PrivateLink
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Message Publishing Simulator
    st.markdown("### 📤 Message Publishing Simulator")
    
    st.markdown('<div class="queue-simulator">', unsafe_allow_html=True)
    
    col5, col6 = st.columns(2)
    
    with col5:
        st.markdown("### 📨 Message Content")
        message_subject = st.text_input("Message Subject:", "New Order Notification")
        message_body = st.text_area("Message Body:", """
{
    "order_id": "ORD-12345",
    "customer_id": "CUST-001", 
    "amount": 199.99,
    "status": "placed",
    "timestamp": "2025-07-15T10:30:00Z"
}
        """.strip(), height=120)
    
    with col6:
        st.markdown("### 🏷️ Message Attributes")
        attr_event_type = st.text_input("event_type:", "order_placed")
        attr_priority = st.selectbox("priority:", ["low", "medium", "high"])
        attr_region = st.text_input("region:", "us-east-1")
    
    if st.button("📡 Publish Message to Topic", use_container_width=True):
        if 'sns_published' not in st.session_state:
            st.session_state.sns_published = []
        
        message = {
            'id': f"msg-{len(st.session_state.sns_published) + 1:04d}",
            'subject': message_subject,
            'body': message_body,
            'attributes': {
                'event_type': attr_event_type,
                'priority': attr_priority,
                'region': attr_region
            },
            'timestamp': time.time(),
            'subscribers_notified': len(subscription_types)
        }
        
        st.session_state.sns_published.append(message)
        
        # Show delivery simulation
        st.success("📡 Message published successfully!")
        
        for sub_type in subscription_types:
            with st.expander(f"📬 Delivered to {sub_type}", expanded=False):
                if "SQS" in sub_type:
                    st.write("✅ Message queued in SQS for reliable processing")
                elif "Lambda" in sub_type:
                    st.write("⚡ Lambda function triggered with message payload")
                elif "HTTP" in sub_type:
                    st.write("🌐 HTTP POST request sent to endpoint")
                elif "Email" in sub_type:
                    st.write("📧 Email notification sent to subscribers")
                elif "SMS" in sub_type:
                    st.write("📱 SMS message sent to phone numbers")
                elif "Push" in sub_type:
                    st.write("📲 Mobile push notification delivered")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Message history
    if 'sns_published' in st.session_state and st.session_state.sns_published:
        st.markdown("### 📊 Recent Publications")
        
        for msg in st.session_state.sns_published[-3:]:  # Show last 3 messages
            st.markdown('<div class="message-card">', unsafe_allow_html=True)
            st.markdown(f"""
            **{msg['id']}** - {msg['subject']}<br>
            **Delivered to**: {msg['subscribers_notified']} subscriber(s)<br>
            **Attributes**: {', '.join([f"{k}={v}" for k, v in msg['attributes'].items()])}
            """)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # SNS Integration Patterns
    st.markdown("### 🔗 Common SNS Integration Patterns")
    
    patterns_data = {
        'Pattern': ['Fanout', 'Event-driven Processing', 'Application Alerts', 'User Notifications', 'System Integration'],
        'Description': [
            'Distribute single message to multiple subscribers',
            'Trigger multiple processing workflows',
            'Send alerts when system events occur',
            'Notify users via email, SMS, or push',
            'Integrate disparate systems and services'
        ],
        'Use Case': [
            'Order processing, data replication',
            'Image processing, data analytics',
            'CloudWatch alarms, security events',
            'Account changes, promotional offers',
            'Legacy system modernization'
        ],
        'Subscribers': [
            'Multiple SQS queues, Lambda functions',
            'Lambda, SQS, HTTP endpoints',
            'Email, SMS, PagerDuty integration',
            'Email, mobile push, in-app notifications',
            'HTTP endpoints, message queues'
        ]
    }
    
    df_patterns = pd.DataFrame(patterns_data)
    st.dataframe(df_patterns, use_container_width=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: SNS Topic Management")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Complete SNS topic management with subscriptions and message filtering
import boto3
import json
from botocore.exceptions import ClientError

class SNSTopicManager:
    def __init__(self, region_name='us-east-1'):
        self.sns = boto3.client('sns', region_name=region_name)
        self.region = region_name
        
    def create_topic(self, topic_name, is_fifo=False, enable_encryption=True):
        """Create SNS topic with optional FIFO and encryption"""
        try:
            topic_attributes = {}
            
            # Configure FIFO topic
            if is_fifo:
                if not topic_name.endswith('.fifo'):
                    topic_name += '.fifo'
                topic_attributes['FifoTopic'] = 'true'
                topic_attributes['ContentBasedDeduplication'] = 'true'
            
            # Enable server-side encryption
            if enable_encryption:
                topic_attributes['KmsMasterKeyId'] = 'alias/aws/sns'
            
            response = self.sns.create_topic(
                Name=topic_name,
                Attributes=topic_attributes
            )
            
            topic_arn = response['TopicArn']
            print(f"✅ Topic created: {topic_arn}")
            
            return topic_arn
            
        except ClientError as e:
            print(f"❌ Error creating topic: {e}")
            return None
    
    def create_subscription(self, topic_arn, protocol, endpoint, filter_policy=None):
        """Create subscription with optional message filtering"""
        try:
            subscription_params = {
                'TopicArn': topic_arn,
                'Protocol': protocol,
                'Endpoint': endpoint
            }
            
            response = self.sns.subscribe(**subscription_params)
            subscription_arn = response['SubscriptionArn']
            
            # Apply message filter policy if provided
            if filter_policy and subscription_arn != 'pending confirmation':
                self.sns.set_subscription_attributes(
                    SubscriptionArn=subscription_arn,
                    AttributeName='FilterPolicy',
                    AttributeValue=json.dumps(filter_policy)
                )
                print(f"🔍 Filter policy applied: {filter_policy}")
            
            print(f"📮 Subscription created: {protocol} -> {endpoint}")
            return subscription_arn
            
        except ClientError as e:
            print(f"❌ Error creating subscription: {e}")
            return None
    
    def publish_message(self, topic_arn, message, subject=None, message_attributes=None, 
                       message_group_id=None, message_deduplication_id=None):
        """Publish message to SNS topic with attributes"""
        try:
            publish_params = {
                'TopicArn': topic_arn,
                'Message': json.dumps(message) if isinstance(message, dict) else message
            }
            
            # Add optional parameters
            if subject:
                publish_params['Subject'] = subject
                
            if message_attributes:
                publish_params['MessageAttributes'] = {}
                for key, value in message_attributes.items():
                    publish_params['MessageAttributes'][key] = {
                        'DataType': 'String',
                        'StringValue': str(value)
                    }
            
            # FIFO-specific parameters
            if message_group_id:
                publish_params['MessageGroupId'] = message_group_id
                
            if message_deduplication_id:
                publish_params['MessageDeduplicationId'] = message_deduplication_id
            
            response = self.sns.publish(**publish_params)
            
            print(f"📡 Message published successfully!")
            print(f"Message ID: {response['MessageId']}")
            
            return response['MessageId']
            
        except ClientError as e:
            print(f"❌ Error publishing message: {e}")
            return None
    
    def setup_fanout_architecture(self, topic_name, subscription_configs):
        """Set up complete fanout architecture with multiple subscriptions"""
        print(f"🚀 Setting up fanout architecture: {topic_name}")
        
        # Create main topic
        topic_arn = self.create_topic(topic_name)
        if not topic_arn:
            return None
        
        subscriptions = []
        
        # Create all subscriptions
        for config in subscription_configs:
            protocol = config['protocol']
            endpoint = config['endpoint']
            filter_policy = config.get('filter_policy')
            
            subscription_arn = self.create_subscription(
                topic_arn, protocol, endpoint, filter_policy
            )
            
            if subscription_arn:
                subscriptions.append({
                    'protocol': protocol,
                    'endpoint': endpoint,
                    'subscription_arn': subscription_arn,
                    'filter_policy': filter_policy
                })
        
        print(f"✅ Fanout setup complete: {len(subscriptions)} subscriptions created")
        
        return {
            'topic_arn': topic_arn,
            'subscriptions': subscriptions
        }
    
    def get_topic_attributes(self, topic_arn):
        """Get detailed topic information and statistics"""
        try:
            response = self.sns.get_topic_attributes(TopicArn=topic_arn)
            attributes = response['Attributes']
            
            print(f"📊 Topic Attributes for {topic_arn}:")
            print(f"  Display Name: {attributes.get('DisplayName', 'N/A')}")
            print(f"  Subscriptions Confirmed: {attributes.get('SubscriptionsConfirmed', 0)}")
            print(f"  Subscriptions Pending: {attributes.get('SubscriptionsPending', 0)}")
            print(f"  Subscriptions Deleted: {attributes.get('SubscriptionsDeleted', 0)}")
            print(f"  Policy: {attributes.get('Policy', 'Default')}")
            print(f"  Encryption: {'Enabled' if attributes.get('KmsMasterKeyId') else 'Disabled'}")
            
            return attributes
            
        except ClientError as e:
            print(f"❌ Error getting topic attributes: {e}")
            return {}
    
    def list_subscriptions_by_topic(self, topic_arn):
        """List all subscriptions for a topic"""
        try:
            response = self.sns.list_subscriptions_by_topic(TopicArn=topic_arn)
            subscriptions = response['Subscriptions']
            
            print(f"📋 Subscriptions for topic {topic_arn}:")
            for sub in subscriptions:
                protocol = sub['Protocol']
                endpoint = sub['Endpoint']
                status = 'Confirmed' if sub['SubscriptionArn'] != 'PendingConfirmation' else 'Pending'
                print(f"  {protocol}: {endpoint} ({status})")
            
            return subscriptions
            
        except ClientError as e:
            print(f"❌ Error listing subscriptions: {e}")
            return []

# Example: E-commerce order processing fanout
def setup_ecommerce_fanout():
    """Set up complete e-commerce order processing with SNS fanout"""
    sns_manager = SNSTopicManager()
    
    # Define subscription configurations
    subscription_configs = [
        {
            'protocol': 'sqs',
            'endpoint': 'arn:aws:sqs:us-east-1:123456789012:order-processing-queue',
            'filter_policy': {
                'event_type': ['order_placed', 'order_updated']
            }
        },
        {
            'protocol': 'sqs', 
            'endpoint': 'arn:aws:sqs:us-east-1:123456789012:inventory-updates-queue',
            'filter_policy': {
                'event_type': ['order_placed'],
                'requires_inventory_update': ['true']
            }
        },
        {
            'protocol': 'lambda',
            'endpoint': 'arn:aws:lambda:us-east-1:123456789012:function:send-order-confirmation',
            'filter_policy': {
                'event_type': ['order_placed']
            }
        },
        {
            'protocol': 'email',
            'endpoint': 'admin@mystore.com',
            'filter_policy': {
                'priority': ['high'],
                'order_value': [{'numeric': ['>', 500]}]
            }
        }
    ]
    
    # Set up fanout architecture
    architecture = sns_manager.setup_fanout_architecture(
        'EcommerceOrderEvents',
        subscription_configs
    )
    
    if architecture:
        topic_arn = architecture['topic_arn']
        
        # Publish sample order events
        sample_orders = [
            {
                'order_id': 'ORD-001',
                'customer_id': 'CUST-123',
                'amount': 299.99,
                'status': 'placed',
                'items': [
                    {'product_id': 'PROD-001', 'quantity': 2},
                    {'product_id': 'PROD-002', 'quantity': 1}
                ]
            },
            {
                'order_id': 'ORD-002', 
                'customer_id': 'CUST-456',
                'amount': 750.00,
                'status': 'high_value',
                'priority': 'high'
            }
        ]
        
        for order in sample_orders:
            message_attributes = {
                'event_type': 'order_placed',
                'priority': order.get('priority', 'normal'),
                'requires_inventory_update': 'true',
                'order_value': str(order['amount'])
            }
            
            sns_manager.publish_message(
                topic_arn=topic_arn,
                message=order,
                subject=f"New Order: {order['order_id']}",
                message_attributes=message_attributes
            )
        
        # Get topic statistics
        sns_manager.get_topic_attributes(topic_arn)
        sns_manager.list_subscriptions_by_topic(topic_arn)
        
        return architecture
    
    return None

# Main execution
if __name__ == "__main__":
    # Set up e-commerce fanout example
    architecture = setup_ecommerce_fanout()
    
    if architecture:
        print("\\n🎉 E-commerce fanout architecture successfully deployed!")
        print(f"Topic ARN: {architecture['topic_arn']}")
        print(f"Subscriptions: {len(architecture['subscriptions'])}")
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def sns_fanout_tab():
    """Content for Common Amazon SNS Scenario - Fanout tab"""
    st.markdown("## 🌟 Common Amazon SNS Scenario - Fanout")
    st.markdown("*Replicate and push messages to multiple endpoints for parallel asynchronous processing*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    The **Fanout scenario** is when a message published to an SNS topic is replicated and pushed to multiple endpoints, 
    such as Amazon Kinesis Data Firehose delivery streams, Amazon SQS queues, HTTP(S) endpoints, and Lambda functions. 
    This allows for parallel asynchronous processing where each subscriber can handle the message independently.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Fanout Architecture
    st.markdown("### 🏗️ E-commerce Order Processing Fanout")
    common.mermaid(create_fanout_scenario_mermaid(), height=400)
    
    # Interactive Fanout Builder
    st.markdown("### 🛠️ Interactive Fanout Pattern Builder")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Event Source Configuration")
        event_source = st.selectbox("Select Event Source:", [
            "E-commerce Order System", "User Registration System", "IoT Sensor Data",
            "File Upload Processing", "Payment Processing", "Custom Application"
        ])
        
        trigger_event = st.selectbox("Trigger Event:", [
            "Order Placed", "User Registered", "Sensor Reading", "File Uploaded", 
            "Payment Completed", "Custom Event"
        ])
        
        message_volume = st.slider("Expected Messages/Day:", 100, 1000000, 10000)
    
    with col2:
        st.markdown("### 🎯 Processing Requirements")
        processing_types = st.multiselect("Select Processing Types:", [
            "Real-time Processing (Lambda)", "Batch Processing (SQS)", 
            "Data Analytics (Kinesis)", "Email Notifications", 
            "SMS Alerts", "Webhook Integration", "Database Updates"
        ], default=["Real-time Processing (Lambda)", "Batch Processing (SQS)"])
        
        reliability_level = st.selectbox("Reliability Level:", [
            "Best Effort", "At Least Once", "Exactly Once"
        ])
    
    # Subscriber Configuration
    st.markdown("### 📮 Subscriber Configuration")
    
    subscribers_config = []
    
    for i, proc_type in enumerate(processing_types):
        with st.expander(f"Configure {proc_type}", expanded=i < 2):
            col3, col4 = st.columns(2)
            
            with col3:
                if "Lambda" in proc_type:
                    function_name = st.text_input(f"Lambda Function Name:", f"process-{proc_type.lower().replace(' ', '-')}", key=f"fn_{i}")
                    timeout = st.slider(f"Function Timeout (seconds):", 5, 900, 30, key=f"timeout_{i}")
                    subscribers_config.append({
                        'type': 'lambda',
                        'name': function_name,
                        'endpoint': f"arn:aws:lambda:us-east-1:123456789012:function:{function_name}",
                        'config': {'timeout': timeout}
                    })
                
                elif "SQS" in proc_type:
                    queue_name = st.text_input(f"SQS Queue Name:", f"{proc_type.lower().replace(' ', '-')}-queue", key=f"queue_{i}")
                    visibility_timeout = st.slider(f"Visibility Timeout (seconds):", 30, 900, 300, key=f"vis_{i}")
                    subscribers_config.append({
                        'type': 'sqs',
                        'name': queue_name,
                        'endpoint': f"arn:aws:sqs:us-east-1:123456789012:{queue_name}",
                        'config': {'visibility_timeout': visibility_timeout}
                    })
                
                elif "Email" in proc_type:
                    email_address = st.text_input(f"Email Address:", "admin@company.com", key=f"email_{i}")
                    subscribers_config.append({
                        'type': 'email',
                        'name': 'Email Notification',
                        'endpoint': email_address,
                        'config': {'format': 'json'}
                    })
                
                elif "SMS" in proc_type:
                    phone_number = st.text_input(f"Phone Number:", "+1234567890", key=f"sms_{i}")
                    subscribers_config.append({
                        'type': 'sms',
                        'name': 'SMS Alert',
                        'endpoint': phone_number,
                        'config': {'format': 'text'}
                    })
                
                elif "Webhook" in proc_type:
                    webhook_url = st.text_input(f"Webhook URL:", "https://api.company.com/webhook", key=f"webhook_{i}")
                    subscribers_config.append({
                        'type': 'http',
                        'name': 'Webhook Integration',
                        'endpoint': webhook_url,
                        'config': {'retry_policy': 'exponential_backoff'}
                    })
            
            with col4:
                # Message filtering for this subscriber
                enable_filter = st.checkbox(f"Enable Message Filtering", key=f"filter_{i}")
                if enable_filter:
                    filter_attr = st.text_input(f"Filter Attribute:", "event_type", key=f"filter_attr_{i}")
                    filter_values = st.text_input(f"Filter Values (comma-separated):", "high_priority,urgent", key=f"filter_vals_{i}")
                    
                    if len(subscribers_config) > i:
                        subscribers_config[i]['filter'] = {
                            filter_attr: filter_values.split(',') if filter_values else []
                        }
    
    # Generate Fanout Architecture
    if st.button("🚀 Generate Fanout Architecture", use_container_width=True):
        total_subscribers = len(subscribers_config)
        estimated_cost_per_million = total_subscribers * 0.50  # Rough estimate
        
        st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### ✅ Fanout Architecture Generated!
        
        **Architecture Overview:**
        - **Event Source**: {event_source} - {trigger_event}
        - **SNS Topic**: {trigger_event.replace(' ', '').lower()}-events
        - **Total Subscribers**: {total_subscribers}
        - **Message Volume**: {message_volume:,} messages/day
        - **Reliability**: {reliability_level}
        
        **Cost Estimation:**
        - **SNS Publishing**: ${(message_volume * 0.50 / 1000000):.2f}/day
        - **Delivery Cost**: ${(message_volume * total_subscribers * 0.50 / 1000000):.2f}/day
        - **Total Estimated**: ${((message_volume * total_subscribers * 0.50 / 1000000) + (message_volume * 0.50 / 1000000)):.2f}/day
        
        🎯 **Benefits**: Parallel processing, loose coupling, fault tolerance
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Fanout Benefits Analysis
    st.markdown("### ✨ Fanout Pattern Benefits")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🚀 Performance Benefits
        - **Parallel Processing**: Multiple subscribers process simultaneously
        - **Scalability**: Add/remove subscribers without affecting others
        - **Load Distribution**: Spread processing across multiple services
        - **Real-time Response**: Immediate delivery to all subscribers
        
        ### 🛡️ Reliability Benefits
        - **Fault Isolation**: Failure in one subscriber doesn't affect others
        - **Redundancy**: Multiple processing paths for critical operations
        - **Dead Letter Queues**: Handle failed deliveries gracefully
        - **Retry Mechanisms**: Automatic retry with exponential backoff
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🔧 Architectural Benefits
        - **Loose Coupling**: Publishers and subscribers are independent
        - **Flexibility**: Easy to add new processing logic
        - **Service Ownership**: Teams can own their subscribers independently
        - **Event-Driven**: Reactive architecture pattern
        
        ### 💰 Cost Benefits
        - **Efficient Resource Usage**: Pay only for messages processed
        - **No Idle Costs**: Serverless components scale to zero
        - **Reduced Infrastructure**: Managed service eliminates overhead
        - **Optimized Throughput**: Built-in batching and filtering
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Real-world Fanout Examples
    st.markdown("### 🌍 Real-world Fanout Use Cases")
    
    use_cases_data = {
        'Use Case': [
            'E-commerce Order Processing',
            'User Registration Pipeline', 
            'IoT Data Processing',
            'Content Publishing',
            'Financial Transactions',
            'System Monitoring'
        ],
        'Event Trigger': [
            'Order placed by customer',
            'New user signs up',
            'Sensor sends data reading',
            'Blog post published',
            'Payment processed',
            'System alarm triggered'
        ],
        'Fanout Destinations': [
            'Order fulfillment, inventory, analytics, notifications',
            'Welcome email, user profile, analytics, CRM sync',
            'Real-time dashboard, data lake, alerting, ML pipeline',
            'Email subscribers, social media, search index',
            'Fraud detection, accounting, notifications, reporting',
            'PagerDuty, email, Slack, ticket creation'
        ],
        'Business Value': [
            'Faster order processing, better customer experience',
            'Improved onboarding, data consistency',
            'Real-time insights, predictive maintenance',
            'Broader reach, better engagement',
            'Enhanced security, regulatory compliance',
            'Faster incident response, reduced downtime'
        ]
    }
    
    df_use_cases = pd.DataFrame(use_cases_data)
    st.dataframe(df_use_cases, use_container_width=True)
    
    # Message Flow Simulation
    st.markdown("### 🔄 Message Flow Simulation")
    
    if st.button("🎬 Simulate Message Flow", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Simulate message publishing
        status_text.text("📡 Publishing message to SNS topic...")
        progress_bar.progress(20)
        time.sleep(1)
        
        # Simulate fanout to subscribers
        status_text.text("🌟 Fanning out to subscribers...")
        progress_bar.progress(40)
        time.sleep(1)
        
        # Simulate parallel processing
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.success("✅ Lambda Function\nProcessing completed in 2.1s")
        with col2:
            st.success("✅ SQS Queue\nMessage queued for batch processing")
        with col3:
            st.success("✅ Email Notification\nSent to admin@company.com")
        
        progress_bar.progress(80)
        time.sleep(1)
        
        status_text.text("🎉 All subscribers processed successfully!")
        progress_bar.progress(100)
        
        st.balloons()
    
    # Best Practices
    st.markdown("### 💡 Fanout Pattern Best Practices") 
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Design Guidelines
    
    **Message Design:**
    - Keep messages **small and focused** - avoid large payloads
    - Use **consistent message format** across all subscribers
    - Include **correlation IDs** for tracking and debugging
    - Design for **idempotency** - handle duplicate messages gracefully
    
    **Subscription Management:**
    - Use **message filtering** to reduce unnecessary processing
    - Implement **dead letter queues** for failed message handling
    - Monitor **subscription health** and delivery metrics
    - Consider **subscriber scaling** requirements and limits
    
    **Error Handling:**
    - Design **retry policies** appropriate for each subscriber type
    - Implement **circuit breakers** for failing downstream services
    - Use **exponential backoff** to avoid overwhelming systems
    - Monitor and **alert on delivery failures**
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Complete Fanout Implementation")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Complete fanout implementation with error handling and monitoring
import boto3
import json
import uuid
from datetime import datetime
from botocore.exceptions import ClientError

class FanoutProcessor:
    def __init__(self, region_name='us-east-1'):
        self.sns = boto3.client('sns', region_name=region_name)
        self.cloudwatch = boto3.client('cloudwatch', region_name=region_name)
        
    def create_fanout_architecture(self, topic_name, subscribers_config):
        """Create complete fanout architecture with multiple subscriber types"""
        print(f"🚀 Creating fanout architecture: {topic_name}")
        
        # Create SNS topic
        topic_response = self.sns.create_topic(
            Name=topic_name,
            Attributes={
                'DisplayName': f'{topic_name} Fanout Topic',
                'DeliveryPolicy': json.dumps({
                    'http': {
                        'defaultHealthyRetryPolicy': {
                            'minDelayTarget': 20,
                            'maxDelayTarget': 300,
                            'numRetries': 3,
                            'numMaxDelayRetries': 2,
                            'backoffFunction': 'exponential'
                        }
                    }
                })
            }
        )
        
        topic_arn = topic_response['TopicArn']
        print(f"📋 Topic created: {topic_arn}")
        
        # Create subscriptions for each subscriber
        subscriptions = []
        
        for config in subscribers_config:
            subscription_arn = self.create_filtered_subscription(
                topic_arn, 
                config['protocol'], 
                config['endpoint'],
                config.get('filter_policy'),
                config.get('delivery_policy')
            )
            
            if subscription_arn:
                subscriptions.append({
                    'protocol': config['protocol'],
                    'endpoint': config['endpoint'], 
                    'subscription_arn': subscription_arn,
                    'name': config.get('name', f"{config['protocol']}_subscriber")
                })
        
        return {
            'topic_arn': topic_arn,
            'subscriptions': subscriptions,
            'total_subscribers': len(subscriptions)
        }
    
    def create_filtered_subscription(self, topic_arn, protocol, endpoint, 
                                   filter_policy=None, delivery_policy=None):
        """Create subscription with optional filtering and delivery policies"""
        try:
            # Create basic subscription
            response = self.sns.subscribe(
                TopicArn=topic_arn,
                Protocol=protocol,
                Endpoint=endpoint
            )
            
            subscription_arn = response['SubscriptionArn']
            
            # Wait for confirmation for certain protocols
            if subscription_arn == 'pending confirmation':
                print(f"⏳ Subscription pending confirmation: {protocol} -> {endpoint}")
                return subscription_arn
            
            # Apply message filter policy
            if filter_policy:
                self.sns.set_subscription_attributes(
                    SubscriptionArn=subscription_arn,
                    AttributeName='FilterPolicy',
                    AttributeValue=json.dumps(filter_policy)
                )
                print(f"🔍 Filter policy applied: {filter_policy}")
            
            # Apply custom delivery policy
            if delivery_policy:
                self.sns.set_subscription_attributes(
                    SubscriptionArn=subscription_arn,
                    AttributeName='DeliveryPolicy',
                    AttributeValue=json.dumps(delivery_policy)
                )
                print(f"📦 Custom delivery policy applied")
            
            print(f"✅ Subscription created: {protocol} -> {endpoint}")
            return subscription_arn
            
        except ClientError as e:
            print(f"❌ Error creating subscription: {e}")
            return None
    
    def publish_event(self, topic_arn, event_data, event_type, attributes=None):
        """Publish event with structured data and attributes"""
        try:
            # Create structured message
            message = {
                'event_id': str(uuid.uuid4()),
                'event_type': event_type,
                'timestamp': datetime.utcnow().isoformat(),
                'data': event_data,
                'version': '1.0'
            }
            
            # Prepare message attributes for filtering
            message_attributes = {
                'event_type': {
                    'DataType': 'String',
                    'StringValue': event_type
                },
                'timestamp': {
                    'DataType': 'String', 
                    'StringValue': message['timestamp']
                }
            }
            
            # Add custom attributes
            if attributes:
                for key, value in attributes.items():
                    message_attributes[key] = {
                        'DataType': 'String',
                        'StringValue': str(value)
                    }
            
            # Publish message
            response = self.sns.publish(
                TopicArn=topic_arn,
                Message=json.dumps(message),
                Subject=f"Event: {event_type}",
                MessageAttributes=message_attributes
            )
            
            message_id = response['MessageId']
            print(f"📡 Event published successfully!")
            print(f"Event ID: {message['event_id']}")
            print(f"Message ID: {message_id}")
            print(f"Event Type: {event_type}")
            
            # Log metrics to CloudWatch
            self.log_publish_metric(event_type)
            
            return message_id
            
        except ClientError as e:
            print(f"❌ Error publishing event: {e}")
            return None
    
    def log_publish_metric(self, event_type):
        """Log custom metrics to CloudWatch"""
        try:
            self.cloudwatch.put_metric_data(
                Namespace='SNS/Fanout',
                MetricData=[
                    {
                        'MetricName': 'EventsPublished',
                        'Dimensions': [
                            {
                                'Name': 'EventType',
                                'Value': event_type
                            }
                        ],
                        'Value': 1,
                        'Unit': 'Count'
                    }
                ]
            )
        except Exception as e:
            print(f"Warning: Could not log metrics: {e}")
    
    def monitor_fanout_health(self, topic_arn):
        """Monitor fanout architecture health and performance"""
        try:
            # Get topic attributes
            topic_response = self.sns.get_topic_attributes(TopicArn=topic_arn)
            topic_attrs = topic_response['Attributes']
            
            print(f"📊 Fanout Health Report")
            print(f"Topic ARN: {topic_arn}")
            print(f"Subscriptions Confirmed: {topic_attrs.get('SubscriptionsConfirmed', 0)}")
            print(f"Subscriptions Pending: {topic_attrs.get('SubscriptionsPending', 0)}")
            print(f"Subscriptions Deleted: {topic_attrs.get('SubscriptionsDeleted', 0)}")
            
            # List all subscriptions and their status
            subs_response = self.sns.list_subscriptions_by_topic(TopicArn=topic_arn)
            subscriptions = subs_response['Subscriptions']
            
            print(f"\\n📋 Subscriber Details:")
            healthy_subs = 0
            
            for sub in subscriptions:
                protocol = sub['Protocol']
                endpoint = sub['Endpoint']
                sub_arn = sub['SubscriptionArn']
                
                if sub_arn != 'PendingConfirmation':
                    # Get subscription attributes
                    try:
                        sub_attrs_response = self.sns.get_subscription_attributes(
                            SubscriptionArn=sub_arn
                        )
                        sub_attrs = sub_attrs_response['Attributes']
                        
                        filter_policy = sub_attrs.get('FilterPolicy', 'None')
                        delivery_policy = sub_attrs.get('DeliveryPolicy', 'Default')
                        
                        print(f"  ✅ {protocol}: {endpoint}")
                        print(f"     Filter Policy: {filter_policy}")
                        print(f"     Delivery Policy: {delivery_policy}")
                        
                        healthy_subs += 1
                        
                    except ClientError as e:
                        print(f"  ❌ {protocol}: {endpoint} - Error: {e}")
                else:
                    print(f"  ⏳ {protocol}: {endpoint} - Pending Confirmation")
            
            health_percentage = (healthy_subs / len(subscriptions)) * 100 if subscriptions else 0
            print(f"\\n🎯 Overall Health: {health_percentage:.1f}% ({healthy_subs}/{len(subscriptions)} subscribers healthy)")
            
            return {
                'total_subscriptions': len(subscriptions),
                'healthy_subscriptions': healthy_subs,
                'health_percentage': health_percentage
            }
            
        except ClientError as e:
            print(f"❌ Error monitoring fanout health: {e}")
            return None

# Example: E-commerce order processing fanout
def setup_ecommerce_fanout_example():
    """Complete e-commerce order processing fanout example"""
    fanout = FanoutProcessor()
    
    # Define subscribers with different protocols and filters
    subscribers_config = [
        {
            'protocol': 'sqs',
            'endpoint': 'arn:aws:sqs:us-east-1:123456789012:order-fulfillment-queue',
            'name': 'Order Fulfillment',
            'filter_policy': {
                'event_type': ['order_placed', 'order_updated'],
                'order_status': ['confirmed']
            }
        },
        {
            'protocol': 'sqs',
            'endpoint': 'arn:aws:sqs:us-east-1:123456789012:inventory-management-queue', 
            'name': 'Inventory Management',
            'filter_policy': {
                'event_type': ['order_placed'],
                'requires_inventory_update': ['true']
            }
        },
        {
            'protocol': 'lambda',
            'endpoint': 'arn:aws:lambda:us-east-1:123456789012:function:send-order-notification',
            'name': 'Order Notifications',
            'filter_policy': {
                'event_type': ['order_placed', 'order_shipped']
            }
        },
        {
            'protocol': 'https',
            'endpoint': 'https://analytics.mystore.com/webhook/orders',
            'name': 'Analytics Webhook',
            'delivery_policy': {
                'healthyRetryPolicy': {
                    'minDelayTarget': 10,
                    'maxDelayTarget': 600,
                    'numRetries': 5
                }
            }
        },
        {
            'protocol': 'email',
            'endpoint': 'orders@mystore.com',
            'name': 'Email Alerts',
            'filter_policy': {
                'priority': ['high'],
                'order_value': [{'numeric': ['>', 500]}]
            }
        }
    ]
    
    # Create fanout architecture
    architecture = fanout.create_fanout_architecture(
        'EcommerceOrderEvents',
        subscribers_config
    )
    
    if architecture:
        topic_arn = architecture['topic_arn']
        
        # Publish sample order events
        sample_orders = [
            {
                'order_id': 'ORD-001',
                'customer_id': 'CUST-12345',
                'items': [
                    {'product_id': 'PROD-001', 'quantity': 2, 'price': 29.99},
                    {'product_id': 'PROD-002', 'quantity': 1, 'price': 49.99}
                ],
                'total_amount': 109.97,
                'shipping_address': {
                    'street': '123 Main St',
                    'city': 'Anytown',
                    'state': 'CA',
                    'zip': '12345'
                },
                'status': 'confirmed'
            },
            {
                'order_id': 'ORD-002',
                'customer_id': 'CUST-67890', 
                'items': [
                    {'product_id': 'PROD-003', 'quantity': 1, 'price': 799.99}
                ],
                'total_amount': 799.99,
                'status': 'high_value_order'
            }
        ]
        
        # Publish events with different attributes for filtering
        for order in sample_orders:
            attributes = {
                'order_status': order['status'],
                'requires_inventory_update': 'true',
                'priority': 'high' if order['total_amount'] > 500 else 'normal',
                'order_value': str(order['total_amount']),
                'customer_id': order['customer_id']
            }
            
            fanout.publish_event(
                topic_arn=topic_arn,
                event_data=order,
                event_type='order_placed',
                attributes=attributes
            )
        
        # Monitor fanout health
        health_report = fanout.monitor_fanout_health(topic_arn)
        
        print(f"\\n🎉 E-commerce fanout architecture deployed successfully!")
        print(f"📊 Architecture Summary:")
        print(f"  Topic ARN: {topic_arn}")
        print(f"  Total Subscribers: {architecture['total_subscribers']}")
        print(f"  Sample Events Published: {len(sample_orders)}")
        
        return architecture
    
    return None

# Main execution
if __name__ == "__main__":
    setup_ecommerce_fanout_example()
    ''', language='python')
    st.markdown('</div>', unsafe_allow_html=True)

def message_channels_tab():
    """Content for Message Channels tab"""
    st.markdown("## 📨 Message Channels")
    st.markdown("*Understanding Point-to-Point (Queue) vs Publish-Subscribe (Topic) communication patterns*")
    
    # Key concept
    st.markdown('<div class="concept-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Key Concept
    **Message Channels** are communication pathways that determine how messages flow between applications. 
    AWS provides two primary messaging patterns: **Point-to-Point** using SQS queues where only one receiver 
    processes each message, and **Publish-Subscribe** using SNS topics where all subscribers receive every message.
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Message Channels Comparison
    st.markdown("### ⚖️ Message Channel Patterns Comparison")
    common.mermaid(create_message_channels_mermaid(), height=450)
    
    # Interactive Pattern Selector
    st.markdown("### 🎮 Interactive Pattern Selector")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Use Case Analysis")
        use_case = st.selectbox("Select Your Use Case:", [
            "Task Processing (Work Queue)",
            "Event Notifications (All Systems)",
            "Load Balancing (Distribute Work)",
            "Broadcasting (Inform Everyone)",
            "Order Processing Pipeline",
            "User Activity Tracking",
            "System Monitoring Alerts",
            "File Processing Workflow"
        ])
        
        message_volume = st.slider("Messages per Day:", 100, 1000000, 10000)
        processing_time = st.slider("Avg Processing Time (seconds):", 1, 300, 30)
    
    with col2:
        st.markdown("### 🎯 Requirements")
        delivery_requirement = st.selectbox("Message Delivery:", [
            "Only one processor should handle each message",
            "All systems need to receive every message",
            "Mixed - some exclusive, some broadcast"
        ])
        
        processing_style = st.selectbox("Processing Style:", [
            "Sequential Processing", "Parallel Processing", "Batch Processing", "Real-time Processing"
        ])
        
        failure_handling = st.selectbox("Failure Handling:", [
            "Retry until success", "Forward to error handler", "Log and continue", "Manual intervention"
        ])
    
    # Pattern Recommendation Engine
    if st.button("🤖 Get Pattern Recommendation", use_container_width=True):
        # Simple recommendation logic
        if "only one processor" in delivery_requirement.lower() or "work queue" in use_case.lower() or "load balancing" in use_case.lower():
            recommended_pattern = "Point-to-Point (SQS Queue)"
            recommended_service = "Amazon SQS"
            pattern_color = AWS_COLORS['success']
            
            benefits = [
                "Only one consumer processes each message",
                "Built-in load balancing across consumers", 
                "Message persistence and reliability",
                "Cost-effective for high-volume processing"
            ]
            
            considerations = [
                "Messages are consumed and removed from queue",
                "No built-in message broadcasting",
                "Requires polling by consumers"
            ]
            
        elif "all systems" in delivery_requirement.lower() or "broadcasting" in use_case.lower() or "event notifications" in use_case.lower():
            recommended_pattern = "Publish-Subscribe (SNS Topic)"
            recommended_service = "Amazon SNS"
            pattern_color = AWS_COLORS['primary']
            
            benefits = [
                "All subscribers receive every message",
                "Supports multiple protocol types",
                "Real-time push delivery",
                "Easy to add/remove subscribers"
            ]
            
            considerations = [
                "All subscribers get all messages",
                "No built-in message queuing",
                "Requires subscription management"
            ]
            
        else:
            recommended_pattern = "Hybrid (SNS + SQS)"
            recommended_service = "Amazon SNS + SQS"
            pattern_color = AWS_COLORS['light_blue']
            
            benefits = [
                "Combines benefits of both patterns",
                "Fanout pattern for broadcasting",
                "Reliable queuing for processing",
                "Flexible architecture"
            ]
            
            considerations = [
                "More complex architecture",
                "Higher cost for multiple services",
                "Requires careful design planning"
            ]
        
        st.markdown(f'<div class="highlight-box">', unsafe_allow_html=True)
        st.markdown(f"""
        ### 🎯 Recommended Pattern: {recommended_pattern}
        
        **Best Service**: {recommended_service}
        
        **Why This Pattern:**
        Based on your use case "{use_case}" and requirement "{delivery_requirement}", 
        this pattern provides the optimal solution for your needs.
        
        **Key Benefits:**
        {chr(10).join([f"• {benefit}" for benefit in benefits])}
        
        **Considerations:**
        {chr(10).join([f"• {consideration}" for consideration in considerations])}
        
        **Estimated Throughput**: {min(message_volume, 120000):,} messages/day
        **Estimated Cost**: ${(message_volume * 0.0000005 * (2 if 'Hybrid' in recommended_pattern else 1)):.2f}/day
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Detailed Pattern Comparison
    st.markdown("### 📊 Detailed Pattern Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 🎯 Point-to-Point (Queue)
        **Service**: Amazon SQS
        
        **How it Works:**
        - Messages sent to a queue
        - **Only one consumer** receives each message
        - Messages removed after processing
        - Multiple consumers can compete for messages
        
        **Best For:**
        - **Task processing** and work distribution
        - **Load balancing** across workers
        - **Sequential processing** workflows
        - **Cost-sensitive** high-volume scenarios
        
        **Key Features:**
        - Message persistence (up to 14 days)
        - Visibility timeout prevents duplicates
        - Dead letter queues for failed messages
        - FIFO queues for ordered processing
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        ### 📢 Publish-Subscribe (Topic)
        **Service**: Amazon SNS
        
        **How it Works:**
        - Messages published to a topic
        - **All subscribers** receive every message
        - Multiple delivery protocols supported
        - Push-based delivery model
        
        **Best For:**
        - **Event notifications** and alerts
        - **Broadcasting** information
        - **Real-time updates** to multiple systems
        - **Decoupled architectures**
        
        **Key Features:**
        - Multiple subscription types (SQS, Lambda, HTTP, Email, SMS)
        - Message filtering for selective delivery
        - Fanout pattern implementation
        - Mobile push notifications
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Pattern Features Comparison Table
    st.markdown("### 🔍 Feature Comparison Matrix")
    
    comparison_data = {
        'Feature': [
            'Message Delivery', 'Consumer Model', 'Message Persistence', 'Delivery Method',
            'Scaling', 'Cost Model', 'Throughput', 'Use Case Fit'
        ],
        'Point-to-Point (SQS)': [
            'One consumer per message', 'Pull-based polling', 'Up to 14 days', 'Consumer pulls messages',
            'Add more consumers', 'Per message + requests', '120K msg/sec', 'Work queues, task processing'
        ],
        'Publish-Subscribe (SNS)': [
            'All subscribers get message', 'Push-based delivery', 'No persistence (delivery only)', 'Push to subscribers',
            'Add more subscribers', 'Per message + deliveries', '300K publishes/sec', 'Events, notifications, broadcasting'
        ]
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True)
    
    # Real-world Usage Scenarios
    st.markdown("### 🌍 Real-world Usage Scenarios")
    
    scenario_tabs = st.tabs(["📦 E-commerce", "📱 Social Media", "🏭 IoT Processing", "💰 Financial Services"])
    
    with scenario_tabs[0]:
        st.markdown("### 📦 E-commerce Platform Architecture")
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        **Order Processing Workflow:**
        
        1. **Customer Places Order** → SNS Topic publishes "OrderPlaced" event
           - *Publish-Subscribe*: All systems need to know about the order
        
        2. **Event Subscribers Receive Notification:**
           - **Inventory Service** → Checks stock levels
           - **Payment Service** → Processes payment
           - **Email Service** → Sends confirmation email
           - **Analytics Service** → Records order metrics
        
        3. **Order Fulfillment Queue** → SQS Queue receives order details
           - *Point-to-Point*: Only one fulfillment worker should process each order
        
        4. **Warehouse Workers** → Poll SQS queue for orders to fulfill
           - Multiple workers compete for orders
           - Load balancing automatically handled
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with scenario_tabs[1]:
        st.markdown("### 📱 Social Media Platform Architecture")
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        **User Activity Processing:**
        
        1. **User Posts Content** → SNS Topic publishes "ContentPosted" event
           - *Publish-Subscribe*: Multiple services need to react
        
        2. **Event Subscribers:**
           - **Timeline Service** → Updates follower timelines
           - **Recommendation Engine** → Analyzes content for recommendations
           - **Content Moderation** → Scans for inappropriate content
           - **Analytics Service** → Tracks engagement metrics
        
        3. **Image Processing Queue** → SQS Queue for image resize/optimization
           - *Point-to-Point*: Only one worker should process each image
        
        4. **Notification Queue** → SQS Queue for push notifications
           - *Point-to-Point*: Distribute notification workload across workers
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with scenario_tabs[2]:
        st.markdown("### 🏭 IoT Data Processing Architecture")
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        **Sensor Data Pipeline:**
        
        1. **IoT Sensors Send Data** → SNS Topic publishes "SensorReading" event
           - *Publish-Subscribe*: Multiple analytics systems need raw data
        
        2. **Event Subscribers:**
           - **Real-time Dashboard** → Updates live monitoring displays
           - **Alerting System** → Checks for threshold violations
           - **Data Lake** → Stores data for historical analysis
           - **ML Pipeline** → Feeds machine learning models
        
        3. **Alert Processing Queue** → SQS Queue for critical alerts
           - *Point-to-Point*: Only one alert handler per critical event
        
        4. **Batch Processing Queue** → SQS Queue for heavy analytics
           - *Point-to-Point*: Distribute computational workload
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with scenario_tabs[3]:
        st.markdown("### 💰 Financial Services Architecture")
        
        st.markdown('<div class="concept-card">', unsafe_allow_html=True)
        st.markdown("""
        **Transaction Processing:**
        
        1. **Transaction Initiated** → SNS Topic publishes "TransactionEvent"
           - *Publish-Subscribe*: Multiple systems need transaction data
        
        2. **Event Subscribers:**
           - **Fraud Detection** → Analyzes transaction patterns
           - **Compliance Service** → Checks regulatory requirements
           - **Customer Service** → Updates account notifications
           - **Reporting Service** → Updates transaction reports
        
        3. **Transaction Processing Queue** → SQS FIFO Queue for ordered processing
           - *Point-to-Point*: Ensure exactly-once processing per transaction
        
        4. **Audit Queue** → SQS Queue for compliance logging
           - *Point-to-Point*: Distribute audit processing workload
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Performance Comparison Chart
    st.markdown("### 📈 Performance Characteristics")
    
    # Create performance comparison chart
    metrics = ['Throughput', 'Latency', 'Scalability', 'Reliability', 'Cost Efficiency']
    sqs_scores = [85, 70, 90, 95, 90]  # Point-to-Point scores
    sns_scores = [95, 95, 85, 90, 80]  # Publish-Subscribe scores
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=sqs_scores,
        theta=metrics,
        fill='toself',
        name='Point-to-Point (SQS)',
        line_color=AWS_COLORS['success']
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=sns_scores,
        theta=metrics,
        fill='toself',
        name='Publish-Subscribe (SNS)',
        line_color=AWS_COLORS['primary']
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        title="Message Pattern Performance Comparison",
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Best Practices
    st.markdown("### 💡 Message Channel Selection Best Practices")
    
    st.markdown('<div class="warning-box">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Decision Framework
    
    **Choose Point-to-Point (SQS) When:**
    - Need **exactly-once processing** per message
    - Implementing **work queues** or task distribution
    - Want **automatic load balancing** across consumers
    - Require **message persistence** and reliability
    - Processing is **resource-intensive** or time-consuming
    
    **Choose Publish-Subscribe (SNS) When:**
    - Need to **notify multiple systems** about events
    - Implementing **event-driven architecture**
    - Want **real-time push delivery**
    - Multiple systems need **different views** of same data
    - Building **loosely coupled** microservices
    
    **Use Hybrid Pattern When:**
    - Need both **broadcasting AND reliable processing**
    - Implementing **complex workflows** with multiple stages  
    - Want **fanout pattern** with queuing benefits
    - Building **enterprise-scale** distributed systems
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Code Example
    st.markdown("### 💻 Code Example: Implementing Both Patterns")
    st.markdown('<div class="code-container">', unsafe_allow_html=True)
    st.code('''
# Complete implementation showing both message channel patterns
import boto3
import json
import time
from concurrent.futures import ThreadPoolExecutor
from botocore.exceptions import ClientError

class MessageChannelDemo:
    def __init__(self, region_name='us-east-1'):
        self.sqs = boto3.client('sqs', region_name=region_name)
        self.sns = boto3.client('sns', region_name=region_name)
        
    def setup_point_to_point_pattern(self, queue_name):
        """Set up Point-to-Point pattern using SQS"""
        print(f"🎯 Setting up Point-to-Point pattern: {queue_name}")
        
        try:
            # Create SQS queue with dead letter queue
            dlq_response = self.sqs.create_queue(
                QueueName=f"{queue_name}-dlq",
                Attributes={
                    'MessageRetentionPeriod': '1209600'  # 14 days
                }
            )
            dlq_url = dlq_response['QueueUrl']
            
            # Get DLQ ARN for main queue configuration
            dlq_attrs = self.sqs.get_queue_attributes(
                QueueUrl=dlq_url,
                AttributeNames=['QueueArn']
            )
            dlq_arn = dlq_attrs['Attributes']['QueueArn']
            
            # Create main queue with DLQ configuration
            queue_response = self.sqs.create_queue(
                QueueName=queue_name,
                Attributes={
                    'VisibilityTimeout': '300',  # 5 minutes
                    'MessageRetentionPeriod': '1209600',  # 14 days
                    'ReceiveMessageWaitTimeSeconds': '20',  # Long polling
                    'RedrivePolicy': json.dumps({
                        'deadLetterTargetArn': dlq_arn,
                        'maxReceiveCount': 3
                    })
                }
            )
            
            queue_url = queue_response['QueueUrl']
            
            print(f"✅ Point-to-Point queue created: {queue_url}")
            print(f"✅ Dead letter queue created: {dlq_url}")
            
            return {
                'queue_url': queue_url,
                'dlq_url': dlq_url,
                'pattern': 'point-to-point'
            }
            
        except ClientError as e:
            print(f"❌ Error setting up Point-to-Point pattern: {e}")
            return None
    
    def setup_publish_subscribe_pattern(self, topic_name, subscriptions):
        """Set up Publish-Subscribe pattern using SNS"""
        print(f"📢 Setting up Publish-Subscribe pattern: {topic_name}")
        
        try:
            # Create SNS topic
            topic_response = self.sns.create_topic(
                Name=topic_name,
                Attributes={
                    'DisplayName': f'{topic_name} Topic',
                    'DeliveryPolicy': json.dumps({
                        'http': {
                            'defaultHealthyRetryPolicy': {
                                'minDelayTarget': 20,
                                'maxDelayTarget': 300,
                                'numRetries': 3
                            }
                        }
                    })
                }
            )
            
            topic_arn = topic_response['TopicArn']
            
            # Create subscriptions
            created_subscriptions = []
            for sub_config in subscriptions:
                try:
                    sub_response = self.sns.subscribe(
                        TopicArn=topic_arn,
                        Protocol=sub_config['protocol'],
                        Endpoint=sub_config['endpoint']
                    )
                    
                    subscription_arn = sub_response['SubscriptionArn']
                    
                    # Apply filter policy if provided
                    if 'filter_policy' in sub_config:
                        self.sns.set_subscription_attributes(
                            SubscriptionArn=subscription_arn,
                            AttributeName='FilterPolicy',  
                            AttributeValue=json.dumps(sub_config['filter_policy'])
                        )
                    
                    created_subscriptions.append({
                        'protocol': sub_config['protocol'],
                        'endpoint': sub_config['endpoint'],
                        'subscription_arn': subscription_arn
                    })
                    
                    print(f"✅ Subscription created: {sub_config['protocol']} -> {sub_config['endpoint']}")
                    
                except ClientError as e:
                    print(f"❌ Error creating subscription: {e}")
            
            print(f"✅ Publish-Subscribe topic created: {topic_arn}")
            print(f"✅ Total subscriptions: {len(created_subscriptions)}")
            
            return {
                'topic_arn': topic_arn,
                'subscriptions': created_subscriptions,
                'pattern': 'publish-subscribe'
            }
            
        except ClientError as e:
            print(f"❌ Error setting up Publish-Subscribe pattern: {e}")
            return None
    
    def demonstrate_point_to_point(self, queue_url, num_messages=5, num_workers=3):
        """Demonstrate Point-to-Point pattern with multiple competing consumers"""
        print(f"\\n🎯 Demonstrating Point-to-Point Pattern")
        print(f"Queue: {queue_url}")
        print(f"Messages: {num_messages}, Workers: {num_workers}")
        
        # Send messages to queue
        print(f"\\n📤 Sending {num_messages} messages to queue...")
        for i in range(num_messages):
            task_data = {
                'task_id': f'TASK-{i+1:03d}',
                'description': f'Process order #{i+1}',
                'priority': 'high' if i % 3 == 0 else 'normal',
                'timestamp': time.time()
            }
            
            try:
                self.sqs.send_message(
                    QueueUrl=queue_url,
                    MessageBody=json.dumps(task_data),
                    MessageAttributes={
                        'priority': {
                            'StringValue': task_data['priority'],
                            'DataType': 'String'
                        }
                    }
                )
                print(f"  ✅ Sent: {task_data['task_id']}")
                
            except ClientError as e:
                print(f"  ❌ Error sending message: {e}")
        
        print(f"\\n👷 Starting {num_workers} competing workers...")
        
        # Start multiple workers that compete for messages
        def worker(worker_id):
            print(f"Worker {worker_id} started")
            processed_count = 0
            
            while processed_count < num_messages // num_workers + 2:  # Allow some overlap
                try:
                    # Receive message with long polling
                    response = self.sqs.receive_message(
                        QueueUrl=queue_url,
                        MaxNumberOfMessages=1,
                        WaitTimeSeconds=5,  # Short wait for demo
                        MessageAttributeNames=['All']
                    )
                    
                    messages = response.get('Messages', [])
                    
                    if not messages:
                        print(f"Worker {worker_id}: No more messages")
                        break
                    
                    message = messages[0]
                    receipt_handle = message['ReceiptHandle']
                    
                    # Parse message
                    task_data = json.loads(message['Body'])
                    task_id = task_data['task_id']
                    
                    print(f"Worker {worker_id}: Processing {task_id}")
                    
                    # Simulate processing time
                    time.sleep(1)
                    
                    # Delete message after successful processing
                    self.sqs.delete_message(
                        QueueUrl=queue_url,
                        ReceiptHandle=receipt_handle
                    )
                    
                    print(f"Worker {worker_id}: Completed {task_id}")
                    processed_count += 1
                    
                except ClientError as e:
                    print(f"Worker {worker_id} error: {e}")
                except Exception as e:
                    print(f"Worker {worker_id} unexpected error: {e}")
            
            print(f"Worker {worker_id} finished processing {processed_count} messages")
        
        # Run workers concurrently
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(worker, i+1) for i in range(num_workers)]
            for future in futures:
                future.result()
        
        print("\\n✅ Point-to-Point demonstration completed")
    
    def demonstrate_publish_subscribe(self, topic_arn, num_events=3):
        """Demonstrate Publish-Subscribe pattern with fanout"""
        print(f"\\n📢 Demonstrating Publish-Subscribe Pattern")
        print(f"Topic: {topic_arn}")
        print(f"Events: {num_events}")
        
        # Publish events that will be delivered to all subscribers
        sample_events = [
            {
                'event_type': 'user_registered',
                'user_id': 'USR-001',
                'email': 'user1@example.com',
                'timestamp': time.time()
            },
            {
                'event_type': 'order_placed',
                'order_id': 'ORD-001',
                'customer_id': 'USR-001',
                'amount': 99.99,
                'timestamp': time.time()
            },
            {
                'event_type': 'payment_processed',
                'payment_id': 'PAY-001',
                'order_id': 'ORD-001',
                'amount': 99.99,
                'status': 'completed',
                'timestamp': time.time()
            }
        ]
        
        print(f"\\n📡 Publishing {len(sample_events)} events...")
        
        for event in sample_events[:num_events]:
            try:
                response = self.sns.publish(
                    TopicArn=topic_arn,
                    Message=json.dumps(event),
                    Subject=f"Event: {event['event_type']}",
                    MessageAttributes={
                        'event_type': {
                            'StringValue': event['event_type'],
                            'DataType': 'String'
                        },
                        'timestamp': {
                            'StringValue': str(event['timestamp']),
                            'DataType': 'Number'
                        }
                    }
                )
                
                print(f"  ✅ Published: {event['event_type']} (Message ID: {response['MessageId']})")
                print(f"     📡 Delivered to ALL subscribers simultaneously")
                
            except ClientError as e:
                print(f"  ❌ Error publishing event: {e}")
        
        print("\\n✅ Publish-Subscribe demonstration completed")
        print("💡 Note: Each event was delivered to ALL subscribers")
    
    def compare_patterns_performance(self):
        """Compare the performance characteristics of both patterns"""
        print("\\n📊 Pattern Performance Comparison")
        print("=" * 50)
        
        comparison = {
            'Point-to-Point (SQS)': {
                'Message Delivery': 'Exclusive (one consumer per message)',
                'Throughput': 'Up to 120,000 messages/second',
                'Latency': 'Poll-based (1-20 seconds)',
                'Persistence': 'Up to 14 days',
                'Cost': '$0.40 per million messages',
                'Best For': 'Task queues, work distribution'
            },
            'Publish-Subscribe (SNS)': {
                'Message Delivery': 'Fanout (all subscribers get message)',
                'Throughput': 'Up to 300,000 publishes/second',
                'Latency': 'Push-based (near real-time)',
                'Persistence': 'No persistence (delivery only)',
                'Cost': '$0.50 per million messages',
                'Best For': 'Event notifications, broadcasting'
            }
        }
        
        for pattern, characteristics in comparison.items():
            print(f"\\n{pattern}:")
            for metric, value in characteristics.items():
                print(f"  {metric}: {value}")

# Comprehensive demonstration
def run_comprehensive_demo():
    """Run comprehensive demonstration of both message patterns"""
    demo = MessageChannelDemo()
    
    print("🚀 Starting Comprehensive Message Channel Demonstration")
    print("=" * 60)
    
    # Set up Point-to-Point pattern
    print("\\n1️⃣ Setting up Point-to-Point Pattern...")
    ptp_setup = demo.setup_point_to_point_pattern('order-processing-queue')
    
    if ptp_setup:
        # Demonstrate Point-to-Point
        demo.demonstrate_point_to_point(
            ptp_setup['queue_url'], 
            num_messages=6, 
            num_workers=3
        )
    
    # Set up Publish-Subscribe pattern
    print("\\n\\n2️⃣ Setting up Publish-Subscribe Pattern...")
    
    # Define subscriptions for demonstration
    subscriptions = [
        {
            'protocol': 'email',
            'endpoint': 'demo@example.com'
        },
        # Note: In real implementation, you'd add actual SQS queues, Lambda functions, etc.
    ]
    
    pubsub_setup = demo.setup_publish_subscribe_pattern(
        'ecommerce-events',
        subscriptions
    )
    
    if pubsub_setup:
        # Demonstrate Publish-Subscribe
        demo.demonstrate_publish_subscribe(
            pubsub_setup['topic_arn'], 
            num_events=3
        )
    
    # Compare patterns
    demo.compare_patterns_performance()
    
    print("\\n🎉 Comprehensive demonstration completed!")
    print("\\nKey Takeaways:")
    print("• Point-to-Point: Use for work distribution and exclusive processing")
    print("• Publish-Subscribe: Use for event broadcasting and fanout scenarios")
    print("• Hybrid: Combine both patterns for complex architectures")

# Main execution
if __name__ == "__main__":
    run_comprehensive_demo()
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
    # 📨 AWS Messaging Services
    
    """)
    st.markdown("""<div class="info-box">
                Learn AWS messaging services for building decoupled, scalable applications. Master SQS queues for reliable message processing, SNS topics for event-driven architectures, and understand when to use point-to-point vs publish-subscribe patterns in real-world scenarios.
                </div>""", unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔄 Amazon SQS", 
        "📢 Amazon SNS", 
        "🌟 SNS Fanout Scenario",
        "📨 Message Channels"
    ])
    
    with tab1:
        sqs_tab()
    
    with tab2:
        sns_tab()
    
    with tab3:
        sns_fanout_tab()
    
    with tab4:
        message_channels_tab()
    
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
