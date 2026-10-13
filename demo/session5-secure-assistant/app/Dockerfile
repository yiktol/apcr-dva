# Assistant Lambda container image. Built ONLY at deploy time by cdk-assets /
# deploy.sh — never at `cdk synth` (synth just stages this build context).
FROM public.ecr.aws/lambda/python:3.12

# Install runtime deps (strands-agents, strands-agents-tools, boto3, xray).
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Copy the assistant package.
COPY assistant/ ${LAMBDA_TASK_ROOT}/assistant/

# Copy the presign package too: the assistant's get_receipt_url tool imports the
# SINGLE shared SigV4/regional presign helper from presign.handler
# (make_s3_presign_client + generate_url), so the module must be present in the
# image. Without this the guarded import degrades to None and the receipt tool
# fails at runtime with AttributeError on every order.
COPY presign/ ${LAMBDA_TASK_ROOT}/presign/

# Handler is <package>.<module>.<function>.
CMD ["assistant.handler.handler"]
