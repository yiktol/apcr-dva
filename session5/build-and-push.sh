#!/bin/bash
set -e

# Configuration
AWS_REGION=${AWS_REGION:-ap-southeast-1}
ACCOUNTID=$(aws sts get-caller-identity --query "Account" --output text)
IMAGE_TAG=${IMAGE_TAG:-latest}
ECRREPO=${ECRREPO:-apcr/dva-5}
APP_NAME=${APP_NAME:-$ECRREPO}  # Use ECRREPO as default app name for docker build

# Get ECR repository URI
ECR_URI="$ACCOUNTID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECRREPO"

echo "ECR Repository URI: $ECR_URI"

# Check if ECR repository exists, create if it doesn't
echo "Checking if ECR repository exists..."
if aws ecr describe-repositories --repository-names $ECRREPO --region $AWS_REGION >/dev/null 2>&1; then
    echo "ECR repository '$ECRREPO' already exists."
else
    echo "ECR repository '$ECRREPO' does not exist. Creating..."
    aws ecr create-repository \
        --repository-name $ECRREPO \
        --region $AWS_REGION \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256
    
    echo "ECR repository '$ECRREPO' created successfully."
    
    # Optional: Set lifecycle policy to manage image retention
    echo "Setting lifecycle policy for image management..."
    aws ecr put-lifecycle-policy \
        --repository-name $ECRREPO \
        --region $AWS_REGION \
        --lifecycle-policy-text '{
            "rules": [
                {
                    "rulePriority": 1,
                    "description": "Delete untagged images after 7 days",
                    "selection": {
                        "tagStatus": "untagged",
                        "countType": "sinceImagePushed",
                        "countUnit": "days",
                        "countNumber": 7
                    },
                    "action": {
                        "type": "expire"
                    }
                },
                {
                    "rulePriority": 2,
                    "description": "Keep only latest 10 tagged images",
                    "selection": {
                        "tagStatus": "tagged",
                        "tagPrefixList": ["latest", "v", "release", "dev", "prod"],
                        "countType": "imageCountMoreThan",
                        "countNumber": 10
                    },
                    "action": {
                        "type": "expire"
                    }
                }
            ]
        }'
fi

# Login to ECR
echo "Logging in to Amazon ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI

# Build Docker image
echo "Building Docker image..."
docker build -t $APP_NAME:$IMAGE_TAG .

# Tag image for ECR
echo "Tagging image for ECR..."
docker tag $APP_NAME:$IMAGE_TAG $ECR_URI:$IMAGE_TAG

# Push image to ECR
echo "Pushing image to ECR..."
docker push $ECR_URI:$IMAGE_TAG

echo "Successfully pushed $ECR_URI:$IMAGE_TAG"
