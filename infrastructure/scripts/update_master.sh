#!/bin/bash

# Enable debugging and error handling
set -e
set -o pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}"
}

# Function to print debug information
debug() {
    if [[ "${DEBUG:-false}" == "true" ]]; then
        print_status $BLUE "DEBUG: $1"
    fi
}

# Configuration
Bucket='yikyakyuk-ap-southeast-1-875692608981'
Prefix='infrastructure/cloudformation'
BucketRegion='ap-southeast-1'
STACK_NAME='saa'
REGION='ap-southeast-1'
TEMPLATE_DIR='./templates'

print_status $BLUE "Starting CloudFormation deployment process..."
print_status $BLUE "Bucket: $Bucket"
print_status $BLUE "Prefix: $Prefix"
print_status $BLUE "Region: $BucketRegion"
print_status $BLUE "Stack Name: $STACK_NAME"

# Step 1: Upload templates to S3
print_status $YELLOW "Step 1: Uploading templates to S3..."
debug "Source directory: $TEMPLATE_DIR"
debug "S3 destination: s3://$Bucket/$Prefix"

if aws s3 cp "$TEMPLATE_DIR" "s3://$Bucket/$Prefix" --recursive --region "$REGION"; then
    print_status $GREEN "✓ Templates uploaded successfully"
else
    print_status $RED "✗ Failed to upload templates"
    exit 1
fi

# Step 2: Verify template exists
print_status $YELLOW "Step 2: Verifying master template exists..."
TEMPLATE_URL="https://$Bucket.s3-$BucketRegion.amazonaws.com/$Prefix/master.yaml"
debug "Template URL: $TEMPLATE_URL"

if aws s3 ls "s3://$Bucket/$Prefix/master.yaml" --region "$REGION" >/dev/null 2>&1; then
    print_status $GREEN "✓ Master template found"
else
    print_status $RED "✗ Master template not found at s3://$Bucket/$Prefix/master.yaml"
    exit 1
fi

# Step 3: Validate template
print_status $YELLOW "Step 3: Validating CloudFormation template..."
if aws cloudformation validate-template \
    --template-url "$TEMPLATE_URL" \
    --region "$REGION" >/dev/null 2>&1; then
    print_status $GREEN "✓ Template validation successful"
else
    print_status $RED "✗ Template validation failed"
    exit 1
fi

# Step 4: Check if stack exists and determine operation
print_status $YELLOW "Step 4: Checking stack status..."

STACK_EXISTS=$(aws cloudformation describe-stacks \
    --region "$REGION" \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].StackName' \
    --output text 2>/dev/null || echo "NONE")

if [[ "$STACK_EXISTS" == "NONE" ]]; then
    print_status $BLUE "Stack does not exist. Creating new stack..."
    OPERATION="create"
    
    UPDATE_OUTPUT=$(aws cloudformation create-stack \
        --region "$REGION" \
        --stack-name "$STACK_NAME" \
        --template-url "$TEMPLATE_URL" \
        --parameters ParameterKey=Bucket,ParameterValue="$Bucket" \
                     ParameterKey=Prefix,ParameterValue="$Prefix" \
                     ParameterKey=BucketRegion,ParameterValue="$BucketRegion" \
        --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM \
        --output text 2>&1)
    
    if [[ $? -eq 0 ]]; then
        print_status $GREEN "✓ Stack creation initiated successfully"
        debug "Stack ID: $UPDATE_OUTPUT"
    else
        print_status $RED "✗ Failed to initiate stack creation"
        echo "$UPDATE_OUTPUT"
        exit 1
    fi
else
    print_status $BLUE "Stack exists. Updating stack..."
    OPERATION="update"
    
    UPDATE_OUTPUT=$(aws cloudformation update-stack \
        --region "$REGION" \
        --stack-name "$STACK_NAME" \
        --template-url "$TEMPLATE_URL" \
        --parameters ParameterKey=Bucket,ParameterValue="$Bucket" \
                     ParameterKey=Prefix,ParameterValue="$Prefix" \
                     ParameterKey=BucketRegion,ParameterValue="$BucketRegion" \
        --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM \
        --output text 2>&1)
    
    if [[ $? -eq 0 ]]; then
        print_status $GREEN "✓ Stack update initiated successfully"
        debug "Stack ID: $UPDATE_OUTPUT"
    else
        if echo "$UPDATE_OUTPUT" | grep -q "No updates are to be performed"; then
            print_status $YELLOW "⚠ No updates required - stack is already up to date"
            exit 0
        else
            print_status $RED "✗ Failed to initiate stack update"
            echo "$UPDATE_OUTPUT"
            exit 1
        fi
    fi
fi

# Step 5: Monitor stack operation progress
print_status $YELLOW "Step 5: Monitoring stack ${OPERATION} progress..."
print_status $BLUE "This may take several minutes..."

PREVIOUS_STATUS=""
PREVIOUS_EVENTS=""
WAIT_COUNTER=0
START_TIME=$(date +%s)
LAST_EVENT_TIME=""

# Determine success and failure statuses based on operation
if [[ "$OPERATION" == "create" ]]; then
    SUCCESS_STATUS="CREATE_COMPLETE"
    IN_PROGRESS_STATUSES="CREATE_IN_PROGRESS"
    FAILURE_STATUSES="CREATE_FAILED|ROLLBACK_COMPLETE|ROLLBACK_FAILED"
else
    SUCCESS_STATUS="UPDATE_COMPLETE"
    IN_PROGRESS_STATUSES="UPDATE_IN_PROGRESS|UPDATE_COMPLETE_CLEANUP_IN_PROGRESS"
    FAILURE_STATUSES="UPDATE_FAILED|UPDATE_ROLLBACK_COMPLETE|UPDATE_ROLLBACK_FAILED"
fi

while true; do
    # Get current stack status
    STACK_STATUS=$(aws cloudformation describe-stacks \
        --region "$REGION" \
        --stack-name "$STACK_NAME" \
        --query 'Stacks[0].StackStatus' \
        --output text 2>/dev/null)
    
    if [[ $? -ne 0 ]]; then
        print_status $RED "✗ Failed to get stack status"
        exit 1
    fi
    
    # Get recent events with timestamps
    CURRENT_EVENTS=$(aws cloudformation describe-stack-events \
        --region "$REGION" \
        --stack-name "$STACK_NAME" \
        --max-items 10 \
        --query 'StackEvents[?ResourceStatus!=`null`].[Timestamp,LogicalResourceId,ResourceType,ResourceStatus,ResourceStatusReason]' \
        --output json 2>/dev/null)
    
    # Display new events only
    if [[ "$CURRENT_EVENTS" != "$PREVIOUS_EVENTS" ]]; then
        # Parse and display events that are newer than last check
        echo "$CURRENT_EVENTS" | jq -r '.[] | @tsv' | while IFS=$'\t' read -r timestamp logical_id resource_type status reason; do
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
            short_time=$(date -d "$timestamp" '+%H:%M:%S' 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%S" "$timestamp" '+%H:%M:%S' 2>/dev/null || echo "$timestamp")
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
    if [[ "$STACK_STATUS" != "$PREVIOUS_STATUS" ]]; then
        print_status $BLUE "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        print_status $BLUE "Stack Status: $STACK_STATUS"
        print_status $BLUE "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        PREVIOUS_STATUS="$STACK_STATUS"
        
        # Get resource summary
        RESOURCE_SUMMARY=$(aws cloudformation list-stack-resources \
            --region "$REGION" \
            --stack-name "$STACK_NAME" \
            --query 'StackResourceSummaries[*].ResourceStatus' \
            --output text 2>/dev/null | sort | uniq -c)
        
        if [[ -n "$RESOURCE_SUMMARY" ]]; then
            print_status $BLUE "Resource Status Summary:"
            echo "$RESOURCE_SUMMARY" | while read count status; do
                print_status $BLUE "  $status: $count"
            done
        fi
    fi
    
    # Check if stack operation is complete
    if [[ "$STACK_STATUS" == "$SUCCESS_STATUS" ]]; then
        print_status $GREEN "✓ Stack ${OPERATION} completed successfully!"
        break
    elif echo "$STACK_STATUS" | grep -qE "$FAILURE_STATUSES"; then
        print_status $RED "✗ Stack ${OPERATION} failed with status: $STACK_STATUS"
        
        # Show detailed failure information
        print_status $RED "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        print_status $RED "Failed Resources:"
        aws cloudformation describe-stack-events \
            --region "$REGION" \
            --stack-name "$STACK_NAME" \
            --query 'StackEvents[?contains(ResourceStatus, `FAILED`)].[LogicalResourceId,ResourceType,ResourceStatus,ResourceStatusReason]' \
            --output table
        exit 1
    elif echo "$STACK_STATUS" | grep -qE "$IN_PROGRESS_STATUSES"; then
        # Continue monitoring
        :
    else
        debug "Unexpected status: $STACK_STATUS"
    fi
    
    # Progress indicator with elapsed time
    WAIT_COUNTER=$((WAIT_COUNTER + 1))
    ELAPSED=$(($(date +%s) - START_TIME))
    MINUTES=$((ELAPSED / 60))
    SECONDS=$((ELAPSED % 60))
    printf "\r${BLUE}⏱  Elapsed time: %02d:%02d${NC}" $MINUTES $SECONDS
    
    # Wait before next check
    sleep 10
done

echo "" # New line after progress indicator

# Step 6: Display final stack information
print_status $YELLOW "Step 6: Displaying final stack information..."

# Get stack outputs
OUTPUTS=$(aws cloudformation describe-stacks \
    --region "$REGION" \
    --stack-name "$STACK_NAME" \
    --query 'Stacks[0].Outputs' \
    --output table 2>/dev/null)

if [[ -n "$OUTPUTS" && "$OUTPUTS" != "None" ]]; then
    print_status $GREEN "Stack Outputs:"
    echo "$OUTPUTS"
else
    debug "No stack outputs found"
fi

# Get stack resources summary
RESOURCES_COUNT=$(aws cloudformation list-stack-resources \
    --region "$REGION" \
    --stack-name "$STACK_NAME" \
    --query 'length(StackResourceSummaries)' \
    --output text)

print_status $GREEN "Stack Resources: $RESOURCES_COUNT resources deployed"

# Calculate total execution time
END_TIME=$(date +%s)
TOTAL_ELAPSED=$((END_TIME - START_TIME))
TOTAL_MINUTES=$((TOTAL_ELAPSED / 60))
TOTAL_SECONDS=$((TOTAL_ELAPSED % 60))

print_status $GREEN "🎉 CloudFormation ${OPERATION} completed successfully!"
print_status $BLUE "Stack Name: $STACK_NAME"
print_status $BLUE "Region: $REGION"
print_status $BLUE "Total execution time: ${TOTAL_MINUTES}m ${TOTAL_SECONDS}s"


# To use this script:

# 1. **Save it to a file** (e.g., `deploy-cf-stack.sh`):
# ```bash
# chmod +x deploy-cf-stack.sh
# ```

# 2. **Run with basic output**:
# ```bash
# ./deploy-cf-stack.sh
# ```

# 3. **Run with debug information**:
# ```bash
# DEBUG=true ./deploy-cf-stack.sh
# ```
