"""
SQS Message Processor Lambda Function

This Lambda function processes messages from an SQS queue and deletes them after processing.
It serves as a basic SQS message consumer.
"""

import boto3
import os
import json
import logging
import traceback
from typing import Dict, Any, List
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get environment variables
QUEUE_URL = os.environ.get('QUEUE_URL')

# Validate required environment variables
if not QUEUE_URL:
    logger.error("Missing required environment variable: QueueURL")

# Initialize AWS clients/resources outside handler for better cold start performance
sqs_resource = boto3.resource('sqs')


def delete_message(queue_url: str, receipt_handle: str) -> bool:
    """
    Delete a message from an SQS queue.
    
    Args:
        queue_url (str): The URL of the SQS queue
        receipt_handle (str): The receipt handle of the message to delete
        
    Returns:
        bool: True if message was successfully deleted, False otherwise
        
    Raises:
        ClientError: If the SQS delete operation fails
    """
    try:
        # Create message object
        message = sqs_resource.Message(queue_url, receipt_handle)
        
        # Delete message from queue
        message.delete()
        logger.info(f"Successfully deleted message with receipt handle: {receipt_handle[:10]}...")
        return True
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_message = e.response.get('Error', {}).get('Message', 'Unknown error')
        logger.error(f"Failed to delete message: {error_code} - {error_message}")
        logger.debug(f"Full error: {e}")
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error deleting message: {str(e)}")
        logger.debug(traceback.format_exc())
        raise


def process_message(message: Dict[str, Any]) -> bool:
    """
    Process a single SQS message.
    
    Currently, this function only deletes the message. Extend this function
    to implement actual message processing logic.
    
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
        # Log message details (safely handling potentially large messages)
        message_id = message.get('messageId', 'unknown')
        body_preview = str(message.get('body', ''))[:100]
        if len(body_preview) == 100:
            body_preview += "..."
            
        logger.info(f"Processing message {message_id}")
        logger.debug(f"Message body preview: {body_preview}")
        
        # Here you would typically process the message contents
        # For now, we're just deleting the message
        
        # Delete message from SQS queue
        delete_message(QUEUE_URL, receipt_handle)
        return True
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        logger.debug(traceback.format_exc())
        return False


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler function for processing and deleting SQS messages.
    
    Args:
        event (dict): The Lambda event containing SQS records
        context (LambdaContext): Lambda context object
        
    Returns:
        dict: Response with processing results
    """
    # Validate queue URL is configured
    if not QUEUE_URL:
        error_msg = "Cannot process messages: QueueURL environment variable not set"
        logger.error(error_msg)
        return {
            "statusCode": 500,
            "message": error_msg
        }
    
    # Get records from event
    records = event.get('Records', [])
    record_count = len(records)
    
    logger.info(f"Starting to process {record_count} SQS messages")
    
    if record_count == 0:
        logger.warning("No records found in the event")
        return {"statusCode": 200, "message": "No records to process"}
    
    # Track processing results
    results = {
        "processed": 0,
        "failed": 0,
        "message_ids": []
    }
    
    # Process each message
    for record in records:
        try:
            message_id = record.get('messageId', 'unknown')
            results["message_ids"].append(message_id)
            
            if process_message(record):
                results["processed"] += 1
            else:
                results["failed"] += 1
                
        except Exception as e:
            logger.error(f"Unhandled exception while processing message: {str(e)}")
            logger.debug(traceback.format_exc())
            results["failed"] += 1
    
    # Log summary of processing
    success_rate = (results["processed"] / record_count) * 100 if record_count > 0 else 0
    logger.info(f"Processing complete. Successfully processed {results['processed']}/{record_count} messages ({success_rate:.1f}%)")
    
    if results["failed"] > 0:
        logger.warning(f"Failed to process {results['failed']} messages")
    
    # Return processing summary
    return {
        "statusCode": 200 if results["failed"] == 0 else 207,  # 207 if partial success
        "message": "Message processing completed",
        "results": results
    }
