#!/bin/bash
# AWS Infrastructure Deployment Commands
# Run these commands from the PROJECT ROOT directory

# ============================================================================
# DEPLOYMENT COMMANDS
# ============================================================================

# Deploy Stack to Singapore Region (Primary)
./infrastructure/scripts/deploy_master.sh

# Deploy Stack to Sydney Region
./infrastructure/scripts/deploy_master_sydney.sh

# Deploy Stack to Mumbai Region
./infrastructure/scripts/deploy_master_mumbai.sh

# Deploy Cross-Region Stack
./infrastructure/scripts/deploy_master_cross_region.sh

# Deploy Storage Stack
./infrastructure/scripts/deploy_master_storage.sh

# ============================================================================
# DELETE COMMANDS
# ============================================================================

# Delete Storage Stack
./infrastructure/scripts/delete_stack.sh --force --region ap-southeast-1 master-storage

# Delete Cross-Region Stack
./infrastructure/scripts/delete_stack.sh --force --region ap-southeast-1 master-cross-region

# Delete Regional Stacks (parallel execution)
./infrastructure/scripts/delete_stack.sh --force --region ap-south-1 master &
./infrastructure/scripts/delete_stack.sh --force --region ap-southeast-2 master & 
./infrastructure/scripts/delete_stack.sh --force --region ap-southeast-1 master &

# Wait for all background jobs to complete
wait

# ============================================================================
# USAGE NOTES
# ============================================================================
# 1. Always run these commands from the project root directory
# 2. Ensure AWS CLI is configured with proper credentials
# 3. Make sure scripts have execute permissions: chmod +x infrastructure/scripts/*.sh
# 4. For parallel deletions, the & runs commands in background, wait ensures completion