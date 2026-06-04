#!/bin/bash

# CloudFormation Sequential Stack Deletion Script
# Usage: ./delete_stacks.sh [--region REGION] [--force] stack1 stack2 stack3 ...
# or define stacks in the STACKS array below

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# AWS CLI profile (optional - comment out if using default)
# AWS_PROFILE="your-profile-name"

# Default values
STACKS=()
FORCE_DELETE=false
AWS_REGION="ap-southeast-1"  # Default region

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if AWS CLI is installed
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed or not in PATH"
        exit 1
    fi
}

# Function to validate AWS region
validate_region() {
    local region=$1
    if [[ ! $region =~ ^[a-z0-9-]+$ ]]; then
        print_error "Invalid region format: $region"
        return 1
    fi
    
    # Try to list regions to validate the region exists and AWS CLI is configured
    if ! aws ec2 describe-regions --region-names "$region" &> /dev/null; then
        print_error "Invalid or inaccessible region: $region"
        print_error "Please check your AWS credentials and region name"
        return 1
    fi
    
    return 0
}

# Function to check if stack exists
stack_exists() {
    local stack_name=$1
    if aws cloudformation describe-stacks --region "$AWS_REGION" --stack-name "$stack_name" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to get stack status
get_stack_status() {
    local stack_name=$1
    local status
    status=$(aws cloudformation describe-stacks \
        --region "$AWS_REGION" \
        --stack-name "$stack_name" \
        --query 'Stacks[0].StackStatus' \
        --output text 2>/dev/null)
    
    if [[ $? -eq 0 && -n "$status" ]]; then
        echo "$status"
    else
        echo "STACK_NOT_FOUND"
    fi
}

# Function to delete a single stack and wait for completion
delete_stack() {
    local stack_name=$1
    
    print_info "Processing stack: $stack_name (Region: $AWS_REGION)"
    
    # Check if stack exists
    if ! stack_exists "$stack_name"; then
        print_warning "Stack '$stack_name' does not exist in region '$AWS_REGION'. Skipping..."
        return 0
    fi
    
    # Get current stack status
    local current_status
    current_status=$(get_stack_status "$stack_name")
    print_info "Current status of '$stack_name': $current_status"
    
    # Check if stack is already being deleted
    if [[ "$current_status" == "DELETE_IN_PROGRESS" ]]; then
        print_info "Stack '$stack_name' is already being deleted. Waiting for completion..."
    elif [[ "$current_status" == "DELETE_COMPLETE" ]]; then
        print_success "Stack '$stack_name' is already deleted."
        return 0
    else
        # Initiate stack deletion
        print_info "Initiating deletion of stack '$stack_name'..."
        
        if aws cloudformation delete-stack --region "$AWS_REGION" --stack-name "$stack_name" 2>/dev/null; then
            print_success "Delete command sent successfully for stack '$stack_name'"
        else
            local exit_code=$?
            print_error "Failed to initiate deletion of stack '$stack_name' (exit code: $exit_code)"
            return 1
        fi
    fi
    
    # Wait for stack deletion to complete
    print_info "Waiting for stack '$stack_name' to be deleted..."
    
    local max_attempts=180  # 30 minutes (180 * 10 seconds)
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        local status
        status=$(get_stack_status "$stack_name")
        
        case "$status" in
            "STACK_NOT_FOUND"|"DELETE_COMPLETE")
                echo ""  # New line after dots
                print_success "Stack '$stack_name' has been successfully deleted!"
                return 0
                ;;
            "DELETE_FAILED")
                echo ""  # New line after dots
                print_error "Failed to delete stack '$stack_name'"
                
                # Get stack events to show the error
                print_info "Recent stack events for '$stack_name':"
                aws cloudformation describe-stack-events \
                    --region "$AWS_REGION" \
                    --stack-name "$stack_name" \
                    --query 'StackEvents[?ResourceStatus==`DELETE_FAILED`].[LogicalResourceId,ResourceStatusReason]' \
                    --output table 2>/dev/null || print_warning "Could not retrieve stack events"
                
                return 1
                ;;
            "DELETE_IN_PROGRESS")
                echo -n "."
                ;;
            *)
                print_warning "Unexpected status for stack '$stack_name': $status"
                echo -n "."
                ;;
        esac
        
        sleep 10
        ((attempt++))
    done
    
    echo ""  # New line after dots
    print_error "Timeout waiting for stack '$stack_name' to be deleted"
    return 1
}

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS] [stack1] [stack2] [stack3] ..."
    echo ""
    echo "Delete CloudFormation stacks sequentially."
    echo ""
    echo "Options:"
    echo "  --region REGION   AWS region (default: ap-southeast-1)"
    echo "  --force           Skip confirmation prompt"
    echo "  -h, --help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 my-stack-1 my-stack-2 my-stack-3"
    echo "  $0 --region us-west-2 my-stack-1 my-stack-2"
    echo "  $0 --region eu-west-1 --force my-stack-1 my-stack-2"
    echo "  $0 --region ap-southeast-1 \$(cat stack-list.txt)"
    echo ""
    echo "Common AWS Regions:"
    echo "  ap-southeast-1      (N. Virginia)"
    echo "  us-east-2      (Ohio)"
    echo "  us-west-1      (N. California)"
    echo "  us-west-2      (Oregon)"
    echo "  eu-west-1      (Ireland)"
    echo "  eu-west-2      (London)"
    echo "  eu-central-1   (Frankfurt)"
    echo "  ap-southeast-1 (Singapore)"
    echo "  ap-southeast-2 (Sydney)"
    echo "  ap-northeast-1 (Tokyo)"
    exit 0
}

# Main function
main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --region)
                if [[ -n "$2" && "$2" != --* ]]; then
                    AWS_REGION="$2"
                    shift 2
                else
                    print_error "Error: --region requires a value"
                    echo ""
                    usage
                fi
                ;;
            --force)
                FORCE_DELETE=true
                shift
                ;;
            -h|--help)
                usage
                ;;
            *)
                STACKS+=("$1")
                shift
                ;;
        esac
    done
    
    # Check if any stacks were provided
    if [[ ${#STACKS[@]} -eq 0 ]]; then
        print_error "No stacks specified for deletion"
        echo ""
        usage
    fi
    
    print_info "CloudFormation Sequential Stack Deletion Script"
    print_info "=============================================="
    
    # Check prerequisites
    check_aws_cli
    
    # Validate region
    print_info "Validating AWS region: $AWS_REGION"
    if ! validate_region "$AWS_REGION"; then
        exit 1
    fi
    print_success "Region validation successful"
    
    # Display configuration
    print_info "Configuration:"
    print_info "  Region: $AWS_REGION"
    print_info "  Force mode: $FORCE_DELETE"
    echo ""
    
    # Display stacks to be deleted
    print_info "Stacks to be deleted (in order):"
    for i in "${!STACKS[@]}"; do
        echo "  $((i+1)). ${STACKS[i]}"
    done
    echo ""
    
    # Confirmation prompt (skip if --force is used)
    if [[ "$FORCE_DELETE" == false ]]; then
        read -p "Are you sure you want to delete these stacks in region '$AWS_REGION'? (yes/no): " -r
        if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            print_info "Operation cancelled by user"
            exit 0
        fi
    else
        print_warning "Force mode enabled - skipping confirmation"
    fi
    
    echo ""
    
    # Delete stacks sequentially
    local success_count=0
    local failed_stacks=()
    
    for stack in "${STACKS[@]}"; do
        echo ""
        print_info "========================================"
        
        if delete_stack "$stack"; then
            ((success_count++))
            print_success "✓ Stack '$stack' processed successfully"
        else
            failed_stacks+=("$stack")
            print_error "✗ Failed to delete stack '$stack'"
            
            # Ask if user wants to continue with remaining stacks (unless --force is used)
            if [[ "$FORCE_DELETE" == false ]]; then
                echo ""
                read -p "Do you want to continue with the remaining stacks? (yes/no): " -r
                if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
                    print_info "Operation stopped by user"
                    break
                fi
            else
                print_warning "Force mode enabled - continuing with remaining stacks"
            fi
        fi
    done
    
    # Summary
    echo ""
    print_info "========================================"
    print_info "DELETION SUMMARY"
    print_info "========================================"
    print_info "Region: $AWS_REGION"
    print_success "Successfully deleted: $success_count stack(s)"
    
    if [[ ${#failed_stacks[@]} -gt 0 ]]; then
        print_error "Failed to delete: ${#failed_stacks[@]} stack(s)"
        for stack in "${failed_stacks[@]}"; do
            echo "  - $stack"
        done
        exit 1
    else
        print_success "All stacks deleted successfully!"
        exit 0
    fi
}

# Run main function with all arguments
main "$@"
```

## Key Changes Made:

1. **Added `--region` parameter**: 
   - Added a new `AWS_REGION` variable with default value `ap-southeast-1`
   - Added argument parsing for `--region` parameter
   - Added validation to ensure a region value is provided with the flag

2. **Region validation**:
   - Added `validate_region()` function to check if the region format is valid
   - Validates region accessibility by attempting to describe regions

3. **Updated all AWS CLI calls**:
   - Replaced hardcoded `ap-southeast-1` with `$AWS_REGION` variable
   - All CloudFormation commands now use the specified region

4. **Enhanced user experience**:
   - Updated usage instructions with region examples
   - Added common AWS regions list in help text
   - Display current region in configuration info
   - Include region in confirmation prompts and summary

5. **Improved logging**:
   - Stack processing now shows which region is being used
   - Error messages include region context
   - Summary includes region information

# ## Usage Examples:

# ```bash
# # Use default region (ap-southeast-1)
# ./delete_stacks.sh stack1 stack2 stack3

# # Specify a different region
# ./delete_stacks.sh --region us-west-2 stack1 stack2 stack3

# # Combine with force mode
# ./delete_stacks.sh --region eu-west-1 --force stack1 stack2

# # Use with stack list from file
# ./delete_stacks.sh --region ap-southeast-1 $(cat stack-list.txt)
# ```

# The script now provides much better flexibility for multi-region AWS deployments while maintaining all the original functionality.