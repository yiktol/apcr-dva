import redis
import json
import uuid
import boto3
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.chat_history import BaseChatMessageHistory
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

def get_redis_password_from_secrets(secret_name: str, region_name: str) -> str:
    """Retrieve Redis password from AWS Secrets Manager"""
    try:
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
        
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        
        # Handle different secret formats
        if isinstance(secret, dict):
            # Try common key names for Redis password
            for key in ['password', 'redis_password', 'auth_token', 'token']:
                if key in secret:
                    return secret[key]
            # If no standard key, return the first value
            return list(secret.values())[0]
        else:
            return secret
            
    except ClientError as e:
        logger.error(f"Error retrieving secret from Secrets Manager: {e}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing secret JSON: {e}")
        # Return as plain text if not JSON
        return response['SecretString']
    except Exception as e:
        logger.error(f"Unexpected error retrieving Redis password: {e}")
        raise

class ElastiCacheRedisMessageHistory(BaseChatMessageHistory):
    """
    Chat message history that uses Amazon ElastiCache for Redis as the backend.
    Optimized for ElastiCache Serverless with proper connection handling and error recovery.
    """
    
    def __init__(
        self,
        session_id: str,
        redis_endpoint: str,
        redis_port: int = 6379,
        redis_password: Optional[str] = None,
        use_ssl: bool = True,
        key_prefix: str = "chat_history",
        ttl: int = 3600,  # 1 hour default
        max_messages: int = 50,
        secret_name: Optional[str] = None,
        aws_region: str = "us-east-1"
    ):
        """
        Initialize Redis message history
        
        Args:
            session_id: Unique session identifier
            redis_endpoint: ElastiCache endpoint
            redis_port: Redis port (default 6379)
            redis_password: Redis auth password
            use_ssl: Whether to use SSL/TLS
            key_prefix: Prefix for Redis keys
            ttl: Time-to-live for sessions in seconds
            max_messages: Maximum messages to keep per session
            secret_name: AWS Secrets Manager secret name for password
            aws_region: AWS region for Secrets Manager
        """
        self.session_id = session_id
        self.key_prefix = key_prefix
        self.ttl = ttl
        self.max_messages = max_messages
        self.aws_region = aws_region
        
        # Get Redis password from Secrets Manager if specified
        if secret_name and not redis_password:
            try:
                redis_password = get_redis_password_from_secrets(secret_name, aws_region)
                logger.info("Successfully retrieved Redis password from Secrets Manager")
            except Exception as e:
                logger.warning(f"Could not retrieve password from Secrets Manager: {e}")
        
        # Configure Redis connection with ElastiCache optimizations
        connection_kwargs = {
            'host': redis_endpoint,
            'port': redis_port,
            'decode_responses': True,
            'socket_connect_timeout': 5,
            'socket_timeout': 5,
            'socket_keepalive': True,
            'socket_keepalive_options': {},
            'retry_on_timeout': True,
            'health_check_interval': 30,  # Health check every 30 seconds
            'max_connections': 10,
        }
        
        if redis_password:
            connection_kwargs['password'] = redis_password
            
        if use_ssl:
            connection_kwargs.update({
                'ssl': True,
                'ssl_cert_reqs': None,  # For ElastiCache, we trust the endpoint
                'ssl_check_hostname': False,
            })
        
        try:
            # Create Redis connection pool for better performance
            self.redis_pool = redis.ConnectionPool(**connection_kwargs)
            self.redis_client = redis.Redis(connection_pool=self.redis_pool)
            
            # Test connection
            self.redis_client.ping()
            logger.info(f"Successfully connected to Redis at {redis_endpoint}:{redis_port}")
            
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
        except redis.AuthenticationError as e:
            logger.error(f"Redis authentication failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected Redis connection error: {e}")
            raise
    
    @property
    def key(self) -> str:
        """Generate Redis key for this session"""
        return f"{self.key_prefix}:{self.session_id}"
    
    @property
    def metadata_key(self) -> str:
        """Generate Redis key for session metadata"""
        return f"{self.key_prefix}:meta:{self.session_id}"
    
    @property
    def messages(self) -> List[BaseMessage]:
        """Retrieve messages for this session"""
        return self.get_messages()
    
    def get_messages(self) -> List[BaseMessage]:
        """
        Retrieve all messages for the current session from Redis
        
        Returns:
            List of BaseMessage objects
        """
        try:
            # Get messages from Redis list
            message_data = self.redis_client.lrange(self.key, 0, -1)
            
            messages = []
            for data in message_data:
                try:
                    message_dict = json.loads(data)
                    message = self._dict_to_message(message_dict)
                    messages.append(message)
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Failed to parse message: {e}")
                    continue
            
            # Update session activity
            self._update_session_metadata()
            
            return messages
            
        except redis.RedisError as e:
            logger.error(f"Redis error retrieving messages: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error retrieving messages: {e}")
            return []
    
    def add_message(self, message: BaseMessage) -> None:
        """
        Add a message to the session history in Redis
        
        Args:
            message: The message to add
        """
        try:
            # Convert message to dictionary
            message_dict = self._message_to_dict(message)
            message_json = json.dumps(message_dict, ensure_ascii=False)
            
            # Use Redis pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            
            # Add message to list
            pipe.rpush(self.key, message_json)
            
            # Trim list to max_messages if specified
            if self.max_messages > 0:
                pipe.ltrim(self.key, -self.max_messages, -1)
            
            # Set TTL if specified
            if self.ttl > 0:
                pipe.expire(self.key, self.ttl)
            
            # Update metadata
            metadata = {
                'last_activity': datetime.utcnow().isoformat(),
                'message_count': self.redis_client.llen(self.key) + 1,
                'session_id': self.session_id,
                'created_at': datetime.utcnow().isoformat()
            }
            pipe.hset(self.metadata_key, mapping=metadata)
            
            if self.ttl > 0:
                pipe.expire(self.metadata_key, self.ttl)
            
            # Execute pipeline
            pipe.execute()
            
            logger.debug(f"Added message to session {self.session_id}")
            
        except redis.RedisError as e:
            logger.error(f"Redis error adding message: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error adding message: {e}")
            raise
    
    def clear(self) -> None:
        """Clear all messages for this session"""
        try:
            pipe = self.redis_client.pipeline()
            pipe.delete(self.key)
            pipe.delete(self.metadata_key)
            pipe.execute()
            
            logger.info(f"Cleared session {self.session_id}")
            
        except redis.RedisError as e:
            logger.error(f"Redis error clearing session: {e}")
            raise
    
    def _message_to_dict(self, message: BaseMessage) -> Dict[str, Any]:
        """Convert BaseMessage to dictionary for JSON serialization"""
        message_dict = {
            'content': message.content,
            'type': message.__class__.__name__,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Add additional data if present
        if hasattr(message, 'additional_kwargs') and message.additional_kwargs:
            message_dict['additional_kwargs'] = message.additional_kwargs
            
        return message_dict
    
    def _dict_to_message(self, message_dict: Dict[str, Any]) -> BaseMessage:
        """Convert dictionary back to BaseMessage"""
        message_type = message_dict.get('type', 'HumanMessage')
        content = message_dict.get('content', '')
        additional_kwargs = message_dict.get('additional_kwargs', {})
        
        if message_type == 'HumanMessage':
            return HumanMessage(content=content, additional_kwargs=additional_kwargs)
        elif message_type == 'AIMessage':
            return AIMessage(content=content, additional_kwargs=additional_kwargs)
        elif message_type == 'SystemMessage':
            return SystemMessage(content=content, additional_kwargs=additional_kwargs)
        else:
            # Default to HumanMessage for unknown types
            return HumanMessage(content=content, additional_kwargs=additional_kwargs)
    
    def _update_session_metadata(self) -> None:
        """Update session metadata"""
        try:
            metadata = {
                'last_activity': datetime.utcnow().isoformat(),
                'message_count': self.redis_client.llen(self.key)
            }
            
            pipe = self.redis_client.pipeline()
            pipe.hset(self.metadata_key, mapping=metadata)
            
            if self.ttl > 0:
                pipe.expire(self.metadata_key, self.ttl)
            
            pipe.execute()
            
        except redis.RedisError as e:
            logger.warning(f"Failed to update session metadata: {e}")
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get session information and statistics"""
        try:
            # Get metadata
            metadata = self.redis_client.hgetall(self.metadata_key)
            
            # Get additional info
            message_count = self.redis_client.llen(self.key)
            ttl_seconds = self.redis_client.ttl(self.key)
            
            session_info = {
                'session_id': self.session_id,
                'message_count': message_count,
                'ttl_seconds': ttl_seconds if ttl_seconds > 0 else None,
                'last_activity': metadata.get('last_activity'),
                'created_at': metadata.get('created_at'),
                'redis_key': self.key,
                'metadata_key': self.metadata_key
            }
            
            return session_info
            
        except redis.RedisError as e:
            logger.error(f"Redis error getting session info: {e}")
            return {'session_id': self.session_id, 'error': str(e)}
    
    def extend_session(self, additional_ttl: int = None) -> bool:
        """
        Extend the session TTL
        
        Args:
            additional_ttl: Additional time in seconds (if None, uses original TTL)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            ttl_to_set = additional_ttl or self.ttl
            if ttl_to_set <= 0:
                return True  # No TTL to set
            
            pipe = self.redis_client.pipeline()
            pipe.expire(self.key, ttl_to_set)
            pipe.expire(self.metadata_key, ttl_to_set)
            pipe.execute()
            
            logger.debug(f"Extended session {self.session_id} TTL by {ttl_to_set} seconds")
            return True
            
        except redis.RedisError as e:
            logger.error(f"Failed to extend session TTL: {e}")
            return False
    
    def get_message_count(self) -> int:
        """Get the number of messages in this session"""
        try:
            return self.redis_client.llen(self.key)
        except redis.RedisError:
            return 0
    
    def close(self) -> None:
        """Close Redis connection"""
        try:
            if hasattr(self, 'redis_client'):
                self.redis_client.close()
            if hasattr(self, 'redis_pool'):
                self.redis_pool.disconnect()
                
        except Exception as e:
            logger.warning(f"Error closing Redis connection: {e}")


class RedisSessionManager:
    """
    Manage user sessions in Redis with support for multiple concurrent sessions
    """
    
    def __init__(
        self, 
        redis_client: redis.Redis,
        session_prefix: str = "session",
        user_sessions_prefix: str = "user_sessions",
        default_ttl: int = 3600
    ):
        """
        Initialize session manager
        
        Args:
            redis_client: Redis client instance
            session_prefix: Prefix for session keys
            user_sessions_prefix: Prefix for user session tracking
            default_ttl: Default session TTL in seconds
        """
        self.redis_client = redis_client
        self.session_prefix = session_prefix
        self.user_sessions_prefix = user_sessions_prefix
        self.default_ttl = default_ttl
    
    def create_session(self, user_id: Optional[str] = None, ttl: Optional[int] = None) -> str:
        """
        Create a new session
        
        Args:
            user_id: Optional user identifier
            ttl: Session time-to-live in seconds
            
        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())
        session_ttl = ttl or self.default_ttl
        
        try:
            session_data = {
                'session_id': session_id,
                'user_id': user_id or 'anonymous',
                'created_at': datetime.utcnow().isoformat(),
                'last_activity': datetime.utcnow().isoformat(),
                'status': 'active'
            }
            
            session_key = f"{self.session_prefix}:{session_id}"
            
            pipe = self.redis_client.pipeline()
            pipe.hset(session_key, mapping=session_data)
            
            if session_ttl > 0:
                pipe.expire(session_key, session_ttl)
            
            # Track user sessions if user_id provided
            if user_id:
                user_sessions_key = f"{self.user_sessions_prefix}:{user_id}"
                pipe.sadd(user_sessions_key, session_id)
                if session_ttl > 0:
                    pipe.expire(user_sessions_key, session_ttl + 3600)  # Extra hour for cleanup
            
            pipe.execute()
            
            logger.info(f"Created session {session_id} for user {user_id or 'anonymous'}")
            return session_id
            
        except redis.RedisError as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data or None if not found
        """
        try:
            session_key = f"{self.session_prefix}:{session_id}"
            session_data = self.redis_client.hgetall(session_key)
            
            if not session_data:
                return None
            
            # Add TTL information
            ttl = self.redis_client.ttl(session_key)
            session_data['ttl_seconds'] = ttl if ttl > 0 else None
            
            return session_data
            
        except redis.RedisError as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None
    
    def update_session_activity(self, session_id: str) -> bool:
        """
        Update session last activity timestamp
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session_key = f"{self.session_prefix}:{session_id}"
            
            # Check if session exists
            if not self.redis_client.exists(session_key):
                return False
            
            self.redis_client.hset(
                session_key, 
                'last_activity', 
                datetime.utcnow().isoformat()
            )
            
            return True
            
        except redis.RedisError as e:
            logger.error(f"Failed to update session activity: {e}")
            return False
    
    def extend_session(self, session_id: str, additional_seconds: int) -> bool:
        """
        Extend session TTL
        
        Args:
            session_id: Session identifier
            additional_seconds: Additional time in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session_key = f"{self.session_prefix}:{session_id}"
            
            current_ttl = self.redis_client.ttl(session_key)
            if current_ttl < 0:
                # No TTL set, set new one
                new_ttl = additional_seconds
            else:
                new_ttl = current_ttl + additional_seconds
            
            self.redis_client.expire(session_key, new_ttl)
            
            logger.debug(f"Extended session {session_id} TTL to {new_ttl} seconds")
            return True
            
        except redis.RedisError as e:
            logger.error(f"Failed to extend session TTL: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session_key = f"{self.session_prefix}:{session_id}"
            
            # Get user_id before deletion for cleanup
            session_data = self.redis_client.hgetall(session_key)
            user_id = session_data.get('user_id')
            
            pipe = self.redis_client.pipeline()
            pipe.delete(session_key)
            
            # Remove from user sessions if applicable
            if user_id and user_id != 'anonymous':
                user_sessions_key = f"{self.user_sessions_prefix}:{user_id}"
                pipe.srem(user_sessions_key, session_id)
            
            result = pipe.execute()
            
            logger.info(f"Deleted session {session_id}")
            return result[0] > 0  # Returns number of keys deleted
            
        except redis.RedisError as e:
            logger.error(f"Failed to delete session: {e}")
            return False
    
    def get_user_sessions(self, user_id: str) -> List[str]:
        """
        Get all sessions for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of session IDs
        """
        try:
            user_sessions_key = f"{self.user_sessions_prefix}:{user_id}"
            sessions = list(self.redis_client.smembers(user_sessions_key))
            
            # Clean up expired sessions
            valid_sessions = []
            pipe = self.redis_client.pipeline()
            
            for session_id in sessions:
                session_key = f"{self.session_prefix}:{session_id}"
                if self.redis_client.exists(session_key):
                    valid_sessions.append(session_id)
                else:
                    # Remove expired session from user's session set
                    pipe.srem(user_sessions_key, session_id)
            
            pipe.execute()
            
            return valid_sessions
            
        except redis.RedisError as e:
            logger.error(f"Failed to get user sessions: {e}")
            return []
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions (manual cleanup for debugging)
        
        Returns:
            Number of sessions cleaned up
        """
        cleaned_count = 0
        
        try:
            # This is a basic implementation - in production, you might want
            # to use Redis's built-in expiration or a more sophisticated cleanup
            
            session_pattern = f"{self.session_prefix}:*"
            session_keys = self.redis_client.keys(session_pattern)
            
            for session_key in session_keys:
                ttl = self.redis_client.ttl(session_key)
                if ttl == -2:  # Key doesn't exist (expired and removed)
                    cleaned_count += 1
                    
            logger.info(f"Cleaned up {cleaned_count} expired sessions")
            return cleaned_count
            
        except redis.RedisError as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
            return 0
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get session statistics
        
        Returns:
            Dictionary with session statistics
        """
        try:
            session_pattern = f"{self.session_prefix}:*"
            session_keys = self.redis_client.keys(session_pattern)
            
            total_sessions = len(session_keys)
            active_sessions = 0
            expired_sessions = 0
            
            for session_key in session_keys:
                ttl = self.redis_client.ttl(session_key)
                if ttl > 0:
                    active_sessions += 1
                elif ttl == -2:
                    expired_sessions += 1
            
            return {
                'total_sessions': total_sessions,
                'active_sessions': active_sessions,
                'expired_sessions': expired_sessions,
                'session_prefix': self.session_prefix
            }
            
        except redis.RedisError as e:
            logger.error(f"Failed to get session stats: {e}")
            return {'error': str(e)}


class RedisHealthChecker:
    """
    Monitor Redis connection health and provide diagnostics
    """
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
    
    def check_connection(self) -> Dict[str, Any]:
        """
        Check Redis connection health
        
        Returns:
            Health check results
        """
        health_info = {
            'connected': False,
            'latency_ms': None,
            'memory_usage': None,
            'info': {},
            'error': None
        }
        
        try:
            # Test basic connectivity
            start_time = datetime.utcnow()
            self.redis_client.ping()
            end_time = datetime.utcnow()
            
            health_info['connected'] = True
            health_info['latency_ms'] = (end_time - start_time).total_seconds() * 1000
            
            # Get Redis info
            redis_info = self.redis_client.info()
            health_info['info'] = {
                'redis_version': redis_info.get('redis_version'),
                'used_memory_human': redis_info.get('used_memory_human'),
                'connected_clients': redis_info.get('connected_clients'),
                'total_commands_processed': redis_info.get('total_commands_processed'),
                'uptime_in_seconds': redis_info.get('uptime_in_seconds')
            }
            
        except redis.ConnectionError as e:
            health_info['error'] = f"Connection error: {e}"
        except redis.TimeoutError as e:
            health_info['error'] = f"Timeout error: {e}"
        except Exception as e:
            health_info['error'] = f"Unexpected error: {e}"
        
        return health_info
    
    def test_operations(self) -> Dict[str, Any]:
        """
        Test basic Redis operations
        
        Returns:
            Test results
        """
        test_results = {
            'set_get': False,
            'list_operations': False,
            'hash_operations': False,
            'expiration': False,
            'errors': []
        }
        
        test_key_prefix = f"health_check_{uuid.uuid4().hex[:8]}"
        
        try:
            # Test SET/GET
            test_key = f"{test_key_prefix}_string"
            self.redis_client.set(test_key, "test_value", ex=60)
            value = self.redis_client.get(test_key)
            if value == "test_value":
                test_results['set_get'] = True
            self.redis_client.delete(test_key)
            
        except Exception as e:
            test_results['errors'].append(f"SET/GET test failed: {e}")
        
        try:
            # Test list operations
            list_key = f"{test_key_prefix}_list"
            self.redis_client.lpush(list_key, "item1", "item2")
            items = self.redis_client.lrange(list_key, 0, -1)
            if len(items) == 2:
                test_results['list_operations'] = True
            self.redis_client.delete(list_key)
            
        except Exception as e:
            test_results['errors'].append(f"List operations test failed: {e}")
        
        try:
            # Test hash operations
            hash_key = f"{test_key_prefix}_hash"
            self.redis_client.hset(hash_key, mapping={"field1": "value1", "field2": "value2"})
            hash_data = self.redis_client.hgetall(hash_key)
            if len(hash_data) == 2:
                test_results['hash_operations'] = True
            self.redis_client.delete(hash_key)
            
        except Exception as e:
            test_results['errors'].append(f"Hash operations test failed: {e}")
        
        try:
            # Test expiration
            exp_key = f"{test_key_prefix}_exp"
            self.redis_client.set(exp_key, "temp_value", ex=1)
            ttl = self.redis_client.ttl(exp_key)
            if 0 < ttl <= 1:
                test_results['expiration'] = True
            self.redis_client.delete(exp_key)
            
        except Exception as e:
            test_results['errors'].append(f"Expiration test failed: {e}")
        
        return test_results