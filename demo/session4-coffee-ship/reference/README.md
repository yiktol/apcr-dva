# Reference: declare the same queue three ways

This folder is a teaching artifact. It declares the **same** coffee-shop orders
SQS queue in three different formats so you can compare the authoring experience
side by side:

| File | Format | What it shows |
| --- | --- | --- |
| [`orders-queue.cfn.json`](./orders-queue.cfn.json) | Raw CloudFormation (JSON) | The lowest-level, fully explicit resource definition. |
| [`orders-queue-cdk.ts`](./orders-queue-cdk.ts) | AWS CDK (TypeScript) | The same queue expressed as a typed construct. |
| [`orders-queue.sam.yaml`](./orders-queue.sam.yaml) | AWS SAM (YAML) | The same queue in a SAM/CloudFormation template. |

All three describe one queue with identical settings:

- **Queue name:** `coffee-shop-orders`
- **Visibility timeout:** 60 seconds
- **Message retention:** 4 days (345600 seconds)

These settings mirror the real `OrdersQueue` construct in
[`../infra/lib/network-data-stack.ts`](../infra/lib/network-data-stack.ts),
which is the queue that actually gets deployed.

## Not deployed

**None of the files in this folder are deployed.** They exist only to be read
and compared during the session. The queue that gets provisioned comes from the
CDK app under `infra/`, not from these reference files.
