"""AWS service clients and utilities."""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AWSServiceError(Exception):
    """Custom exception for AWS service errors."""
    pass

class SNSPublisher:
    """Handles SNS publishing operations."""
    
    def __init__(self, topic_arn: str, region: str = 'ap-southeast-1'):
        self.topic_arn = topic_arn
        self.region = region
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            try:
                self._client = boto3.client('sns', region_name=self.region)
            except NoCredentialsError:
                raise AWSServiceError("AWS credentials not configured")
        return self._client
    
    def publish_message(self, message: Dict[str, Any], subject: str = None) -> Dict[str, Any]:
        """Publish message to SNS topic with detailed response."""
        try:
            # Add metadata
            enhanced_message = {
                **message,
                'timestamp': datetime.utcnow().isoformat(),
                'source': 'publisher',
                'message_id': f"msg_{int(datetime.utcnow().timestamp() * 1000)}"
            }
            
            # Publish message
            response = self.client.publish(
                TopicArn=self.topic_arn,
                Message=json.dumps(enhanced_message, indent=2),
                Subject=subject or message.get('title', 'Notification')
            )
            
            message_id = response['MessageId']
            
            # Get detailed response info
            result = {
                'message_id': message_id,
                'response_metadata': response.get('ResponseMetadata', {}),
                'published_at': datetime.utcnow().isoformat(),
                'topic_arn': self.topic_arn,
                'message_content': enhanced_message
            }
            
            logger.info(f"Message published successfully: {message_id}")
            return result
            
        except ClientError as e:
            error_msg = f"Failed to publish message: {e.response['Error']['Message']}"
            logger.error(error_msg)
            raise AWSServiceError(error_msg)
    
    def get_topic_attributes(self) -> Dict[str, Any]:
        """Get topic attributes."""
        try:
            response = self.client.get_topic_attributes(TopicArn=self.topic_arn)
            return response['Attributes']
        except ClientError as e:
            logger.error(f"Failed to get topic attributes: {e}")
            return {}
    
    def get_subscriptions(self) -> List[Dict[str, Any]]:
        """Get all subscriptions for the topic."""
        try:
            response = self.client.list_subscriptions_by_topic(TopicArn=self.topic_arn)
            return response['Subscriptions']
        except ClientError as e:
            logger.error(f"Failed to get subscriptions: {e}")
            return []

class SQSConsumer:
    """Handles SQS message consumption."""
    
    def __init__(self, queue_url: str, region: str = 'ap-southeast-1'):
        self.queue_url = queue_url
        self.region = region
        self._client = None
    
    @property
    def client(self):
        if self._client is None:
            try:
                self._client = boto3.client('sqs', region_name=self.region)
            except NoCredentialsError:
                raise AWSServiceError("AWS credentials not configured")
        return self._client
    
    def receive_messages(self, max_messages: int = 10, wait_time: int = 0) -> List[Dict[str, Any]]:
        """Receive messages from SQS queue with detailed logging."""
        try:
            logger.info(f"Attempting to receive messages from queue: {self.queue_url}")
            
            # Use short polling for immediate response
            response = self.client.receive_message(
                QueueUrl=self.queue_url,
                MaxNumberOfMessages=min(max_messages, 10),
                WaitTimeSeconds=wait_time,  # 0 for immediate response
                MessageAttributeNames=['All'],
                AttributeNames=['All']
            )
            
            logger.info(f"SQS response received: {response.get('ResponseMetadata', {}).get('HTTPStatusCode', 'Unknown')}")
            
            messages = response.get('Messages', [])
            logger.info(f"Raw messages count: {len(messages)}")
            
            if not messages:
                logger.info("No messages available in queue")
                return []
            
            processed_messages = []
            
            for idx, message in enumerate(messages):
                logger.info(f"Processing message {idx + 1}/{len(messages)}")
                
                try:
                    # Get basic message info
                    receipt_handle = message.get('ReceiptHandle')
                    message_id = message.get('MessageId')
                    body = message.get('Body', '{}')
                    
                    logger.info(f"Message ID: {message_id}")
                    logger.info(f"Message body length: {len(body)}")
                    
                    # Parse message body
                    parsed_body = json.loads(body)
                    
                    # Check if this is an SNS message
                    if 'Message' in parsed_body and 'TopicArn' in parsed_body:
                        logger.info("Detected SNS message format")
                        try:
                            actual_message = json.loads(parsed_body['Message'])
                            message_source = 'SNS'
                        except json.JSONDecodeError:
                            logger.warning("Failed to parse SNS message content")
                            actual_message = parsed_body['Message']
                            message_source = 'SNS_RAW'
                    else:
                        logger.info("Detected direct SQS message format")
                        actual_message = parsed_body
                        message_source = 'SQS'
                    
                    processed_message = {
                        'receipt_handle': receipt_handle,
                        'message_id': message_id,
                        'content': actual_message,
                        'received_at': datetime.utcnow().isoformat(),
                        'source': message_source,
                        'raw_body': parsed_body,
                        'attributes': message.get('Attributes', {}),
                        'message_attributes': message.get('MessageAttributes', {})
                    }
                    
                    processed_messages.append(processed_message)
                    logger.info(f"Successfully processed message {idx + 1}")
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error for message {idx + 1}: {e}")
                    
                    # Create error message entry
                    error_message = {
                        'receipt_handle': message.get('ReceiptHandle'),
                        'message_id': message.get('MessageId'),
                        'content': {
                            'error': 'Failed to parse message',
                            'raw_body': body,
                            'parse_error': str(e)
                        },
                        'received_at': datetime.utcnow().isoformat(),
                        'source': 'ERROR',
                        'parse_error': str(e)
                    }
                    
                    processed_messages.append(error_message)
                    
                except Exception as e:
                    logger.error(f"Unexpected error processing message {idx + 1}: {e}")
                    continue
            
            logger.info(f"Successfully processed {len(processed_messages)} messages")
            return processed_messages
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', 'Unknown error')
            logger.error(f"AWS ClientError: {error_code} - {error_message}")
            raise AWSServiceError(f"Failed to receive messages: {error_message}")
        
        except Exception as e:
            logger.error(f"Unexpected error in receive_messages: {e}")
            raise AWSServiceError(f"Unexpected error: {str(e)}")
    
    def delete_message(self, receipt_handle: str) -> bool:
        """Delete message from queue."""
        try:
            self.client.delete_message(
                QueueUrl=self.queue_url,
                ReceiptHandle=receipt_handle
            )
            logger.info(f"Message deleted successfully")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete message: {e}")
            return False
    
    def get_queue_attributes(self) -> Dict[str, Any]:
        """Get queue attributes including message counts."""
        try:
            response = self.client.get_queue_attributes(
                QueueUrl=self.queue_url,
                AttributeNames=['All']
            )
            return response['Attributes']
        except ClientError as e:
            logger.error(f"Failed to get queue attributes: {e}")
            return {}
    
    def test_connection(self) -> bool:
        """Test connection to SQS queue."""
        try:
            self.get_queue_attributes()
            return True
        except:
            return False


class SNSSubscriptionManager:
    """Manages SNS subscriptions to SQS queues."""
    
    def __init__(self, region: str = 'ap-southeast-1'):
        self.region = region
        self._sns_client = None
        self._sqs_client = None
    
    @property
    def sns_client(self):
        if self._sns_client is None:
            self._sns_client = boto3.client('sns', region_name=self.region)
        return self._sns_client
    
    @property
    def sqs_client(self):
        if self._sqs_client is None:
            self._sqs_client = boto3.client('sqs', region_name=self.region)
        return self._sqs_client
    
    def setup_sqs_subscription(self, topic_arn: str, queue_url: str) -> bool:
        """Setup SNS subscription to SQS queue with proper permissions."""
        try:
            # Get queue ARN
            queue_attrs = self.sqs_client.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=['QueueArn']
            )
            queue_arn = queue_attrs['Attributes']['QueueArn']
            
            # Create subscription
            response = self.sns_client.subscribe(
                TopicArn=topic_arn,
                Protocol='sqs',
                Endpoint=queue_arn
            )
            
            subscription_arn = response['SubscriptionArn']
            
            # Set up SQS queue policy to allow SNS to send messages
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "sqs:SendMessage",
                        "Resource": queue_arn,
                        "Condition": {
                            "ArnEquals": {
                                "aws:SourceArn": topic_arn
                            }
                        }
                    }
                ]
            }
            
            self.sqs_client.set_queue_attributes(
                QueueUrl=queue_url,
                Attributes={
                    'Policy': json.dumps(policy)
                }
            )
            
            logger.info(f"Successfully subscribed queue {queue_url} to topic {topic_arn}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to setup subscription: {e}")
            return False
    
    def list_subscriptions(self, topic_arn: str) -> List[Dict]:
        """List all subscriptions for a topic."""
        try:
            response = self.sns_client.list_subscriptions_by_topic(TopicArn=topic_arn)
            return response['Subscriptions']
        except ClientError as e:
            logger.error(f"Failed to list subscriptions: {e}")
            return []


class AWSResourceManager:
    """Manages AWS resources and provides health checks."""
    
    def __init__(self, config):
        """Initialize resource manager."""
        self.config = config
        self.sns_publisher = SNSPublisher(config.topic_arn, config.region)
        self.sqs_consumers = {
            name: SQSConsumer(url, config.region)
            for name, url in config.queue_urls.items()
            if url
        }
        self.subscription_manager = SNSSubscriptionManager(config.region)
    
    def setup_subscriptions(self) -> Dict[str, bool]:
        """Setup SNS subscriptions for all SQS queues."""
        results = {}
        for name, url in self.config.queue_urls.items():
            if url:
                success = self.subscription_manager.setup_sqs_subscription(
                    self.config.topic_arn, url
                )
                results[name] = success
        return results
    
    def get_subscription_status(self) -> Dict[str, Any]:
        """Get current subscription status."""
        subscriptions = self.subscription_manager.list_subscriptions(self.config.topic_arn)
        
        status = {
            'total_subscriptions': len(subscriptions),
            'subscriptions': []
        }
        
        for sub in subscriptions:
            status['subscriptions'].append({
                'protocol': sub['Protocol'],
                'endpoint': sub['Endpoint'],
                'subscription_arn': sub['SubscriptionArn']
            })
        
        return status
    
    def health_check(self) -> Dict[str, bool]:
        """Perform health check on AWS resources."""
        health_status = {}
        
        # Check SNS topic
        try:
            self.sns_publisher.get_topic_attributes()
            health_status['sns_topic'] = True
        except Exception:
            health_status['sns_topic'] = False
        
        # Check SQS queues
        for name, consumer in self.sqs_consumers.items():
            try:
                consumer.get_queue_attributes()
                health_status[f'sqs_{name}'] = True
            except Exception:
                health_status[f'sqs_{name}'] = False
        
        # Check subscriptions
        try:
            subscriptions = self.subscription_manager.list_subscriptions(self.config.topic_arn)
            health_status['subscriptions'] = len(subscriptions) > 0
        except Exception:
            health_status['subscriptions'] = False
        
        return health_status