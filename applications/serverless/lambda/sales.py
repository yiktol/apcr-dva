import json
import boto3
import os
from operator import itemgetter
import logging
from botocore.exceptions import ClientError
from decimal import Decimal

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize DynamoDB client globally for reuse across invocations
dynamodb = boto3.client('dynamodb')
TABLE_NAME = os.environ['TABLE_NAME']
MAX_ITEMS = 50

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)

def create_response(status_code, body, error=False):
    """
    Create a properly formatted API Gateway Lambda proxy response
    
    Args:
        status_code: HTTP status code
        body: Response body (dict or list)
        error: Boolean indicating if this is an error response
        
    Returns:
        dict: Formatted proxy integration response
    """
    response = {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',  # Configure as needed for CORS
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,OPTIONS'
        }
    }
    
    if error:
        response['body'] = json.dumps({'error': body}, cls=DecimalEncoder)
    else:
        response['body'] = json.dumps(body, cls=DecimalEncoder)
    
    return response

def handler(event, context):
    """
    Retrieve and return the most recent coffee orders
    Lambda proxy integration handler
    
    Args:
        event: Lambda event object from API Gateway
        context: Lambda context object
        
    Returns:
        dict: API Gateway Lambda proxy response
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Handle OPTIONS request for CORS
    if event.get('httpMethod') == 'OPTIONS':
        return create_response(200, {'message': 'OK'})
    
    # Parse query parameters if needed (for future enhancements)
    query_params = event.get('queryStringParameters') or {}
    limit = int(query_params.get('limit', MAX_ITEMS))
    
    # Ensure limit is within reasonable bounds
    limit = min(limit, MAX_ITEMS)
    
    try:
        logger.info(f"Retrieving recent coffee orders with limit: {limit}")
        
        # Query only necessary attributes to improve performance
        response = dynamodb.scan(
            TableName=TABLE_NAME,
            Limit=limit,
            ProjectionExpression="SalesId, Customer, Coffee, Size, Quantity, Milk, #ts",
            ExpressionAttributeNames={"#ts": "Timestamp"}
        )
        
        logger.info(f"Retrieved {len(response.get('Items', []))} orders from DynamoDB")
        
        # Process results more efficiently
        orders = []
        for item in response.get('Items', []):
            try:
                orders.append({
                    'salesid': item.get('SalesId', {}).get('S', ''),
                    'customer': item.get('Customer', {}).get('S', ''),
                    'coffee': item.get('Coffee', {}).get('S', ''),
                    'size': item.get('Size', {}).get('S', ''),
                    'qty': item.get('Quantity', {}).get('S', ''),
                    'milk': item.get('Milk', {}).get('S', ''),
                    'timestamp': item.get('Timestamp', {}).get('S', '')
                })
            except KeyError as e:
                logger.warning(f"Missing field in order: {e}")
                continue
        
        # Sort by timestamp, most recent first
        sorted_orders = sorted(orders, key=itemgetter('timestamp'), reverse=True)
        
        # Prepare successful response
        response_body = {
            'success': True,
            'count': len(sorted_orders),
            'orders': sorted_orders
        }
        
        logger.info(f"Returning {len(sorted_orders)} sorted orders")
        return create_response(200, response_body)
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = f"DynamoDB error: {error_code} - {e.response['Error']['Message']}"
        logger.error(error_msg)
        
        # Return appropriate HTTP status based on DynamoDB error
        if error_code == 'ResourceNotFoundException':
            return create_response(404, f"Table {TABLE_NAME} not found", error=True)
        elif error_code == 'ValidationException':
            return create_response(400, "Invalid request parameters", error=True)
        elif error_code == 'ProvisionedThroughputExceededException':
            return create_response(429, "Too many requests, please try again later", error=True)
        else:
            return create_response(500, "Internal server error", error=True)
            
    except ValueError as e:
        error_msg = f"Invalid parameter value: {str(e)}"
        logger.error(error_msg)
        return create_response(400, error_msg, error=True)
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return create_response(500, "Internal server error", error=True)