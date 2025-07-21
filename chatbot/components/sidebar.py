import streamlit as st
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

def render_sidebar(chat_manager, redis_session_manager, session_info: Dict[str, Any]):
    """Render the sidebar with session information and controls"""
    
    with st.sidebar:
        st.title("🤖 Bedrock Chat Settings")
        
        # Model Information
        st.subheader("🧠 Model Information")
        if chat_manager:
            model_info = chat_manager.get_model_info()
            st.info(f"**Model:** {model_info.get('model_name', 'Claude 3.5 Sonnet')}")
            st.info(f"**Provider:** {model_info.get('provider', 'Anthropic')}")
            st.info(f"**Region:** {model_info.get('region', 'us-east-1')}")
            
            # Model selection
            if st.button("🔄 Switch Model", use_container_width=True):
                show_model_selector(chat_manager)
        
        # Session Information
        st.subheader("📊 Session Info")
        if session_info:
            st.info(f"**Session ID:** {session_info.get('session_id', 'N/A')[:8]}...")
            st.info(f"**Messages in Redis:** {session_info.get('message_count', 0)}")
            
            ttl = session_info.get('ttl_seconds', 0)
            if ttl > 0:
                st.info(f"**Session expires in:** {ttl//60}m {ttl%60}s")
            else:
                st.warning("Session expired or no TTL set")
        
        # Connection Status
        st.subheader("🔌 Connection Status")
        bedrock_status = check_bedrock_connection(chat_manager)
        redis_status = st.session_state.get("redis_connected", False)
        
        if bedrock_status:
            st.success("✅ Bedrock Connected")
        else:
            st.error("❌ Bedrock Disconnected")
            
        if redis_status:
            st.success("✅ Redis Connected")
        else:
            st.error("❌ Redis Disconnected")
        
        # Chat Statistics
        if chat_manager:
            st.subheader("💬 Chat Statistics")
            summary = chat_manager.get_conversation_summary()
            if summary:
                st.metric("Total Messages", summary.get("total_messages", 0))
                st.metric("Your Messages", summary.get("human_messages", 0))
                st.metric("AI Responses", summary.get("ai_messages", 0))
        
        # Model Parameters
        st.subheader("⚙️ Model Parameters")
        render_model_parameters(chat_manager)
        
        # Action Buttons
        st.subheader("🔧 Actions")
        render_action_buttons(chat_manager, redis_session_manager)
        
        # Export Chat
        if st.session_state.get("chat_history"):
            st.subheader("📥 Export Chat")
            render_export_options()
        
        # Advanced Settings
        render_advanced_settings(chat_manager)
        
        # Footer
        st.markdown("---")
        st.caption("Powered by Claude 3.5 via Bedrock, Redis & Streamlit")

def show_model_selector(chat_manager):
    """Show model selection interface"""
    try:
        available_models = chat_manager.list_available_models()
        if available_models:
            with st.expander("🎯 Select Model", expanded=True):
                model_options = {
                    f"{model['model_name']} ({model['model_id']})": model['model_id']
                    for model in available_models
                }
                
                selected_model = st.selectbox(
                    "Choose a model:",
                    options=list(model_options.keys()),
                    key="model_selector"
                )
                
                if st.button("Apply Model", key="apply_model"):
                    new_model_id = model_options[selected_model]
                    st.session_state.selected_model_id = new_model_id
                    st.success(f"Model updated to: {selected_model}")
                    st.rerun()
        else:
            st.warning("Unable to fetch available models")
    except Exception as e:
        st.error(f"Error loading models: {e}")

def check_bedrock_connection(chat_manager) -> bool:
    """Check Bedrock connection status"""
    try:
        if chat_manager and hasattr(chat_manager, 'bedrock_client'):
            chat_manager.bedrock_client.list_foundation_models(maxResults=1)
            return True
        return False
    except Exception:
        return False

def render_model_parameters(chat_manager):
    """Render model parameter controls"""
    col1, col2 = st.columns(2)
    
    with col1:
        temperature = st.slider(
            "Temperature", 
            0.0, 1.0, 
            st.session_state.get("temperature", 0.7), 
            0.1, 
            key="temperature_slider",
            help="Controls randomness in responses"
        )
        
        max_tokens = st.slider(
            "Max Tokens", 
            1000, 8000, 
            st.session_state.get("max_tokens", 4000), 
            500, 
            key="max_tokens_slider",
            help="Maximum response length"
        )
    
    with col2:
        top_p = st.slider(
            "Top P", 
            0.1, 1.0, 
            st.session_state.get("top_p", 0.9), 
            0.1, 
            key="top_p_slider",
            help="Controls diversity of responses"
        )
        
        streaming = st.checkbox(
            "Enable Streaming", 
            value=st.session_state.get("enable_streaming", True),
            key="streaming_checkbox",
            help="Stream responses in real-time"
        )
    
    # Update parameters button
    if st.button("🔄 Update Parameters", use_container_width=True):
        if chat_manager:
            try:
                chat_manager.update_model_parameters(
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=top_p
                )
                st.success("Parameters updated!")
            except Exception as e:
                st.error(f"Error updating parameters: {e}")

def render_action_buttons(chat_manager, redis_session_manager):
    """Render action buttons"""
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            if chat_manager:
                chat_manager.clear_conversation()
            st.session_state.chat_history = []
            st.success("Chat cleared!")
            st.rerun()
    
    with col2:
        if st.button("🔄 New Session", use_container_width=True):
            # Create new session
            if redis_session_manager:
                new_session_id = redis_session_manager.create_session()
                st.session_state.session_id = new_session_id
                st.session_state.chat_history = []
                st.session_state.chat_manager = None
                st.success("New session created!")
                st.rerun()

def render_export_options():
    """Render chat export options"""
    export_format = st.selectbox(
        "Export Format:",
        ["Text", "JSON", "Markdown"],
        key="export_format"
    )
    
    if export_format == "Text":
        chat_text = "\n\n".join([
            f"{msg['role'].title()}: {msg['content']}"
            for msg in st.session_state.chat_history
        ])
        file_extension = "txt"
        mime_type = "text/plain"
    elif export_format == "JSON":
        import json
        chat_text = json.dumps(st.session_state.chat_history, indent=2)
        file_extension = "json"
        mime_type = "application/json"
    else:  # Markdown
        chat_text = "\n\n".join([
            f"**{msg['role'].title()}:** {msg['content']}"
            for msg in st.session_state.chat_history
        ])
        file_extension = "md"
        mime_type = "text/markdown"
    
    st.download_button(
        label=f"💾 Download as {export_format}",
        data=chat_text,
        file_name=f"chat_history.{file_extension}",
        mime=mime_type,
        use_container_width=True
    )

def render_advanced_settings(chat_manager):
    """Render advanced settings"""
    with st.expander("🔧 Advanced Settings"):
        # AWS Region
        aws_region = st.selectbox(
            "AWS Region:",
            ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
            index=0,
            key="aws_region_selector"
        )
        
        # Debug mode
        debug_mode = st.checkbox(
            "Debug Mode", 
            value=False,
            key="debug_mode",
            help="Show detailed logging information"
        )
        
        if debug_mode and chat_manager:
            st.json(chat_manager.get_conversation_summary())
        
        # Connection Test
        if st.button("🔍 Test Connections", use_container_width=True):
            test_connections(chat_manager)

def test_connections(chat_manager):
    """Test all connections"""
    with st.spinner("Testing connections..."):
        # Test Bedrock
        try:
            if chat_manager and hasattr(chat_manager, 'bedrock_client'):
                chat_manager.bedrock_client.list_foundation_models(maxResults=1)
                st.success("✅ Bedrock connection successful")
            else:
                st.error("❌ Bedrock client not initialized")
        except Exception as e:
            st.error(f"❌ Bedrock connection failed: {e}")
        
        # Test Redis
        try:
            if st.session_state.get("redis_client"):
                st.session_state.redis_client.ping()
                st.success("✅ Redis connection successful")
            else:
                st.error("❌ Redis client not initialized")
        except Exception as e:
            st.error(f"❌ Redis connection failed: {e}")