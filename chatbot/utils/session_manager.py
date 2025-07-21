import streamlit as st
import uuid
import hashlib
import time
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class StreamlitSessionManager:
    """
    Manage Streamlit sessions with persistent session IDs and state management
    """
    
    @staticmethod
    def initialize_session() -> None:
        """Initialize session with required state variables"""
        
        # Initialize session ID if not present
        if "session_id" not in st.session_state:
            st.session_state.session_id = StreamlitSessionManager.generate_session_id()
            logger.info(f"Initialized new session: {st.session_state.session_id}")
        
        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Initialize connection states
        if "aws_connected" not in st.session_state:
            st.session_state.aws_connected = False
            
        if "redis_connected" not in st.session_state:
            st.session_state.redis_connected = False
        
        # Initialize model parameters
        if "temperature" not in st.session_state:
            st.session_state.temperature = 0.7
            
        if "max_tokens" not in st.session_state:
            st.session_state.max_tokens = 4000
            
        if "top_p" not in st.session_state:
            st.session_state.top_p = 0.9
            
        if "enable_streaming" not in st.session_state:
            st.session_state.enable_streaming = True
        
        # Initialize session metadata
        if "session_created_at" not in st.session_state:
            st.session_state.session_created_at = datetime.utcnow().isoformat()
            
        if "session_last_activity" not in st.session_state:
            st.session_state.session_last_activity = datetime.utcnow().isoformat()
        
        # Initialize managers (will be set later)
        if "chat_manager" not in st.session_state:
            st.session_state.chat_manager = None
            
        if "redis_session_manager" not in st.session_state:
            st.session_state.redis_session_manager = None
            
        if "redis_client" not in st.session_state:
            st.session_state.redis_client = None
            
        if "aws_session" not in st.session_state:
            st.session_state.aws_session = None
    
    @staticmethod
    def generate_session_id() -> str:
        """
        Generate a unique session ID based on various factors
        
        Returns:
            Unique session identifier
        """
        # Get Streamlit's internal session info if available
        try:
            from streamlit.runtime.scriptrunner import get_script_run_ctx
            ctx = get_script_run_ctx()
            if ctx and hasattr(ctx, 'session_id'):
                base_id = ctx.session_id
            else:
                base_id = str(uuid.uuid4())
        except:
            base_id = str(uuid.uuid4())
        
        # Add timestamp for uniqueness
        timestamp = str(int(time.time() * 1000))
        
        # Create hash for shorter ID
        combined = f"{base_id}_{timestamp}"
        session_hash = hashlib.md5(combined.encode()).hexdigest()[:16]
        
        return f"session_{session_hash}"
    
    @staticmethod
    def get_session_id() -> str:
        """
        Get current session ID
        
        Returns:
            Current session ID
        """
        if "session_id" not in st.session_state:
            StreamlitSessionManager.initialize_session()
        
        return st.session_state.session_id
    
    @staticmethod
    def update_last_activity() -> None:
        """Update session last activity timestamp"""
        st.session_state.session_last_activity = datetime.utcnow().isoformat()
    
    @staticmethod
    def get_session_info() -> Dict[str, Any]:
        """
        Get session information
        
        Returns:
            Dictionary with session information
        """
        session_info = {
            'session_id': st.session_state.get('session_id'),
            'created_at': st.session_state.get('session_created_at'),
            'last_activity': st.session_state.get('session_last_activity'),
            'aws_connected': st.session_state.get('aws_connected', False),
            'redis_connected': st.session_state.get('redis_connected', False),
            'chat_history_length': len(st.session_state.get('chat_history', [])),
            'model_parameters': {
                'temperature': st.session_state.get('temperature', 0.7),
                'max_tokens': st.session_state.get('max_tokens', 4000),
                'top_p': st.session_state.get('top_p', 0.9),
                'streaming_enabled': st.session_state.get('enable_streaming', True)
            }
        }
        
        # Add session duration
        if session_info['created_at']:
            try:
                created_time = datetime.fromisoformat(session_info['created_at'])
                duration = datetime.utcnow() - created_time
                session_info['duration_seconds'] = int(duration.total_seconds())
                session_info['duration_human'] = str(duration).split('.')[0]  # Remove microseconds
            except:
                session_info['duration_seconds'] = 0
                session_info['duration_human'] = "Unknown"
        
        return session_info
    
    @staticmethod
    def reset_session() -> str:
        """
        Reset current session and create a new one
        
        Returns:
            New session ID
        """
        # Clear all session state except for some persistent settings
        persistent_keys = {'temperature', 'max_tokens', 'top_p', 'enable_streaming'}
        persistent_values = {key: st.session_state.get(key) for key in persistent_keys if key in st.session_state}
        
        # Clear session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        # Restore persistent settings
        for key, value in persistent_values.items():
            st.session_state[key] = value
        
        # Initialize new session
        StreamlitSessionManager.initialize_session()
        
        logger.info(f"Reset session, new session ID: {st.session_state.session_id}")
        return st.session_state.session_id
    
    @staticmethod
    def clear_chat_history() -> None:
        """Clear chat history while preserving session"""
        st.session_state.chat_history = []
        StreamlitSessionManager.update_last_activity()
        logger.info("Cleared chat history")
    
    @staticmethod
    def add_chat_message(role: str, content: str) -> None:
        """
        Add a message to chat history
        
        Args:
            role: Message role ('user' or 'assistant')
            content: Message content
        """
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        st.session_state.chat_history.append(message)
        StreamlitSessionManager.update_last_activity()
    
    @staticmethod
    def get_chat_history() -> list:
        """
        Get chat history
        
        Returns:
            List of chat messages
        """
        return st.session_state.get('chat_history', [])
    
    @staticmethod
    def export_session_data() -> Dict[str, Any]:
        """
        Export session data for backup or transfer
        
        Returns:
            Dictionary with exportable session data
        """
        exportable_data = {
            'session_info': StreamlitSessionManager.get_session_info(),
            'chat_history': StreamlitSessionManager.get_chat_history(),
            'export_timestamp': datetime.utcnow().isoformat(),
            'format_version': '1.0'
        }
        
        return exportable_data
    
    @staticmethod
    def import_session_data(data: Dict[str, Any]) -> bool:
        """
        Import session data from backup
        
        Args:
            data: Session data dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate data format
            if not isinstance(data, dict) or 'chat_history' not in data:
                logger.error("Invalid session data format")
                return False
            
            # Import chat history
            if isinstance(data['chat_history'], list):
                st.session_state.chat_history = data['chat_history']
                StreamlitSessionManager.update_last_activity()
                logger.info("Successfully imported session data")
                return True
            else:
                logger.error("Invalid chat history format")
                return False
                
        except Exception as e:
            logger.error(f"Failed to import session data: {e}")
            return False
    
    @staticmethod
    def is_session_valid() -> bool:
        """
        Check if current session is valid
        
        Returns:
            True if session is valid, False otherwise
        """
        # Check if required session variables exist
        required_keys = ['session_id', 'session_created_at']
        
        for key in required_keys:
            if key not in st.session_state:
                return False
        
        # Check if session ID is properly formatted
        session_id = st.session_state.get('session_id', '')
        if not session_id.startswith('session_') or len(session_id) < 16:
            return False
        
        return True
    
    @staticmethod
    def get_session_metrics() -> Dict[str, Any]:
        """
        Get session performance metrics
        
        Returns:
            Dictionary with session metrics
        """
        chat_history = st.session_state.get('chat_history', [])
        
        # Count messages by role
        user_messages = sum(1 for msg in chat_history if msg.get('role') == 'user')
        assistant_messages = sum(1 for msg in chat_history if msg.get('role') == 'assistant')
        
        # Calculate average message length
        if chat_history:
            total_length = sum(len(msg.get('content', '')) for msg in chat_history)
            avg_message_length = total_length / len(chat_history)
        else:
            avg_message_length = 0
        
        # Session duration
        created_at = st.session_state.get('session_created_at')
        if created_at:
            try:
                created_time = datetime.fromisoformat(created_at)
                session_duration = (datetime.utcnow() - created_time).total_seconds()
            except:
                session_duration = 0
        else:
            session_duration = 0
        
        metrics = {
            'total_messages': len(chat_history),
            'user_messages': user_messages,
            'assistant_messages': assistant_messages,
            'average_message_length': round(avg_message_length, 2),
            'session_duration_seconds': round(session_duration, 2),
            'messages_per_minute': round((len(chat_history) / max(session_duration / 60, 1)), 2) if session_duration > 0 else 0,
            'connection_status': {
                'aws': st.session_state.get('aws_connected', False),
                'redis': st.session_state.get('redis_connected', False)
            }
        }
        
        return metrics


class SessionStateManager:
    """
    Advanced session state management with validation and cleanup
    """
    
    @staticmethod
    def validate_state() -> Dict[str, Any]:
        """
        Validate current session state
        
        Returns:
            Validation results
        """
        validation_results = {
            'valid': True,
            'issues': [],
            'warnings': []
        }
        
        # Check required session variables
        required_vars = ['session_id', 'chat_history']
        for var in required_vars:
            if var not in st.session_state:
                validation_results['valid'] = False
                validation_results['issues'].append(f"Missing required variable: {var}")
        
        # Check session ID format
        session_id = st.session_state.get('session_id', '')
        if session_id and not session_id.startswith('session_'):
            validation_results['warnings'].append("Session ID doesn't follow expected format")
        
        # Check chat history format
        chat_history = st.session_state.get('chat_history', [])
        if not isinstance(chat_history, list):
            validation_results['valid'] = False
            validation_results['issues'].append("Chat history is not a list")
        else:
            for i, msg in enumerate(chat_history):
                if not isinstance(msg, dict):
                    validation_results['issues'].append(f"Chat message {i} is not a dictionary")
                elif 'role' not in msg or 'content' not in msg:
                    validation_results['issues'].append(f"Chat message {i} missing required fields")
        
        # Check connection states
        connections = ['aws_connected', 'redis_connected']
        for conn in connections:
            if conn in st.session_state and not isinstance(st.session_state[conn], bool):
                validation_results['warnings'].append(f"{conn} should be boolean")
        
        return validation_results
    
    @staticmethod
    def cleanup_invalid_state() -> None:
        """Clean up invalid session state variables"""
        try:
            # Remove invalid chat messages
            chat_history = st.session_state.get('chat_history', [])
            if isinstance(chat_history, list):
                valid_messages = []
                for msg in chat_history:
                    if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                        valid_messages.append(msg)
                
                if len(valid_messages) != len(chat_history):
                    st.session_state.chat_history = valid_messages
                    logger.info(f"Cleaned up {len(chat_history) - len(valid_messages)} invalid messages")
            
            # Ensure boolean connection states
            for conn in ['aws_connected', 'redis_connected']:
                if conn in st.session_state and not isinstance(st.session_state[conn], bool):
                    st.session_state[conn] = bool(st.session_state[conn])
            
            # Ensure numeric model parameters
            numeric_params = ['temperature', 'max_tokens', 'top_p']
            for param in numeric_params:
                if param in st.session_state:
                    try:
                        st.session_state[param] = float(st.session_state[param])
                    except (ValueError, TypeError):
                        # Reset to default if invalid
                        defaults = {'temperature': 0.7, 'max_tokens': 4000, 'top_p': 0.9}
                        st.session_state[param] = defaults.get(param, 0.0)
            
        except Exception as e:
            logger.error(f"Error during session state cleanup: {e}")
    
    @staticmethod
    def get_memory_usage() -> Dict[str, Any]:
        """
        Get memory usage information for session state
        
        Returns:
            Memory usage statistics
        """
        import sys
        
        memory_info = {
            'total_variables': len(st.session_state),
            'variable_sizes': {},
            'total_size_bytes': 0
        }
        
        for key, value in st.session_state.items():
            try:
                size = sys.getsizeof(value)
                memory_info['variable_sizes'][key] = size
                memory_info['total_size_bytes'] += size
            except:
                memory_info['variable_sizes'][key] = 'unknown'
        
        # Convert to human readable
        total_bytes = memory_info['total_size_bytes']
        if total_bytes < 1024:
            memory_info['total_size_human'] = f"{total_bytes} B"
        elif total_bytes < 1024 * 1024:
            memory_info['total_size_human'] = f"{total_bytes / 1024:.1f} KB"
        else:
            memory_info['total_size_human'] = f"{total_bytes / (1024 * 1024):.1f} MB"
        
        return memory_info