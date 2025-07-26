import streamlit as st
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List
import uuid

import utils.common as common
import utils.authenticate as authenticate

from utils.sqs.config import load_aws_config, SAMPLE_MESSAGES, CUSTOM_CSS
from utils.sqs.sqs_service import SQSService

# Page configuration
st.set_page_config(
    page_title="AWS SQS Producer/Consumer",
    page_icon="📨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
def load_css():
    """Load custom CSS for modern UI/UX"""
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #FF9900, #232F3E);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #FF9900;
        margin: 1rem 0;
    }
    
    .message-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 4px;
        color: #155724;
        padding: 0.75rem;
        margin: 1rem 0;
    }
    
    .error-message {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 4px;
        color: #721c24;
        padding: 0.75rem;
        margin: 1rem 0;
    }
    
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #232F3E;
        color: white;
        text-align: center;
        padding: 10px 0;
        font-size: 12px;
    }
    
    /* Hide Streamlit default footer */
    .css-1d391kg {
        display: none;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.5rem;
        }
        .metric-container {
            margin: 0.5rem 0;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    
    common.initialize_session_state()
    
    if 'messages_sent' not in st.session_state:
        st.session_state.messages_sent = 0
    if 'messages_received' not in st.session_state:
        st.session_state.messages_received = 0
    if 'received_messages' not in st.session_state:
        st.session_state.received_messages = []
    if 'sqs_service' not in st.session_state:
        config = load_aws_config()
        st.session_state.sqs_service = SQSService(config)

def render_header():
    """Render the application header"""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown("""
    <div class="main-header">
        <h1>🚀 AWS SQS Producer/Consumer Application</h1>
        <p>Modern, responsive SQS message handling with real-time processing</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render the sidebar with configuration and metrics"""
    
    with st.sidebar:
        
        common.render_sidebar()
        
        st.markdown("### 📊 Metrics")
        
        st.markdown(f"""
        <div class="metric-container">
            <h4>📤 Messages Sent</h4>
            <h2>{st.session_state.messages_sent}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-container">
            <h4>📥 Messages Received</h4>
            <h2>{st.session_state.messages_received}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### ⚙️ Configuration")
        config = load_aws_config()
        
        st.text_input("AWS Region", value=config.region, disabled=True)
        
        if config.queue_url:
            st.text_input("Queue URL", value=config.queue_url[:50] + "...", disabled=True)
        else:
            st.warning("⚠️ Queue URL not configured")
        
        # Queue attributes
        if st.button("🔄 Refresh Queue Stats"):
            with st.spinner("Fetching queue attributes..."):
                attrs = st.session_state.sqs_service.get_queue_attributes()
                if attrs:
                    st.success("✅ Queue connected")
                    st.json({
                        "Messages Available": attrs.get('ApproximateNumberOfMessages', 'N/A'),
                        "Messages in Flight": attrs.get('ApproximateNumberOfMessagesNotVisible', 'N/A')
                    })

def render_producer_tab():
    """Render the producer tab"""
    st.markdown("## 📤 Message Producer")
    st.markdown("Send messages to your SQS queue with ease.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Quick Send Sample Messages")
        
        # Sample message selector
        sample_options = [f"{msg['type'].title()} - {msg['id']}" for msg in SAMPLE_MESSAGES]
        selected_sample = st.selectbox(
            "Choose a sample message:",
            options=range(len(SAMPLE_MESSAGES)),
            format_func=lambda i: sample_options[i]
        )
        
        # Display selected message
        if selected_sample is not None:
            st.markdown("**Preview:**")
            st.json(SAMPLE_MESSAGES[selected_sample])
            
            if st.button("🚀 Send Sample Message", type="primary"):
                with st.spinner("Sending message..."):
                    result = st.session_state.sqs_service.send_message(
                        SAMPLE_MESSAGES[selected_sample]
                    )
                    
                    if result.get('success'):
                        st.session_state.messages_sent += 1
                        st.markdown(f"""
                        <div class="success-message">
                            ✅ Message sent successfully!<br>
                            <strong>Message ID:</strong> {result['message_id']}<br>
                            <strong>MD5:</strong> {result['md5'][:16]}...
                        </div>
                        """, unsafe_allow_html=True)
                        st.balloons()
                    else:
                        st.markdown(f"""
                        <div class="error-message">
                            ❌ Failed to send message: {result.get('error', 'Unknown error')}
                        </div>
                        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Custom Message")
        
        # Custom message form
        with st.form("custom_message_form"):
            message_type = st.selectbox(
                "Message Type",
                ["order", "user_registration", "notification", "inventory_update", "custom"]
            )
            
            message_id = st.text_input(
                "Message ID",
                value=f"{message_type}_{str(uuid.uuid4())[:8]}"
            )
            
            custom_data = st.text_area(
                "Message Data (JSON)",
                value='{\n  "key": "value",\n  "timestamp": "' + datetime.now().isoformat() + '"\n}',
                height=150
            )
            
            submit_custom = st.form_submit_button("📨 Send Custom Message", type="secondary")
            
            if submit_custom:
                try:
                    parsed_data = json.loads(custom_data)
                    custom_message = {
                        "id": message_id,
                        "type": message_type,
                        "data": parsed_data
                    }
                    
                    with st.spinner("Sending custom message..."):
                        result = st.session_state.sqs_service.send_message(custom_message)
                        
                        if result.get('success'):
                            st.session_state.messages_sent += 1
                            st.success(f"✅ Custom message sent! ID: {result['message_id']}")
                        else:
                            st.error(f"❌ Failed to send: {result.get('error')}")
                            
                except json.JSONDecodeError:
                    st.error("❌ Invalid JSON format in message data")

def render_consumer_tab():
    """Render the consumer tab"""
    st.markdown("## 📥 Message Consumer")
    st.markdown("Receive and process messages from your SQS queue.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        max_messages = st.slider("Max messages to receive", 1, 10, 5)
        
        if st.button("🔄 Consume Messages", type="primary"):
            with st.spinner("Consuming messages..."):
                messages = st.session_state.sqs_service.receive_messages(max_messages)
                
                if messages:
                    st.session_state.received_messages.extend(messages)
                    st.session_state.messages_received += len(messages)
                    st.success(f"✅ Received {len(messages)} message(s)")
                else:
                    st.info("📭 No messages available in the queue")
    
    with col2:
        if st.button("🗑️ Clear Received Messages"):
            st.session_state.received_messages = []
            st.success("✅ Cleared all received messages")
        
        auto_delete = st.checkbox("🔄 Auto-delete after processing", value=True)
    
    # Display received messages
    if st.session_state.received_messages:
        st.markdown("### 📬 Received Messages")
        
        for idx, message in enumerate(reversed(st.session_state.received_messages)):
            with st.expander(f"Message {len(st.session_state.received_messages) - idx} - ID: {message['message_id'][:16]}..."):
                col_msg, col_actions = st.columns([3, 1])
                
                with col_msg:
                    st.markdown("**Message Body:**")
                    st.json(message['body'])
                    
                    st.markdown("**Metadata:**")
                    st.json({
                        "Message ID": message['message_id'],
                        "MD5": message['md5'],
                        "Attributes": message['attributes']
                    })
                
                with col_actions:
                    if st.button(f"🗑️ Delete", key=f"delete_{idx}"):
                        success = st.session_state.sqs_service.delete_message(
                            message['receipt_handle']
                        )
                        if success:
                            st.session_state.received_messages.remove(message)
                            st.success("✅ Message deleted")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete")
    else:
        st.info("👈 Click 'Consume Messages' to receive messages from the queue")

def render_footer():
    """Render the footer"""
    st.markdown("""
    <div class="footer">
        © 2025, Amazon Web Services, Inc. or its affiliates. All rights reserved.
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application function"""
    # Load CSS and initialize
    initialize_session_state()
    
    # Render components
    render_header()
    render_sidebar()
    
    # Main content with tabs
    tab1, tab2 = st.tabs(["📤 Producer", "📥 Consumer"])
    
    with tab1:
        render_producer_tab()
    
    with tab2:
        render_consumer_tab()
    
    # Render footer
    render_footer()
    
    # Add some spacing at the bottom for the fixed footer
    st.markdown("<br><br><br>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()