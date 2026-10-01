# Verification — Test/Prod ECS split + real CodeDeploy ECS blue/green (coffee-ship)

Branch `coffee-ship-bluegreen`. LOCAL ONLY — no `cdk deploy`, no `docker push`, no live AWS.
Account used for synth `875692608981`, region pinned `ap-southeast-1`, Node v25 (JSII warning silenced).

## Commands run

```
# frontend
cd container/frontend && npm install && npm run build        # dist/ produced
# container app
python3 -m py_compile container/app.py                        # exit 0
# diagram
cd container && python3 build_diagram.py                      # wrote architecture.svg 76019 bytes
cp container/architecture.svg architecture.svg
rsvg-convert container/architecture.svg -o architecture.png   # architecture.png 212214 bytes
# scripts
bash -n demo-pipeline.sh deploy.sh destroy.sh                 # all exit 0
# infra
cd infra && npx tsc --noEmit                                  # exit 0 (TSC_CLEAN)
CDK_DEFAULT_ACCOUNT=875692608981 JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=1 \
  npx cdk synth CoffeeShipAppPipeline                         # exit 0
```

Synthesized template inspected: `infra/cdk.out/CoffeeShipAppPipeline.template.json` (copied to `/tmp/synth.template.json` for jq).

## Per-item verifications

### Frontend — PASS
- `npm run build` produced `container/frontend/dist/` (index.html + assets).
- `grep -c "export const APP_NAME" src/App.jsx` == 1 (`export const APP_NAME = 'Coffee Shop';`).
- `grep -rn "Coffee Ship" src index.html` returns nothing (no stray "Coffee Ship").
- `APP_NAME` drives header (`<h1>{`☕ ${APP_NAME}`}</h1>`), `document.title` (useEffect), and the diagram `<img>` alt. `index.html` static fallback `<title>Coffee Shop</title>`.

### `python3 -m py_compile container/app.py` — PASS (exit 0). app.py left unchanged (Decision 5).

### Diagram — PASS
- `python3 build_diagram.py` wrote `container/architecture.svg` (76019 bytes) without error.
- `grep -c 'data:image/svg+xml;base64' container/architecture.svg` == 14 (real embedded icons).
- CodeDeploy icon wired: `build_diagram.py` ICONS maps `"codedeploy": "Arch_Developer-Tools/64/Arch_AWS-CodeDeploy_64.svg"` (file present at repo-root `aws-icons/...`), and `grep -ci 'codedeploy' container/architecture.svg` == 4 (node + label).
- Copied to top-level `architecture.svg`; `rsvg-convert` produced non-empty `architecture.png` (212214 bytes).

### Scripts — PASS
- `bash -n demo-pipeline.sh deploy.sh destroy.sh` all exit 0.
- `demo-pipeline.sh` and `deploy.sh` BOTH resolve+print prod `CloudFrontUrl` AND `TestCloudFrontUrl`:
  - `deploy.sh`: `CLOUDFRONT_URL` from `OutputKey=='CloudFrontUrl'`, `TEST_CLOUDFRONT_URL` from `OutputKey=='TestCloudFrontUrl'`; summary lines ` CloudFront URL :` (PROD) and ` Test CloudFront :` (TEST).
  - `demo-pipeline.sh`: prints `PROD CloudFront ... (OutputKey CloudFrontUrl)` and `TEST CloudFront ... (OutputKey TestCloudFrontUrl)`.
- `put-approval-result` uses `--pipeline-name "${PIPELINE_NAME}"` (not `--pipeline`).
- `aws deploy get-deployment --deployment-id ...` present in demo-pipeline.sh (blue/green canary watch).
- `container/buildspec.yml` has NO active `|| true` gate (the only `|| true` text is in a comment explaining its absence).

## Synth template checks (a)–(j) — all PASS

Evidence from `jq` over `/tmp/synth.template.json`.

### (a) Two ECS clusters — PASS
`jq '[.Resources|to_entries[]|select(.value.Type=="AWS::ECS::Cluster")|{id:.key,name:.value.Properties.ClusterName}]'`
→ `CoffeeShipTestCluster` (`coffee-ship-test`), `CoffeeShipProdCluster` (`coffee-ship-prod`).

### (b) Prod service DeploymentController == CODE_DEPLOY — PASS
`jq` over `AWS::ECS::Service`:
- `coffee-ship-test` → `DeploymentController.Type == "ECS"` (rolling)
- `coffee-ship-prod` → `DeploymentController.Type == "CODE_DEPLOY"`

### (c) Two prod target groups on port 8080 — PASS
`jq` over `AWS::ElasticLoadBalancingV2::TargetGroup`:
- `ProdBlueTg` port 8080 HealthCheckPath `/`
- `ProdGreenTg` port 8080 HealthCheckPath `/`
(the test service TG is the ALBFargateService default on port 80.)

### (d) Two prod listeners (80 + 8080) — PASS
`jq` over `AWS::ElasticLoadBalancingV2::Listener`:
- `CoffeeShipProdAlbProdListener` port 80
- `CoffeeShipProdAlbProdTestListener` port 8080
(plus the test service listener on port 80.)

### (e) One CodeDeploy DeploymentGroup, canary + autoRollback on failure AND alarm — PASS
`jq` over `AWS::CodeDeploy::DeploymentGroup` (`ProdDeployGroup`):
- `DeploymentConfigName: CodeDeployDefault.ECSCanary10Percent5Minutes`
- `AutoRollbackConfiguration.Events: ["DEPLOYMENT_FAILURE","DEPLOYMENT_STOP_ON_ALARM"]`
- `AlarmConfiguration.Alarms: [{ Ref: ProdUnhealthyHostAlarm }]`, Enabled true.

### (f) Prod alarm evaluationPeriods 1, test alarm evaluationPeriods 2 — PASS (NIT finding 3)
`jq` over `AWS::CloudWatch::Alarm`:
- `coffee-ship-prod-unhealthy-hosts` EvaluationPeriods **1** (fast alarm-driven rollback; wired to deploymentInAlarm)
- `coffee-ship-test-unhealthy-hosts` EvaluationPeriods **2** (informational only, NOT wired to rollback — not normalized).

### (g) No `CidrIp: 0.0.0.0/0` ingress on either ALB SG — PASS (NIT finding 4)
- Zero `SecurityGroupIngress`/standalone `AWS::EC2::SecurityGroupIngress` with `CidrIp == 0.0.0.0/0`.
- `grep -c '0.0.0.0/0'` == 2, and both are `SecurityGroupEgress` ("allow all outbound") on the two **service** SGs (CDK default), not ALB ingress.
- Test ALB SG ingress: `SourcePrefixListId: { Ref: CloudFrontPrefixListId }` on port 80 only.
- Prod ALB SG ingress: single standalone rule `CoffeeShipProdAlbSecurityGroupfromIndirectPeer80` → prefix list `{ Ref: CloudFrontPrefixListId }` on port 80; **no** port-8080 internet ingress.
- `prodService.attachToApplicationTargetGroup` only added the task-SG-from-ALB-SG ingress on 8080 (`CoffeeShipProdServiceSecurityGroupfrom...ProdAlbSecurityGroup...8080`); it added no listener/world ingress. Assertion run against the fully-synthed template.

### (h) Build project env vars present — PASS
`jq` over `AWS::CodeBuild::Project` EnvironmentVariables names → `PROD_EXECUTION_ROLE_ARN`, `PROD_TASK_ROLE_ARN`, `ORDERS_QUEUE_URL` (keys match the buildspec).

### (i) TestCloudFrontUrl output + second CloudFront distribution — PASS
- `.Outputs` keys include `CloudFrontUrl` (prod) and `TestCloudFrontUrl` (test, exact logical id).
- Two `AWS::CloudFront::Distribution`: `CoffeeShipCdn` (prod ALB origin) + `CoffeeShipTestCdn` (test ALB origin).
- CloudFront adds no `AWS::S3::Bucket`, so `deploy.sh`'s `AWS::S3::Bucket | [0]` source-bucket lookup is unaffected (MEDIUM finding 2).

### (j) Prod CodeDeployEcsDeployAction wired — PASS (HIGH finding 1)
Pipeline stage `Deploy-Prod` action `Deploy_To_Prod`, provider `CodeDeployToECS`:
- `TaskDefinitionTemplatePath: taskdef.json`, `AppSpecTemplatePath: appspec.yaml` (both from `BuildArtifact`)
- `Image1ArtifactName: BuildArtifact`, `Image1ContainerName: IMAGE1_NAME`.
- Build emits `imageDetails.json` (`{"ImageURI":...}`) consumed by `containerImageInputs` to resolve `<IMAGE1_NAME>` in `taskdef.json`; `imagedefinitions.json` (`[{name,imageUri}]`) feeds the rolling test action. All four artifacts (`imagedefinitions.json`, `imageDetails.json`, `taskdef.json`, `appspec.yaml`) are listed under `artifacts.files`.

## Design-review findings status (design-review.json)
- HIGH #1 (imageDetails.json / IMAGE1_NAME resolution, no `|| true`) — FIXED, verified by (j) + buildspec grep. Option A chosen (emit imageDetails.json, keep containerImageInputs placeholder IMAGE1_NAME).
- MEDIUM #2 (both CloudFront URLs; TestCloudFrontUrl output; CloudFront adds no bucket) — FIXED, verified by (i) + script greps.
- NIT #3 (prod ep1 / test ep2, not normalized; test metric from testService.targetGroup) — HELD, verified by (f).
- NIT #4 (attachToApplicationTargetGroup adds no world ingress; no-0.0.0.0/0 assertion on synthed template) — HELD, verified by (g).
- NIT #5 (health `/` 200 in degraded mode gates liveness not SPA correctness) — documented in design/runbook; app.py `_serve_index` unchanged by design.

## Cleanup
Temp files `/tmp/synth.json`, `/tmp/synth.err`, `/tmp/synth.template.json`, `/tmp/npm-*.log` removed after inspection. `infra/cdk.out/` is CDK build output (gitignored). `container/frontend/dist` + `node_modules` are build output, excluded from `source.zip` and not committed.
