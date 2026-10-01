# Design — Separate Test/Prod ECS environments + real CodeDeploy ECS blue/green

> **Revision note.** This is a revised design incorporating `design-review.md` (CHANGES_REQUESTED: 1 HIGH, 3 MEDIUM, 4 NIT). All findings are addressed; see "Responses to design review" at the end for the per-finding resolution. Key changes from the reviewed draft: prod ALB listeners are now `open: false` with a prefix-list-only rule (finding 1); the buildspec substitution mechanism is committed to and fully specified with exact commands (findings 2–3); the port-8080 test listener gets no internet ingress and its no-validation role is stated (finding 4).

## Overview

The `coffee-ship` demo currently stands up a **single** ECS Fargate service and points **both** the pipeline's `Deploy-Test` and `Deploy-Prod` `EcsDeployAction`s at it, so there is no real difference between test and prod and no blue/green deployment to show students. This design re-architects the delivery topology so that:

1. **Test** is its own ECS Fargate service behind its own ALB, deployed by a standard CodePipeline `EcsDeployAction` (ECS **rolling** update with a deployment circuit breaker + rollback).
2. **Prod** is a separate ECS Fargate service whose `deploymentController` is `CODE_DEPLOY`, fronted by its own ALB with **two listeners** (prod + test/replacement) and **two target groups** (blue + green), driven by a real **CodeDeploy ECS blue/green** deployment group (`CodeDeployDefault.ECSCanary10Percent5Minutes`) with automatic rollback on deployment failure and on a CloudWatch alarm.
3. The CodeBuild stage emits **both** `imagedefinitions.json` (for the rolling test deploy) **and** `appspec.yaml` + `taskdef.json` (for the CodeDeploy prod deploy).
4. The user-facing app name becomes **"Coffee Shop"** via a single `APP_NAME` constant; internal resource names stay `coffee-ship`.
5. The diagram, README, FACILITATOR-RUNBOOK, and a new step-by-step demo script are updated to show the separate environments and the blue/green promotion, including a code edit that renames "Coffee Shop" → "BeanThere Cafe" and runs the pipeline.

The technology stack is **locked** by the existing project and does not change: AWS CDK v2 TypeScript (`aws-cdk-lib` 2.160.0, cdk CLI 2.1126.0), Node tooling via `npx`, the Python 3.12 boto3 container app, the Vite/React 18 SPA, CodePipeline with an S3 source, CodeBuild (privileged Docker), ECR, ECS Fargate, ALB, CloudFront, DynamoDB, SQS, SSM, Secrets Manager, AppConfig. Region `ap-southeast-1`, account `875692608981`, VPC imported from CloudFormation exports (no VPC created). **Verification is LOCAL only: `npm install` + `tsc`/`cdk synth` for infra, `npm run build` for the SPA, `python -m py_compile` for the container, `python3 build_diagram.py` for the diagram. NO live AWS deploy.**

All CDK changes live in `infra/lib/app-pipeline-stack.ts` (the `AppPipelineStack`), which already owns ECR, the cluster, the service, the ALB, CloudFront, the SNS topic, the alarm, and the pipeline. `infra/bin/coffee-ship.ts` and `infra/lib/network-data-stack.ts` need no structural change (the data plane is shared by both services). The container artifacts (`buildspec.yml`, a new `taskdef.json`, a new `appspec.yaml`) and the frontend rename round out the change.

---

## Decision 1 — Test environment (dedicated service, rolling deploy)

**Construct.** Keep using `ecs_patterns.ApplicationLoadBalancedFargateService` for Test, because it already gives us the ALB + listener + target group + service wiring that the current code relies on, and the rolling `EcsDeployAction` consumes `imagedefinitions.json` exactly as today. This is the lowest-risk, most pattern-consistent choice.

```
const testService = new ecs_patterns.ApplicationLoadBalancedFargateService(this, 'CoffeeShipTestService', {
  cluster: testCluster,          // see Decision below on clusters
  serviceName: 'coffee-ship-test',
  cpu: 256, memoryLimitMiB: 512, desiredCount: 1,
  assignPublicIp: true,
  taskSubnets: { subnetType: ec2.SubnetType.PUBLIC },
  publicLoadBalancer: true,
  minHealthyPercent: 100, maxHealthyPercent: 200,
  circuitBreaker: { rollback: true },
  healthCheckGracePeriod: cdk.Duration.seconds(120),
  taskImageOptions: {
    image: ecs.ContainerImage.fromEcrRepository(repository, 'latest'),
    containerName: 'web',        // make the name EXPLICIT (see Decision 3 note)
    containerPort: 8080,
    environment: { ORDERS_QUEUE_URL: ordersQueue.queueUrl, ORDERS_TABLE_NAME: ordersTable.tableName },
  },
});
```

The pattern defaults the container name to `"web"`; today the code relies on that implicit default. We set `containerName: 'web'` **explicitly** so the test `imagedefinitions.json` (`name: "web"`) and the prod `taskdef.json`/`appspec.yaml` (which also reference `web`) are provably aligned and cannot drift if a future CDK default changes.

**Clusters.** The task explicitly asks for a separate ECS cluster for Test and Prod so students can see the difference. Create two clusters in the imported VPC:

```
const testCluster = new ecs.Cluster(this, 'CoffeeShipTestCluster', { vpc, clusterName: 'coffee-ship-test' });
const prodCluster = new ecs.Cluster(this, 'CoffeeShipProdCluster', { vpc, clusterName: 'coffee-ship-prod' });
```

(The old single `clusterName: 'coffee-ship'` is replaced by these two. This is a resource rename in CloudFormation — on a real deploy it would replace the cluster, which is fine for a demo and irrelevant to `cdk synth`.)

**Deploy action (unchanged shape).**

```
const deployTestAction = new codepipeline_actions.EcsDeployAction({
  actionName: 'Deploy_To_Test',
  service: testService.service,
  input: buildOutput,            // reads imagedefinitions.json
});
```

**Data-plane grants (both services keep them — Decision 7 of the brief).**

```
ordersQueue.grantConsumeMessages(testService.taskDefinition.taskRole);
ordersTable.grantReadWriteData(testService.taskDefinition.taskRole);
props.loyaltyParam.grantRead(testService.taskDefinition.taskRole);
repository.grantPull(testService.taskDefinition.obtainExecutionRole());
```

---

## Decision 2 — Prod environment (CODE_DEPLOY controller, blue/green)

`ecs_patterns.ApplicationLoadBalancedFargateService` cannot model CodeDeploy blue/green cleanly (it owns a single listener/target group and defaults the deployment controller to ECS rolling). So for **prod** we drop to the lower-level constructs and build the blue/green topology by hand. This is a deliberate, reasoned deviation from the pattern used for test, because blue/green **requires** two target groups and a second (test) listener that the pattern does not expose.

**Prod ALB + two target groups + two listeners.**

```
const prodAlb = new elbv2.ApplicationLoadBalancer(this, 'CoffeeShipProdAlb', {
  vpc, internetFacing: true,
  vpcSubnets: { subnetType: ec2.SubnetType.PUBLIC },
});

const prodBlueTg = new elbv2.ApplicationTargetGroup(this, 'ProdBlueTg', {
  vpc, port: 8080, protocol: elbv2.ApplicationProtocol.HTTP,
  targetType: elbv2.TargetType.IP,
  healthCheck: { path: '/', healthyHttpCodes: '200' },
  deregistrationDelay: cdk.Duration.seconds(10),
});
const prodGreenTg = new elbv2.ApplicationTargetGroup(this, 'ProdGreenTg', {
  vpc, port: 8080, protocol: elbv2.ApplicationProtocol.HTTP,
  targetType: elbv2.TargetType.IP,
  healthCheck: { path: '/', healthyHttpCodes: '200' },
  deregistrationDelay: cdk.Duration.seconds(10),
});

// Production listener (port 80) — serves live traffic, starts on blue.
// CRITICAL: open:false. `addListener` defaults open:true, which injects a
// 0.0.0.0/0 ingress rule on the ALB SG for the listener port (verified in
// aws-cdk-lib/aws-elasticloadbalancingv2 ApplicationListenerProps.open,
// @default true). Requirement 4 forbids ANY 0.0.0.0/0 on either ALB, so we
// must disable the auto-open and add the prefix-list rule ourselves.
const prodListener = prodAlb.addListener('ProdListener', {
  port: 80, protocol: elbv2.ApplicationProtocol.HTTP,
  open: false,
  defaultTargetGroups: [prodBlueTg],
});
// Test/replacement listener (port 8080) — CodeDeploy's blue/green orchestration
// shifts the replacement (green) task set here before promoting it to the prod
// listener. open:false for the same reason; see Decision 4 for who may reach it.
const prodTestListener = prodAlb.addListener('ProdTestListener', {
  port: 8080, protocol: elbv2.ApplicationProtocol.HTTP,
  open: false,
  defaultTargetGroups: [prodGreenTg],
});
```

Health check path is `/`, which `app.py` answers with the SPA `index.html` at HTTP 200 (confirmed in `app.py` `_serve_index`), matching the current test health check.

**What the port-8080 "test" listener does (and does not) do.** CodeDeploy's ECS blue/green config requires a second ("test") listener; CodeDeploy registers the green task set behind `prodGreenTg`, uses the test listener during its internal validation window, then reroutes the prod listener from blue to green per the canary schedule. In **this demo there is no automated pre-promotion test**: the appspec defines no `BeforeAllowTraffic`/`AfterAllowTestTraffic` lifecycle hooks, and the manual approval gate *before* `Deploy-Prod` is the human checkpoint. The test listener therefore exists only to satisfy the blue/green contract; nothing external (not CloudFront, not a reviewer) is wired to probe it, and its port is **not** opened to the internet (see Decision 4). The green task set's own ECS/ALB target-group health check (`path: '/'`) is still what gates traffic shift — a green task that fails health checks blocks the shift and triggers `failedDeployment` rollback.

**Prod task definition + service with CODE_DEPLOY controller.**

```
const prodTaskDef = new ecs.FargateTaskDefinition(this, 'ProdTaskDef', {
  family: 'coffee-ship-prod',
  cpu: 256, memoryLimitMiB: 512,
});
const prodContainer = prodTaskDef.addContainer('web', {   // name MUST be 'web'
  image: ecs.ContainerImage.fromEcrRepository(repository, 'latest'),
  logging: ecs.LogDrivers.awsLogs({ streamPrefix: 'coffee-ship-prod' }),
  environment: { ORDERS_QUEUE_URL: ordersQueue.queueUrl, ORDERS_TABLE_NAME: ordersTable.tableName },
});
prodContainer.addPortMappings({ containerPort: 8080, protocol: ecs.Protocol.TCP });

const prodService = new ecs.FargateService(this, 'CoffeeShipProdService', {
  cluster: prodCluster,
  serviceName: 'coffee-ship-prod',
  taskDefinition: prodTaskDef,
  desiredCount: 1,
  assignPublicIp: true,
  vpcSubnets: { subnetType: ec2.SubnetType.PUBLIC },
  minHealthyPercent: 100, maxHealthyPercent: 200,
  healthCheckGracePeriod: cdk.Duration.seconds(120),
  deploymentController: { type: ecs.DeploymentControllerType.CODE_DEPLOY },
});
// Register the service with the BLUE target group only; CodeDeploy manages green.
prodService.attachToApplicationTargetGroup(prodBlueTg);
```

Same data-plane grants as test are added to `prodTaskDef.taskRole`, plus `repository.grantPull(prodTaskDef.obtainExecutionRole())`.

**`LOYALTY_PARAM_NAME` env var (resolves review finding 6).** Neither the test service nor the prod taskdef sets `LOYALTY_PARAM_NAME`; both intentionally rely on the `app.py` default `/coffee-ship/loyalty/points-per-dollar`, which exactly matches the SSM parameter created in `network-data-stack.ts` (verified). This is deliberate parity with the existing single-service design — the implementer should **not** "fix" this by adding the env var to one service and not the other. Setting only `ORDERS_QUEUE_URL` + `ORDERS_TABLE_NAME` on both services is the intended, consistent shape.

**CodeDeploy application + ECS blue/green deployment group.**

```
const prodDeployApp = new codedeploy.EcsApplication(this, 'ProdCodeDeployApp', {
  applicationName: 'coffee-ship-prod',
});
const prodDeployGroup = new codedeploy.EcsDeploymentGroup(this, 'ProdDeployGroup', {
  application: prodDeployApp,
  deploymentGroupName: 'coffee-ship-prod',
  service: prodService,
  blueGreenDeploymentConfig: {
    blueTargetGroup: prodBlueTg,
    greenTargetGroup: prodGreenTg,
    listener: prodListener,
    testListener: prodTestListener,
    // keep the old (blue) task set 10 min after a successful shift so a manual
    // console rollback is possible without a full redeploy.
    terminationWaitTime: cdk.Duration.minutes(10),
  },
  deploymentConfig: codedeploy.EcsDeploymentConfig.CANARY_10PERCENT_5MINUTES,
  autoRollback: { failedDeployment: true, deploymentInAlarm: true },
  alarms: [prodUnhealthyHostAlarm],   // see Decision 2 "Prod alarm" below
});
```

`EcsDeploymentConfig.CANARY_10PERCENT_5MINUTES` maps to the managed `CodeDeployDefault.ECSCanary10Percent5Minutes` config requested in the brief. `autoRollback.deploymentInAlarm: true` wires the alarm so a prod spike rolls the deployment back automatically; `failedDeployment: true` covers task-set launch/health failures.

**Prod alarm.** Add a prod-specific CloudWatch alarm wired into `autoRollback`. Alarm on the **blue target group unhealthy host count** (reliable signal that the live task set is failing health checks). We keep the metric source simple and verifiable at synth time:

```
const prodUnhealthyHostAlarm = new cloudwatch.Alarm(this, 'ProdUnhealthyHostAlarm', {
  alarmName: 'coffee-ship-prod-unhealthy-hosts',
  metric: prodBlueTg.metrics.unhealthyHostCount({ period: cdk.Duration.minutes(1), statistic: cloudwatch.Stats.MAXIMUM }),
  threshold: 1, evaluationPeriods: 1,
  comparisonOperator: cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
  treatMissingData: cloudwatch.TreatMissingData.NOT_BREACHING,
});
```

**Design note / unverified assumption on the alarm during a healthy deploy.** During a blue/green cut-over the green target group briefly has 0 healthy hosts while the replacement task registers. We alarm on **blue** (the stable live set), not green, specifically to avoid a false rollback during the normal registration window. A 5xx-based alarm on the ALB was considered but rejected for the demo: unhealthy-host count is deterministic and does not require generating traffic to populate the metric, so it is easier for a reviewer/student to reason about. This is called out as an assumption to validate on a future live run; it does not affect `cdk synth`.

**Rename `UnhealthyHostAlarm` → test alarm.** The existing `coffee-ship-unhealthy-hosts` alarm becomes the **test** alarm (metric from `testService.targetGroup`), renamed to `coffee-ship-test-unhealthy-hosts`, so test and prod alarms are distinct.

---

## Decision 3 — Build artifacts (both rolling + blue/green inputs)

The build must now produce two artifact sets from one CodeBuild run.

**Buildspec outputs (`container/buildspec.yml`).** Keep the existing docker build/push and `imagedefinitions.json` emission; add generation of `taskdef.json` and `appspec.yaml` for the prod CodeDeploy action. The build already resolves `ACCOUNT_ID`, `REPO_URI`, and `IMAGE_TAG`.

- `imagedefinitions.json` — unchanged, `[{"name":"web","imageUri":"$REPO_URI:$IMAGE_TAG"}]`. Consumed by the **test** rolling action.
- `taskdef.json` — the prod task-definition template, checked into `container/taskdef.json`. The buildspec reads it, substitutes the role ARNs and queue URL from CodeBuild env vars, writes the result to the **artifact root** `taskdef.json`, and leaves `<IMAGE1_NAME>` intact for CodeDeploy. The image placeholder is resolved by the pipeline action's `containerImageInputs[0].taskDefinitionPlaceholder = 'IMAGE1_NAME'`, not by the build.
- `appspec.yaml` — the ECS blue/green appspec checked into `container/appspec.yaml`; copied to the artifact root unchanged (it references `<TASK_DEFINITION>`, which the `CodeDeployEcsDeployAction` fills in from the registered task definition).

**Committed substitution mechanism (resolves review findings 2 & 3).** There is exactly **one** mechanism, and it is mandatory — not an either/or. The buildspec substitutes `<EXECUTION_ROLE_ARN>`, `<TASK_ROLE_ARN>`, and `<ORDERS_QUEUE_URL>` with the CodeBuild env-var values **in the build**; only `<IMAGE1_NAME>` is left for CodeDeploy. The pipeline action's `taskDefinitionTemplateInput` and `appSpecTemplateInput` both point at the single `buildOutput` artifact, so by the time CodeDeploy calls `RegisterTaskDefinition` the role ARNs and queue URL are already real literals. (A taskdef still carrying literal `<EXECUTION_ROLE_ARN>` would be rejected by `RegisterTaskDefinition`, which is why the substitution is required, not optional.)

Exact `post_build` commands (replacing the current `imagedefinitions.json`-only block). The `test -n` guard makes the build **fail loudly** if any required env var is empty rather than emitting a broken taskdef:

```yaml
  post_build:
    commands:
      - echo "Pushing images to ECR..."
      - docker push "$REPO_URI:$IMAGE_TAG"
      - docker push "$REPO_URI:latest"
      # (1) imagedefinitions.json for the TEST rolling EcsDeployAction.
      - printf '[{"name":"web","imageUri":"%s"}]' "$REPO_URI:$IMAGE_TAG" > imagedefinitions.json
      # (2) Fail loudly if any prod substitution var is missing.
      - test -n "$PROD_EXECUTION_ROLE_ARN" && test -n "$PROD_TASK_ROLE_ARN" && test -n "$ORDERS_QUEUE_URL"
      # (3) Render the prod taskdef template -> artifact-root taskdef.json;
      #     leave <IMAGE1_NAME> for CodeDeploy. '#' delimiter avoids '/' in ARNs/URLs.
      - |
        sed -e "s#<EXECUTION_ROLE_ARN>#${PROD_EXECUTION_ROLE_ARN}#g" \
            -e "s#<TASK_ROLE_ARN>#${PROD_TASK_ROLE_ARN}#g" \
            -e "s#<ORDERS_QUEUE_URL>#${ORDERS_QUEUE_URL}#g" \
            container/taskdef.json > taskdef.json
      # (4) appspec.yaml for CodeDeploy (copied unchanged to the artifact root).
      - cp container/appspec.yaml appspec.yaml
      - cat imagedefinitions.json taskdef.json appspec.yaml
```

Env-var → token mapping (CDK sets these on the build project; keys MUST match):

| CodeBuild env var          | source (CDK)                               | taskdef token          |
|----------------------------|--------------------------------------------|------------------------|
| `PROD_EXECUTION_ROLE_ARN`  | `prodTaskDef.obtainExecutionRole().roleArn`| `<EXECUTION_ROLE_ARN>` |
| `PROD_TASK_ROLE_ARN`       | `prodTaskDef.taskRole.roleArn`             | `<TASK_ROLE_ARN>`      |
| `ORDERS_QUEUE_URL`         | `ordersQueue.queueUrl`                     | `<ORDERS_QUEUE_URL>`   |

`ORDERS_TABLE_NAME` is **not** substituted — the table name is the fixed literal `coffee-ship-orders` (verified in `network-data-stack.ts`), so it is hard-coded in the template, matching the live resource name.

CodeBuild `artifacts` section lists all three files at the artifact root:

```
artifacts:
  files:
    - imagedefinitions.json
    - taskdef.json
    - appspec.yaml
```

**New `container/taskdef.json`** (replaces the current stale one; family `coffee-ship-prod`, container name `web`, image placeholder `<IMAGE1_NAME>`):

```
{
  "family": "coffee-ship-prod",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "runtimePlatform": { "cpuArchitecture": "X86_64", "operatingSystemFamily": "LINUX" },
  "executionRoleArn": "<EXECUTION_ROLE_ARN>",
  "taskRoleArn": "<TASK_ROLE_ARN>",
  "containerDefinitions": [
    {
      "name": "web",
      "image": "<IMAGE1_NAME>",
      "essential": true,
      "portMappings": [{ "containerPort": 8080, "protocol": "tcp" }],
      "environment": [
        { "name": "ORDERS_QUEUE_URL", "value": "<ORDERS_QUEUE_URL>" },
        { "name": "ORDERS_TABLE_NAME", "value": "coffee-ship-orders" }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/coffee-ship-prod",
          "awslogs-region": "ap-southeast-1",
          "awslogs-stream-prefix": "coffee-ship-prod"
        }
      }
    }
  ]
}
```

The buildspec resolves `<EXECUTION_ROLE_ARN>`, `<TASK_ROLE_ARN>`, and `<ORDERS_QUEUE_URL>` at build time from the env vars above (set by the CDK on the build project via `environmentVariables`). This avoids hard-coding ARNs and keeps the template account-agnostic. `<IMAGE1_NAME>` is left untouched for CodeDeploy.

> **CDK dependency ordering (verify at synth):** sourcing the build project's `environmentVariables` from `prodTaskDef.obtainExecutionRole().roleArn` / `prodTaskDef.taskRole.roleArn` / `ordersQueue.queueUrl` creates a CloudFormation dependency from the build project to the prod task definition and the queue. Both the task def and the build project live in `AppPipelineStack`, so this is an in-stack dependency CDK orders automatically — acceptable and correct. There is no alternative "resolve it in CodeDeploy instead" path: the taskdef that CodeDeploy registers MUST already contain real role ARNs, so the build-time substitution is the single mechanism (see "Committed substitution mechanism" above).

**New `container/appspec.yaml`** (ECS blue/green form — replaces the Lambda-oriented `app/appspec.yaml`, which stays for the serverless path; this new one lives in `container/`):

```
version: 0.0
Resources:
  - TargetService:
      Type: AWS::ECS::Service
      Properties:
        TaskDefinition: <TASK_DEFINITION>
        LoadBalancerInfo:
          ContainerName: "web"
          ContainerPort: 8080
        PlatformVersion: "LATEST"
```

**Pipeline wiring for prod (CodeDeployEcsDeployAction).**

```
const deployProdAction = new codepipeline_actions.CodeDeployEcsDeployAction({
  actionName: 'Deploy_To_Prod',
  deploymentGroup: prodDeployGroup,
  appSpecTemplateInput: buildOutput,          // appspec.yaml at artifact root
  taskDefinitionTemplateInput: buildOutput,   // taskdef.json at artifact root
  containerImageInputs: [{
    input: buildOutput,
    taskDefinitionPlaceholder: 'IMAGE1_NAME',  // matches <IMAGE1_NAME>
  }],
});
```

Because both the appspec and taskdef live at the **root** of the single build artifact, no custom file names are needed; `CodeDeployEcsDeployAction` defaults to `appspec.yaml` and `taskdef.json`. The one build artifact (`buildOutput`) feeds the test action (via `imagedefinitions.json`) and the prod action (via `appspec.yaml` + `taskdef.json`), so the pipeline keeps a single Build stage with a single output artifact.

**Final pipeline stages:**

```
Source (S3 source.zip, EventBridge trigger)
  -> Build (CodeBuild privileged docker; emits imagedefinitions.json + taskdef.json + appspec.yaml)
  -> Deploy-Test  (EcsDeployAction, rolling, coffee-ship-test service)
  -> Approval     (ManualApprovalAction, SNS coffee-ship-approval)
  -> Deploy-Prod  (CodeDeployEcsDeployAction, blue/green, coffee-ship-prod)
```

---

## Decision 4 — Security topology for BOTH ALBs

Both ALBs stay locked to the CloudFront origin-facing prefix list; **no `0.0.0.0/0` ingress on either ALB**. The `CloudFrontPrefixListId` `CfnParameter` (default `pl-31a34658`) is kept and reused for both.

**Chosen CloudFront topology (simplest acceptable):**
- The **prod** ALB is the CloudFront origin (replacing the current single-service origin). The `CloudFrontUrl` output continues to point students at prod.
- The **test** ALB is reachable for reviewer verification but **still prefix-list-locked** — it is added as a **second origin + second cache behavior** on the *same* CloudFront distribution under a path prefix (e.g. `/__test/*` → test ALB origin) **OR**, preferred for clarity, a **second CloudFront distribution** dedicated to test. 

**Decision: second cache behavior on one distribution is rejected** because the SPA uses same-origin absolute paths (`/order`, `/orders`, `/health`, `/architecture.svg`) and a path-prefixed behavior would break those relative calls for the test app. Instead we add a **second CloudFront distribution** (`CoffeeShipTestCdn`) whose origin is the test ALB, output as `TestCloudFrontUrl`. Both distributions use `CACHING_DISABLED` + `ALL_VIEWER` origin request policy, exactly like the existing one, so the SPA's same-origin API calls work unchanged for both environments.

**Scope acknowledgement (resolves review finding 5).** The second CloudFront distribution is a second billable, slow-to-provision resource whose only purpose is to give a reviewer/student a prefix-list-locked way to see the TEST environment in a browser. It is deliberate, justified purely by (a) the SPA's same-origin routing (which rules out a path-prefixed single-distribution behavior) and (b) the requirement that TEST be reviewer-verifiable while staying locked down. It mirrors the prod distribution's config exactly (`CACHING_DISABLED` + `ALL_VIEWER`), so it adds no new config surface — only a second instance of the same pattern.

Each ALB's auto-created `0.0.0.0/0` ingress is stripped and replaced with a single prefix-list rule, reusing the existing override pattern:

- Test ALB SG: the `ApplicationLoadBalancedFargateService` opens `0.0.0.0/0`; we apply the same `cfnAlbSg.addPropertyOverride('SecurityGroupIngress', [...])` override already in the code, pointing at the prefix list.
- Prod ALB SG: the prod ALB is created directly, and **both listeners are created with `open: false`** (see Decision 2) so CDK injects **no** `0.0.0.0/0` rule. We then add exactly one internet-facing ingress rule — the prod listener (port 80) from the CloudFront prefix list:
  ```
  prodListener.connections.allowDefaultPortFrom(
    ec2.Peer.prefixList(cloudFrontPrefixList.prefixListId), 'CloudFront prod listener');
  ```
  **Port 8080 (the CodeDeploy test/replacement listener) gets NO internet ingress at all** — not from CloudFront, not from `0.0.0.0/0`. Rationale (resolves review finding 4): the port-8080 listener exists solely to satisfy CodeDeploy's blue/green requirement for a second listener; CodeDeploy orchestrates the green task-set validation and traffic shift via the ELB APIs, so it does not need the listener reachable from the public internet or from CloudFront. This demo defines **no** `BeforeAllowTraffic`/`AfterAllowTestTraffic` lifecycle hook and does **no** automated pre-promotion probe of green, so nothing external hits 8080. Leaving 8080 closed to the internet keeps the "no `0.0.0.0/0`" invariant trivially true and makes the SG minimal. If a future iteration wants reviewers to manually hit green before approval, that is a deliberate, separately-added prefix-list rule + a documented path — out of scope here.

**How a reviewer verifies TEST.** Use the `TestCloudFrontUrl` output (`https://<test-dist>.cloudfront.net/`). `GET /` returns the Coffee Shop SPA; `GET /health` returns the running version; `POST /order` + `GET /orders` exercise the same DynamoDB table. The test ALB DNS name itself returns nothing to the public internet (SG admits only CloudFront), proving the lock. This is documented in README + runbook. (Live verification is out of scope for this pass — synth only.)

**Imported VPC unchanged.** Both ALBs and both services use the imported VPC and its three public subnets; no VPC, subnet, or NAT is created.

---

## Decision 5 — Rename to "Coffee Shop" via a single constant

User-visible name becomes **"Coffee Shop"** everywhere a human sees it; internal resource names (`coffee-ship` ECR repo, clusters `coffee-ship-test`/`coffee-ship-prod`, stacks, pipeline, DynamoDB/SQS) stay as-is.

**Single source of truth.** Add `export const APP_NAME = 'Coffee Shop';` at the top of `container/frontend/src/App.jsx`. Use it in:
- the header `<h1>` — `{`☕ ${APP_NAME}`}` (replacing the literal `☕ Coffee Ship`),
- `document.title` — set via a `useEffect(() => { document.title = APP_NAME; }, [])` so the browser tab matches without a build-time HTML edit.

`container/frontend/index.html` `<title>` is set to `Coffee Shop` as the static fallback (shown before React hydrates), kept consistent with `APP_NAME`. The `alt` text on the architecture `<img>` and any other visible copy referencing "Coffee Ship" are updated to `APP_NAME` / "Coffee Shop".

**Why this shape.** The brief's demo edit changes the name to "BeanThere Cafe". With `APP_NAME` as the one constant driving both the header and `document.title`, that demo edit is a **one-line change** to `APP_NAME` (plus the one-word `index.html` fallback), which is exactly the "change the page name and run the pipeline" story. `app.py`'s `APP_VERSION` stays the independent version signal shown next to the name.

**Container app (resolves review finding 8).** `app.py` serves the baked SPA, so no server-side string drives the real UI name. The tiny HTML fallback in `_serve_index` (`<title>coffee-ship</title>`) is shown **only** in degraded mode — when the SPA failed to bake into the image. **Decision: leave `_serve_index` exactly as-is.** It is a degraded-mode placeholder, not user-facing demo copy, and keeping it untouched means the rename stays a one-line `APP_NAME` change in `App.jsx` (plus the one-word `index.html` fallback) with zero container-code churn. The demo edit to "BeanThere Cafe" never touches `app.py`.

---

## Decision 6 — First-run / bootstrap order (two services + CodeDeploy)

The chicken-and-egg problem is larger now: the prod `FargateService` with a CODE_DEPLOY controller will not accept image rolls from `cdk deploy` (CodeDeploy owns deployments), and CodeDeploy needs a **registered task definition** and a **running task set** before it can run a blue/green deployment. Ordering:

1. **`cdk deploy --all`** creates: ECR (empty), both clusters, the test service + test ALB, the prod service + prod ALB (two listeners, two target groups), the CodeDeploy app + deployment group, both CloudFront distributions, the pipeline, SNS, alarms. The prod service launches a task from `coffee-ship:latest`; like today it will **not** stabilize until an image exists — expected.
2. **Seed ECR `:latest`** (as `deploy.sh` already does) so both services can pull a startable image. This gives the prod service an initial (blue) running task set that CodeDeploy can later replace. Without a seeded image the prod service has no stable blue task set and the first CodeDeploy deployment has nothing to shift from.
3. **First pipeline run** (upload `source.zip`): Build pushes a uniquely tagged image and emits all three artifact files. `Deploy-Test` rolls the test service (rolling) to the new image. Approve. `Deploy-Prod` runs the **first CodeDeploy blue/green deployment**: it registers the new prod task definition from `taskdef.json`, launches the green task set, shifts the prod listener per the canary config, and (on success) terminates blue after `terminationWaitTime`.
4. Subsequent uploads repeat step 3; every prod promotion is a real blue/green cut-over.

**Bootstrap note for `deploy.sh`:** the existing seed step (build + push `:latest`) is still required and now matters for **both** services — keep it. Document that the prod service's `desiredCount` must be ≥ 1 with a seeded image before the first CodeDeploy run, else the deployment group has no blue task set.

**Unverified assumption:** that a CODE_DEPLOY-controlled `FargateService` created by CDK comes up with a usable blue task set once `:latest` is seeded, and that the first `CodeDeployEcsDeployAction` succeeds against it. This is the standard documented flow but is **not** verified here (synth only, no live deploy). Called out explicitly.

---

## IAM additions

- **Test rolling deploy:** `EcsDeployAction` auto-grants `ecs:UpdateService`, `ecs:DescribeServices`, `ecs:RegisterTaskDefinition`, and `iam:PassRole` for the test task/execution roles to the action role — no manual policy needed (same as today).
- **Prod CodeDeploy service role:** `codedeploy.EcsDeploymentGroup` creates a CodeDeploy service role with the AWS managed `AWSCodeDeployRoleForECS` policy by default. Verify it includes `ecs:*` task-set APIs, `elasticloadbalancing:*` on the listeners/target groups, `cloudwatch:DescribeAlarms`, and `iam:PassRole` for the prod task + execution roles. If the default role is insufficient, attach `iam:PassRole` for `prodTaskDef.taskRole` and `prodTaskDef.obtainExecutionRole()` explicitly.
- **Pipeline prod action role:** `CodeDeployEcsDeployAction` grants the pipeline action role `codedeploy:CreateDeployment`, `codedeploy:GetDeployment*`, `codedeploy:RegisterApplicationRevision`, and the `ecs:RegisterTaskDefinition` + `iam:PassRole` needed to register the prod task definition from `taskdef.json`. Confirm `iam:PassRole` covers both prod roles (CDK usually scopes this automatically from the action; if synth shows a wildcard or a gap, add an explicit grant).
- **CodeBuild env-var role ARNs:** passing the prod role ARNs as build env vars needs no extra IAM (they are plain strings); `repository.grantPullPush(buildProject)` stays.
- **Task roles (both services, unchanged requirement):** keep DynamoDB read/write (`ordersTable.grantReadWriteData`), SQS consume (`ordersQueue.grantConsumeMessages`), and `ssm:GetParameter` (`loyaltyParam.grantRead`) on **both** the test and prod task roles; `repository.grantPull` on both execution roles.

New CDK imports in `app-pipeline-stack.ts`: `aws-cdk-lib/aws-elasticloadbalancingv2` (as `elbv2`) and `aws-cdk-lib/aws-codedeploy` (as `codedeploy`).

---

## Error handling (per operation that can fail)

- **Test rolling deploy fails health checks:** deployment **circuit breaker** (`circuitBreaker: { rollback: true }`, `minHealthyPercent 100`) rolls the test service back to the prior task def automatically. Pipeline `Deploy-Test` action goes to **Failed**; the pipeline stops before Approval. Recoverable: fix the image, re-upload. Logged to the pipeline execution history + ECS service events.
- **Prod CodeDeploy deployment fails (task launch/health):** `autoRollback.failedDeployment: true` reverts traffic to blue; green task set is torn down. `Deploy-Prod` action → **Failed**. Blue keeps serving (zero downtime). Recoverable.
- **Prod post-shift alarm fires:** `autoRollback.deploymentInAlarm: true` + `coffee-ship-prod-unhealthy-hosts` alarm triggers CodeDeploy rollback to blue. Recoverable; alarm state visible in CloudWatch and the deployment history.
- **ECR pull failure on first boot (no image seeded):** service tasks fail to start and never stabilize — this is the documented bootstrap state (fatal to `cdk deploy` stabilization, resolved by seeding `:latest`). Expected, not an error to "handle."
- **Build compile/`docker build` failure:** `python -m py_compile` or a nonzero docker exit fails the Build action (no `|| true`); pipeline stops before any deploy. Recoverable.
- **appspec/taskdef substitution failure in build (missing env var):** buildspec should `set -e`-style fail if `PROD_EXECUTION_ROLE_ARN`/`PROD_TASK_ROLE_ARN`/`ORDERS_QUEUE_URL` are empty, so a misconfigured build fails loudly in CodeBuild rather than emitting a broken taskdef that CodeDeploy later rejects. Logged to CodeBuild logs.
- **Prefix-list / CloudFront misconfig:** out of scope at synth; a wrong `CloudFrontPrefixListId` would make the ALB unreachable from CloudFront (502 at the edge). Documented, not code-handled.

---

## Input validation

- `CloudFrontPrefixListId` `CfnParameter`: string, defaulted to `pl-31a34658`, overridable per region; no runtime validation beyond CloudFormation's (an invalid prefix-list id fails at deploy, not synth).
- Container API input validation (`total` numeric/non-negative, `items` well-formed) is unchanged in `app.py` and already enforced; this design does not alter the API contract.

---

## Testability

- **Unit-level (synth-time, in scope):** `cdk synth` renders the full CloudFormation for both services, both ALBs/listeners/target groups, the CodeDeploy app + deployment group, both CloudFront distributions, the pipeline with the `CodeDeployEcsDeployAction`, and both alarms. A fine-grained assertion (recommended, via `aws-cdk-lib/assertions`) should assert: two `AWS::ECS::Cluster`, the prod service `DeploymentController: { Type: 'CODE_DEPLOY' }`, two `AWS::ElasticLoadBalancingV2::TargetGroup`, two prod listeners, one `AWS::CodeDeploy::DeploymentGroup` with the canary config, and — specifically to catch the finding-1 regression — **no `CidrIp: 0.0.0.0/0` ingress on EITHER ALB security group** (template-match the prod SG's `SecurityGroupIngress` to the prefix-list source only, and confirm the prod port-8080 listener added no internet ingress). These are the primary local checks for this pass.
- **SPA:** `npm run build` must succeed with the `APP_NAME` refactor; a quick `vite preview` confirms the header + tab title read "Coffee Shop".
- **Container:** `python -m py_compile container/app.py` (unchanged behavior).
- **Diagram:** `python3 container/build_diagram.py` regenerates `architecture.svg` without error.
- **Integration (out of scope — no live deploy):** the real blue/green cut-over, the alarm-driven rollback, and the prefix-list lock can only be fully verified on a live account; explicitly deferred per the task constraint.

---

## Diagram, docs, and demo-script plan

**Diagram (`container/build_diagram.py` → `architecture.svg`).** Update the runtime lane to show the split: User → CloudFront (prod) → **prod ALB** (blue/green: two target groups) → **prod ECS service** (CODE_DEPLOY), and a second edge User → CloudFront (test) → **test ALB** → **test ECS service** (rolling). Update the CI/CD lane's deploy edges to two actions: `EcsDeployAction (rolling)` → test service, and `CodeDeployEcsDeployAction (blue/green canary 10%/5m)` → prod service, with the Approval gate between them. Add a CodeDeploy icon (`Arch_Developer-Tools/.../Arch_AWS-CodeDeploy_64.svg` from `aws-icons`) and relabel nodes "Coffee Shop". Keep the self-contained base64-SVG approach and the AWS category color zones already in the script.

**README.md.** Rewrite the Architecture section and ASCII diagram to show separate `coffee-ship-test` and `coffee-ship-prod` clusters/services, two ALBs, two CloudFront URLs (`CloudFrontUrl` = prod, `TestCloudFrontUrl` = test), and the blue/green prod path. Update the Bootstrap-order section for the two-service + CodeDeploy flow (Decision 6). Rename user-facing references to "Coffee Shop" (keep resource names `coffee-ship`). Add a short "What blue/green looks like here" subsection (two target groups, canary 10%/5min, auto-rollback on failure + alarm).

**FACILITATOR-RUNBOOK.md.** Update **Act 4** (pipeline) and **Act 5** (deploy safely) to show: Deploy-Test = rolling to `coffee-ship-test`; Approval; Deploy-Prod = CodeDeploy blue/green to `coffee-ship-prod`. Add CLI to watch the CodeDeploy deployment (`aws deploy list-deployments --application-name coffee-ship-prod`, `aws deploy get-deployment`). Add the "verify TEST via `TestCloudFrontUrl`" step. Replace the single-service `aws ecs describe-services --cluster coffee-ship --services coffee-ship` with the two-cluster equivalents.

**New step-by-step demo script (`DEMO-SCRIPT.md`, new file).** A linear, copy-paste runbook that satisfies the user's "script I can use to demonstrate the pipeline, write the command step by step … change the page name from Coffee Shop to BeanThere Cafe and run the pipeline":
1. Resolve `SOURCE_BUCKET`, `CloudFrontUrl` (prod), `TestCloudFrontUrl` (test).
2. Show both environments live (prod + test URLs; `/health`, place an order).
3. **Code edit:** change `APP_NAME` in `container/frontend/src/App.jsx` from `'Coffee Shop'` to `'BeanThere Cafe'` (and the one-word `index.html` fallback). Show the diff.
4. Zip `container/` → `source.zip`, upload to `SOURCE_BUCKET` (same exclusions as `deploy.sh`).
5. Watch Source → Build → Deploy-Test (rolling) and verify the **test** URL already shows "BeanThere Cafe" while **prod** still shows "Coffee Shop" — this is the visible test/prod difference the user asked for.
6. Approve the manual gate.
7. Watch the **CodeDeploy blue/green** prod deployment shift traffic (canary 10%/5min); verify prod now shows "BeanThere Cafe".
8. Optional rollback demo: describe the CodeDeploy auto-rollback (alarm/failure) path.

`deploy.sh`/`destroy.sh` plan: `deploy.sh` keeps the ECR seed step (now required for the prod blue task set) and prints both CloudFront URLs; `destroy.sh` adds deletion of the second CloudFront distribution and the CodeDeploy app/deployment group (CDK destroy handles these in-stack, so the main addition is emptying/awaiting both services). These script edits are implementation detail for the build step, listed here for completeness.

---

## Files to create / modify

**Modify**
- `infra/lib/app-pipeline-stack.ts` — the whole re-architecture (two clusters, test service, prod service + ALB + 2 TGs + 2 listeners + CodeDeploy group, prod alarm, rename test alarm, prod build env vars, swap `Deploy_To_Prod` to `CodeDeployEcsDeployAction`, second CloudFront distribution, prod ALB SG prefix-list lock, new outputs).
- `container/buildspec.yml` — emit `taskdef.json` + `appspec.yaml` alongside `imagedefinitions.json`; substitute role ARNs/queue URL from env vars; add all three to `artifacts.files`.
- `container/taskdef.json` — replace with the `coffee-ship-prod` / `web` / `<IMAGE1_NAME>` template above.
- `container/frontend/src/App.jsx` — add `APP_NAME`, use it in header + `document.title`; update visible copy/alt text.
- `container/frontend/index.html` — `<title>Coffee Shop</title>` (fallback kept consistent).
- `container/build_diagram.py` — redraw split test/prod + blue/green + CodeDeploy icon + "Coffee Shop" labels; regenerate `container/architecture.svg`.
- `README.md`, `FACILITATOR-RUNBOOK.md` — docs updates above.
- `deploy.sh`, `destroy.sh` — two-service / two-CloudFront / CodeDeploy adjustments.

**Create**
- `container/appspec.yaml` — ECS blue/green appspec (above).
- `DEMO-SCRIPT.md` — the step-by-step pipeline demo including the Coffee Shop → BeanThere Cafe edit.

**Leave unchanged**
- `infra/bin/coffee-ship.ts`, `infra/lib/network-data-stack.ts` (shared data plane; no structural change).
- `container/app.py` (API contract unchanged; optional cosmetic fallback-title tweak noted).
- `app/appspec.yaml` (serverless Lambda path — separate; the new container appspec lives in `container/`).

---

## Unverified assumptions (explicit)

1. The prod `FargateService` (CODE_DEPLOY controller) comes up with a usable blue task set once `:latest` is seeded, and the first `CodeDeployEcsDeployAction` succeeds against it. Standard flow; not live-verified (synth only).
2. The default CodeDeploy service role from `codedeploy.EcsDeploymentGroup` includes sufficient `iam:PassRole` for the prod task/execution roles; if synth/live shows a gap, add an explicit `iam:PassRole` grant.
3. Alarming on **blue** target-group unhealthy-host count (not green) avoids false rollback during the normal green-registration window. Reasoned choice; not live-verified.
4. Two separate CloudFront distributions (prod + test) is the clean way to expose a prefix-list-locked test environment without breaking the SPA's same-origin API paths; a single distribution with a path-prefixed behavior was considered and rejected for that reason.
5. CloudFront origin-facing prefix list `pl-31a34658` is correct for `ap-southeast-1` (carried over from the existing stack; unchanged).

---

## Responses to design review (`design-review.md` — CHANGES_REQUESTED: 1 HIGH, 3 MEDIUM, 4 NIT)

All eight findings are **addressed** in this revision. None are backlogged or ignored; each change aligns with the original requirements (separate test/prod ECS, real CodeDeploy blue/green, no `0.0.0.0/0` on either ALB, Coffee Shop rename via one constant).

- **Finding 1 (HIGH) — prod ALB listeners create `0.0.0.0/0`. ADDRESSED.** Decision 2 now creates both prod listeners with `open: false` (with an inline comment citing the verified `ApplicationListenerProps.open` default of `true`), and Decision 4 adds the CloudFront prefix-list rule only via `prodListener.connections.allowDefaultPortFrom(...)`. The Testability section now mandates a synth-time assertion that neither ALB SG has a `0.0.0.0/0` ingress, so the regression is caught locally.

- **Finding 2 (MEDIUM) — build-substitution either/or ambiguity. ADDRESSED.** Decision 3 now commits to a **single mandatory** mechanism: the buildspec substitutes the role ARNs + queue URL at build time; only `<IMAGE1_NAME>` is left for CodeDeploy via `containerImageInputs[0].taskDefinitionPlaceholder`. The "if the … approach is used instead" alternative is deleted and replaced with a clear statement that build-time substitution is required because `RegisterTaskDefinition` rejects literal placeholders.

- **Finding 3 (MEDIUM) — buildspec substitution step unspecified. ADDRESSED.** Decision 3 now gives the exact `post_build` commands (push, `imagedefinitions.json`, the `test -n` guard that fails the build on an empty var, the `sed` using `#` delimiters to render `container/taskdef.json` → artifact-root `taskdef.json`, and `cp` of the appspec) plus an env-var→token mapping table that matches the CDK `environmentVariables` keys. It also states `ORDERS_TABLE_NAME` stays a hard-coded literal.

- **Finding 4 (MEDIUM) — port-8080 listener grant misleading / no green validator. ADDRESSED (option a).** Decision 2 now states plainly that the test listener exists only to satisfy CodeDeploy's blue/green contract and performs **no** automated pre-promotion probe (no lifecycle hooks; the manual approval gate is the human checkpoint). Decision 4 **drops** the CloudFront 8080 grant entirely — port 8080 gets no internet ingress at all — and explains the green task set is still gated by its own target-group health check.

- **Finding 5 (NIT) — second CloudFront distribution cost/scope. ADDRESSED.** Decision 4 adds an explicit scope-acknowledgement paragraph: the second distribution is deliberate, justified by the SPA's same-origin routing and the reviewer-verifiability requirement, and mirrors the prod distribution's config.

- **Finding 6 (NIT) — prod omits `LOYALTY_PARAM_NAME`. ADDRESSED.** Decision 2 now explicitly states both services intentionally rely on the `app.py` default (which matches the SSM param name) and instructs the implementer not to add the env var inconsistently.

- **Finding 7 (NIT) — `ORDERS_QUEUE_URL` passed but SQS unused by the container.** No change required and none made; the review itself confirms the SQS grant is kept deliberately to satisfy the brief's "DynamoDB/SQS/SSM on both task roles" requirement. The IAM section already documents this as intentional demo parity.

- **Finding 8 (NIT) — `_serve_index` fallback title left to implementer. ADDRESSED.** Decision 5 now decides it: leave `_serve_index` as-is (degraded-mode placeholder), keeping the rename a one-line `APP_NAME` change.
