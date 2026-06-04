
"""
SNS to DynamoDB Message Processor Lambda Function

This Lambda function processes messages from SNS notifications and stores
coffee order data in a DynamoDB table.
"""

import boto3
import os
import json
import logging
import traceback
from typing import Dict, Any
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get environment variables
TABLE_NAME = os.environ.get("TABLE_NAME")

# Validate required environment variables
if not TABLE_NAME:
    logger.error("Missing required environment variable: TableName")
    # Still initialize the table reference to avoid errors in cold starts
    # It will fail later with a clearer error if the variable is missing
    TABLE_NAME = "undefined"

# Initialize AWS clients/resources outside handler for better cold start performance
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)


def put_item_to_dynamodb(order_data: Dict[str, str]) -> Dict[str, Any]:
    """
    Store a coffee order in the DynamoDB table.
    
    Args:
        order_data (dict): Coffee order details to store
        
    Returns:
        dict: DynamoDB response
        
    Raises:
        KeyError: If required fields are missing
        ClientError: If DynamoDB operation fails
    """
    # Validate required fields
    required_fields = ["SalesId", "Customer", "Size", "Quantity", "Coffee", "Timestamp", "Milk"]
    missing_fields = [field for field in required_fields if field not in order_data]
    
    if missing_fields:
        error_msg = f"Missing required fields in order data: {', '.join(missing_fields)}"
        logger.error(error_msg)
        raise KeyError(error_msg)
    
    # Log the item being inserted (excluding potentially sensitive customer data)
    log_data = {k: v for k, v in order_data.items() if k != "Customer"}
    logger.info(f"Storing order in DynamoDB with SalesId: {order_data.get('SalesId')}")
    logger.debug(f"Order details: {json.dumps(log_data)}")
    
    try:
        # Insert the item into DynamoDB
        response = table.put_item(
            Item={
                "SalesId": order_data["SalesId"],
                "Customer": order_data["Customer"],
                "Size": order_data["Size"],
                "Quantity": order_data["Quantity"],
                "Coffee": order_data["Coffee"],
                "Timestamp": order_data["Timestamp"],
                "Milk": order_data["Milk"]
            }
        )
        
        # Log success
        logger.info(f"Successfully stored order {order_data.get('SalesId')} in DynamoDB")
        logger.debug(f"DynamoDB response: {json.dumps(response)}")
        
        return response
        
    except ClientError as e:
        logger.error(f"DynamoDB error: {str(e)}")
        logger.debug(traceback.format_exc())
        raise
    except Exception as e:
        logger.error(f"Unexpected error storing item: {str(e)}")
        logger.debug(traceback.format_exc())
        raise


def parse_sns_message(event: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract and parse the message from the SNS event.
    
    Args:
        event (dict): Lambda event containing SNS records
        
    Returns:
        dict: Parsed coffee order data
        
    Raises:
        ValueError: If message parsing fails
        KeyError: If required event structure is missing
    """
    try:
        # Extract SNS message
        record = event.get("Records", [{}])[0]
        sns_data = record.get("Sns", {})
        message_str = sns_data.get("Message")
        
        if not message_str:
            raise KeyError("No message found in SNS event")
        
        # Parse the message as JSON
        message = json.loads(message_str)
        
        # Log the received message (excluding potentially sensitive data)
        log_data = {k: v for k, v in message.items() if k != "Customer"}
        logger.info(f"Received SNS message with SalesId: {message.get('SalesId')}")
        logger.debug(f"Message contents: {json.dumps(log_data)}")
        
        return message
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse SNS message as JSON: {str(e)}")
        logger.debug(f"Raw message content: {message_str if 'message_str' in locals() else 'undefined'}")
        raise ValueError(f"Invalid JSON in SNS message: {str(e)}")
    except KeyError as e:
        logger.error(f"Missing expected field in event structure: {str(e)}")
        logger.debug(f"Event structure: {json.dumps(event)}")
        raise
    except Exception as e:
        logger.error(f"Error extracting SNS message: {str(e)}")
        logger.debug(traceback.format_exc())
        raise


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler function that processes SNS events and stores coffee orders in DynamoDB.
    
    Args:
        event (dict): The Lambda event containing SNS records
        context (LambdaContext): Lambda context object
        
    Returns:
        dict: Response with processing status
    """
    try:
        logger.info(f"Processing SNS notification event")
        logger.debug(f"Event: {json.dumps(event)}")
        
        # Extract message from SNS
        order_data = parse_sns_message(event)
        
        # Store the order in DynamoDB
        put_item_to_dynamodb(order_data)
        
        return {
            "statusCode": 200,
            "message": "Order processed successfully",
            "salesId": order_data.get("SalesId")
        }
        
    except KeyError as e:
        logger.error(f"Data structure error: {str(e)}")
        return {
            "statusCode": 400,
            "message": f"Bad request: {str(e)}"
        }
    except ValueError as e:
        logger.error(f"Value error: {str(e)}")
        return {
            "statusCode": 400,
            "message": f"Bad request: {str(e)}"
        }
    except ClientError as e:
        logger.error(f"DynamoDB error: {str(e)}")
        return {
            "statusCode": 500,
            "message": f"Database error: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.debug(traceback.format_exc())
        return {
            "statusCode": 500,
            "message": f"Internal server error: {str(e)}"
        }
