import json
import boto3
import os
import logging
from typing import Dict, Any

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda function handler with proxy integration support
    """
    session = boto3.session.Session()
    sqs = session.client("sqs")
    dynamodb = session.client('dynamodb')

    queueone_url = os.environ['PROCESSING_QUEUE_URL']
    queuetwo_url = os.environ['DELIVERY_QUEUE_URL']
    table_name = os.environ.get('TABLE_NAME', 'Coffeeshop')

    # CORS headers for cross-origin requests
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,OPTIONS'
    }

    try:
        # Handle preflight OPTIONS request
        if event.get('httpMethod') == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'CORS preflight successful'})
            }

        # Only allow GET requests for monitoring
        if event.get('httpMethod') != 'GET':
            return {
                'statusCode': 405,
                'headers': headers,
                'body': json.dumps({
                    'error': 'Method not allowed',
                    'message': 'Only GET requests are supported'
                })
            }

        data = {}
        
        # Get Queue One metrics
        q1_response = sqs.get_queue_attributes(
            QueueUrl=queueone_url,
            AttributeNames=[
                'ApproximateNumberOfMessages',
                'ApproximateNumberOfMessagesNotVisible',
                'ApproximateNumberOfMessagesDelayed'
            ]
        )
        
        # Extract and store metrics directly
        data["Queue1_MessagesInQueue"] = int(q1_response['Attributes']['ApproximateNumberOfMessages'])
        data["Queue1_MessagesInFlight"] = int(q1_response['Attributes']['ApproximateNumberOfMessagesNotVisible'])
        data["Queue1_MessagesDelayed"] = int(q1_response['Attributes']['ApproximateNumberOfMessagesDelayed'])
        
        # Get Queue Two metrics
        q2_response = sqs.get_queue_attributes(
            QueueUrl=queuetwo_url,
            AttributeNames=['ApproximateNumberOfMessagesNotVisible']
        )
        
        data["Queue2_MessagesInFlight"] = int(q2_response['Attributes']['ApproximateNumberOfMessagesNotVisible'])
        
        # Get DynamoDB count
        dynamo_response = dynamodb.scan(
            TableName=table_name,
            Select='COUNT'
        )
        
        data["OrdersInDatabase"] = dynamo_response['Count']
        
        # Add timestamp and metadata
        from datetime import datetime
        data["timestamp"] = datetime.utcnow().isoformat() + 'Z'
        data["status"] = "success"
        
        # Log important metrics using logging library
        logger.info(f"New orders entering system: {data['Queue1_MessagesInQueue']}")
        logger.info(f"Orders being processed: {data['Queue1_MessagesInFlight']}")
        logger.info(f"Orders ready for delivery: {data['Queue1_MessagesDelayed']}")
        logger.info(f"Orders recorded in database: {data['OrdersInDatabase']}")
        logger.info(f"Orders entering second queue: {data['Queue2_MessagesInFlight']}")
        
        # Return successful proxy response
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps(data, indent=2)
        }
        
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error monitoring orders: {error_message}")
        
        # Return error response in proxy format
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({
                "error": error_message,
                "status": "failed",
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }, indent=2)
        }