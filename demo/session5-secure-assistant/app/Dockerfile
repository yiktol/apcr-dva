# Assistant Lambda container image. Built ONLY at deploy time by cdk-assets /
# deploy.sh — never at `cdk synth` (synth just stages this build context).
FROM public.ecr.aws/lambda/python:3.12

# Install runtime deps (strands-agents, strands-agents-tools, boto3, xray).
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Copy the assistant package.
COPY assistant/ ${LAMBDA_TASK_ROOT}/assistant/

# Handler is <package>.<module>.<function>.
CMD ["assistant.handler.handler"]
