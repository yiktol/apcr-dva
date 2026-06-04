import boto3
import logging
from botocore.exceptions import ClientError
import os

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Environment Variables
REGION = os.environ.get('AWS_REGION', 'ap-southeast-1')
QUEUE_ONE_URL = os.environ.get('QUEUE_ONE_URL')
QUEUE_TWO_URL = os.environ.get('QUEUE_TWO_URL')
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE')

# Initialize AWS clients
sqs = boto3.client("sqs", region_name=REGION)
dynamodb = boto3.client('dynamodb', region_name=REGION)

def get_queue_attributes(queue_url, attributes):
    """
    Get attributes for an SQS queue using its URL.
    
    Args:
        queue_url (str): The URL of the SQS queue
        attributes (list): List of attribute names to retrieve
        
    Returns:
        dict: The queue attributes
    """
    try:
        logger.debug(f"Getting attributes {attributes} for queue URL: {queue_url}")
        response = sqs.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=attributes
        )
        return response['Attributes']
    except ClientError as e:
        logger.error(f"Error getting attributes for queue {queue_url}: {str(e)}")
        raise

def get_orders():
    """
    Get the current status of orders in the coffee shop system.
    
    This function collects metrics from two SQS queues and a DynamoDB table
    to provide a complete picture of order processing status:
    - New orders entering the system
    - Orders being processed
    - Orders ready for delivery
    - Orders stored in the database
    
    The function uses environment variables for queue URLs and table name:
    - QUEUE_ONE_URL: URL of the first order processing queue
    - QUEUE_TWO_URL: URL of the second order processing queue
    - DYNAMODB_TABLE: Name of the orders database table
    
    Returns:
        dict: A dictionary containing order processing metrics
    """
    try:
        logger.info("Retrieving order processing status")
        
        # Validate environment variables
        if not QUEUE_ONE_URL or not QUEUE_TWO_URL or not DYNAMODB_TABLE:
            missing_vars = []
            if not QUEUE_ONE_URL: missing_vars.append("QUEUE_ONE_URL")
            if not QUEUE_TWO_URL: missing_vars.append("QUEUE_TWO_URL")
            if not DYNAMODB_TABLE: missing_vars.append("DYNAMODB_TABLE")
            error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        # Get Queue One attributes (order processing queue)
        queue_one_attrs = get_queue_attributes(
            QUEUE_ONE_URL,
            [
                'ApproximateNumberOfMessages',
                'ApproximateNumberOfMessagesNotVisible',
                'ApproximateNumberOfMessagesDelayed'
            ]
        )
        
        # Get Queue Two attributes (completed orders queue)
        queue_two_attrs = get_queue_attributes(
            QUEUE_TWO_URL,
            ['ApproximateNumberOfMessagesNotVisible']
        )
        
        # Get DynamoDB table count
        db_response = dynamodb.scan(
            TableName=DYNAMODB_TABLE,
            Select='COUNT'
        )
        
        # Extract metrics
        new_orders = queue_one_attrs['ApproximateNumberOfMessages']
        processing_orders = queue_one_attrs['ApproximateNumberOfMessagesNotVisible']
        delivery_ready_orders = queue_one_attrs['ApproximateNumberOfMessagesDelayed']
        queue_two_processing = queue_two_attrs['ApproximateNumberOfMessagesNotVisible']
        total_db_orders = db_response['Count']
        
        # Log the metrics
        logger.info(f"New orders waiting to be processed: {new_orders}")
        logger.info(f"Orders currently being fulfilled: {processing_orders}")
        logger.info(f"Orders ready for delivery to customer: {delivery_ready_orders}")
        logger.info(f"Orders in second queue processing: {queue_two_processing}")
        logger.info(f"Total orders recorded in database: {total_db_orders}")
        
        # Prepare and return status
        status = {
            "NewOrders": int(new_orders),
            "ProcessingOrders": int(processing_orders),
            "DeliveryReadyOrders": int(delivery_ready_orders),
            "SecondaryQueueOrders": int(queue_two_processing),
            "DatabaseOrderCount": total_db_orders
        }
        
        # For backward compatibility
        status.update({
            "ApproximateNumberOfMessagesNotVisible": processing_orders,
            "ApproximateNumberOfMessagesDelayed": delivery_ready_orders,
            "ApproximateNumberOfMessages": queue_two_processing,
            "dynamoItems": total_db_orders
        })
        
        logger.info("Successfully retrieved order status information")
        return status
        
    except Exception as e:
        logger.error(f"Error retrieving order status: {str(e)}")
        raise
