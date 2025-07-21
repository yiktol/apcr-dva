import json
import boto3
from typing import Optional, Dict, Any, List, Generator
from langchain_aws import ChatBedrock
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain.callbacks.base import BaseCallbackHandler
from botocore.exceptions import ClientError, NoCredentialsError
import streamlit as st
import logging

logger = logging.getLogger(__name__)

class BedrockStreamingCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for Bedrock streaming with Streamlit"""
    
    def __init__(self, container):
        self.container = container
        self.text = ""
        self.tokens = []
    
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Called when a new token is generated"""
        self.text += token
        self.tokens.append(token)
        self.container.markdown(self.text + "▋")
    
    def on_llm_end(self, response, **kwargs) -> None:
        """Called when LLM finishes"""
        self.container.markdown(self.text)

class BedrockChatManager:
    """Enhanced chat manager using Amazon Bedrock Claude models"""
    
    def __init__(
        self,
        redis_memory_history,
        model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0",
        region: str = "us-east-1",
        temperature: float = 0.7,
        max_tokens: int = 4000,
        top_p: float = 0.9,
        window_size: int = 10,
        aws_session: Optional[boto3.Session] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None
    ):
        self.redis_memory_history = redis_memory_history
        self.model_id = model_id
        self.region = region
        
        # Initialize AWS session
        try:
            # Use provided session if available
            if aws_session:
                self.session = aws_session
            else:
                # Create a new session if none provided
                session_kwargs = {"region_name": region}
                if aws_access_key_id and aws_secret_access_key:
                    session_kwargs.update({
                        "aws_access_key_id": aws_access_key_id,
                        "aws_secret_access_key": aws_secret_access_key
                    })
                    if aws_session_token:
                        session_kwargs["aws_session_token"] = aws_session_token
                    
                self.session = boto3.Session(**session_kwargs)
            
            # Create bedrock-runtime client
            self.bedrock_client = self.session.client('bedrock-runtime', region_name=region)
            
            # Test connection
            self._test_bedrock_connection()
            
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            raise
        
        # Model configuration
        self.model_kwargs = {
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stop_sequences": ["\n\nHuman:", "\n\nAssistant:"]
        }
        
        # Initialize Bedrock LLM
        try:
            self.llm = ChatBedrock(
                client=self.bedrock_client,
                model_id=model_id,
                model_kwargs=self.model_kwargs,
                streaming=True,
                region_name=region
            )
            logger.info(f"Initialized Bedrock ChatManager with model: {model_id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChatBedrock: {e}")
            raise
        
        # Initialize memory with Redis backend
        self.memory = ConversationBufferWindowMemory(
            chat_memory=redis_memory_history,
            k=window_size,
            return_messages=True,
            memory_key="chat_history"
        )
        
        # System prompt for Claude
        self.system_prompt = """You are Claude, an AI assistant created by Anthropic. You are helpful, harmless, and honest. You have access to conversation history stored in Redis, allowing you to maintain context across our conversation.

Key guidelines:
- Provide clear, accurate, and helpful responses
- If you're unsure about something, say so rather than guessing
- Be conversational but professional
- Remember our previous exchanges in this conversation
- Ask clarifying questions when needed

Please respond helpfully to the user's questions and requests."""
    
    def _test_bedrock_connection(self):
        """Test connection to Bedrock"""
        try:
            # Create a bedrock client (not bedrock-runtime) for testing
            bedrock = self.session.client('bedrock', region_name=self.region)
            
            # Try a simple operation that doesn't require model access
            try:
                bedrock.list_foundation_models()
                logger.info("Successfully connected to Amazon Bedrock")
                return True
            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')
                error_msg = e.response.get('Error', {}).get('Message', '')
                
                # If it's just a permissions issue but connection works, log and continue
                if error_code == 'AccessDeniedException' and 'not authorized' in error_msg:
                    logger.warning(f"Limited Bedrock permissions, but connection established: {error_msg}")
                    return True
                else:
                    logger.error(f"AWS ClientError connecting to Bedrock: {e}")
                    raise
                    
        except NoCredentialsError as e:
            logger.error(f"AWS credentials not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to Bedrock: {e}")
            raise
    
    def get_response(self, user_input: str, stream_container=None) -> str:
        """Get response from Claude via Bedrock"""
        try:
            # Add user message to memory
            self.memory.chat_memory.add_message(HumanMessage(content=user_input))
            
            # Prepare messages for the model
            messages = self._prepare_messages()
            
            if stream_container and hasattr(self.llm, 'stream'):
                # Streaming response
                ai_response = self._get_streaming_response(messages, stream_container)
            else:
                # Non-streaming response
                ai_response = self._get_standard_response(messages)
            
            # Add AI response to memory
            self.memory.chat_memory.add_message(AIMessage(content=ai_response))
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error getting response from Bedrock: {e}")
            error_message = f"I apologize, but I encountered an error: {str(e)}"
            self.memory.chat_memory.add_message(AIMessage(content=error_message))
            return error_message
    
    def _get_streaming_response(self, messages: List[BaseMessage], stream_container) -> str:
        """Get streaming response from Bedrock"""
        try:
            callback_handler = BedrockStreamingCallbackHandler(stream_container)
            
            # Use the streaming method
            response = self.llm.invoke(
                input=messages,
                config={"callbacks": [callback_handler]}
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error in streaming response: {e}")
            # Fallback to standard response
            return self._get_standard_response(messages)
    
    def _get_standard_response(self, messages: List[BaseMessage]) -> str:
        """Get standard (non-streaming) response from Bedrock"""
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"Error in standard response: {e}")
            raise
    
    def _prepare_messages(self) -> List[BaseMessage]:
        """Prepare messages for the Bedrock model"""
        # Get conversation history from memory
        memory_variables = self.memory.load_memory_variables({})
        chat_history = memory_variables.get("chat_history", [])
        
        # Create system message
        system_message = SystemMessage(content=self.system_prompt)
        
        # Combine system message with chat history
        messages = [system_message] + chat_history
        
        return messages
    
    def invoke_bedrock_direct(self, prompt: str) -> str:
        """Direct invocation of Bedrock API for advanced use cases"""
        try:
            # Prepare the request body for Claude
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": self.model_kwargs["max_tokens"],
                "temperature": self.model_kwargs["temperature"],
                "top_p": self.model_kwargs["top_p"],
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Invoke the model
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body),
                contentType='application/json',
                accept='application/json'
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            logger.error(f"Error in direct Bedrock invocation: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        try:
            response = self.bedrock_client.get_foundation_model(
                modelIdentifier=self.model_id
            )
            return {
                "model_id": self.model_id,
                "model_name": response.get("modelDetails", {}).get("modelName", "Unknown"),
                "provider": response.get("modelDetails", {}).get("providerName", "Unknown"),
                "input_modalities": response.get("modelDetails", {}).get("inputModalities", []),
                "output_modalities": response.get("modelDetails", {}).get("outputModalities", []),
                "region": self.region
            }
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {
                "model_id": self.model_id,
                "region": self.region,
                "error": str(e)
            }
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """List available Claude models in Bedrock"""
        try:
            response = self.bedrock_client.list_foundation_models(
                byProvider="Anthropic"
            )
            
            models = []
            for model in response.get("modelSummaries", []):
                if "claude" in model.get("modelId", "").lower():
                    models.append({
                        "model_id": model.get("modelId"),
                        "model_name": model.get("modelName"),
                        "provider": model.get("providerName"),
                        "input_modalities": model.get("inputModalities", []),
                        "output_modalities": model.get("outputModalities", [])
                    })
            
            return models
            
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            return []
    
    def update_model_parameters(
        self, 
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None
    ):
        """Update model parameters"""
        if temperature is not None:
            self.model_kwargs["temperature"] = temperature
        if max_tokens is not None:
            self.model_kwargs["max_tokens"] = max_tokens
        if top_p is not None:
            self.model_kwargs["top_p"] = top_p
        
        # Reinitialize LLM with new parameters
        try:
            self.llm = ChatBedrock(
                client=self.bedrock_client,
                model_id=self.model_id,
                model_kwargs=self.model_kwargs,
                streaming=True,
                region_name=self.region
            )
            logger.info("Updated model parameters successfully")
        except Exception as e:
            logger.error(f"Error updating model parameters: {e}")
            raise
    
    def clear_conversation(self) -> None:
        """Clear the conversation history"""
        try:
            self.memory.clear()
            logger.info("Cleared conversation history")
        except Exception as e:
            logger.error(f"Error clearing conversation: {e}")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation"""
        try:
            memory_variables = self.memory.load_memory_variables({})
            chat_history = memory_variables.get("chat_history", [])
            
            message_count = len(chat_history)
            human_messages = len([msg for msg in chat_history if isinstance(msg, HumanMessage)])
            ai_messages = len([msg for msg in chat_history if isinstance(msg, AIMessage)])
            
            return {
                "total_messages": message_count,
                "human_messages": human_messages,
                "ai_messages": ai_messages,
                "memory_key": self.memory.memory_key,
                "model_id": self.model_id,
                "model_params": self.model_kwargs
            }
            
        except Exception as e:
            logger.error(f"Error getting conversation summary: {e}")
            return {}

class BedrockModelManager:
    """Manage Bedrock model selection and configuration"""
    
    def __init__(self, bedrock_client):
        self.bedrock_client = bedrock_client
    
    def get_claude_models(self) -> List[Dict[str, str]]:
        """Get available Claude models"""
        try:
            response = self.bedrock_client.list_foundation_models(
                byProvider="Anthropic"
            )
            
            claude_models = []
            for model in response.get("modelSummaries", []):
                model_id = model.get("modelId", "")
                if "claude" in model_id.lower():
                    claude_models.append({
                        "id": model_id,
                        "name": model.get("modelName", model_id),
                        "description": self._get_model_description(model_id)
                    })
            
            # Sort by model version (newest first)
            claude_models.sort(key=lambda x: x["id"], reverse=True)
            return claude_models
            
        except Exception as e:
            logger.error(f"Error fetching Claude models: {e}")
            return []
    
    def _get_model_description(self, model_id: str) -> str:
        """Get human-readable description for model"""
        descriptions = {
            "anthropic.claude-3-5-sonnet-20241022-v2:0": "Claude 3.5 Sonnet (Latest) - Best balance of intelligence and speed",
            "anthropic.claude-3-5-sonnet-20240620-v1:0": "Claude 3.5 Sonnet - Advanced reasoning and analysis",
            "anthropic.claude-3-sonnet-20240229-v1:0": "Claude 3 Sonnet - Strong performance across diverse tasks",
            "anthropic.claude-3-opus-20240229-v1:0": "Claude 3 Opus - Most capable model for complex tasks",
            "anthropic.claude-3-haiku-20240307-v1:0": "Claude 3 Haiku - Fastest model for simple tasks"
        }
        return descriptions.get(model_id, "Claude model for conversational AI")