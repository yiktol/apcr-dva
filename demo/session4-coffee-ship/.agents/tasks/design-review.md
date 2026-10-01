# Design review — Test/Prod split + real CodeDeploy ECS blue/green (coffee-ship)

Reviewed document: `.agents/tasks/design.md` (revised draft that already folded in a prior
`design-review.md` round of 1 HIGH + 3 MEDIUM + 4 NIT).

This review was done fresh against the actual source in the `bluegreen` worktree. Every
"the API does X" / "the existing code does Y" claim in the design was checked against the
installed `aws-cdk-lib@2.160.0` type definitions and the real project files, not taken on
the design's word.

---

## Verdict

**CHANGES_REQUESTED.** 1 HIGH, 1 MEDIUM, 3 NIT.

The architecture (two services, two clusters, prod CodeDeploy blue/green with two target
groups + two listeners + canary + dual auto-rollback, prefix-list lock on both ALBs, single
`APP_NAME` constant) is sound and almost entirely verifiable. The one blocking defect is a
missing build artifact (`imageDetails.json`) that breaks the prod image-placeholder
substitution the design relies on — the first and every prod CodeDeploy deployment would
register a task definition whose image is the literal string `<IMAGE1_NAME>` and fail.

---

## Findings

### 1. HIGH — Prod `<IMAGE1_NAME>` placeholder is never resolved: buildspec emits `imagedefinitions.json`, but `containerImageInputs` requires `imageDetails.json`

**Where.** Decision 3, "Buildspec outputs" + "Pipeline wiring for prod"; the `post_build`
command block; the `container/taskdef.json` template (`"image": "<IMAGE1_NAME>"`).

**Problem.** The design resolves the prod image two ways that do not meet:

- The buildspec emits `imagedefinitions.json` with the shape
  `[{"name":"web","imageUri":"$REPO_URI:$IMAGE_TAG"}]` and the taskdef keeps
  `"image": "<IMAGE1_NAME>"`, "resolved by the pipeline action's
  `containerImageInputs[0].taskDefinitionPlaceholder = 'IMAGE1_NAME'`."
- But the `CodeDeployEcsContainerImageInput.input` artifact is documented (verified in
  `aws-codedeploy/.../ecs-deploy-action.d.ts`, 2.160.0) to require **an `imageDetails.json`
  file containing an `ImageURI` property**, e.g.
  `{ "ImageURI": "ACCTID.dkr.ecr.region.amazonaws.com/repo@sha256:…" }`.
  The compiled action (`ecs-deploy-action.js`) sets `Image{i}ArtifactName` /
  `Image{i}ContainerName` on the `CodeDeployToECS` provider; CodeDeploy then reads
  `ImageURI` from `imageDetails.json` in that artifact to substitute the `<…>` placeholder.

`imagedefinitions.json` (schema `[{name, imageUri}]`, used by the standard rolling
`EcsDeployAction`) is **not** `imageDetails.json` (schema `{ImageURI}`). The build never
emits an `imageDetails.json`, so CodeDeploy has no `ImageURI` to inject. `<IMAGE1_NAME>`
stays literal, `RegisterTaskDefinition` is called with `image: "<IMAGE1_NAME>"`, and the
prod deployment fails on the first run (and every run). This is the core blue/green path the
whole task is about, so it is blocking.

**Concrete fix.** Emit `imageDetails.json` in the build and point the image input at it (or
drop `containerImageInputs` entirely and bake the image in the build). Pick one:

Option A (recommended, keeps CodeDeploy as the image substituter — add one line to the
`post_build` block and list the file as an artifact):
```yaml
      # imageDetails.json for the prod CodeDeploy <IMAGE1_NAME> substitution.
      - printf '{"ImageURI":"%s"}' "$REPO_URI:$IMAGE_TAG" > imageDetails.json
```
```yaml
artifacts:
  files:
    - imagedefinitions.json
    - imageDetails.json
    - taskdef.json
    - appspec.yaml
```
Keep the action wiring exactly as the design has it (`containerImageInputs: [{ input:
buildOutput, taskDefinitionPlaceholder: 'IMAGE1_NAME' }]`), and keep `"image":
"<IMAGE1_NAME>"` in the template.

Option B (resolve the image in the build like the role ARNs, drop the dynamic input): add
`-e "s#<IMAGE1_NAME>#${REPO_URI}:${IMAGE_TAG}#g"` to the `sed` that renders `taskdef.json`,
and **remove** `containerImageInputs` from `CodeDeployEcsDeployAction`. (Simpler, but the
immutable per-build tag then comes from the build, not from CodeDeploy's artifact
indirection — fine for this demo.)

Either way the design must stop implying `imagedefinitions.json` doubles as the CodeDeploy
image source. State the chosen option explicitly so the implementer does not wire a
non-existent file.

---

### 2. MEDIUM — `deploy.sh` cannot surface `TestCloudFrontUrl` with its current single-bucket/single-output resolution, and the "both URLs" claim is unspecified

**Where.** Decision 4 ("The `CloudFrontUrl` output continues to point students at prod",
new `TestCloudFrontUrl` output); "Diagram, docs, and demo-script plan" →
`deploy.sh`/`DEMO-SCRIPT.md` ("prints both CloudFront URLs", "Resolve … `CloudFrontUrl`
(prod), `TestCloudFrontUrl` (test)").

**Problem.** Verified in `deploy.sh`: step 5 resolves exactly one output
(`OutputKey=='CloudFrontUrl'`) and the summary prints one URL. The design says the demo
script and `deploy.sh` surface *both* URLs, but it never specifies the second resolution,
and both CloudFront distributions are added to the **same** `PIPELINE_STACK`. The demo's
headline payoff — "test shows BeanThere Cafe while prod still shows Coffee Shop" (DEMO-SCRIPT
step 5) — depends on the reviewer actually having the test URL. Leaving the resolution
unspecified risks an implementer shipping a script that only prints prod, defeating the
visible test/prod difference the user explicitly asked for.

The design also does not state whether the two distributions change the
`AWS::S3::Bucket` count that `deploy.sh` resolves with `… | [0]`. (They do not — CloudFront
adds no bucket — but the design should confirm it so the `[0]` source-bucket lookup is not
silently broken.)

**Concrete fix.** In the plan for `deploy.sh` / `DEMO-SCRIPT.md`, specify the exact second
resolution and print line, e.g.:
```bash
TEST_CLOUDFRONT_URL="$(aws cloudformation describe-stacks \
  --stack-name "${PIPELINE_STACK}" \
  --query "Stacks[0].Outputs[?OutputKey=='TestCloudFrontUrl'].OutputValue | [0]" \
  --output text 2>/dev/null || true)"
```
and add a summary line mirroring the existing `CloudFront URL :` line. Also state that the
new CDK output logical id is `TestCloudFrontUrl` (matching `aws cloudformation describe-stacks`
`OutputKey`) and that the source-bucket `[0]` lookup is unaffected because CloudFront adds no
S3 bucket.

---

### 3. NIT — Alarm `evaluationPeriods` mismatch between prod (1) and the (renamed) test alarm (2) is unexplained

**Where.** Decision 2, "Prod alarm" (`evaluationPeriods: 1`) vs the existing
`UnhealthyHostAlarm` being renamed to the test alarm (verified `evaluationPeriods: 2` in
`app-pipeline-stack.ts`).

**Problem.** The prod alarm fires after 1 breaching period; the test alarm keeps 2. For an
alarm wired into `autoRollback.deploymentInAlarm`, a single-period evaluation is a reasonable
"roll back fast" choice, but the design does not say whether the test alarm keeps 2 or should
match. An unstated inconsistency invites the implementer to "normalize" them and change
rollback timing by accident.

**Concrete fix.** Add one sentence: "Prod uses `evaluationPeriods: 1` (fast rollback,
alarm-driven); the test alarm keeps its existing `evaluationPeriods: 2` and is informational
only (not wired to any rollback) — do not normalize them." Confirm the test alarm's metric
source becomes `testService.targetGroup.metrics.unhealthyHostCount(...)`.

---

### 4. NIT — "Register the service with the BLUE target group only" uses `attachToApplicationTargetGroup`; confirm it does not also mutate the ALB SG

**Where.** Decision 2: `prodService.attachToApplicationTargetGroup(prodBlueTg);`

**Problem.** `attachToApplicationTargetGroup` exists on the ECS base service (verified in
`aws-ecs/lib/base/base-service.d.ts:498`), so the call is valid. The risk is subtle: the
design's whole finding-1 resolution hinges on **no** `0.0.0.0/0` landing on the prod ALB SG.
`attachToApplicationTargetGroup` wires target-group membership and can open ingress from the
ALB to the task SG, which is fine, but the design should assert that it does not re-open the
listener/ALB SG to the world and that the synth-time assertion (Testability section) covers
the prod ALB SG specifically after this call.

**Concrete fix.** Add a line: "`attachToApplicationTargetGroup` only registers the task set
as a target and adds task-SG ingress from the ALB; it does not add listener ingress. The
Testability assertion (no `CidrIp: 0.0.0.0/0` on the prod ALB SG) runs on the fully-synthed
template, so it catches any regression here."

---

### 5. NIT — Health check path `/` for the prod target groups: 200 is served by `_serve_index` fallback even with no SPA baked

**Where.** Decision 2 (prod TG `healthCheck: { path: '/', healthyHttpCodes: '200' }`) and the
claim "`/`, which `app.py` answers … at HTTP 200 (confirmed in `app.py` `_serve_index`)".

**Problem.** Verified: `app.py` `do_GET` routes `/` to `_serve_index`, which returns 200 even
in degraded mode (the baked-in `<title>coffee-ship</title>` fallback). So the health check
passes **even if the SPA failed to bake**, i.e. a green task set with a broken frontend can
still go healthy and get promoted. For a demo this is acceptable and the design's claim is
accurate, but it means the blue/green "a bad build is caught" story is weaker than it reads:
only a container that fails to *start/serve* is caught, not one that serves a broken SPA.

**Concrete fix.** No code change required. Add a one-line caveat in Decision 2 (and the
runbook) that `/` returns 200 in degraded mode, so the health check gates *process liveness*,
not SPA correctness; a reviewer confirms SPA correctness via the browser / `TestCloudFrontUrl`
step. Keep `/health` in mind if a future iteration wants a stricter gate.

---

## Verified assumptions

These design claims were checked against source and are correct:

1. **`EcsDeploymentConfig.CANARY_10PERCENT_5MINUTES` exists** and maps to the managed canary
   config — `aws-codedeploy/lib/ecs/deployment-config.d.ts` (2.160.0).
2. **`EcsDeploymentGroup` props** `blueGreenDeploymentConfig` (`blueTargetGroup`,
   `greenTargetGroup`, `listener`, `testListener`, `terminationWaitTime`), `deploymentConfig`,
   `alarms`, `service`, `autoRollback` — all present in `ecs/deployment-group.d.ts`.
3. **`AutoRollbackConfig.failedDeployment` + `deploymentInAlarm`** are the correct property
   names — `aws-codedeploy/lib/rollback-config.d.ts`.
4. **`EcsApplication` + `applicationName`** prop — `aws-codedeploy/lib/ecs/application.d.ts`.
5. **`CodeDeployEcsDeployAction` props** `deploymentGroup`, `taskDefinitionTemplateInput`,
   `appSpecTemplateInput`, `containerImageInputs[].taskDefinitionPlaceholder` and the default
   file names (`taskdef.json`, `appspec.yaml`) — `aws-codepipeline-actions/.../ecs-deploy-action.d.ts`.
6. **`ApplicationListenerProps.open` defaults to `true`** and injects a world-open ingress
   when not set `false` — `aws-elasticloadbalancingv2/lib/alb/application-listener.d.ts:80`.
   The finding-1 (prior round) resolution of `open: false` + prefix-list rule is correct.
7. **`listener.connections.allowDefaultPortFrom(...)`** exists —
   `aws-ec2/lib/connections.d.ts:118`.
8. **`attachToApplicationTargetGroup`** exists on the ECS base service —
   `aws-ecs/lib/base/base-service.d.ts:498`.
9. **`ApplicationLoadBalancedFargateService` exposes `targetGroup`** and
   `taskImageOptions.containerName` — `aws-ecs-patterns/.../application-load-balanced-service-base.d.ts:380,300`.
   The current code relies on the implicit `"web"` default; making it explicit is sound and
   matches today's `imagedefinitions.json` (`name:"web"`).
10. **Data-plane names** `coffee-ship-orders` (table + queue) and
    `/coffee-ship/loyalty/points-per-dollar` (SSM) — `network-data-stack.ts`. The design's
    hard-coded `ORDERS_TABLE_NAME: coffee-ship-orders` literal and the "both services rely on
    the `app.py` default `LOYALTY_PARAM_NAME`" decision match `app.py`
    (`ORDERS_TABLE_NAME` / `LOYALTY_PARAM_NAME` defaults).
11. **Current single-service topology** (one `coffee-ship` cluster, one
    `ApplicationLoadBalancedFargateService`, both `Deploy_To_Test` and `Deploy_To_Prod`
    pointing at the same service, prefix-list override via
    `cfnAlbSg.addPropertyOverride('SecurityGroupIngress', …)`, `CloudFrontPrefixListId`
    default `pl-31a34658`) — exactly as the design's Overview describes it.
12. **`app.py` `/orders`** returns the 10 most recent (`list_recent_orders(10)`); `/health`
    returns `APP_VERSION`; `/` is a 200 — matches the design.
13. **Frontend rename surface**: `App.jsx` header literal `☕ Coffee Ship`, `img` alt
    `Coffee Ship architecture diagram`, and `index.html` `<title>Coffee Ship</title>` all
    exist as the design says; `App.jsx` already imports `useEffect`, so the
    `document.title` effect is a clean add.
14. **Existing `container/taskdef.json`** has container name `coffee-ship` and family
    `coffee-ship`; the design's replacement (family `coffee-ship-prod`, container `web`,
    image `<IMAGE1_NAME>`) is a deliberate, consistent rewrite. No `container/appspec.yaml`
    exists yet (design creates it); `app/appspec.yaml` (serverless) exists and is correctly
    left untouched.
15. **`deploy.sh`** seeds ECR `:latest` before the first pipeline run and zips `container/`
    with `node_modules`/`dist` excluded — the design's bootstrap-order and demo-script zip
    steps match the existing script.

## Unverified / wrong assumptions

- **WRONG (Finding 1).** "The image placeholder is resolved by the pipeline action's
  `containerImageInputs[0].taskDefinitionPlaceholder = 'IMAGE1_NAME'`" while the build emits
  only `imagedefinitions.json`. CodeDeploy's image input requires an `imageDetails.json`
  (`{ImageURI}`), which the build never produces, so the placeholder is **not** resolved.
  See Finding 1 for the fix.

- **Unverified (carried from design, acceptable for a synth-only pass; not downgraded to a
  blocker because the task constraint is explicitly "no live deploy"):**
  1. A `CODE_DEPLOY`-controlled `FargateService` comes up with a usable blue task set once
     `:latest` is seeded, and the first `CodeDeployEcsDeployAction` succeeds. Standard flow,
     not live-verified here.
  2. The default CodeDeploy service role from `EcsDeploymentGroup` includes sufficient
     `iam:PassRole` for the prod task/execution roles. The design flags this and provides a
     fallback (explicit `iam:PassRole` grant); the compiled action also adds `PassRole`
     scoped to `ecs-tasks.amazonaws.com` on the pipeline action role (seen in
     `ecs-deploy-action.js`), which supports the design's IAM-section claim.
  3. Alarming on **blue** (not green) unhealthy-host count avoids a false rollback during the
     green-registration window. Reasoned, not live-verified.
  4. CloudFront origin-facing prefix list `pl-31a34658` is correct for `ap-southeast-1`
     (carried over unchanged from the existing stack).
  5. Two CloudFront distributions is the clean way to expose a prefix-list-locked test
     environment without breaking the SPA's same-origin paths. Reasoned; the second
     distribution's config mirrors prod (`CACHING_DISABLED` + `ALL_VIEWER`).

---

## Verdict math

HIGH = 1, MEDIUM = 1 → total blocking = 2 (> 0) → **CHANGES_REQUESTED**. NITs (3) do not
affect the gate but should be folded in during implementation.
