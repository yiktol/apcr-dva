import streamlit as st
import logging
import sys
from config import settings
from utils.redis_memory import ElastiCacheRedisMessageHistory, RedisSessionManager, get_redis_password_from_secrets
from utils.bedrock_chat_manager import BedrockChatManager, BedrockModelManager
from utils.session_manager import StreamlitSessionManager
from components.sidebar import render_sidebar
from components.chat_interface import render_chat_interface, display_error_message
import redis
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title=settings.APP_TITLE,
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_aws_session():
    """Initialize AWS session with proper credentials"""
    try:
        # Create session with region from settings
        session_kwargs = {"region_name": settings.BEDROCK_REGION}
        
        # Only add explicit credentials if they're provided in settings
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            session_kwargs.update({
                "aws_access_key_id": settings.AWS_ACCESS_KEY_ID,
                "aws_secret_access_key": settings.AWS_SECRET_ACCESS_KEY
            })
            if settings.AWS_SESSION_TOKEN:
                session_kwargs["aws_session_token"] = settings.AWS_SESSION_TOKEN      
        
        # Create the AWS session
        session = boto3.Session(**session_kwargs)
        
        # Test connection by creating clients
        bedrock_runtime = session.client('bedrock-runtime', region_name=settings.BEDROCK_REGION)
        bedrock = session.client('bedrock', region_name=settings.BEDROCK_REGION)
        
        # Verify the session is working by making a simple API call
        try:
            # Test with a simple operation
            bedrock.list_foundation_models(maxResults=1)
            logger.info(f"Successfully connected to AWS Bedrock in region: {settings.BEDROCK_REGION}")
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            error_msg = e.response.get('Error', {}).get('Message', '')
            
            # If it's just a permissions issue but connection works, log and continue
            if error_code == 'AccessDeniedException':
                logger.warning(f"Limited Bedrock permissions, but connection established: {error_msg}")
            else:
                logger.error(f"Error connecting to Bedrock: {e}")
                return None
        
        return session
        
    except NoCredentialsError:
        logger.error("AWS credentials not found. Please configure AWS credentials via AWS CLI, environment variables, or IAM role.")
        return None
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        logger.error(f"AWS client error ({error_code}): {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error initializing AWS session: {e}")
        return None

def initialize_redis_connection():
    """Initialize Redis connection and return redis client"""
    try:
        # Get Redis password
        redis_password = settings.REDIS_PASSWORD
        
        if not redis_password and settings.REDIS_SECRET_NAME:
            try:
                redis_password = get_redis_password_from_secrets(
                    settings.REDIS_SECRET_NAME,
                    settings.AWS_REGION
                )
            except Exception as e:
                logger.warning(f"Could not get Redis password from Secrets Manager: {e}")
        
        # Create Redis client
        connection_kwargs = {
            'host': settings.REDIS_ENDPOINT,
            'port': settings.REDIS_PORT,
            'decode_responses': True,
            'socket_connect_timeout': 5,
            'socket_timeout': 5,
            'retry_on_timeout': True,
            'health_check_interval': 30
        }
        
        if redis_password:
            connection_kwargs['password'] = redis_password
            
        if settings.REDIS_SSL:
            connection_kwargs['ssl'] = True
            connection_kwargs['ssl_cert_reqs'] = None
        
        redis_client = redis.Redis(**connection_kwargs)
        
        # Test connection
        redis_client.ping()
        st.session_state.redis_connected = True
        logger.info("Successfully connected to Redis")
        
        return redis_client
        
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        st.session_state.redis_connected = False
        return None

def initialize_bedrock_chat_manager(session_id: str, aws_session) -> BedrockChatManager:
    """Initialize Bedrock chat manager with Redis memory"""
    try:
        # Create Redis message history
        redis_memory = ElastiCacheRedisMessageHistory(
            session_id=session_id,
            redis_endpoint=settings.REDIS_ENDPOINT,
            redis_port=settings.REDIS_PORT,
            redis_password=settings.REDIS_PASSWORD,
            use_ssl=settings.REDIS_SSL,
            ttl=settings.SESSION_TIMEOUT,
            max_messages=settings.MAX_HISTORY_LENGTH
        )
        
        # Get model ID (allow runtime switching)
        model_id = st.session_state.get("selected_model_id", settings.BEDROCK_MODEL_ID)
        
        # Create Bedrock chat manager with the AWS session
        chat_manager = BedrockChatManager(
            redis_memory_history=redis_memory,
            model_id=model_id,
            region=settings.BEDROCK_REGION,
            temperature=st.session_state.get("temperature", settings.TEMPERATURE),
            max_tokens=st.session_state.get("max_tokens", settings.MAX_TOKENS),
            top_p=st.session_state.get("top_p", settings.TOP_P),
            aws_session=aws_session
        )
        
        logger.info(f"Successfully initialized Bedrock chat manager with model: {model_id}")
        return chat_manager
        
    except Exception as e:
        logger.error(f"Failed to initialize Bedrock chat manager: {e}")
        return None

def display_connection_status():
    """Display connection status in the main area"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.session_state.get("aws_connected", False):
            st.success("🟢 AWS Bedrock Connected")
        else:
            st.error("🔴 AWS Bedrock Disconnected")
    
    with col2:
        if st.session_state.get("redis_connected", False):
            st.success("🟢 Redis Connected")
        else:
            st.error("🔴 Redis Disconnected")
    
    with col3:
        session_id = st.session_state.get("session_id", "N/A")
        st.info(f"📋 Session: {session_id[:8]}...")

def main():
    """Main application function"""
    
    # Initialize session
    StreamlitSessionManager.initialize_session()
    
    # App header
    st.title("🤖 AI Chatbot with Bedrock & Redis")
    st.markdown("*Powered by Claude 3.5 Sonnet via Amazon Bedrock, ElastiCache Serverless, and Streamlit*")

    
    # Initialize AWS session
    if "aws_session" not in st.session_state:
        with st.spinner("🔗 Connecting to AWS Bedrock..."):
            st.session_state.aws_session = initialize_aws_session()
            st.session_state.aws_connected = st.session_state.aws_session is not None
    
    aws_session = st.session_state.aws_session

    # Display connection status
    display_connection_status()
    
    if not aws_session:
        display_error_message("Failed to connect to AWS Bedrock. Please check your AWS credentials and permissions.")
        
        with st.expander("🔧 AWS Configuration Help"):
            st.markdown("""
            **Required AWS Configuration:**
            
            1. **AWS Credentials**: Configure via one of these methods:
               - AWS CLI: `aws configure`
               - Environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
               - IAM role (if running on EC2)
               - AWS credentials file
            
            2. **IAM Permissions**: Your user/role needs these permissions:
               ```json
               {
                   "Version": "2012-10-17",
                   "Statement": [
                       {
                           "Effect": "Allow",
                           "Action": [
                               "bedrock:InvokeModel",
                               "bedrock:InvokeModelWithResponseStream",
                               "bedrock:ListFoundationModels",
                               "bedrock:GetFoundationModel"
                           ],
                           "Resource": "*"
                       }
                   ]
               }
               ```
            
            3. **Model Access**: Enable Claude models in Bedrock console
            """)
        return
    
    # Initialize Redis connection
    if "redis_client" not in st.session_state:
        with st.spinner("🔗 Connecting to Redis..."):
            st.session_state.redis_client = initialize_redis_connection()
    
    redis_client = st.session_state.redis_client
    
    if not redis_client:
        display_error_message("Failed to connect to Redis. Please check your ElastiCache configuration.")
        return
    
    # Initialize session manager
    if "redis_session_manager" not in st.session_state:
        st.session_state.redis_session_manager = RedisSessionManager(redis_client)
    
    redis_session_manager = st.session_state.redis_session_manager
    
    # Initialize chat manager
    if not st.session_state.get("chat_manager") or st.session_state.get("model_changed", False):
        with st.spinner("🤖 Initializing Claude..."):
            session_id = StreamlitSessionManager.get_session_id()
            st.session_state.chat_manager = initialize_bedrock_chat_manager(session_id, aws_session)
            st.session_state.model_changed = False
    
    chat_manager = st.session_state.chat_manager
    
    if not chat_manager:
        display_error_message("Failed to initialize chat manager. Please check your configuration.")
        return
    
    # Get session info
    try:
        session_info = chat_manager.redis_memory_history.get_session_info()
    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        session_info = {}
    
    # Create layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Main chat interface
        render_chat_interface(chat_manager)
    
    with col2:
        # Sidebar
        render_sidebar(chat_manager, redis_session_manager, session_info)
    
    # Update session activity
    try:
        redis_session_manager.update_session_activity(
            StreamlitSessionManager.get_session_id()
        )
    except Exception as e:
        logger.warning(f"Could not update session activity: {e}")

# Add custom CSS for better styling
def add_custom_css():
    st.markdown("""
    <style>
    .stApp > header {
        background-color: transparent;
    }
    
    .stApp {
        margin-top: -80px;
    }
    
    .main-header {
        padding: 1rem 0;
        border-bottom: 1px solid #e0e0e0;
        margin-bottom: 2rem;
    }
    
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-connected {
        background-color: #28a745;
    }
    
    .status-disconnected {
        background-color: #dc3545;
    }
    
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }
    
    .user-message {
        background-color: #e3f2fd;
        margin-left: 2rem;
    }
    
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    add_custom_css()
    main()