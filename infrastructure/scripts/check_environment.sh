#!/bin/bash

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== AWS Infrastructure Environment Check ===${NC}\n"

# Check 1: Current directory
echo -e "${BLUE}1. Checking current directory...${NC}"
CURRENT_DIR=$(pwd)
echo "   Current: $CURRENT_DIR"

if [ -d "infrastructure/cloudformation" ]; then
    echo -e "   ${GREEN}✓ CloudFormation directory found${NC}"
else
    echo -e "   ${RED}✗ CloudFormation directory NOT found${NC}"
    echo -e "   ${YELLOW}⚠  You must run scripts from the project root directory${NC}"
    exit 1
fi

# Check 2: AWS CLI
echo -e "\n${BLUE}2. Checking AWS CLI...${NC}"
if command -v aws &> /dev/null; then
    AWS_VERSION=$(aws --version 2>&1 | cut -d' ' -f1)
    echo -e "   ${GREEN}✓ AWS CLI installed: $AWS_VERSION${NC}"
else
    echo -e "   ${RED}✗ AWS CLI not found${NC}"
    exit 1
fi

# Check 3: AWS Credentials
echo -e "\n${BLUE}3. Checking AWS credentials...${NC}"
if aws sts get-caller-identity &> /dev/null; then
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    USER_ARN=$(aws sts get-caller-identity --query Arn --output text)
    echo -e "   ${GREEN}✓ AWS credentials configured${NC}"
    echo "   Account: $ACCOUNT_ID"
    echo "   Identity: $USER_ARN"
else
    echo -e "   ${RED}✗ AWS credentials not configured or invalid${NC}"
    exit 1
fi

# Check 4: S3 Bucket
echo -e "\n${BLUE}4. Checking S3 bucket access...${NC}"
BUCKET='yikyakyuk-ap-southeast-1-875692608981'
if aws s3 ls "s3://$BUCKET" --region ap-southeast-1 &> /dev/null; then
    echo -e "   ${GREEN}✓ S3 bucket accessible: $BUCKET${NC}"
else
    echo -e "   ${YELLOW}⚠  Cannot access S3 bucket: $BUCKET${NC}"
    echo "   This may be normal if bucket doesn't exist yet"
fi

# Check 5: Required templates
echo -e "\n${BLUE}5. Checking CloudFormation templates...${NC}"
REQUIRED_TEMPLATES=(
    "infrastructure/cloudformation/master.yaml"
    "infrastructure/cloudformation/vpc.yaml"
    "infrastructure/cloudformation/ec2-asg-alb.yaml"
)

for template in "${REQUIRED_TEMPLATES[@]}"; do
    if [ -f "$template" ]; then
        echo -e "   ${GREEN}✓ Found: $template${NC}"
    else
        echo -e "   ${RED}✗ Missing: $template${NC}"
    fi
done

# Check 6: Script permissions
echo -e "\n${BLUE}6. Checking script permissions...${NC}"
SCRIPTS=(
    "infrastructure/scripts/deploy_master.sh"
    "infrastructure/scripts/delete_stack.sh"
)

for script in "${SCRIPTS[@]}"; do
    if [ -x "$script" ]; then
        echo -e "   ${GREEN}✓ Executable: $script${NC}"
    else
        echo -e "   ${YELLOW}⚠  Not executable: $script${NC}"
        echo "      Run: chmod +x $script"
    fi
done

# Summary
echo -e "\n${GREEN}=== Environment Check Complete ===${NC}"
echo -e "\n${BLUE}You can now run deployment scripts:${NC}"
echo "  ./infrastructure/scripts/deploy_master.sh"
echo ""
