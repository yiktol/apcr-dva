import streamlit as st
import boto3
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import time
import logging
from utils.sns.config import CUSTOM_CSS

import utils.common as common
import utils.authenticate as authenticate
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="E-commerce Order Processing Demo",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

common.initialize_session_state()

with st.sidebar:
    common.render_sidebar()

class EventBridgeOrderDemo:
    """Main class for EventBridge Order Processing Demo."""
    
    def __init__(self):
        """Initialize the demo application."""
        self.eventbridge_client = None
        self.logs_client = None
        self.initialize_aws_clients()
    
    def initialize_aws_clients(self):
        """Initialize AWS clients with error handling."""
        try:
            session = boto3.Session(region_name='ap-southeast-1')
            self.eventbridge_client = session.client('events')
            self.logs_client = session.client('logs')
        except Exception as e:
            logger.error(f"Failed to initialize AWS clients: {str(e)}")
            st.error("Failed to initialize AWS clients. Please check your AWS credentials.")
    
    def publish_order_event(self, order_data: Dict[str, Any]) -> bool:
        """
        Publish order event to EventBridge.
        
        Args:
            order_data: Dictionary containing order information
            
        Returns:
            bool: True if event published successfully, False otherwise
        """
        try:
            event_detail = {
                "orderId": order_data["order_id"],
                "customerId": order_data["customer_id"],
                "customerEmail": order_data["customer_email"],
                "amount": order_data["total_amount"],
                "items": order_data["items"],
                "timestamp": datetime.now().isoformat()
            }
            
            response = self.eventbridge_client.put_events(
                Entries=[
                    {
                        'Source': 'ecommerce.orders',
                        'DetailType': 'Order Placed',
                        'Detail': json.dumps(event_detail),
                        'EventBusName': 'ecommerce-order-bus'
                    }
                ]
            )
            
            return response['FailedEntryCount'] == 0
            
        except Exception as e:
            logger.error(f"Failed to publish event: {str(e)}")
            return False
    
    def get_lambda_logs(self, function_name: str, limit: int = 10) -> list:
        """
        Retrieve recent Lambda function logs.
        
        Args:
            function_name: Name of the Lambda function
            limit: Number of log entries to retrieve
            
        Returns:
            list: List of log entries
        """
        try:
            log_group_name = f"/aws/lambda/{function_name}"
            
            # Get log streams
            streams_response = self.logs_client.describe_log_streams(
                logGroupName=log_group_name,
                orderBy='LastEventTime',
                descending=True,
                limit=5
            )
            
            log_entries = []
            for stream in streams_response.get('logStreams', []):
                try:
                    events_response = self.logs_client.get_log_events(
                        logGroupName=log_group_name,
                        logStreamName=stream['logStreamName'],
                        limit=limit,
                        startFromHead=False
                    )
                    
                    for event in events_response.get('events', []):
                        log_entries.append({
                            'timestamp': datetime.fromtimestamp(event['timestamp'] / 1000),
                            'message': event['message']
                        })
                        
                except Exception as stream_error:
                    logger.warning(f"Failed to get logs from stream {stream['logStreamName']}: {str(stream_error)}")
                    continue
            
            # Sort by timestamp and return most recent
            log_entries.sort(key=lambda x: x['timestamp'], reverse=True)
            return log_entries[:limit]
            
        except Exception as e:
            logger.error(f"Failed to retrieve logs for {function_name}: {str(e)}")
            return []

def render_order_form(demo: EventBridgeOrderDemo):
    """Render the order form tab."""
    st.markdown("### 🛒 Place Your Order")
    
    # Information box
    st.markdown("""
    <div class="info-box">
    <strong>About This Demo:</strong><br>
    This form simulates an e-commerce order placement. When you submit an order, 
    it publishes an event to Amazon EventBridge, which then triggers multiple 
    backend services automatically.
    </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for responsive design
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Order form
        with st.form("order_form"):
            st.subheader("Order Details")
            
            # Customer information
            customer_name = st.text_input("Customer Name *", placeholder="John Doe")
            customer_email = st.text_input("Email Address *", placeholder="john.doe@example.com")
            
            # Product selection
            st.subheader("Select Products")
            available_products = {
                "Laptop": 999.99,
                "Wireless Mouse": 29.99,
                "Keyboard": 79.99,
                "Monitor": 299.99,
                "Headphones": 199.99,
                "Webcam": 89.99
            }
            
            selected_items = []
            total_amount = 0.0
            
            for product, price in available_products.items():
                if st.checkbox(f"{product} - ${price:.2f}", key=product):
                    selected_items.append({"name": product, "price": price})
                    total_amount += price
            
            # Display total
            if selected_items:
                st.success(f"**Total Amount: ${total_amount:.2f}**")
            
            # Submit button
            submitted = st.form_submit_button("🚀 Place Order", type="primary")
            
            if submitted:
                # Validation
                if not customer_name or not customer_email or not selected_items:
                    st.error("Please fill in all required fields and select at least one product.")
                elif "@" not in customer_email:
                    st.error("Please enter a valid email address.")
                else:
                    # Create order data
                    order_data = {
                        "order_id": str(uuid.uuid4())[:8].upper(),
                        "customer_id": f"CUST_{str(uuid.uuid4())[:8].upper()}",
                        "customer_name": customer_name,
                        "customer_email": customer_email,
                        "items": [item["name"] for item in selected_items],
                        "total_amount": total_amount
                    }
                    
                    # Store in session state
                    st.session_state.last_order = order_data
                    
                    # Publish event
                    if demo.publish_order_event(order_data):
                        st.markdown(f"""
                        <div class="success-box">
                        <strong>✅ Order Placed Successfully!</strong><br>
                        Order ID: <strong>{order_data['order_id']}</strong><br>
                        Total: <strong>${total_amount:.2f}</strong><br>
                        Processing your order through EventBridge...
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Trigger rerun to update other tabs
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.markdown("""
                        <div class="error-box">
                        <strong>❌ Failed to place order.</strong><br>
                        Please check your AWS configuration and try again.
                        </div>
                        """, unsafe_allow_html=True)
    
    with col2:
        # Order summary and info
        st.subheader("💡 How It Works")
        st.markdown("""
        1. **Submit Order**: Fill out the form and click submit
        2. **Event Published**: Order data sent to EventBridge
        3. **Services Triggered**: Multiple Lambda functions process the order
        4. **View Results**: Check other tabs to see processing results
        """)
        
        if hasattr(st.session_state, 'last_order'):
            st.subheader("📋 Last Order")
            order = st.session_state.last_order
            st.json({
                "Order ID": order["order_id"],
                "Customer": order["customer_name"],
                "Items": order["items"],
                "Total": f"${order['total_amount']:.2f}"
            })

def render_service_tab(demo: EventBridgeOrderDemo, service_name: str, function_name: str, 
                      icon: str, description: str, features: list):
    """Render a service processing tab."""
    st.markdown(f"### {icon} {service_name}")
    
    # Service description
    st.markdown(f"""
    <div class="info-box">
    <strong>Service Function:</strong> {description}
    </div>
    """, unsafe_allow_html=True)
    
    # Service features
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📋 Key Features")
        for feature in features:
            st.markdown(f"• {feature}")
    
    with col2:
        st.subheader("⚙️ Technical Details")
        st.markdown(f"""
        - **Function Name**: `{function_name}`
        - **Event Source**: EventBridge Rule
        - **Runtime**: Python 3.9
        - **Trigger**: Order Placed Events
        """)
    
    # Recent activity
    st.subheader("📊 Recent Activity")
    
    # Get logs
    logs = demo.get_lambda_logs(function_name)
    
    if logs:
        st.success(f"✅ Service is active - {len(logs)} recent events processed")
        
        # Display logs in expandable section
        with st.expander("View Processing Logs", expanded=False):
            for log in logs[:5]:  # Show only recent 5 logs
                st.text(f"[{log['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}] {log['message']}")
    else:
        st.info("No recent activity. Place an order to see this service in action!")
    
    # Simulated metrics (in real implementation, these would come from CloudWatch)
    st.subheader("📈 Service Metrics")
    
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        st.metric("Success Rate", "99.9%", "0.1%")
    
    with metric_col2:
        st.metric("Avg Response Time", "145ms", "-12ms")
    
    with metric_col3:
        st.metric("Events Processed", "1,247", "+23")

def main():
    """Main function to run the Streamlit application."""
    # Apply custom CSS
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # Main header
    st.markdown('''<div class="main-header">
                <h1>E-commerce Order Processing Demo</h1>
                <p>Amazon EventBridge with serverless order processing</p>
                </div>
                ''', unsafe_allow_html=True)
    
    
    # Initialize demo
    demo = EventBridgeOrderDemo()
    
    # Create tabs
    tabs = st.tabs(["🛒 Place Order", "📦 Inventory Service", "📧 Email Service", "💳 Payment Service"])
    
    with tabs[0]:
        render_order_form(demo)
    
    with tabs[1]:
        render_service_tab(
            demo=demo,
            service_name="Inventory Management Service",
            function_name="InventoryProcessorFunction",
            icon="📦",
            description="Automatically updates product inventory levels when orders are placed, ensuring stock accuracy in real-time.",
            features=[
                "Real-time inventory updates",
                "Stock level monitoring",
                "Low inventory alerts",
                "Product availability tracking",
                "Automatic reorder triggers"
            ]
        )
    
    with tabs[2]:
        render_service_tab(
            demo=demo,
            service_name="Email Notification Service",
            function_name="EmailProcessorFunction",
            icon="📧",
            description="Sends automated order confirmation emails to customers and internal notifications to staff.",
            features=[
                "Order confirmation emails",
                "Delivery notifications",
                "Status update alerts",
                "Promotional campaigns",
                "Customer communication logs"
            ]
        )
    
    with tabs[3]:
        render_service_tab(
            demo=demo,
            service_name="Payment Processing Service",
            function_name="PaymentProcessorFunction",
            icon="💳",
            description="Handles secure payment processing, transaction logging, and financial record keeping.",
            features=[
                "Secure payment processing",
                "Transaction verification",
                "Fraud detection",
                "Payment method validation",
                "Financial reporting"
            ]
        )
    
    # Sidebar with additional information
    with st.sidebar:
        st.markdown("### 🔧 Configuration")
        st.info("EventBridge Bus: ecommerce-order-bus")
        
        
        if st.button("🔄 Refresh All Data", use_container_width=True):
            st.rerun()

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
