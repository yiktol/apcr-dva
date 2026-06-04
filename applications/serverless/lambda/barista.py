"""
SQS to SNS Message Forwarding Lambda Function

This Lambda function processes SQS messages and forwards their contents to an SNS topic.
It extracts coffee order details from SQS message attributes and publishes them to SNS.
"""

import boto3
import os
import json
import logging
import traceback
from typing import Dict, Any, List

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients/resources outside handler for better cold start performance
sqs_resource = boto3.resource('sqs')
sns_client = boto3.client('sns')

# Get environment variables
QUEUE_URL = os.environ.get('QUEUE_URL')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC')

# Validate required environment variables
if not QUEUE_URL:
    logger.error("Missing required environment variable: QueueURL")
if not SNS_TOPIC_ARN:
    logger.error("Missing required environment variable: SNSTopic")


def publish_to_sns(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract message attributes from SQS message and publish to SNS topic.
    
    Args:
        message (dict): The SQS message containing coffee order details
        
    Returns:
        dict: The extracted message payload sent to SNS
        
    Raises:
        KeyError: If required message attributes are missing
        Exception: For other errors in processing or publishing
    """
    try:
        # Get message attributes
        message_attributes = message.get("messageAttributes", {})
        
        # Check if all required attributes exist
        required_attributes = ["SalesId", "Customer", "Size", "Quantity", 
                             "Coffee", "Timestamp", "Milk"]
        
        for attr in required_attributes:
            if attr not in message_attributes or "stringValue" not in message_attributes[attr]:
                raise KeyError(f"Missing required attribute: {attr}")
        
        # Extract coffee order details from message attributes
        payload = {
            'SalesId': message_attributes["SalesId"]["stringValue"],
            'Customer': message_attributes["Customer"]["stringValue"],
            'Size': message_attributes["Size"]["stringValue"],
            'Quantity': message_attributes["Quantity"]["stringValue"],
            'Coffee': message_attributes["Coffee"]["stringValue"],
            'Timestamp': message_attributes["Timestamp"]["stringValue"],
            'Milk': message_attributes["Milk"]["stringValue"]
        }
        
        logger.info(f"Publishing message to SNS: {json.dumps(payload)}")
        
        # Publish message to SNS topic
        response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=json.dumps(payload)
        )
        
        logger.info(f"Successfully published to SNS, message ID: {response.get('MessageId')}")
        logger.debug(f"Full SNS response: {json.dumps(response)}")
        
        return payload
        
    except KeyError as e:
        logger.error(f"Missing required attribute in message: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error publishing to SNS: {str(e)}")
        logger.debug(traceback.format_exc())
        raise


def process_message(message: Dict[str, Any]) -> bool:
    """
    Process a single SQS message.
    
    Args:
        message (dict): SQS message to process
        
    Returns:
        bool: True if message was successfully processed and deleted, False otherwise
    """
    receipt_handle = message.get('receiptHandle')
    
    if not receipt_handle:
        logger.error("Missing receiptHandle in SQS message")
        return False
    
    try:
        # Extract message body for logging (limited to avoid excessive logging)
        message_body_preview = str(message.get('body', ''))[:100]
        if len(message_body_preview) == 100:
            message_body_preview += "..."
            
        logger.info(f"Processing message: {message_body_preview}")
        
        # Publish message to SNS
        published_payload = publish_to_sns(message)
        
        # Delete message from SQS queue
        sqs_message = sqs_resource.Message(QUEUE_URL, receipt_handle)
        sqs_message.delete()
        logger.info(f"Successfully deleted message from SQS, SalesId: {published_payload.get('SalesId')}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to process message: {str(e)}")
        logger.debug(traceback.format_exc())
        return False


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler function for processing SQS messages and forwarding to SNS.
    
    Args:
        event (dict): The Lambda event containing SQS records
        context (LambdaContext): Lambda context object
        
    Returns:
        dict: Response with processing results
    """
    logger.info(f"Starting processing of {len(event.get('Records', []))} SQS messages")
    
    if not event.get('Records'):
        logger.warning("No records found in the event")
        return {"statusCode": 200, "message": "No records to process"}
    
    results = {
        "processed": 0,
        "failed": 0
    }
    
    for record in event['Records']:
        try:
            if process_message(record):
                results["processed"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            logger.error(f"Unhandled exception while processing message: {str(e)}")
            logger.debug(traceback.format_exc())
            results["failed"] += 1
            
    logger.info(f"Processing complete. Results: {json.dumps(results)}")
    
    # Return processing summary
    return {
        "statusCode": 200 if results["failed"] == 0 else 207,  # 207 if partial success
        "message": "Message processing completed",
        "results": results
    }
