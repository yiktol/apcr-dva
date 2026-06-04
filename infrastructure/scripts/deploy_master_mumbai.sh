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
STACK_NAME='saa'
REGION='ap-south-1'

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

# Function to check if master.yaml exists in S3
verify_master_template() {
    print_status $BLUE "Verifying master template exists in S3..."
    local template_url="https://$Bucket.s3-$BucketRegion.amazonaws.com/$Prefix/master.yaml"
    
    if aws s3 ls "s3://$Bucket/$Prefix/master.yaml" --region $BucketRegion >/dev/null 2>&1; then
        print_status $GREEN "Master template verified at: $template_url"
    else
        print_status $RED "ERROR: master.yaml not found in S3"
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
        print_status $BLUE "Automatically proceeding with stack update..."
        UPDATE_STACK=true
    else
        print_status $GREEN "Stack does not exist, proceeding with creation"
        UPDATE_STACK=false
    fi
}

# Function to create or update CloudFormation stack
deploy_stack() {
    local template_url="https://$Bucket.s3-$BucketRegion.amazonaws.com/$Prefix/master.yaml"
    
    if [ "$UPDATE_STACK" = true ]; then
        print_status $BLUE "Updating CloudFormation stack '$STACK_NAME'..."
        local output=$(aws cloudformation update-stack \
            --region $REGION \
            --stack-name $STACK_NAME \
            --template-url $template_url \
            --disable-rollback \
            --parameters ParameterKey=Bucket,ParameterValue=$Bucket \
                         ParameterKey=Prefix,ParameterValue=$Prefix \
                         ParameterKey=BucketRegion,ParameterValue=$BucketRegion \
            --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM 2>&1)
        
        if [ $? -eq 0 ]; then
            print_status $GREEN "Stack update initiated successfully"
        elif echo "$output" | grep -q "No updates are to be performed"; then
            print_status $YELLOW "No updates required - stack is already up to date"
            exit 0
        else
            print_status $RED "ERROR: Failed to initiate stack update"
            echo "$output"
            exit 1
        fi
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
        
        if [ $? -eq 0 ]; then
            print_status $GREEN "Stack creation initiated successfully"
        else
            print_status $RED "ERROR: Failed to initiate stack creation"
            exit 1
        fi
    fi
}

# Function to monitor stack progress
monitor_stack() {
    print_status $BLUE "Monitoring stack progress..."
    print_status $BLUE "This may take several minutes..."
    
    local operation
    if [ "$UPDATE_STACK" = true ]; then
        operation="update"
    else
        operation="create"
    fi
    
    local PREVIOUS_STATUS=""
    local PREVIOUS_EVENTS=""
    local START_TIME=$(date +%s)
    local LAST_EVENT_TIME=""
    
    # Determine success and failure statuses based on operation
    if [[ "$operation" == "create" ]]; then
        local SUCCESS_STATUS="CREATE_COMPLETE"
        local IN_PROGRESS_STATUSES="CREATE_IN_PROGRESS"
        local FAILURE_STATUSES="CREATE_FAILED|ROLLBACK_COMPLETE|ROLLBACK_FAILED"
    else
        local SUCCESS_STATUS="UPDATE_COMPLETE"
        local IN_PROGRESS_STATUSES="UPDATE_IN_PROGRESS|UPDATE_COMPLETE_CLEANUP_IN_PROGRESS"
        local FAILURE_STATUSES="UPDATE_FAILED|UPDATE_ROLLBACK_COMPLETE|UPDATE_ROLLBACK_FAILED"
    fi
    
    while true; do
        # Get current stack status
        local current_status=$(aws cloudformation describe-stacks \
            --region $REGION \
            --stack-name $STACK_NAME \
            --query 'Stacks[0].StackStatus' \
            --output text 2>/dev/null)
        
        if [ $? -ne 0 ]; then
            print_status $RED "ERROR: Failed to get stack status"
            exit 1
        fi
        
        # Get recent events with timestamps
        local CURRENT_EVENTS=$(aws cloudformation describe-stack-events \
            --region $REGION \
            --stack-name $STACK_NAME \
            --max-items 10 \
            --query 'StackEvents[?ResourceStatus!=`null`].[Timestamp,LogicalResourceId,ResourceType,ResourceStatus,ResourceStatusReason]' \
            --output json 2>/dev/null)
        
        # Display new events only
        if [[ "$CURRENT_EVENTS" != "$PREVIOUS_EVENTS" ]]; then
            # Parse and display events that are newer than last check
            echo "$CURRENT_EVENTS" | jq -r '.[] | @tsv' 2>/dev/null | while IFS=$'\t' read -r timestamp logical_id resource_type status reason; do
                # Skip if we've seen this timestamp before
                if [[ -n "$LAST_EVENT_TIME" ]] && [[ "$timestamp" < "$LAST_EVENT_TIME" ]]; then
                    continue
                fi
                
                # Color code based on status
                if [[ "$status" =~ COMPLETE$ ]] && [[ ! "$status" =~ ROLLBACK ]]; then
                    event_color=$GREEN
                elif [[ "$status" =~ FAILED$ ]] || [[ "$status" =~ ROLLBACK ]]; then
                    event_color=$RED
                elif [[ "$status" =~ IN_PROGRESS$ ]]; then
                    event_color=$YELLOW
                else
                    event_color=$BLUE
                fi
                
                # Format and print event
                local short_time=$(date -d "$timestamp" '+%H:%M:%S' 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%S" "${timestamp%%.*}" '+%H:%M:%S' 2>/dev/null || echo "$timestamp")
                print_status $event_color "  [$short_time] $logical_id ($resource_type) - $status"
                
                if [[ -n "$reason" ]] && [[ "$reason" != "null" ]]; then
                    echo -e "${event_color}    Reason: $reason${NC}"
                fi
            done
            
            PREVIOUS_EVENTS="$CURRENT_EVENTS"
            # Update last event time
            LAST_EVENT_TIME=$(echo "$CURRENT_EVENTS" | jq -r '.[0][0]' 2>/dev/null)
        fi
        
        # Print status if it changed
        if [[ "$current_status" != "$PREVIOUS_STATUS" ]]; then
            print_status $BLUE "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            print_status $BLUE "Stack Status: $current_status"
            print_status $BLUE "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            PREVIOUS_STATUS="$current_status"
            
            # Get resource summary
            local RESOURCE_SUMMARY=$(aws cloudformation list-stack-resources \
                --region $REGION \
                --stack-name $STACK_NAME \
                --query 'StackResourceSummaries[*].ResourceStatus' \
                --output text 2>/dev/null | tr '\t' '\n' | sort | uniq -c)
            
            if [[ -n "$RESOURCE_SUMMARY" ]]; then
                print_status $BLUE "Resource Status Summary:"
                echo "$RESOURCE_SUMMARY" | while read count status; do
                    print_status $BLUE "  $status: $count"
                done
            fi
        fi
        
        # Check if stack operation is complete
        if [[ "$current_status" == "$SUCCESS_STATUS" ]]; then
            print_status $GREEN "Stack deployment completed successfully!"
            break
        elif echo "$current_status" | grep -qE "$FAILURE_STATUSES"; then
            print_status $RED "Stack deployment failed with status: $current_status"
            print_failure_details
            exit 1
        elif echo "$current_status" | grep -qE "$IN_PROGRESS_STATUSES"; then
            # Continue monitoring
            :
        else
            # Handle other statuses
            :
        fi
        
        # Progress indicator with elapsed time
        local ELAPSED=$(($(date +%s) - START_TIME))
        local MINUTES=$((ELAPSED / 60))
        local SECONDS=$((ELAPSED % 60))
        printf "\r${BLUE}⏱  Elapsed time: %02d:%02d${NC}" $MINUTES $SECONDS
        
        # Wait before next check
        sleep 10
    done
    
    echo "" # New line after progress indicator
}

# Function to print failure details
print_failure_details() {
    print_status $RED "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    print_status $RED "Fetching failure details..."
    local failed_events=$(aws cloudformation describe-stack-events \
        --region $REGION \
        --stack-name $STACK_NAME \
        --query 'StackEvents[?contains(ResourceStatus, `FAILED`)].[LogicalResourceId,ResourceType,ResourceStatus,ResourceStatusReason]' \
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