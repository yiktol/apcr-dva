#!/bin/bash

# Script to empty and delete an S3 bucket completely
# Usage: ./delete_s3_bucket.sh <bucket-name>

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
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

print_debug() {
    echo -e "${YELLOW}[DEBUG]${NC} $1"
}

# Function to check if AWS CLI is installed
check_aws_cli() {
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
}

# Function to check if bucket exists
check_bucket_exists() {
    local bucket_name=$1
    if ! aws s3api head-bucket --bucket "$bucket_name" 2>/dev/null; then
        print_error "Bucket '$bucket_name' does not exist or you don't have access to it."
        exit 1
    fi
}

# Function to get bucket region
get_bucket_region() {
    local bucket_name=$1
    local region=$(aws s3api get-bucket-location --bucket "$bucket_name" --query 'LocationConstraint' --output text 2>/dev/null || echo "us-east-1")
    [[ "$region" == "None" || "$region" == "null" ]] && region="us-east-1"
    echo "$region"
}

# Function to completely empty bucket using aws s3 rm (most reliable method)
empty_bucket_completely() {
    local bucket_name=$1
    
    print_status "Method 1: Using AWS S3 RM to empty bucket..."
    
    # This handles both versioned and non-versioned objects
    if aws s3 rm "s3://$bucket_name" --recursive 2>/dev/null; then
        print_success "AWS S3 RM completed"
    else
        print_warning "AWS S3 RM completed with some warnings (this is normal)"
    fi
    
    print_status "Method 2: Removing any remaining object versions..."
    
    # Handle versioned objects specifically
    local versions_exist=false
    if aws s3api list-object-versions --bucket "$bucket_name" --max-items 1 >/dev/null 2>&1; then
        # Get all versions and delete them
        local temp_file="/tmp/delete_batch_$$"
        
        # Create delete request for versions
        aws s3api list-object-versions --bucket "$bucket_name" \
            --query '{Objects: Versions[?Key != null].{Key: Key, VersionId: VersionId}}' \
            --output json > "$temp_file"
        
        local version_count=$(jq -r '.Objects | length' "$temp_file" 2>/dev/null || echo "0")
        
        if [[ "$version_count" -gt 0 ]]; then
            print_status "Found $version_count object versions to delete"
            versions_exist=true
            
            # Delete in batches
            local batch_size=1000
            local total_batches=$(( (version_count + batch_size - 1) / batch_size ))
            
            for ((i=0; i<total_batches; i++)); do
                local start=$((i * batch_size))
                print_status "Deleting version batch $((i+1))/$total_batches..."
                
                jq --argjson start "$start" --argjson size "$batch_size" \
                    '.Objects = (.Objects | .[$start:$start+$size]) | if (.Objects | length) > 0 then . else empty end' \
                    "$temp_file" > "$temp_file.batch" 2>/dev/null
                
                if [[ -s "$temp_file.batch" ]]; then
                    aws s3api delete-objects --bucket "$bucket_name" --delete "file://$temp_file.batch" --quiet || true
                fi
            done
        fi
        
        # Handle delete markers
        aws s3api list-object-versions --bucket "$bucket_name" \
            --query '{Objects: DeleteMarkers[?Key != null].{Key: Key, VersionId: VersionId}}' \
            --output json > "$temp_file.markers"
        
        local marker_count=$(jq -r '.Objects | length' "$temp_file.markers" 2>/dev/null || echo "0")
        
        if [[ "$marker_count" -gt 0 ]]; then
            print_status "Found $marker_count delete markers to remove"
            versions_exist=true
            
            local batch_size=1000
            local total_batches=$(( (marker_count + batch_size - 1) / batch_size ))
            
            for ((i=0; i<total_batches; i++)); do
                local start=$((i * batch_size))
                print_status "Deleting marker batch $((i+1))/$total_batches..."
                
                jq --argjson start "$start" --argjson size "$batch_size" \
                    '.Objects = (.Objects | .[$start:$start+$size]) | if (.Objects | length) > 0 then . else empty end' \
                    "$temp_file.markers" > "$temp_file.batch" 2>/dev/null
                
                if [[ -s "$temp_file.batch" ]]; then
                    aws s3api delete-objects --bucket "$bucket_name" --delete "file://$temp_file.batch" --quiet || true
                fi
            done
        fi
        
        # Cleanup temp files
        rm -f "$temp_file" "$temp_file.markers" "$temp_file.batch" 2>/dev/null || true
    fi
    
    if [[ "$versions_exist" == false ]]; then
        print_status "No object versions or delete markers found"
    fi
}

# Function to verify bucket is truly empty
verify_bucket_empty() {
    local bucket_name=$1
    
    print_debug "Checking for remaining objects..."
    
    # Check current objects
    local current_objects=$(aws s3api list-objects-v2 --bucket "$bucket_name" --max-keys 1 --query 'Contents[0].Key' --output text 2>/dev/null || echo "None")
    
    # Check versions
    local versions=$(aws s3api list-object-versions --bucket "$bucket_name" --max-keys 1 --query 'Versions[0].Key' --output text 2>/dev/null || echo "None")
    
    # Check delete markers
    local markers=$(aws s3api list-object-versions --bucket "$bucket_name" --max-keys 1 --query 'DeleteMarkers[0].Key' --output text 2>/dev/null || echo "None")
    
    print_debug "Current objects: $current_objects"
    print_debug "Versions: $versions"  
    print_debug "Delete markers: $markers"
    
    if [[ "$current_objects" == "None" && "$versions" == "None" && "$markers" == "None" ]]; then
        print_success "Bucket is confirmed empty"
        return 0
    else
        print_error "Bucket is NOT empty!"
        print_error "  Current objects: $current_objects"
        print_error "  Versions: $versions"
        print_error "  Delete markers: $markers"
        return 1
    fi
}

# Function to remove all bucket configurations
remove_bucket_configurations() {
    local bucket_name=$1
    
    print_status "Removing bucket configurations..."
    
    # Remove bucket policy
    print_debug "Removing bucket policy..."
    aws s3api delete-bucket-policy --bucket "$bucket_name" 2>/dev/null && print_debug "✓ Policy removed" || print_debug "✗ No policy or failed to remove"
    
    # Remove bucket lifecycle
    print_debug "Removing lifecycle configuration..."
    aws s3api delete-bucket-lifecycle --bucket "$bucket_name" 2>/dev/null && print_debug "✓ Lifecycle removed" || print_debug "✗ No lifecycle or failed to remove"
    
    # Remove bucket cors
    print_debug "Removing CORS configuration..."
    aws s3api delete-bucket-cors --bucket "$bucket_name" 2>/dev/null && print_debug "✓ CORS removed" || print_debug "✗ No CORS or failed to remove"
    
    # Remove bucket website
    print_debug "Removing website configuration..."
    aws s3api delete-bucket-website --bucket "$bucket_name" 2>/dev/null && print_debug "✓ Website config removed" || print_debug "✗ No website config or failed to remove"
    
    # Remove notification configuration
    print_debug "Removing notification configuration..."
    aws s3api put-bucket-notification-configuration --bucket "$bucket_name" --notification-configuration '{}' 2>/dev/null && print_debug "✓ Notifications removed" || print_debug "✗ Failed to remove notifications"
    
    # Remove bucket logging
    print_debug "Removing logging configuration..."
    aws s3api put-bucket-logging --bucket "$bucket_name" --bucket-logging-status '{}' 2>/dev/null && print_debug "✓ Logging removed" || print_debug "✗ No logging or failed to remove"
    
    # Remove bucket encryption
    print_debug "Removing encryption configuration..."
    aws s3api delete-bucket-encryption --bucket "$bucket_name" 2>/dev/null && print_debug "✓ Encryption removed" || print_debug "✗ No encryption or failed to remove"
    
    # Remove bucket tagging
    print_debug "Removing bucket tagging..."
    aws s3api delete-bucket-tagging --bucket "$bucket_name" 2>/dev/null && print_debug "✓ Tags removed" || print_debug "✗ No tags or failed to remove"
    
    # Remove bucket request payment
    print_debug "Removing request payment configuration..."
    aws s3api put-bucket-request-payment --bucket "$bucket_name" --request-payment-configuration 'Payer=BucketOwner' 2>/dev/null && print_debug "✓ Request payment reset" || print_debug "✗ Failed to reset request payment"
    
    print_success "Bucket configurations cleanup completed"
}

# Function to delete the bucket
delete_bucket() {
    local bucket_name=$1
    local region=$(get_bucket_region "$bucket_name")
    
    print_status "Attempting to delete bucket '$bucket_name' in region '$region'..."
    
    # Try deletion with region specification
    local delete_cmd="aws s3api delete-bucket --bucket $bucket_name"
    if [[ "$region" != "us-east-1" ]]; then
        delete_cmd="$delete_cmd --region $region"
    fi
    
    print_debug "Executing: $delete_cmd"
    
    if eval "$delete_cmd" 2>/dev/null; then
        print_success "Bucket deletion command executed successfully"
        return 0
    else
        print_error "Bucket deletion failed"
        
        # Get more details about why it failed
        print_debug "Attempting to get more error details..."
        eval "$delete_cmd" 2>&1 | while read -r line; do
            print_error "AWS Error: $line"
        done
        
        return 1
    fi
}

# Function to verify bucket is deleted
verify_bucket_deleted() {
    local bucket_name=$1
    
    print_status "Verifying bucket deletion..."
    
    # Wait a moment for AWS to propagate the deletion
    sleep 2
    
    # Try to access the bucket
    if aws s3api head-bucket --bucket "$bucket_name" 2>/dev/null; then
        print_error "Bucket '$bucket_name' still exists!"
        return 1
    else
        # Double-check by trying to list the bucket
        if aws s3 ls "s3://$bucket_name" 2>/dev/null; then
            print_error "Bucket '$bucket_name' still accessible!"
            return 1
        else
            print_success "✓ Bucket '$bucket_name' has been successfully deleted!"
            return 0
        fi
    fi
}

# Main function
main() {
    local bucket_name=""
    local empty_only=false
    local debug_mode=false
    local force_mode=false
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --empty-only)
                empty_only=true
                shift
                ;;
            --debug)
                debug_mode=true
                shift
                ;;
            --force)
                force_mode=true
                shift
                ;;
            -*)
                print_error "Unknown option: $1"
                echo "Usage: $0 [--empty-only] [--debug] [--force] <bucket-name>"
                exit 1
                ;;
            *)
                bucket_name="$1"
                shift
                ;;
        esac
    done
    
    # Validate input
    if [[ -z "$bucket_name" ]]; then
        echo "Usage: $0 [--empty-only] [--debug] [--force] <bucket-name>"
        echo "  --empty-only: Only empty the bucket, don't delete it"
        echo "  --debug: Show detailed debug information"
        echo "  --force: Skip confirmation prompt"
        exit 1
    fi
    
    # Set debug mode
    if [[ "$debug_mode" == true ]]; then
        set -x  # Enable bash debug mode
    fi
    
    print_status "=== S3 Bucket Deletion Script ==="
    print_status "Bucket: $bucket_name"
    print_status "Empty only: $empty_only"
    print_status "Debug mode: $debug_mode"
    print_status "Force mode: $force_mode"
    
    # Perform initial checks
    print_status "Step 1: Performing initial checks..."
    check_aws_cli
    check_bucket_exists "$bucket_name"
    
    local region=$(get_bucket_region "$bucket_name")
    print_status "Bucket region: $region"
    
    # Confirmation (skip if force mode)
    if [[ "$force_mode" == false ]]; then
        if [[ "$empty_only" == true ]]; then
            print_warning "This will EMPTY the bucket '$bucket_name' (but keep the bucket)"
        else
            print_warning "This will COMPLETELY DELETE the bucket '$bucket_name' and all its contents"
        fi
        
        read -p "Are you sure? Type 'DELETE' to confirm: " confirmation
        if [[ "$confirmation" != "DELETE" ]]; then
            print_status "Operation cancelled."
            exit 0
        fi
    else
        if [[ "$empty_only" == true ]]; then
            print_warning "FORCE MODE: Proceeding to empty bucket '$bucket_name' without confirmation"
        else
            print_warning "FORCE MODE: Proceeding to completely delete bucket '$bucket_name' without confirmation"
        fi
    fi
    
    # Step 2: Empty the bucket
    print_status "Step 2: Emptying the bucket..."
    empty_bucket_completely "$bucket_name"
    
    # Step 3: Verify bucket is empty
    print_status "Step 3: Verifying bucket is empty..."
    if ! verify_bucket_empty "$bucket_name"; then
        print_error "Cannot proceed - bucket is not empty"
        exit 1
    fi
    
    # Step 4: Delete bucket (unless empty-only)
    if [[ "$empty_only" == false ]]; then
        print_status "Step 4: Removing bucket configurations..."
        remove_bucket_configurations "$bucket_name"
        
        print_status "Step 5: Deleting the bucket..."
        if ! delete_bucket "$bucket_name"; then
            print_error "Failed to delete bucket. Manual intervention may be required."
            exit 1
        fi
        
        print_status "Step 6: Verifying deletion..."
        if verify_bucket_deleted "$bucket_name"; then
            print_success "🎉 SUCCESS: Bucket '$bucket_name' has been completely deleted!"
        else
            print_error "Bucket deletion verification failed"
            exit 1
        fi
    else
        print_success "🎉 SUCCESS: Bucket '$bucket_name' has been emptied!"
    fi
}

# Trap for cleanup
trap 'rm -f /tmp/delete_batch_$$ /tmp/delete_batch_$$.* 2>/dev/null || true' EXIT

# Run the script
main "$@"


# ## Updated Usage:

# ```bash
# # Debug mode to see exactly what's happening
# ./delete_s3_bucket.sh --debug my-bucket-name

# # Just empty (for testing)
# ./delete_s3_bucket.sh --empty-only my-bucket-name

# # Complete deletion
# ./delete_s3_bucket.sh my-bucket-name

# # Force mode - skip confirmation (useful for automation)
# ./delete_s3_bucket.sh --force my-bucket-name

# # Force empty only (skip confirmation)
# ./delete_s3_bucket.sh --force --empty-only my-bucket-name

# # Combine all options
# ./delete_s3_bucket.sh --force --debug --empty-only my-bucket-name
# ```
