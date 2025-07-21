import streamlit as st
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def render_chat_interface(chat_manager):
    """Render the main chat interface"""
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        if st.session_state.get("chat_history"):
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        else:
            # Welcome message
            with st.chat_message("assistant"):
                welcome_message = get_welcome_message(chat_manager)
                st.markdown(welcome_message)
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        handle_user_input(prompt, chat_manager)

def get_welcome_message(chat_manager) -> str:
    """Generate welcome message with model info"""
    try:
        if chat_manager:
            model_info = chat_manager.get_model_info()
            model_name = model_info.get('model_name', 'Claude 3.5 Sonnet')
        else:
            model_name = 'Claude 3.5 Sonnet'
        
        return f"""
👋 **Welcome to the AI Chatbot!**

I'm Claude, powered by **{model_name}** via Amazon Bedrock. This application features:

🧠 **{model_name}** - Latest Claude model from Anthropic
💾 **Amazon ElastiCache Serverless for Redis** - Persistent conversation memory  
🚀 **Streamlit** - Modern, responsive user interface
☁️ **Amazon Bedrock** - Fully managed AI service

**Key Features:**
- 💬 Persistent conversation history across sessions
- 🔄 Real-time streaming responses
- ⚙️ Adjustable model parameters
- 📊 Session management and monitoring
- 🔒 Secure AWS integration

Ask me anything to get started! I'll remember our conversation thanks to Redis memory.
        """
    except Exception as e:
        logger.error(f"Error generating welcome message: {e}")
        return "👋 Welcome! Ask me anything to get started."

def handle_user_input(user_input: str, chat_manager):
    """Handle user input and generate AI response"""
    
    if not chat_manager:
        st.error("Chat manager not initialized. Please check your AWS configuration.")
        return
    
    # Add user message to chat history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Generate and display AI response
    with st.chat_message("assistant"):
        try:
            if st.session_state.get("enable_streaming", True):
                # Streaming response
                message_placeholder = st.empty()
                ai_response = chat_manager.get_response(
                    user_input, 
                    stream_container=message_placeholder
                )
            else:
                # Non-streaming response
                with st.spinner("Claude is thinking..."):
                    ai_response = chat_manager.get_response(user_input)
                    st.markdown(ai_response)
                    
        except Exception as e:
            logger.error(f"Error in response generation: {e}")
            ai_response = handle_error_response(e)
            st.error(ai_response)
    
    # Add AI response to chat history
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": ai_response
    })
    
    # Update session activity
    update_session_activity()

def handle_error_response(error: Exception) -> str:
    """Handle different types of errors and provide appropriate responses"""
    error_str = str(error).lower()
    
    if "throttling" in error_str or "rate limit" in error_str:
        return """
🚫 **Rate Limit Exceeded**

I'm receiving too many requests right now. Please wait a moment and try again.

*Amazon Bedrock has usage limits to ensure fair access for all users.*
        """
    elif "access denied" in error_str or "unauthorized" in error_str:
        return """
🔒 **Access Denied**

There seems to be an authentication issue with AWS Bedrock. Please check:
- Your AWS credentials are properly configured
- Your IAM role has Bedrock permissions
- The model is available in your region
        """
    elif "model not found" in error_str:
        return """
🤖 **Model Not Available**

The requested Claude model isn't available. This could be because:
- The model ID is incorrect
- The model isn't available in your AWS region
- You don't have access to this specific model
        """
    elif "timeout" in error_str:
        return """
⏱️ **Request Timeout**

The request took too long to complete. This might be due to:
- Network connectivity issues
- High service load
- Complex processing requirements

Please try again with a shorter message.
        """
    else:
        return f"""
❌ **Unexpected Error**

I encountered an unexpected error: {error}

Please try again, and if the issue persists, check your configuration or contact support.
        """

def update_session_activity():
    """Update session activity timestamp"""
    try:
        from utils.session_manager import StreamlitSessionManager
        session_id = StreamlitSessionManager.get_session_id()
        
        if hasattr(st.session_state, 'redis_session_manager'):
            st.session_state.redis_session_manager.update_session_activity(session_id)
            
    except Exception as e:
        logger.warning(f"Could not update session activity: {e}")

def display_error_message(error: str):
    """Display comprehensive error message"""
    st.error(f"❌ **Error:** {error}")
    
    with st.expander("🔧 Troubleshooting Guide"):
        st.markdown("""
        **AWS Bedrock Issues:**
        - Verify your AWS credentials are configured
        - Check IAM permissions for Bedrock access
        - Ensure the model is available in your region
        - Confirm you have access to Claude models
        
        **Redis Issues:**
        - Check your ElastiCache endpoint configuration
        - Verify Redis password/authentication
        - Ensure network connectivity to ElastiCache
        - Check security group configurations
        
        **General Issues:**
        - Refresh the page to reset the session
        - Check your internet connection
        - Try switching to a different AWS region
        - Contact your AWS administrator for permission issues
        """)
        
        # Quick fixes
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Refresh Page"):
                st.rerun()
        with col2:
            if st.button("🆕 New Session"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

def render_conversation_stats():
    """Render conversation statistics"""
    if st.session_state.get("chat_history"):
        total_messages = len(st.session_state.chat_history)
        user_messages = len([msg for msg in st.session_state.chat_history if msg["role"] == "user"])
        assistant_messages = len([msg for msg in st.session_state.chat_history if msg["role"] == "assistant"])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Messages", total_messages)
        with col2:
            st.metric("Your Messages", user_messages)
        with col3:
            st.metric("AI Responses", assistant_messages)