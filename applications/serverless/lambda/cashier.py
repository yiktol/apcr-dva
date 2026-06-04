
import boto3
import json
import logging
import os
from typing import Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize SQS client
session = boto3.session.Session()
sqs = session.client("sqs")

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler that receives API Gateway events and forwards them to an SQS queue.
    
    This function processes POST requests containing coffee order details,
    formats them as SQS message attributes, and sends them to the specified queue.
    
    Args:
        event: API Gateway event dictionary containing the HTTP request details
        context: Lambda context object
        
    Returns:
        Dict containing HTTP status code, response body, and headers
    
    Environment Variables:
        QUEUEONE_URL: The URL of the SQS queue to send messages to
    """
    try:
        # Get queue URL from environment variable
        queue_url = os.environ.get('QUEUE_URL')
        if not queue_url:
            logger.warning("QUEUEONE_URL environment variable not set. Attempting to get URL from queue name.")
            try:
                queue_name = os.environ.get('QUEUE_NAME', 'OrderProcessingQueue')
                queue_url = sqs.get_queue_url(QueueName=queue_name)['QueueUrl']
                logger.info(f"Retrieved queue URL: {queue_url}")
            except Exception as e:
                logger.error(f"Failed to get queue URL: {str(e)}")
                return build_response(500, "Failed to get queue URL")
        
        # Log the incoming event body
        logger.info(f"Received event: {event}")
        
        # Validate HTTP method is POST
        if event.get('httpMethod') != 'POST':
            logger.warning(f"Unsupported HTTP method: {event.get('httpMethod')}")
            return build_response(405, "Method Not Allowed")
        
        # Parse the request body
        try:
            if not event.get('body'):
                logger.error("Request body is empty")
                return build_response(400, "Request body is missing")
                
            request_data = json.loads(event['body'])
            logger.debug(f"Parsed request data: {request_data}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON body: {str(e)}")
            return build_response(400, "Invalid JSON in request body")
        
        # Extract and validate order details
        try:
            order = {
                "Customer": request_data["customer"],
                "SalesId": request_data["saleid"],
                "Timestamp": str(request_data["timestamp"]),
                "Coffee": request_data["coffee"],
                "Milk": request_data["milk"],
                "Size": request_data["size"],
                "Quantity": str(request_data["qty"])
            }
        except KeyError as e:
            logger.error(f"Missing required field in request: {str(e)}")
            return build_response(400, f"Missing required field: {str(e)}")
        
        # Format message attributes
        message_attributes = format_message_attributes(order)
        logger.info(f"Prepared message attributes: {message_attributes}")
        
        # Send message to SQS queue
        try:
            response = sqs.send_message(
                QueueUrl=queue_url, 
                DelaySeconds=10, 
                MessageAttributes=message_attributes, 
                MessageBody='Coffee Order'
            )
            logger.info(f"Message sent successfully. MessageId: {response.get('MessageId')}")
            return build_response(200, f"Order received. MessageId: {response.get('MessageId')}")
        except Exception as e:
            logger.error(f"Failed to send message to SQS: {str(e)}")
            return build_response(500, f"Failed to process order")
            
    except Exception as e:
        logger.error(f"Unhandled error in Lambda function: {str(e)}", exc_info=True)
        return build_response(500, "Internal server error")

def format_message_attributes(order: Dict[str, str]) -> Dict[str, Dict[str, str]]:
    """
    Formats order details as SQS message attributes.
    
    Args:
        order: Dictionary containing order details
        
    Returns:
        Dictionary formatted as SQS message attributes
    """
    attributes = {}
    
    # Format string attributes
    for key in ["Customer", "SalesId", "Timestamp", "Coffee", "Milk", "Size"]:
        if order[key] is None:
            # Provide default values for None attributes
            default_values = {
                "Customer": "Anonymous",
                "Coffee": "Regular",
                "Milk": "None",
                "Size": "Medium"
            }
            value = default_values.get(key, "")
        else:
            value = order[key]
        
        attributes[key] = {
            "DataType": "String",
            "StringValue": value
        }

    # Format numeric attribute
    attributes["Quantity"] = {
        "DataType": "Number",
        "StringValue": order["Quantity"]
    }
    
    return attributes

def build_response(status_code: int, body: str) -> Dict[str, Any]:
    """
    Builds a standardized API Gateway response.
    
    Args:
        status_code: HTTP status code
        body: Response body content
        
    Returns:
        Dictionary formatted as an API Gateway response
    """
    return {
        "statusCode": status_code,
        "body": json.dumps({"message": body}) if isinstance(body, str) else json.dumps(body),
        "headers": {
            "Content-Type": "application/json"}
    }
