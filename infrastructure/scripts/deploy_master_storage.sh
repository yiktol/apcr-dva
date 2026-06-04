#!/bin/bash

# Enable strict error handling
set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
export Bucket='yikyakyuk-ap-southeast-1-875692608981'
export Prefix='infrastructure/cloudformation'
export BucketRegion='ap-southeast-1'
STACK_NAME='saa-storage'
REGION='ap-southeast-1'

# Determine the correct template directory based on where script is run from
if [ -d "infrastructure/cloudformation" ]; then
    TEMPLATE_DIR='infrastructure/cloudformation'
elif [ -d "cloudformation" ]; then
    TEMPLATE_DIR='cloudformation'
else
    echo "ERROR: Cannot find cloudformation template directory"
    exit 1
fi

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}"
}

# Function to check if AWS CLI is configured
check_aws_config() {
    print_status $BLUE "Checking AWS CLI configuration..."
    if ! aws sts get-caller-identity --region $REGION >/dev/null 2>&1; then
        print_status $RED "ERROR: AWS CLI not configured or no valid credentials"
        exit 1
    fi
    local identity=$(aws sts get-caller-identity --region $REGION --output text --query 'Account')
    print_status $GREEN "AWS CLI configured. Account ID: $identity"
}

# Function to check if bucket exists and is accessible
check_bucket() {
    print_status $BLUE "Checking if S3 bucket exists and is accessible..."
    if ! aws s3 ls "s3://$Bucket" --region $BucketRegion >/dev/null 2>&1; then
        print_status $RED "ERROR: Cannot access bucket s3://$Bucket"
        exit 1
    fi
    print_status $GREEN "S3 bucket is accessible"
}

# Function to upload templates
upload_templates() {
    print_status $BLUE "Uploading templates to S3..."
    
    if [ ! -d "$TEMPLATE_DIR" ]; then
        print_status $RED "ERROR: Template directory $TEMPLATE_DIR does not exist"
        exit 1
    fi
    
    print_status $YELLOW "Source: $TEMPLATE_DIR"
    print_status $YELLOW "Destination: s3://$Bucket/$Prefix"
    
    # Upload with verbose output
    aws s3 cp "$TEMPLATE_DIR" "s3://$Bucket/$Prefix" --recursive --region $BucketRegion
    
    if [ $? -eq 0 ]; then
        print_status $GREEN "Templates uploaded successfully"
    else
        print_status $RED "ERROR: Failed to upload templates"
        exit 1
    fi
}

# Function to check if master_storage.yaml exists in S3
verify_master_template() {
    print_status $BLUE "Verifying master_storage template exists in S3..."
    local template_url="https://$Bucket.s3-$BucketRegion.amazonaws.com/$Prefix/master_storage.yaml"
    
    if aws s3 ls "s3://$Bucket/$Prefix/master_storage.yaml" --region $BucketRegion >/dev/null 2>&1; then
        print_status $GREEN "Master template verified at: $template_url"
    else
        print_status $RED "ERROR: master_storage.yaml not found in S3"
        exit 1
    fi
}

# Function to check if stack already exists
check_existing_stack() {
    print_status $BLUE "Checking if stack '$STACK_NAME' already exists..."
    
    local stack_status=$(aws cloudformation describe-stacks \
        --region $REGION \
        --stack-name $STACK_NAME \
        --query 'Stacks[0].StackStatus' \
        --output text 2>/dev/null || echo "DOES_NOT_EXIST")
    
    if [ "$stack_status" != "DOES_NOT_EXIST" ]; then
        print_status $YELLOW "Stack '$STACK_NAME' already exists with status: $stack_status"
        read -p "Do you want to update the existing stack? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            UPDATE_STACK=true
        else
            print_status $RED "Aborting deployment"
            exit 1
        fi
    else
        print_status $GREEN "Stack does not exist, proceeding with creation"
        UPDATE_STACK=false
    fi
}

# Function to create or update CloudFormation stack
deploy_stack() {
    local template_url="https://$Bucket.s3-$BucketRegion.amazonaws.com/$Prefix/master_storage.yaml"
    
    if [ "$UPDATE_STACK" = true ]; then
        print_status $BLUE "Updating CloudFormation stack '$STACK_NAME'..."
        aws cloudformation update-stack \
            --region $REGION \
            --stack-name $STACK_NAME \
            --template-url $template_url \
            --disable-rollback \
            --parameters ParameterKey=Bucket,ParameterValue=$Bucket \
                         ParameterKey=Prefix,ParameterValue=$Prefix \
                         ParameterKey=BucketRegion,ParameterValue=$BucketRegion \
            --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM
    else
        print_status $BLUE "Creating CloudFormation stack '$STACK_NAME'..."
        aws cloudformation create-stack \
            --region $REGION \
            --stack-name $STACK_NAME \
            --template-url $template_url \
            --disable-rollback \
            --parameters ParameterKey=Bucket,ParameterValue=$Bucket \
                         ParameterKey=Prefix,ParameterValue=$Prefix \
                         ParameterKey=BucketRegion,ParameterValue=$BucketRegion \
            --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM
    fi
    
    if [ $? -eq 0 ]; then
        print_status $GREEN "Stack deployment initiated successfully"
    else
        print_status $RED "ERROR: Failed to initiate stack deployment"
        exit 1
    fi
}

# Function to monitor stack progress
monitor_stack() {
    print_status $BLUE "Monitoring stack progress..."
    local target_status
    
    if [ "$UPDATE_STACK" = true ]; then
        target_status="UPDATE_COMPLETE"
    else
        target_status="CREATE_COMPLETE"
    fi
    
    local check_interval=10
    
    while true; do
        # Get current stack status
        local current_status=$(aws cloudformation describe-stacks \
            --region $REGION \
            --stack-name $STACK_NAME \
            --query 'Stacks[0].StackStatus' \
            --output text 2>/dev/null || echo "UNKNOWN")
        
        print_status $YELLOW "Current stack status: $current_status"
        
        # Get the 10 most recent events
        local events=$(aws cloudformation describe-stack-events \
            --region $REGION \
            --stack-name $STACK_NAME \
            --query 'StackEvents[:10].[Timestamp,LogicalResourceId,ResourceStatus,ResourceStatusReason]' \
            --output table 2>/dev/null || echo "")
        
        if [ ! -z "$events" ] && [ "$events" != "None" ]; then
            echo -e "\n${BLUE}Recent Events (last 10):${NC}"
            echo "$events"
        fi
        
        # Also show any events that are currently in progress
        local in_progress_events=$(aws cloudformation describe-stack-events \
            --region $REGION \
            --stack-name $STACK_NAME \
            --query 'StackEvents[?contains(ResourceStatus, `IN_PROGRESS`)].[Timestamp,LogicalResourceId,ResourceStatus]' \
            --output table 2>/dev/null || echo "")
        
        if [ ! -z "$in_progress_events" ] && [ "$in_progress_events" != "None" ]; then
            echo -e "\n${YELLOW}Currently In Progress:${NC}"
            echo "$in_progress_events"
        fi
        
        # Check if stack deployment completed
        case $current_status in
            "CREATE_COMPLETE"|"UPDATE_COMPLETE")
                print_status $GREEN "Stack deployment completed successfully!"
                break
                ;;
            "CREATE_FAILED"|"UPDATE_FAILED"|"ROLLBACK_COMPLETE"|"UPDATE_ROLLBACK_COMPLETE"|"DELETE_COMPLETE")
                print_status $RED "Stack deployment failed with status: $current_status"
                print_failure_details
                exit 1
                ;;
            "CREATE_IN_PROGRESS"|"UPDATE_IN_PROGRESS"|"UPDATE_COMPLETE_CLEANUP_IN_PROGRESS")
                print_status $YELLOW "Stack deployment in progress..."
                ;;
            *)
                print_status $YELLOW "Stack status: $current_status"
                ;;
        esac
        
        echo "----------------------------------------"
        sleep $check_interval
    done
}

# Function to print failure details
print_failure_details() {
    print_status $RED "Fetching failure details..."
    local failed_events=$(aws cloudformation describe-stack-events \
        --region $REGION \
        --stack-name $STACK_NAME \
        --query 'StackEvents[?ResourceStatus==`CREATE_FAILED` || ResourceStatus==`UPDATE_FAILED`].[LogicalResourceId,ResourceStatusReason]' \
        --output table 2>/dev/null || echo "Could not fetch failure details")
    
    echo -e "\n${RED}Failed Resources:${NC}"
    echo "$failed_events"
}

# Function to display stack outputs
display_outputs() {
    print_status $BLUE "Fetching stack outputs..."
    local outputs=$(aws cloudformation describe-stacks \
        --region $REGION \
        --stack-name $STACK_NAME \
        --query 'Stacks[0].Outputs' \
        --output table 2>/dev/null || echo "No outputs available")
    
    if [ "$outputs" != "No outputs available" ]; then
        echo -e "\n${GREEN}Stack Outputs:${NC}"
        echo "$outputs"
    else
        print_status $YELLOW "No outputs defined for this stack"
    fi
}

# Main execution
main() {
    print_status $GREEN "Starting CloudFormation deployment process..."
    
    echo "Configuration:"
    echo "  Bucket: $Bucket"
    echo "  Prefix: $Prefix"
    echo "  Region: $BucketRegion"
    echo "  Stack Name: $STACK_NAME"
    echo "  Template Directory: $TEMPLATE_DIR"
    echo ""
    
    # Pre-deployment checks
    check_aws_config
    check_bucket
    check_existing_stack
    
    # Upload templates
    upload_templates
    verify_master_template
    
    # Deploy stack
    deploy_stack
    
    # Monitor progress
    monitor_stack
    
    # Display results
    display_outputs
    
    print_status $GREEN "Deployment process completed successfully!"
}

# Trap to handle script interruption
trap 'print_status $RED "Script interrupted by user"; exit 1' INT

# Run main function
main "$@"