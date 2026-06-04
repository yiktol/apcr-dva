
aws s3 cp infrastructure/cloudformation/iac/ s3://yikyakyuk-ap-southeast-1-875692608981/infrastructure/cloudformation/iac/ --recursive

aws cloudformation create-stack-set \
    --stack-set-name multiregional \
    --template-url https://yikyakyuk-ap-southeast-1-875692608981.s3.ap-southeast-1.amazonaws.com/infrastructure/cloudformation/iac/main.yaml \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND

aws cloudformation update-stack-set \
    --stack-set-name multiregional \
    --template-url https://yikyakyuk-ap-southeast-1-875692608981.s3.ap-southeast-1.amazonaws.com/infrastructure/cloudformation/iac/main.yaml \
    --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND

aws cloudformation create-stack-instances \
    --stack-set-name multiregional \
    --accounts 875692608981 \
    --regions ap-southeast-3 ap-southeast-4 ap-south-1 ap-northeast-2 us-east-1 \
    --operation-preferences FailureToleranceCount=0

aws cloudformation update-stack-instances \
    --stack-set-name multiregional \
    --accounts 875692608981 \
    --regions ap-southeast-3 ap-southeast-4 ap-south-1 ap-northeast-2 \
    --operation-preferences FailureToleranceCount=0

aws cloudformation delete-stack-instances \
    --stack-set-name multiregional \
    --accounts 875692608981 \
    --regions us-east-1 ap-southeast-3 ap-southeast-4 ap-south-1 ap-northeast-2  \
    --no-retain-stacks

aws cloudformation delete-stack-set --stack-set-name multiregional




aws cloudformation create-stack-instances \
    --stack-set-name multiregional \
    --accounts 875692608981 \
    --regions ap-southeast-3 \
    --operation-preferences FailureToleranceCount=0