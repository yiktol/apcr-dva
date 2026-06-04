# Set your configuration
export AWS_REGION=ap-southeast-1
export STACK_NAME=one-ec2

echo "Deploying AWS infrastructure..."

# Get VPC and subnet information
VPC_ID=$(aws cloudformation describe-stacks --stack-name saa \
  --query 'Stacks[0].Outputs[?OutputKey==`VpcId`].OutputValue' \
  --output text) && \
echo "VPC_ID: $VPC_ID"

PRIVATESUBNET=$(aws cloudformation describe-stacks  --stack-name saa \
  --query 'Stacks[0].Outputs[?OutputKey==`PrivateSubnetOne`].OutputValue' \
  --output text) && \
echo "PRIVATESUBNET: $PRIVATESUBNET"

# Deploy CloudFormation stack
aws cloudformation deploy \
  --stack-name $STACK_NAME \
  --template-file ec2.yaml \
  --parameter-overrides \
    VpcId=$VPC_ID \
    SubnetId=$PRIVATESUBNET \
  --region $AWS_REGION \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM


echo "Infrastructure deployed successfully!"
