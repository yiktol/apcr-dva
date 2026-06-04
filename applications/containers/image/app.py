"""
Coffee Shop Order Management System

A Flask application for managing coffee orders through a web interface.
The app integrates with AWS services (SQS, DynamoDB) for order processing.
"""

import json
import logging
import os
import time
import uuid
from functools import wraps

import boto3
import requests
from flask import Flask, jsonify, redirect, render_template, request
from flask_cors import CORS
from jinja2 import Template

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Get environment variables with defaults
REGION = os.environ.get('REGION', 'ap-southeast-1')
PORT = int(os.environ.get('PORT', 8080))
QUEUE_ONE_URL = os.environ.get('QUEUE_ONE_URL')
QUEUE_TWO_URL = os.environ.get('QUEUE_TWO_URL')
TABLENAME = os.environ.get('TABLENAME', 'CoffeeshopTable-prod')

logger.info(f"Using AWS region: {REGION}")
logger.info(f"Using DynamoDB table: {TABLENAME}")
logger.info(f"Queue One URL: {QUEUE_ONE_URL}")
logger.info(f"Queue Two URL: {QUEUE_TWO_URL}")

# Initialize AWS clients with error handling
try:
    sqs = boto3.client("sqs", region_name=REGION)
    dynamodb = boto3.client('dynamodb', region_name=REGION)
    ssm = boto3.client('ssm', region_name=REGION)
    logger.info("AWS clients initialized successfully")
except Exception as e:
    logger.critical(f"Failed to initialize AWS clients: {str(e)}")
    raise

# Initialize Flask app
app = Flask(__name__, static_url_path='/', static_folder='static')
CORS(app)

# Error handling decorator
def error_handler(f):
    """Decorator to handle exceptions and provide appropriate responses."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}", exc_info=True)
            return render_template('error.html', error=str(e)), 500
    return decorated_function

def get_container_metadata():
    """
    Retrieves container metadata based on the environment.
    
    Returns:
        dict: Container metadata information
    """
    try:
        if 'ECS_CONTAINER_METADATA_FILE' in os.environ:
            logger.info("Getting container metadata from ECS_CONTAINER_METADATA_FILE")
            return ec2_container(os.environ['ECS_CONTAINER_METADATA_FILE'])
        elif 'ECS_CONTAINER_METADATA_URI_V4' in os.environ:
            logger.info("Getting container metadata from ECS_CONTAINER_METADATA_URI_V4")
            url = os.getenv('ECS_CONTAINER_METADATA_URI_V4')
            r = requests.get(f'{url}/task', timeout=3)
            r.raise_for_status()
            return fargate_container(r.json())
        else:
            logger.info("Running in local environment, no container metadata available")
            return {
                "LaunchType": 'Local',
                "ContainerId": 'N/A',
                "PublicIP": 'N/A',
                "PrivateIP": 'N/A',
                "AZ": 'N/A',
                "HostPort": 'N/A',
                "ContainerPort": 'N/A',
                "ClusterName": 'N/A',
                "TaskARN": 'N/A',
                "TaskDefinition": 'N/A'
            }
    except Exception as e:
        logger.error(f"Error retrieving container metadata: {str(e)}")
        return {
            "LaunchType": 'Error',
            "ContainerId": str(e),
            "PublicIP": 'N/A',
            "PrivateIP": 'N/A',
            "AZ": 'N/A'
        }

def ec2_container(file):
    """
    Parse EC2 container metadata from file.
    
    Args:
        file (str): Path to metadata file
        
    Returns:
        dict: Container metadata
    """
    try:
        with open(file, 'r') as f:
            metadata = f.read()
        metadata_json = json.loads(metadata)
        
        return {
            "LaunchType": "EC2",
            "ContainerId": metadata_json.get('ContainerID', 'N/A'),
            "PublicIP": metadata_json.get('HostPublicIPv4Address', 'N/A'),
            "PrivateIP": metadata_json.get('HostPrivateIPv4Address', 'N/A'),
            "AZ": metadata_json.get('AvailabilityZone', 'N/A'),
            "HostPort": metadata_json.get('PortMappings', [{}])[0].get('HostPort', 'N/A'),
            "ContainerPort": metadata_json.get('PortMappings', [{}])[0].get('ContainerPort', 'N/A'),
            "ClusterName": metadata_json.get('Cluster', 'N/A'),
            "TaskARN": metadata_json.get('TaskARN', 'N/A'),
            "TaskDefinition": metadata_json.get('TaskDefinitionFamily', 'N/A')
        }
    except Exception as e:
        logger.error(f"Error parsing EC2 container metadata: {str(e)}")
        raise

def fargate_container(metadata_json):
    """
    Parse Fargate container metadata from JSON.
    
    Args:
        metadata_json (dict): JSON metadata from Fargate
        
    Returns:
        dict: Container metadata
    """
    try:
        # Enhanced Fargate metadata extraction
        containers = metadata_json.get("Containers", [{}])
        container = containers[0] if containers else {}
        networks = container.get('Networks', [{}])
        network = networks[0] if networks else {}
        
        return {
            "LaunchType": metadata_json.get("LaunchType", "Fargate"),
            "ContainerId": container.get("DockerId", "N/A"),
            "PublicIP": metadata_json.get("PublicIPv4Address", "N/A"),
            "PrivateIP": network.get('IPv4Addresses', ["N/A"])[0],
            "AZ": metadata_json.get("AvailabilityZone", "N/A"),
            "ContainerPort": container.get("PortMappings", [{}])[0].get("ContainerPort", "N/A") if container.get("PortMappings") else "N/A",
            "HostPort": container.get("PortMappings", [{}])[0].get("HostPort", "N/A") if container.get("PortMappings") else "N/A",
            "ClusterName": metadata_json.get("Cluster", "N/A"),
            "TaskARN": metadata_json.get("TaskARN", "N/A"),
            "TaskDefinition": metadata_json.get("Family", "N/A"),
            "TaskRevision": metadata_json.get("Revision", "N/A"),
            "CPU": metadata_json.get("Limits", {}).get("CPU", "N/A"),
            "Memory": metadata_json.get("Limits", {}).get("Memory", "N/A")
        }
    except Exception as e:
        logger.error(f"Error parsing Fargate container metadata: {str(e)}")
        raise

def get_queue_attributes():
    """
    Retrieve SQS queue attributes and DynamoDB table count.
    
    Returns:
        dict: Queue and database statistics
    """
    try:
        # Use direct queue URLs from environment variables instead of looking them up
        queue_one_url = QUEUE_ONE_URL
        queue_two_url = QUEUE_TWO_URL
        
        # If environment variables aren't set, fallback to lookup method
        if not queue_one_url:
            logger.warning("QUEUE_ONE_URL not set, looking up by name")
            queue_one_url = sqs.get_queue_url(QueueName='QueueOne')['QueueUrl']
        
        if not queue_two_url:
            logger.warning("QUEUE_TWO_URL not set, looking up by name")
            queue_two_url = sqs.get_queue_url(QueueName='QueueTwo')['QueueUrl']
            
        # Get Queue One attributes
        q1_response = sqs.get_queue_attributes(
            QueueUrl=queue_one_url,
            AttributeNames=[
                'ApproximateNumberOfMessages',
                'ApproximateNumberOfMessagesNotVisible',
                'ApproximateNumberOfMessagesDelayed'
            ]
        )
        
        # Get Queue Two attributes
        q2_response = sqs.get_queue_attributes(
            QueueUrl=queue_two_url,
            AttributeNames=['ApproximateNumberOfMessagesNotVisible']
        )
        
        # Get DynamoDB table count using environment variable
        try:
            ddb_response = dynamodb.scan(TableName=TABLENAME, Select='COUNT')
            dynamo_items = ddb_response['Count']
            logger.info(f"Found {dynamo_items} items in table {TABLENAME}")
        except dynamodb.exceptions.ResourceNotFoundException:
            logger.warning(f"Table {TABLENAME} not found")
            dynamo_items = 0
        
        return {
            'pending': q1_response['Attributes']['ApproximateNumberOfMessages'],
            'processing': q1_response['Attributes']['ApproximateNumberOfMessagesNotVisible'],
            'delayed': q1_response['Attributes']['ApproximateNumberOfMessagesDelayed'],
            'delivering': q2_response['Attributes']['ApproximateNumberOfMessagesNotVisible'],
            'recorded': dynamo_items
        }
    except Exception as e:
        logger.error(f"Error getting queue attributes: {str(e)}")
        raise

@app.route('/index.html')
@app.route('/')
@error_handler
def index():
    """Render the index page."""
    logger.info("Serving index page")
    return render_template('index.html')

@app.route('/healthcheck')
@error_handler
def healthcheck():
    """
    Health check endpoint that displays container metadata.
    
    Returns:
        rendered template: Health check information
    """
    logger.info("Health check requested")
    data = get_container_metadata()
    # Add environment details
    data["TableName"] = TABLENAME
    data["Region"] = REGION
    return render_template('healthcheck.html', data=data)

@app.route('/orders', methods=['POST'])
@error_handler
def post_orders():
    """
    API endpoint to submit a new coffee order.
    
    Returns:
        str: JSON message with order details
    """
    logger.info("Processing new order submission")
    
    try:
        queue_url = QUEUE_ONE_URL
        if not queue_url:
            queue_url = sqs.get_queue_url(QueueName="QueueOne")["QueueUrl"]
            
        response = request.get_json()
        
        with open('coffee-record-template.json', 'r') as fh:
            tmpl = fh.read()

        tm = Template(tmpl)
        msg = tm.render(
            Customer=response["customer"], 
            SalesId=response["saleid"],
            Timestamp=response["timestamp"], 
            Coffee=response["coffee"],
            Milk=response["milk"], 
            Size=response["size"],
            Quantity=response["qty"]
        )

        logger.debug(f"Order message: {msg}")
        
        response = sqs.send_message(
            QueueUrl=queue_url, 
            DelaySeconds=10, 
            MessageAttributes=json.loads(msg), 
            MessageBody='Coffee Order'
        )
        
        logger.info(f"Order submitted successfully. MessageId: {response['MessageId']}")
        return msg
        
    except Exception as e:
        logger.error(f"Error posting order: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/orders', methods=['GET'])
@error_handler
def get_orders():
    """
    Display queue statistics and order counts.
    
    Returns:
        rendered template: Orders page with statistics
    """
    logger.info("Getting order statistics")
    try:
        stats = get_queue_attributes()
        logger.info(f"Queue statistics: {stats}")
        return render_template('orders.html', stats=stats)
    except Exception as e:
        logger.error(f"Error retrieving order statistics: {str(e)}")
        raise

@app.route('/dashboard', methods=['GET'])
@error_handler
def get_dashboard():
    """
    Redirect to external dashboard using SSM parameter.
    
    Returns:
        redirect: Redirect to dashboard URL
    """
    logger.info("Dashboard redirect requested")
    try:
        response = ssm.get_parameter(
            Name='/cpe/serverless/dashboard',
            WithDecryption=False
        )
        dashboard_url = response['Parameter']['Value']
        logger.info(f"Redirecting to dashboard: {dashboard_url}")
        return redirect(dashboard_url)
    except Exception as e:
        logger.error(f"Error retrieving dashboard URL: {str(e)}")
        raise

@app.route('/order', methods=['GET']) 
@error_handler
def order():
    """
    Display recent orders from DynamoDB.
    
    Returns:
        rendered template: Order page with recent orders
    """
    logger.info("Retrieving recent orders")
    try:
        orders = []
        # Use table name from environment variable
        response = dynamodb.scan(
            TableName=TABLENAME,
            Limit=10
        )
     
        for x in response['Items']:
            ddborder = {
                'salesid': x['SalesId']['S'],
                'name': x['Customer']['S'],
                'coffee': x['Coffee']['S'],
                'size': x['Size']['S'],
                'qty': x['Quantity']['S'],
                'milk': x['Milk']['S'],
                'timestamp': x['Timestamp']['S']
            }
            orders.append(ddborder)
            
        from operator import itemgetter
        sortedorders = sorted(orders, key=itemgetter('timestamp'), reverse=True)
        stats = get_queue_attributes()
        
        logger.info(f"Retrieved {len(orders)} recent orders")
        return render_template('order.html', orders=sortedorders, stats=stats)
    
    except Exception as e:
        logger.error(f"Error retrieving orders: {str(e)}")
        raise

@app.route('/read-form', methods=['POST'])
@error_handler
def read_form():
    """
    Process order form submission.
    
    Returns:
        redirect: Redirect to order page
    """
    logger.info("Processing form submission")
    try:
        saleid = str(uuid.uuid4())[24:]
        timestamp = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
        
        data = request.form
        logger.debug(f"Form data: {data}")
        
        order_data = {
            'saleid': saleid,
            'timestamp': timestamp,
            'customer': data['NAME'],
            'coffee': data['COFFEE'],
            'size': data['SIZE'],
            'milk': data['MILK'],
            'qty': data['QTY'],
        }
        
        # Use queue URL from environment variable
        queue_url = QUEUE_ONE_URL
        if not queue_url:
            queue_url = sqs.get_queue_url(QueueName="QueueOne")["QueueUrl"]
        
        with open('coffee-record-template.json', 'r') as fh:
            tmpl = fh.read()

        tm = Template(tmpl)
        msg = tm.render(
            Customer=order_data["customer"],
            SalesId=order_data["saleid"],
            Timestamp=order_data["timestamp"],
            Coffee=order_data["coffee"],
            Milk=order_data["milk"],
            Size=order_data["size"],
            Quantity=order_data["qty"]
        )

        logger.debug(f"Order message: {msg}")
        
        response = sqs.send_message(
            QueueUrl=queue_url,
            DelaySeconds=10,
            MessageAttributes=json.loads(msg),
            MessageBody='Coffee Order'
        )
        
        logger.info(f"Order form processed successfully. MessageId: {response['MessageId']}")
        return redirect('cicd/order')
    
    except Exception as e:
        logger.error(f"Error processing form submission: {str(e)}")
        raise

@app.route('/status', methods=['GET'])
@error_handler
def status():
    """
    API endpoint to get current order statistics.
    
    Returns:
        dict: JSON with order statistics
    """
    logger.info("Status API called")
    try:
        stats = get_queue_attributes()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error retrieving status: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/container-info', methods=['GET'])
@error_handler
def container_info_api():
    """
    API endpoint to get container metadata.
    
    Returns:
        dict: JSON with container metadata
    """
    logger.info("Container info API called")
    try:
        data = get_container_metadata()
        # Add environment configuration details
        data["TableName"] = TABLENAME
        data["Region"] = REGION
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error retrieving container info: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/environment', methods=['GET'])
@error_handler
def environment():
    """
    Display environment configuration information.
    
    Returns:
        rendered template: Environment information
    """
    logger.info("Environment info requested")
    env_info = {
        "Region": REGION,
        "TableName": TABLENAME,
        "QueueOneURL": QUEUE_ONE_URL,
        "QueueTwoURL": QUEUE_TWO_URL,
        "Port": PORT
    }
    return render_template('environment.html', env_info=env_info)

if __name__ == '__main__':
    logger.info(f"Starting Coffee Shop Order Management System on port {PORT}")
    app.run('0.0.0.0', PORT, debug=True)