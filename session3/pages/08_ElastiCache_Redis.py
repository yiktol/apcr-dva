# ------------------------------------------------------------------------
# Streamlit Chat with ElastiCache Redis Memory - Amazon Bedrock and LangChain
# ------------------------------------------------------------------------
import streamlit as st
import boto3
import botocore
import uuid
import redis
import json
import os
from typing import Optional, List
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_aws import ChatBedrock
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import utils.common as common
import utils.authenticate as authenticate


class RedisChatMessageHistory(BaseChatMessageHistory):
    """Custom Redis chat message history implementation for LangChain."""
    
    def __init__(self, session_id: str, redis_client: redis.Redis, ttl: int = 3600):
        self.session_id = session_id
        self.redis_client = redis_client
        self.ttl = ttl
        self.key = f"chat_history:{session_id}"
    
    @property
    def messages(self) -> List[BaseMessage]:
        """Retrieve messages from Redis."""
        try:
            messages_data = self.redis_client.get(self.key)
            if not messages_data:
                return []
            
            messages_list = json.loads(messages_data)
            messages = []
            
            for msg_data in messages_list:
                if msg_data["type"] == "human":
                    messages.append(HumanMessage(content=msg_data["content"]))
                elif msg_data["type"] == "ai":
                    messages.append(AIMessage(content=msg_data["content"]))
            
            return messages
        except Exception as e:
            st.error(f"Error retrieving messages from Redis: {e}")
            return []
    
    def add_message(self, message: BaseMessage) -> None:
        """Add a message to Redis."""
        try:
            current_messages = self.messages
            current_messages.append(message)
            
            # Convert messages to serializable format
            messages_data = []
            for msg in current_messages:
                if isinstance(msg, HumanMessage):
                    messages_data.append({"type": "human", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    messages_data.append({"type": "ai", "content": msg.content})
            
            # Store in Redis with TTL
            self.redis_client.setex(
                self.key, 
                self.ttl, 
                json.dumps(messages_data)
            )
        except Exception as e:
            st.error(f"Error adding message to Redis: {e}")
    
    def clear(self) -> None:
        """Clear the chat history."""
        try:
            self.redis_client.delete(self.key)
        except Exception as e:
            st.error(f"Error clearing messages from Redis: {e}")


class RedisConnectionManager:
    """Manages Redis connections with proper error handling and connection pooling."""
    
    def __init__(self):
        self._redis_client: Optional[redis.Redis] = None
        self._connection_pool: Optional[redis.ConnectionPool] = None
    
    def get_redis_client(self, host: str, port: int = 6379, 
                        ssl: bool = True, decode_responses: bool = True) -> Optional[redis.Redis]:
        """Get Redis client with connection pooling."""
        try:
            if not self._connection_pool:
                self._connection_pool = redis.ConnectionPool(
                    host=host,
                    port=port,
                    ssl=ssl,
                    ssl_cert_reqs=None,
                    decode_responses=decode_responses,
                    max_connections=10,
                    retry_on_timeout=True,
                    socket_keepalive=True,
                    socket_keepalive_options={},
                )
            
            if not self._redis_client:
                self._redis_client = redis.Redis(connection_pool=self._connection_pool)
            
            # Test connection
            self._redis_client.ping()
            return self._redis_client
            
        except redis.ConnectionError as e:
            st.error(f"Redis connection error: {e}")
            return None
        except Exception as e:
            st.error(f"Unexpected Redis error: {e}")
            return None
    
    def test_connection(self, redis_client: redis.Redis) -> bool:
        """Test Redis connection."""
        try:
            return redis_client.ping()
        except Exception:
            return False


def get_model_kwargs(model: str, temperature: float, top_p: float, max_tokens: int) -> dict:
    """Get model-specific parameters based on the provider."""
    provider = model.split(":")[0] if ":" in model else model.split(".")[0]
    
    model_configs = {
        "anthropic": {
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_k": 200,
            "top_p": top_p,
            "stop_sequences": ["\n\nHuman"],
        },
        "mistral": {
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_k": 200,
            "top_p": top_p,
        },
        "amazon": {
            "maxTokenCount": max_tokens,
            "temperature": temperature,
            "topP": top_p,
        },
        "meta": {
            "max_gen_len": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
        },
    }
    
    return model_configs.get(provider, {})


def initialize_bedrock_client(region: str = "us-east-1") -> boto3.client:
    """Initialize Amazon Bedrock client."""
    try:
        return boto3.client(
            service_name="bedrock-runtime",
            region_name=region,
        )
    except Exception as e:
        st.error(f"Error initializing Bedrock client: {e}")
        return None


def create_chat_chain(bedrock_client, model_id: str, model_kwargs: dict, 
                     redis_client: redis.Redis, session_id: str):
    """Create the chat chain with Redis message history."""
    
    template = [
        ("system", "You are a helpful assistant."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]

    prompt = ChatPromptTemplate.from_messages(template)

    bedrock_model = ChatBedrock(
        client=bedrock_client,
        model_id=model_id,
        model_kwargs=model_kwargs,
    )

    chain = prompt | bedrock_model | StrOutputParser()

    # Chain with Redis History
    chain_with_history = RunnableWithMessageHistory(
        chain,
        lambda session_id: RedisChatMessageHistory(
            session_id=session_id, 
            redis_client=redis_client
        ),
        input_messages_key="question",
        history_messages_key="history",
    )
    
    return chain_with_history


def render_sidebar_controls(redis_client: Optional[redis.Redis]) -> tuple:
    """Render sidebar controls and return configuration values."""
    with st.sidebar:
        common.render_sidebar()
        
        # Redis Connection Status
        with st.container(border=True):
            st.write(":orange[Redis Connection Status]")
            if redis_client:
                try:
                    if redis_client.ping():
                        st.success("✅ Connected to Redis")
                        if st.button("Test Redis Connection"):
                            try:
                                info = redis_client.info()
                                st.write(f"Redis Version: {info.get('redis_version', 'Unknown')}")
                                st.write(f"Connected Clients: {info.get('connected_clients', 'Unknown')}")
                            except Exception as e:
                                st.error(f"Error getting Redis info: {e}")
                except:
                    st.error("❌ Redis Connection Failed")
            else:
                st.error("❌ No Redis Connection")
        
        # Model Parameters
        with st.expander('Model Parameters', expanded=False):
            model = st.selectbox('Model', [
                "anthropic.claude-3-sonnet-20240229-v1:0",
                "mistral.mistral-large-2402-v1:0",
                "amazon.titan-tg1-large",
                "meta.llama2-70b-chat-v1"
            ])
            temperature = st.slider('Temperature', min_value=0.0, max_value=1.0, value=0.1, step=0.1)
            top_p = st.slider('Top P', min_value=0.0, max_value=1.0, value=0.9, step=0.1)
            max_tokens = st.slider('Max Tokens', min_value=50, max_value=4096, value=1024, step=10)
        
        # Chat Controls
        with st.container(border=True):
            st.markdown(':orange[Chat Controls]')
            streaming_on = st.toggle('Enable Streaming', value=True)
            
            if st.button('Clear Chat History', use_container_width=True):
                if redis_client and 'session_id' in st.session_state:
                    try:
                        redis_history = RedisChatMessageHistory(
                            session_id=st.session_state.session_id,
                            redis_client=redis_client
                        )
                        redis_history.clear()
                        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error clearing history: {e}")
    
    return model, temperature, top_p, max_tokens, streaming_on


def process_chat_message(chain_with_history, user_prompt: str, session_id: str, streaming_on: bool):
    """Process chat message and display response."""
    config = {"configurable": {"session_id": session_id}}
    
    if streaming_on:
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ''
            try:
                for chunk in chain_with_history.stream({"question": user_prompt}, config=config):
                    full_response += chunk
                    placeholder.markdown(full_response)
                placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"Error during streaming: {e}")
    else:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = chain_with_history.invoke({"question": user_prompt}, config=config)
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Error getting response: {e}")


def main():
    """Main application function."""
    # Page configuration
    st.set_page_config(
        page_title='Chatbot with Redis Memory',
        page_icon=":brain:",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize session state
    common.initialize_session_state()
    
    # Page header
    st.subheader("Chatbot with ElastiCache Redis Memory")
    st.write("Amazon ElastiCache for Redis provides persistent memory for your conversational AI application")

    # Get Redis endpoint from environment or Streamlit secrets
    redis_endpoint = os.getenv('REDIS_ENDPOINT') or st.secrets.get("REDIS_ENDPOINT")
    
    if not redis_endpoint:
        st.error("Redis endpoint not configured. Please set REDIS_ENDPOINT environment variable or add it to Streamlit secrets.")
        st.stop()

    # Initialize Redis connection
    redis_manager = RedisConnectionManager()
    redis_client = redis_manager.get_redis_client(host=redis_endpoint, port=6379)

    if not redis_client:
        st.error("Failed to connect to Redis. Please check your configuration.")
        st.stop()

    # Initialize Bedrock client
    bedrock_client = initialize_bedrock_client()
    if not bedrock_client:
        st.stop()

    # Render sidebar and get configuration
    model, temperature, top_p, max_tokens, streaming_on = render_sidebar_controls(redis_client)

    # Get model parameters
    model_kwargs = get_model_kwargs(model, temperature, top_p, max_tokens)

    # Create chat chain
    chain_with_history = create_chat_chain(
        bedrock_client, model, model_kwargs, redis_client, st.session_state.session_id
    )

    # Initialize chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input and processing
    if user_prompt := st.chat_input("What can I help you with?"):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.write(user_prompt)

        # Process and display response
        process_chat_message(chain_with_history, user_prompt, st.session_state.session_id, streaming_on)


if __name__ == "__main__":
    if 'localhost' in st.context.headers.get("host", ""):
        main()
    else:
        # Check authentication for non-local environments
        is_authenticated = authenticate.login()
        
        if is_authenticated:
            main()