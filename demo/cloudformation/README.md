# APCR-DVA Session 1 - Demo Environment

## Architecture

```
Internet → CloudFront → API Gateway → Lambda (in Private Subnet) → DynamoDB (via VPC Endpoint)
```

**Concepts demonstrated:**
- VPC with public/private subnets across 2 AZs
- Security Groups (three-tier: presentation → logic → data)
- Network ACLs (stateless subnet-level filtering)
- VPC Endpoint for DynamoDB (no internet exposure)
- Lambda in VPC with least-privilege IAM role
- API Gateway (REST API with proxy integration)
- CloudFront CDN distribution
- IAM Roles, STS AssumeRole, condition-based policies

## Deployment

```bash
# Deploy the stack
aws cloudformation create-stack \
  --stack-name apcr-dva-session1-demo \
  --template-body file://session1-demo.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ap-southeast-1

# Wait for completion (~5 minutes)
aws cloudformation wait stack-create-complete \
  --stack-name apcr-dva-session1-demo \
  --region ap-southeast-1

# Get outputs (URLs, ARNs)
aws cloudformation describe-stacks \
  --stack-name apcr-dva-session1-demo \
  --query 'Stacks[0].Outputs' \
  --output table \
  --region ap-southeast-1
```

## Quick Test

```bash
# Get the API URL from stack outputs
API_URL=$(aws cloudformation describe-stacks \
  --stack-name apcr-dva-session1-demo \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
  --output text --region ap-southeast-1)

CF_URL=$(aws cloudformation describe-stacks \
  --stack-name apcr-dva-session1-demo \
  --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontUrl`].OutputValue' \
  --output text --region ap-southeast-1)

# Test endpoints
curl $API_URL/health
curl $API_URL/inventory
curl $API_URL/inventory/ITEM-001

# Test via CloudFront
curl $CF_URL/health

# Create a new item
curl -X POST $API_URL/inventory \
  -H "Content-Type: application/json" \
  -d '{"itemId": "ITEM-006", "name": "Laptop Stand", "category": "Furniture", "quantity": 45}'
```

## Demo Walkthrough

### 1. Show the Working System (2 min)
- Hit `/health` → show it works end-to-end
- Hit `/inventory` → show seed data
- Show CloudFront URL responding (same data, CDN layer)

### 2. Walk Through the Console (10 min)

**VPC & Networking:**
- Show VPC with 4 subnets (2 public, 2 private)
- Show route tables: public has IGW route, private has NO internet route
- Show VPC Endpoint for DynamoDB on the private route table
- Show NACL rules: private subnet blocks all non-VPC inbound traffic

**Security Groups (The "Bouncer" from Slide 52):**
- `presentation-sg`: allows 80/443 from anywhere
- `logic-sg`: allows 443 only FROM presentation-sg
- `data-sg`: allows 443 only FROM logic-sg
- Explain: traffic can only flow in one direction through tiers

**Lambda:**
- Show function is deployed IN the VPC (private subnets)
- Show attached security group
- Show environment variables (table name)

**IAM:**
- Show Lambda execution role → only GetItem, PutItem, Query, Scan on one table
- Show the condition-based policy (date range + VPC condition)
- Show the auditor role trust policy

### 3. Break Things on Purpose (5 min)

**Demo: Remove VPC Endpoint → Lambda can't reach DynamoDB**
```bash
# Note the VPC endpoint ID from outputs, then:
# In Console: VPC → Endpoints → Delete the DynamoDB endpoint
# Hit the API → Lambda times out (15s) because it has no internet route
# Re-create the endpoint to fix it
```

**Demo: Tighten IAM → AccessDenied**
```bash
# In Console: IAM → Roles → apcr-dva-session1-lambda-role
# Remove the DynamoDBAccess inline policy
# Hit the API → returns 500 with AccessDeniedException
# Re-attach the policy to fix it
```

**Demo: STS AssumeRole**
```bash
AUDITOR_ARN=$(aws cloudformation describe-stacks \
  --stack-name apcr-dva-session1-demo \
  --query 'Stacks[0].Outputs[?OutputKey==`AuditorRoleArn`].OutputValue' \
  --output text --region ap-southeast-1)

# Assume the auditor role
CREDS=$(aws sts assume-role \
  --role-arn $AUDITOR_ARN \
  --role-session-name demo-auditor)

# Use temporary creds to read DynamoDB (works - read allowed)
export AWS_ACCESS_KEY_ID=$(echo $CREDS | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo $CREDS | jq -r '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(echo $CREDS | jq -r '.Credentials.SessionToken')

aws dynamodb scan --table-name apcr-dva-session1-inventory --region ap-southeast-1

# Try to write (fails - auditor is read-only)
aws dynamodb put-item \
  --table-name apcr-dva-session1-inventory \
  --item '{"itemId": {"S": "HACK-001"}, "name": {"S": "Unauthorized"}}' \
  --region ap-southeast-1

# Unset temp creds
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
```

### 4. CloudFront Demo (2 min)
```bash
# First request - cache MISS (X-Cache: Miss from cloudfront)
curl -I $CF_URL/inventory

# Second request - cache HIT (X-Cache: Hit from cloudfront)
curl -I $CF_URL/inventory
```

Note: Since we use CachingDisabled policy for the API, you'll see Miss on both.
To show caching, you could add an S3 origin with a static file.

## Cleanup

```bash
aws cloudformation delete-stack \
  --stack-name apcr-dva-session1-demo \
  --region ap-southeast-1
```

## Cost Estimate

All resources are serverless/on-demand, so cost is near zero when idle:
- Lambda: Free tier covers 1M requests/month
- DynamoDB: On-demand, pennies for demo usage
- API Gateway: Free tier covers 1M calls/month
- CloudFront: Free tier covers 1TB/month
- VPC Endpoint: ~$0.01/hr per AZ (~$14/month if left running)

**Recommendation**: Deploy before the session, tear down after. Total cost < $1.
