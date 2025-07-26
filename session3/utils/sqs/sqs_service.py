import boto3
import json
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError, NoCredentialsError
from utils.sqs.config import AWSConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQSService:
    """Service class for AWS SQS operations"""
    
    def __init__(self, config: AWSConfig):
        self.config = config
        self._client = None
        
    @property
    def client(self):
        """Lazy initialization of SQS client"""
        if self._client is None:
            try:
                self._client = boto3.client(
                    'sqs',
                    region_name=self.config.region,
                    aws_access_key_id=self.config.access_key_id,
                    aws_secret_access_key=self.config.secret_access_key
                )
            except Exception as e:
                logger.error(f"Failed to initialize SQS client: {e}")
                raise
        return self._client
    
    def send_message(self, message_body: Dict[str, Any], 
                    queue_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a message to SQS queue
        
        Args:
            message_body: Message content as dictionary
            queue_url: SQS queue URL (optional, uses config default)
            
        Returns:
            Dict containing message ID and other metadata
        """
        try:
            url = queue_url or self.config.queue_url
            if not url:
                raise ValueError("Queue URL not provided")
            
            # Add metadata to message
            enhanced_message = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.utcnow().isoformat(),
                "body": message_body
            }
            
            message_body_str = json.dumps(enhanced_message, default=str)
            
            response = self.client.send_message(
                QueueUrl=url,
                MessageBody=message_body_str,
                MessageAttributes={
                    'MessageType': {
                        'StringValue': message_body.get('type', 'unknown'),
                        'DataType': 'String'
                    },
                    'Source': {
                        'StringValue': 'StreamlitApp',
                        'DataType': 'String'
                    }
                }
            )
            
            logger.info(f"Message sent successfully: {response.get('MessageId', 'Unknown')}")
            return {
                "success": True,
                "message_id": response.get('MessageId', 'Unknown'),
                "md5": response.get('MD5OfBody', 'N/A')
            }
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_msg = e.response.get('Error', {}).get('Message', str(e))
            logger.error(f"AWS Client Error [{error_code}]: {error_msg}")
            return {"success": False, "error": f"{error_code}: {error_msg}"}
        except NoCredentialsError:
            logger.error("AWS credentials not found")
            return {"success": False, "error": "AWS credentials not configured"}
        except KeyError as e:
            logger.error(f"Missing expected field in response: {e}")
            return {"success": False, "error": f"Missing field in SQS response: {e}"}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {"success": False, "error": str(e)}
    
    def receive_messages(self, max_messages: int = 10, 
                        queue_url: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Receive messages from SQS queue
        
        Args:
            max_messages: Maximum number of messages to receive
            queue_url: SQS queue URL (optional, uses config default)
            
        Returns:
            List of message dictionaries
        """
        try:
            url = queue_url or self.config.queue_url
            if not url:
                raise ValueError("Queue URL not provided")
            
            response = self.client.receive_message(
                QueueUrl=url,
                MaxNumberOfMessages=min(max_messages, 10),
                WaitTimeSeconds=1,
                MessageAttributeNames=['All']
            )
            
            messages = response.get('Messages', [])
            processed_messages = []
            
            for message in messages:
                try:
                    body = json.loads(message['Body'])
                    processed_messages.append({
                        "message_id": message['MessageId'],
                        "receipt_handle": message['ReceiptHandle'],
                        "body": body,
                        "attributes": message.get('MessageAttributes', {}),
                        "md5": message['MD5OfBody']
                    })
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse message body: {e}")
                    continue
            
            logger.info(f"Received {len(processed_messages)} messages")
            return processed_messages
            
        except ClientError as e:
            logger.error(f"AWS Client Error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return []
    
    def delete_message(self, receipt_handle: str, 
                      queue_url: Optional[str] = None) -> bool:
        """
        Delete a message from SQS queue
        
        Args:
            receipt_handle: Message receipt handle
            queue_url: SQS queue URL (optional, uses config default)
            
        Returns:
            Boolean indicating success
        """
        try:
            url = queue_url or self.config.queue_url
            if not url:
                raise ValueError("Queue URL not provided")
            
            self.client.delete_message(
                QueueUrl=url,
                ReceiptHandle=receipt_handle
            )
            
            logger.info("Message deleted successfully")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to delete message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False
    
    def get_queue_attributes(self, queue_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Get queue attributes
        
        Args:
            queue_url: SQS queue URL (optional, uses config default)
            
        Returns:
            Dictionary of queue attributes
        """
        try:
            url = queue_url or self.config.queue_url
            if not url:
                return {}
            
            response = self.client.get_queue_attributes(
                QueueUrl=url,
                AttributeNames=['All']
            )
            
            return response.get('Attributes', {})
            
        except Exception as e:
            logger.error(f"Failed to get queue attributes: {e}")
            return {}
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test SQS connection and queue accessibility
        
        Returns:
            Dictionary with connection test results
        """
        try:
            if not self.config.queue_url:
                return {"success": False, "error": "Queue URL not configured"}
            
            # Try to get queue attributes as a connection test
            attributes = self.get_queue_attributes()
            
            if attributes:
                return {
                    "success": True,
                    "message": "Connection successful",
                    "queue_name": self.config.queue_url.split('/')[-1]
                }
            else:
                return {"success": False, "error": "Unable to access queue"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}