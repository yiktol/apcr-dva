# Implementation Plan — session4-coffee-ship (standalone AWS DVA-C03 demo)

All paths are absolute under the project root:
`/Users/erictole/demo/apcr-dva/.worktrees/session4-demo/demo/session4-coffee-ship` (abbreviated `<ROOT>` below).

Region is **ap-southeast-1** everywhere (CDK env, samconfig, scripts, runbook, SNS, alarms).
This is a fully self-contained greenfield build. Do NOT read or import from
`/Users/erictole/demo/apcr-dva/applications` or `/Users/erictole/demo/apcr-dva/demo/session3`.

## Design decisions (made here, grounded in the task + current tooling)

- **CDK v2, pinned.** Use `aws-cdk-lib` `2.160.0` and `constructs` `^10.3.0`, `aws-cdk` (toolkit, devDep) `2.160.0`, TypeScript `~5.5.4`, `ts-node` `^10.9.2`, `@types/node` `^20.14.0`. These are real, mutually compatible pins (CDK v2 current series is 2.2xx; 2.160 is a safe, widely-available pin). Rationale: task requires pinned/explicit versions and aws-cdk-lib v2.
- **CDK stacks split by layer:** `NetworkDataStack` (VPC with PUBLIC subnets only + no NAT, DynamoDB orders table, SQS orders queue, SSM param, Secrets Manager secret, AppConfig app/env/profile/deployment) and `AppPipelineStack` (ECR + lifecycle, ECS/Fargate+ALB, CodePipeline S3-source→CodeBuild→deploy-test→manual approval(SNS)→deploy-prod, SNS topic, CloudWatch alarms). Rationale: matches "split by layer" and keeps data/network reusable.
- **S3 source pipeline, no GitHub/CodeCommit.** CodePipeline source action is S3 (versioned bucket + zipped `source.zip`). Rationale: task mandates zero external accounts.
- **Lambda canary** via CodeDeploy using `CodeDeployDefault.LambdaCanary10Percent5Minutes` with a CloudWatch alarm rollback, declared in the SAM template's `DeploymentPreference`. Rationale: SAM owns the serverless app; canary belongs with the function + alias.
- **ECS circuit breaker** with `minimumHealthyPercent 100 / maximumPercent 200`, `deploymentController` default rolling, circuit breaker `{ rollback: true }`, task 256 CPU / 512 mem, desiredCount 1. Rationale: cost-light + task spec.
- **Headless gate** in buildspec is a documented no-op placeholder (`exit 0`) modeled as `kiro --headless --prompt "review the deploy log"`. Rationale: must not break the pipeline but must teach the concept.
- **Kiro hook** uses documented v1 schema: `PostFileSave` trigger, matcher `\.py$`, action type `agent`. Static artifact.
- **SAM CLI may be absent** (confirmed not installed locally). Verification treats `sam validate` as conditional; otherwise confirm YAML parses with a Python `yaml.safe_load` (SAM intrinsic tags handled via a permissive loader) or `python -c` check.

## Directory layout (final)

```
<ROOT>/
├── README.md
├── FACILITATOR-RUNBOOK.md
├── deploy.sh
├── destroy.sh
├── .gitignore
├── .kiro/hooks/generate-tests-on-save.kiro.hook   (standalone v1 hook JSON)
├── infra/                      (CDK TypeScript app)
│   ├── package.json
│   ├── tsconfig.json
│   ├── cdk.json
│   ├── bin/coffee-ship.ts
│   └── lib/
│       ├── network-data-stack.ts
│       └── app-pipeline-stack.ts
├── app/                        (SAM serverless app the pipeline ships)
│   ├── template.yaml
│   ├── samconfig.toml
│   ├── appspec.yaml
│   ├── buildspec.yml
│   ├── src/app.py
│   ├── requirements.txt
│   ├── dev-requirements.txt
│   └── tests/test_handler.py
├── container/                  (ECS container path)
│   ├── Dockerfile
│   ├── app.py                  (tiny health/order web app)
│   ├── requirements.txt
│   └── taskdef.json
├── events/
│   ├── apigw-happy.json        (body is a STRING)
│   └── apigw-malformed.json
└── reference/                  ("same SQS queue three ways")
    ├── README.md
    ├── orders-queue.cfn.json
    ├── orders-queue-cdk.ts
    └── orders-queue.sam.yaml
```

## Build order (dependency-ordered)

- [ ] 1. Scaffold project skeleton + root `.gitignore`.
      Create directory tree above (empty dirs ok) and `<ROOT>/.gitignore` ignoring `node_modules/`, `cdk.out/`, `*.pyc`, `__pycache__/`, `.aws-sam/`, `*.zip`, `.venv/`.
      Files: `<ROOT>/.gitignore` plus directories.
      Verify: `ls -R <ROOT>` shows the layout; `bash -n` not applicable yet.

- [ ] 2. CDK app config + dependencies (`infra/package.json`, `tsconfig.json`, `cdk.json`, `bin/coffee-ship.ts`).
      Pin versions as in design decisions; `bin` instantiates both stacks with `env: { region: 'ap-southeast-1', account: process.env.CDK_DEFAULT_ACCOUNT }`.
      Files: `<ROOT>/infra/package.json`, `<ROOT>/infra/tsconfig.json`, `<ROOT>/infra/cdk.json`, `<ROOT>/infra/bin/coffee-ship.ts`.
      Verify: `cd <ROOT>/infra && npm install` succeeds (produces lockfile).

- [ ] 3. `NetworkDataStack` (VPC public-only/no NAT, DynamoDB orders table, SQS orders queue, SSM param, Secrets Manager secret, AppConfig app+env+profile+deployment strategy). Expose VPC/queue/table as public props for the pipeline stack.
      Files: `<ROOT>/infra/lib/network-data-stack.ts`.
      Verify: part of step 5 synth.

- [ ] 4. `AppPipelineStack` (ECR+lifecycle keep-10, ECS/Fargate+ALB with circuit breaker + min100/max200, CodePipeline S3-source→CodeBuild(buildspec)→deploy-test→manual approval→deploy-prod, SNS topic for approval, CloudWatch alarms). Consume props from `NetworkDataStack`.
      Files: `<ROOT>/infra/lib/app-pipeline-stack.ts`.
      Verify: part of step 5 synth.

- [ ] 5. Synth the CDK app clean.
      Files: none new.
      Verify: `cd <ROOT>/infra && npx cdk synth > /dev/null` exits 0 with no errors (set a dummy `CDK_DEFAULT_ACCOUNT=111111111111` if needed).

- [ ] 6. SAM serverless app: `template.yaml` (Transform AWS::Serverless-2016-10-31, Python 3.12, Handler `app.handler`, SQS event source, Lambda version+alias, `DeploymentPreference` canary 10%/5min with alarm), `samconfig.toml` (region ap-southeast-1), `src/app.py` handler, `requirements.txt`, `dev-requirements.txt`.
      Files: `<ROOT>/app/template.yaml`, `<ROOT>/app/samconfig.toml`, `<ROOT>/app/src/app.py`, `<ROOT>/app/requirements.txt`, `<ROOT>/app/dev-requirements.txt`.
      Verify: `sam validate --lint` if SAM CLI present; else `python3 -c "import yaml,sys; ..."` confirms YAML parses (permissive loader for `!` tags).

- [ ] 7. CodeDeploy appspec + CodeBuild buildspec + ECS taskdef.
      `appspec.yaml` references the Lambda alias/version + hooks; `buildspec.yml` installs deps, `sam validate`, runs pytest, runs the headless gate placeholder (`exit 0`, documented); `taskdef.json` for ECS Fargate (256/512).
      Files: `<ROOT>/app/appspec.yaml`, `<ROOT>/app/buildspec.yml`, `<ROOT>/container/taskdef.json`.
      Verify: all parse as YAML/JSON (`python3 -c` / `yaml.safe_load`); documented placeholder exits 0.

- [ ] 8. Lambda unit test + test events.
      pytest test for `app.handler` covering happy path and malformed body; `events/apigw-happy.json` (body is a STRING) and `events/apigw-malformed.json`.
      Files: `<ROOT>/app/tests/test_handler.py`, `<ROOT>/events/apigw-happy.json`, `<ROOT>/events/apigw-malformed.json`.
      Verify: `cd <ROOT>/app && python3 -m pip install -r dev-requirements.txt && python3 -m pytest -q` passes.

- [ ] 9. Container path app + Dockerfile.
      Minimal Python web app (stdlib http.server or tiny Flask pinned) returning health + order echo; Dockerfile FROM python:3.12-slim.
      Files: `<ROOT>/container/app.py`, `<ROOT>/container/requirements.txt`, `<ROOT>/container/Dockerfile`.
      Verify: `python3 -c "compile(open('<ROOT>/container/app.py').read(),'app.py','exec')"` ok; Dockerfile lints by inspection (no build required).

- [ ] 10. Reference "queue three ways" + README.
      Same SQS orders queue as raw CFN JSON, CDK TS construct snippet, and SAM resource; README explains the teaching intent.
      Files: `<ROOT>/reference/orders-queue.cfn.json`, `<ROOT>/reference/orders-queue-cdk.ts`, `<ROOT>/reference/orders-queue.sam.yaml`, `<ROOT>/reference/README.md`.
      Verify: JSON parses; YAML parses; TS snippet matches CDK construct used in step 3.

- [ ] 11. Kiro hook JSON (v1 schema).
      `PostFileSave`, matcher `\.py$`, action type `agent` to generate/update unit tests.
      Files: `<ROOT>/.kiro/hooks/generate-tests-on-save.kiro.hook`.
      Verify: `python3 -c "import json; json.load(open(...))"` parses; fields match v1 schema (version, enabled, when.type=PostFileSave, when.patterns, then.type=agent, then.prompt).

- [ ] 12. deploy.sh + destroy.sh.
      Bash, `set -euo pipefail`, region pinned ap-southeast-1. deploy: cdk bootstrap note, docker build+push to ECR, zip+upload SAM source to S3 source bucket, cdk deploy; echo ALB URL + API endpoint. destroy: confirmation prompt, cdk destroy, empty+delete buckets, delete ECR images.
      Files: `<ROOT>/deploy.sh`, `<ROOT>/destroy.sh`.
      Verify: `bash -n <ROOT>/deploy.sh && bash -n <ROOT>/destroy.sh` exit 0.

- [ ] 13. README.md + FACILITATOR-RUNBOOK.md.
      README: prerequisites, architecture, cost warning, deploy/destroy commands. Runbook: five acts mapped to services + teardown reminder.
      Files: `<ROOT>/README.md`, `<ROOT>/FACILITATOR-RUNBOOK.md`.
      Verify: files exist, internal paths/commands match the actual tree.

- [ ] 14. Full verification pass.
      Files: none.
      Verify: `cd <ROOT>/infra && npm install && npx cdk synth >/dev/null`; `cd <ROOT>/app && python3 -m pytest -q`; `bash -n` both scripts; hook + JSON/YAML parse; `sam validate --lint` if available (report if not). Report what was verified and what could not be. Do NOT run `cdk deploy`.

## Assumptions
- SAM CLI is not installed in the build environment (confirmed); `sam validate` is best-effort and YAML parse is the hard gate.
- A dummy AWS account id can be exported for `cdk synth` since no credentials/deploy are required.
- Node 20+/npm available; local Python 3.13 runs pytest fine for a 3.12-targeted handler (no 3.12-only syntax used).
