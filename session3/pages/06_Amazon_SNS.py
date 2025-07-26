"""Main Streamlit application for SNS-SQS Publisher-Subscriber demo."""

import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import streamlit as st
import pandas as pd
import utils.common as common
import utils.authenticate as authenticate
import logging
from utils.sns.config import AWSConfig, AppConfig, SAMPLE_MESSAGES, CUSTOM_CSS
from utils.sns.aws_services import AWSResourceManager, AWSServiceError


# Configure logging for debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure Streamlit page
def configure_page():
    """Configure Streamlit page settings."""
    config = AppConfig()
    st.set_page_config(
        page_title=config.page_title,
        page_icon=config.page_icon,
        layout=config.layout,
        initial_sidebar_state=config.initial_sidebar_state
    )

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    
    common.initialize_session_state()
    
    defaults = {
        'messages_sent': 0,
        'messages_received': {'subscriber_1': 0, 'subscriber_2': 0, 'subscriber_3': 0},
        'received_messages': {'subscriber_1': [], 'subscriber_2': [], 'subscriber_3': []},
        'last_refresh': datetime.now(),
        'aws_health': {},
        'auto_refresh': False,
        'debug_logs': []  # Add this for debugging
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def render_header():
    """Render application header."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown("""
        <div class="main-header">
            <h1>📨 SNS-SQS Publisher-Subscriber Demo</h1>
            <p>Real-time message distribution using Amazon SNS and SQS</p>
        </div>
    """, unsafe_allow_html=True)

def render_sidebar(aws_manager: AWSResourceManager):
    """Render sidebar with controls and status."""
    with st.sidebar:
        
        common.render_sidebar()
        
        st.header("🔧 Controls")
        
        # Setup subscriptions button
        if st.button("🔗 Setup Subscriptions", use_container_width=True):
            with st.spinner("Setting up subscriptions..."):
                results = aws_manager.setup_subscriptions()
                
                success_count = sum(1 for success in results.values() if success)
                total_count = len(results)
                
                if success_count == total_count:
                    st.success(f"✅ All {total_count} subscriptions setup successfully!")
                else:
                    st.warning(f"⚠️ {success_count}/{total_count} subscriptions setup successfully")
                
                # Show detailed results
                for name, success in results.items():
                    status = "✅" if success else "❌"
                    st.write(f"{status} {name}")
        
        # Health check
        if st.button("🔍 Health Check", use_container_width=True):
            with st.spinner("Checking AWS resources..."):
                st.session_state.aws_health = aws_manager.health_check()
        
        # Display health status
        if st.session_state.aws_health:
            st.subheader("📊 Resource Status")
            for resource, status in st.session_state.aws_health.items():
                icon = "✅" if status else "❌"
                st.write(f"{icon} {resource.replace('_', ' ').title()}")
        
        # Subscription status
        if st.button("📋 Check Subscriptions", use_container_width=True):
            with st.spinner("Checking subscriptions..."):
                subscription_status = aws_manager.get_subscription_status()
                st.session_state.subscription_status = subscription_status
        
        if hasattr(st.session_state, 'subscription_status'):
            st.subheader("🔗 Subscriptions")
            status = st.session_state.subscription_status
            st.write(f"Total: {status['total_subscriptions']}")
            
            for sub in status['subscriptions']:
                if sub['protocol'] == 'sqs':
                    queue_name = sub['endpoint'].split('/')[-1]
                    st.write(f"📥 {queue_name}")
        
        # Auto-refresh toggle
        st.subheader("⚙️ Settings")
        st.session_state.auto_refresh = st.toggle("Auto-refresh subscribers", value=st.session_state.auto_refresh)
        
        # Statistics
        st.subheader("📈 Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Messages Sent", st.session_state.messages_sent)
        with col2:
            total_received = sum(st.session_state.messages_received.values())
            st.metric("Total Received", total_received)

def render_publisher_tab(aws_manager: AWSResourceManager):
    """Render publisher tab interface."""
    st.header("📤 Message Publisher")
    
    # Add subscription status check
    col_status, col_refresh = st.columns([3, 1])
    with col_status:
        st.info("💡 Tip: Check subscriptions in the sidebar before publishing messages")
    with col_refresh:
        if st.button("🔄 Refresh Subscriptions", use_container_width=True):
            st.session_state.subscription_check = aws_manager.sns_publisher.get_subscriptions()
    
    # Display subscription status
    if hasattr(st.session_state, 'subscription_check'):
        subscriptions = st.session_state.subscription_check
        active_sqs_subs = [sub for sub in subscriptions if sub['Protocol'] == 'sqs']
        
        if active_sqs_subs:
            st.success(f"✅ {len(active_sqs_subs)} SQS subscriptions active")
        else:
            st.error("❌ No active SQS subscriptions found!")
            if st.button("🔧 Setup Subscriptions Now"):
                with st.spinner("Setting up subscriptions..."):
                    results = aws_manager.setup_subscriptions()
                    st.rerun()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Create Message")
        
        # Message type selection
        message_types = ["Custom", "Sample Template"]
        message_type = st.selectbox("Message Type", message_types)
        
        if message_type == "Sample Template":
            template_options = [msg['title'] for msg in SAMPLE_MESSAGES]
            selected_template = st.selectbox("Select Template", template_options)
            
            selected_msg = next(msg for msg in SAMPLE_MESSAGES if msg['title'] == selected_template)
            st.json(selected_msg)
            
            if st.button("📤 Publish Sample Message", type="primary", use_container_width=True):
                try:
                    with st.spinner("Publishing message..."):
                        result = aws_manager.sns_publisher.publish_message(selected_msg)
                        st.session_state.messages_sent += 1
                        st.session_state.last_published_message = result
                        
                        st.success(f"✅ Message published successfully!")
                        st.json(result)
                        
                except AWSServiceError as e:
                    st.error(f"❌ Failed to publish message: {e}")
        
        else:
            # Custom message form (keep existing code)
            with st.form("custom_message_form"):
                title = st.text_input("Title", placeholder="Enter message title")
                message = st.text_area("Message", placeholder="Enter your message content")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    priority = st.selectbox("Priority", ["low", "medium", "high"])
                with col_b:
                    category = st.selectbox("Category", ["system", "user", "error", "marketing", "security"])
                
                message_type_custom = st.selectbox("Type", ["notification", "alert", "info", "warning"])
                
                submitted = st.form_submit_button("📤 Publish Custom Message", type="primary", use_container_width=True)
                
                if submitted and title and message:
                    custom_msg = {
                        "type": message_type_custom,
                        "title": title,
                        "message": message,
                        "priority": priority,
                        "category": category
                    }
                    
                    try:
                        with st.spinner("Publishing message..."):
                            result = aws_manager.sns_publisher.publish_message(custom_msg)
                            st.session_state.messages_sent += 1
                            st.session_state.last_published_message = result
                            
                            st.success(f"✅ Message published successfully!")
                            st.json(result)
                            
                    except AWSServiceError as e:
                        st.error(f"❌ Failed to publish message: {e}")
                elif submitted:
                    st.warning("⚠️ Please fill in both title and message fields")
    
    with col2:
        st.subheader("Quick Actions")
        
        if st.button("🚀 Send 1 Test Message", use_container_width=True):
            try:
                test_msg = {
                    "type": "test",
                    "title": f"Test Message {datetime.now().strftime('%H:%M:%S')}",
                    "message": "This is a test message to verify SNS-SQS delivery",
                    "priority": "medium",
                    "category": "system"
                }
                
                result = aws_manager.sns_publisher.publish_message(test_msg)
                st.session_state.messages_sent += 1
                st.session_state.last_published_message = result
                
                st.success("✅ Test message sent!")
                st.json(result)
                
            except AWSServiceError as e:
                st.error(f"❌ Failed to send test message: {e}")
        
        # Display last published message details
        if hasattr(st.session_state, 'last_published_message'):
            st.subheader("📄 Last Published")
            result = st.session_state.last_published_message
            st.write(f"**Message ID:** {result['message_id']}")
            st.write(f"**Published At:** {result['published_at']}")
            st.write(f"**Topic:** {result['topic_arn'].split(':')[-1]}")

def render_subscriber_tab(subscriber_name: str, aws_manager: AWSResourceManager):
    """Render subscriber tab interface."""
    subscriber_key = f"subscriber_{subscriber_name}"
    
    st.header(f"📥 Subscriber {subscriber_name.upper()}")
    
    # Test connection first
    if subscriber_key in aws_manager.sqs_consumers:
        consumer = aws_manager.sqs_consumers[subscriber_key]
        connection_status = consumer.test_connection()
        
        if connection_status:
            st.success(f"✅ Connected to queue: {consumer.queue_url.split('/')[-1]}")
        else:
            st.error(f"❌ Cannot connect to queue: {consumer.queue_url}")
            return
    else:
        st.error(f"❌ Queue not configured for {subscriber_key}")
        return
    
    # Get and display queue attributes
    try:
        queue_attrs = consumer.get_queue_attributes()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            msgs_available = queue_attrs.get('ApproximateNumberOfMessages', '0')
            st.metric("Available", msgs_available)
        with col2:
            msgs_in_flight = queue_attrs.get('ApproximateNumberOfMessagesNotVisible', '0')
            st.metric("In Flight", msgs_in_flight)
        with col3:
            msgs_delayed = queue_attrs.get('ApproximateNumberOfMessagesDelayed', '0')
            st.metric("Delayed", msgs_delayed)
        with col4:
            local_msgs = len(st.session_state.received_messages[subscriber_key])
            st.metric("Local Cache", local_msgs)
    except Exception as e:
        st.error(f"Error getting queue stats: {e}")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.subheader("🎛️ Controls")
        
        # Consume messages button with immediate feedback
        if st.button(f"📥 Consume Messages", key=f"consume_{subscriber_name}", use_container_width=True, type="primary"):
            # Create placeholder for real-time updates
            status_placeholder = st.empty()
            result_placeholder = st.empty()
            
            try:
                status_placeholder.info("🔄 Connecting to SQS queue...")
                
                # Test connection
                if not consumer.test_connection():
                    status_placeholder.error("❌ Failed to connect to queue")
                    return
                
                status_placeholder.info("🔄 Fetching messages from queue...")
                
                # Receive messages
                messages = consumer.receive_messages(max_messages=10, wait_time=0)
                
                status_placeholder.info(f"🔄 Processing {len(messages)} messages...")
                
                if messages:
                    # Add to session state
                    st.session_state.received_messages[subscriber_key].extend(messages)
                    st.session_state.messages_received[subscriber_key] += len(messages)
                    
                    # Delete messages from queue (acknowledge)
                    deleted_count = 0
                    for msg in messages:
                        if consumer.delete_message(msg['receipt_handle']):
                            deleted_count += 1
                    
                    status_placeholder.success(f"✅ Received {len(messages)} messages, deleted {deleted_count}")
                    
                    # Show message preview
                    result_placeholder.json({
                        'messages_received': len(messages),
                        'messages_deleted': deleted_count,
                        'sample_message': messages[0]['content'] if messages else None
                    })
                    
                else:
                    status_placeholder.info("📭 No messages available in queue")
                    
                    # Show queue status
                    attrs = consumer.get_queue_attributes()
                    result_placeholder.json({
                        'queue_empty': True,
                        'approximate_messages': attrs.get('ApproximateNumberOfMessages', '0'),
                        'queue_url': consumer.queue_url.split('/')[-1]
                    })
                    
            except AWSServiceError as e:
                status_placeholder.error(f"❌ AWS Error: {e}")
                result_placeholder.error(f"Details: {str(e)}")
            except Exception as e:
                status_placeholder.error(f"❌ Unexpected error: {e}")
                result_placeholder.error(f"Details: {str(e)}")
        
        # Manual refresh queue stats
        if st.button(f"🔄 Refresh Stats", key=f"refresh_{subscriber_name}", use_container_width=True):
            try:
                attrs = consumer.get_queue_attributes()
                st.json({
                    'ApproximateNumberOfMessages': attrs.get('ApproximateNumberOfMessages', '0'),
                    'ApproximateNumberOfMessagesNotVisible': attrs.get('ApproximateNumberOfMessagesNotVisible', '0'),
                    'QueueArn': attrs.get('QueueArn', 'Unknown'),
                    'LastModifiedTimestamp': attrs.get('LastModifiedTimestamp', 'Unknown')
                })
            except Exception as e:
                st.error(f"Error refreshing stats: {e}")
        
        # Test message sending (for debugging)
        if st.button(f"🧪 Test Direct SQS Send", key=f"test_{subscriber_name}", use_container_width=True):
            try:
                # Send a test message directly to SQS (bypassing SNS)
                import boto3
                sqs_client = boto3.client('sqs', region_name=consumer.region)
                
                test_message = {
                    "type": "test",
                    "title": f"Direct SQS Test - {datetime.now().strftime('%H:%M:%S')}",
                    "message": "This is a direct SQS test message",
                    "priority": "low",
                    "category": "test"
                }
                
                response = sqs_client.send_message(
                    QueueUrl=consumer.queue_url,
                    MessageBody=json.dumps(test_message)
                )
                
                st.success(f"✅ Test message sent: {response['MessageId']}")
                
            except Exception as e:
                st.error(f"❌ Failed to send test message: {e}")
        
        # Clear messages
        if st.button(f"🗑️ Clear Local Cache", key=f"clear_{subscriber_name}", use_container_width=True):
            count = len(st.session_state.received_messages[subscriber_key])
            st.session_state.received_messages[subscriber_key] = []
            st.success(f"✅ Cleared {count} messages from local cache")
    
    with col1:
        st.subheader("📨 Received Messages")
        
        messages = st.session_state.received_messages[subscriber_key]
        
        if messages:
            # Show total count
            st.info(f"📊 Total messages in cache: {len(messages)}")
            
            # Sort messages by received time (newest first)
            sorted_messages = sorted(messages, key=lambda x: x['received_at'], reverse=True)
            
            # Display messages
            for i, msg in enumerate(sorted_messages[:10]):  # Show latest 10
                content = msg['content']
                
                # Message header with source info
                col_header1, col_header2 = st.columns([2, 1])
                with col_header1:
                    st.markdown(f"**Message {i+1}** - Source: `{msg.get('source', 'Unknown')}`")
                with col_header2:
                    st.markdown(f"*{msg['received_at'][:19]}*")
                
                # Display message content
                if isinstance(content, dict) and 'error' not in content:
                    priority = content.get('priority', 'medium')
                    
                    st.markdown(f"""
                        <div class="message-card priority-{priority}">
                            <h4>{content.get('title', 'No Title')}</h4>
                            <p><strong>Type:</strong> {content.get('type', 'N/A')} | 
                               <strong>Priority:</strong> {priority} | 
                               <strong>Category:</strong> {content.get('category', 'N/A')}</p>
                            <p>{content.get('message', 'No message content')}</p>
                            <small>
                                <strong>Message ID:</strong> {msg['message_id'][:12]}...
                            </small>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"❌ Error in message: {content}")
                
                # Expandable raw data
                with st.expander(f"🔍 Raw Message Data {i+1}", expanded=False):
                    st.json(msg)
                
                st.divider()
        else:
            st.info("📭 No messages in local cache")
            st.markdown("""
                **Next Steps:**
                1. Click '📥 Consume Messages' to fetch from queue
                2. Or send messages from the Publisher tab
                3. Check queue stats above for available messages
            """)
            
            
def render_debug_tab(aws_manager: AWSResourceManager):
    """Render debug information tab."""
    st.header("🔍 Debug Information")
    
    # Show recent logs
    st.subheader("📋 Recent Logs")
    if hasattr(st.session_state, 'debug_logs') and st.session_state.debug_logs:
        for log in st.session_state.debug_logs[-10:]:  # Show last 10 logs
            st.text(log)
    else:
        st.info("No debug logs available")
    
    # Clear logs button
    if st.button("🗑️ Clear Logs"):
        st.session_state.debug_logs = []
        st.success("Logs cleared")
    
    # Test individual components
    st.subheader("🧪 Component Tests")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**SQS Queue Tests**")
        for name, consumer in aws_manager.sqs_consumers.items():
            if st.button(f"Test {name} Connection", key=f"test_conn_{name}"):
                try:
                    attrs = consumer.get_queue_attributes()
                    st.success(f"✅ {name} connected")
                    st.json({
                        'QueueUrl': consumer.queue_url.split('/')[-1],
                        'ApproximateNumberOfMessages': attrs.get('ApproximateNumberOfMessages', '0'),
                        'Region': consumer.region
                    })
                except Exception as e:
                    st.error(f"❌ {name} failed: {e}")
    
    with col2:
        st.write("**SNS Topic Tests**")
        if st.button("Test SNS Connection"):
            try:
                attrs = aws_manager.sns_publisher.get_topic_attributes()
                st.success("✅ SNS connected")
                st.json({
                    'TopicArn': aws_manager.sns_publisher.topic_arn.split(':')[-1],
                    'SubscriptionsConfirmed': attrs.get('SubscriptionsConfirmed', '0'),
                    'SubscriptionsPending': attrs.get('SubscriptionsPending', '0')
                })
            except Exception as e:
                st.error(f"❌ SNS failed: {e}")


def render_footer():
    """Render application footer."""
    st.markdown("""
        <div class="footer">
            © 2025, Amazon Web Services, Inc. or its affiliates. All rights reserved.
        </div>
    """, unsafe_allow_html=True)

def main():
    """Main application function."""
    # Configure page
    configure_page()
    
    # Initialize session state
    initialize_session_state()
    
    # Load AWS configuration
    try:
        aws_config = AWSConfig.from_env()
        aws_manager = AWSResourceManager(aws_config)
    except Exception as e:
        st.error(f"❌ Failed to initialize AWS services: {e}")
        st.stop()
    
    # Render UI components
    render_header()
    render_sidebar(aws_manager)
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📤 Publisher", 
        "📥 Subscriber 1", 
        "📥 Subscriber 2", 
        "📥 Subscriber 3",
        "🔍 Debug"
    ])
    
    with tab1:
        render_publisher_tab(aws_manager)
    
    with tab2:
        render_subscriber_tab("1", aws_manager)
    
    with tab3:
        render_subscriber_tab("2", aws_manager)
    
    with tab4:
        render_subscriber_tab("3", aws_manager)
    
    with tab5:
        render_debug_tab(aws_manager)
    
    # Auto-refresh mechanism
    if st.session_state.auto_refresh:
        time.sleep(AppConfig.auto_refresh_interval)
        st.rerun()
    
    # Render footer
    render_footer()

if __name__ == "__main__":
    main()