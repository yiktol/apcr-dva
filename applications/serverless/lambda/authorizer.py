"""
Lambda authorizer for API Gateway.

This authorizer validates requests based on:
1. An authentication header (name and value configured via environment variables)
2. A stage variable (configured via environment variable)

Environment variables:
- AUTH_HEADER_NAME: Name of the header to check (default: 'HeaderAuth1')
- AUTH_HEADER_VALUE: Expected value of the auth header (default: 'headerValue1')
- STAGE: Expected value of the StageVar1 stage variable (default: 'stageValue1')
"""

import os
import json
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    Main handler for Lambda authorizer requests.
    
    Args:
        event (dict): The event data from API Gateway
        context (object): Lambda context object
        
    Returns:
        dict: Authorization policy document with context information
    """
    try:
        logger.info(f"Authorization request: {json.dumps(event)}")
        
        # Get environment variables with defaults
        auth_header_name = os.environ.get('AUTH_HEADER_NAME', 'HeaderAuth1')
        auth_header_value = os.environ.get('AUTH_HEADER_VALUE', 'headerValue1')
        required_stage = os.environ.get('STAGE', 'stageValue1')
        
        # Log configuration
        logger.info(f"Configuration: AUTH_HEADER_NAME={auth_header_name}, STAGE={required_stage}")
        
        # Extract request data
        headers = event.get('headers', {}) or {}
        stage_variables = event.get('requestContext', {}) or {}
        
        # Get the method ARN for policy generation
        method_arn = event.get('methodArn', '')
        if not method_arn:
            logger.error("Method ARN not found in event")
            return generate_deny('anonymous', '*')
            
        # Perform authorization checks
        header_valid = headers.get(auth_header_name) == auth_header_value
        stage_valid = stage_variables.get('stage') == required_stage
        
        logger.info(f"Authorization checks: header_valid={header_valid}, stage_valid={stage_valid}")
        
        if header_valid and stage_valid:
            logger.info(f"Request authorized for method ARN: {method_arn}")
            return generate_allow('user', method_arn)
        else:
            logger.warning(f"Request denied for method ARN: {method_arn}")
            return generate_deny('user', method_arn)
            
    except Exception as e:
        logger.error(f"Error during authorization: {str(e)}", exc_info=True)
        return generate_deny('anonymous', '*')


def generate_policy(principal_id, effect, resource):
    """
    Generate IAM policy document for API Gateway authorization.
    
    Args:
        principal_id (str): ID of the principal (user)
        effect (str): 'Allow' or 'Deny'
        resource (str): AWS resource ARN
        
    Returns:
        dict: Policy document with context
    """
    policy = {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': effect,
                'Resource': resource
            }]
        },
        'context': {
            'isAuthorized': effect.lower() == 'allow'
        }
    }
    
    logger.debug(f"Generated policy: {json.dumps(policy)}")
    return policy


def generate_allow(principal_id, resource):
    """Generate an Allow policy."""
    return generate_policy(principal_id, 'Allow', resource)


def generate_deny(principal_id, resource):
    """Generate a Deny policy."""
    return generate_policy(principal_id, 'Deny', resource)
