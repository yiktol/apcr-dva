# Real coffee-ship ECS CI/CD pipeline — container path

The branch `real-ecs-pipeline` rewrites the session4 coffee-ship pipeline from a
fake S3-copy "deploy" into a genuine container delivery pipeline: CodeBuild does
a real `docker build`/`docker push` to ECR, and two `EcsDeployAction` stages roll
the live Fargate service via `imagedefinitions.json`. It also brings the worktree
up to the preserved security model (CloudFront in front of the ALB, ALB SG locked
to the CloudFront prefix list, VPC imported from CloudFormation exports instead of
created). The serverless `app/**` path is untouched. The design satisfies the
absolute requirement that everything be real and student-verifiable — no
simulation, no `|| true` no-op gates, no stand-in image.

Watch for: a runbook ergonomics nit in Act 4 step 3 — the `zip` command assumes
the facilitator's shell is already in the `session4-coffee-ship` directory, unlike
`deploy.sh` which `cd`s explicitly (possible). Non-blocking.

**Verdict**: APPROVED

## High-level view

The fake deploy is gone. Both `S3DeployAction`s are replaced by
`EcsDeployAction`s targeting the single `coffee-ship` Fargate service, and the
build stage reads `container/buildspec.yml` with `privileged: true` so Docker is
available. The five-stage shape (Source → Build → Deploy-Test → manual Approval
on the `coffee-ship-approval` SNS topic → Deploy-Prod) and the versioned-S3
`source.zip` trigger are preserved.

The ECS service runs the real image via `ContainerImage.fromEcrRepository(repo,
'latest')` on container port 8080, keeps the pattern-default container name `web`,
and the deploy safety settings (circuit breaker rollback, minHealthy 100 /
maxHealthy 200) are intact. The ALB health check stays on `GET /`, which the
coffee-ship app answers.

The build-to-deploy contract holds end to end: the buildspec tags and pushes both
`:latest` and a unique per-build tag, then writes `imagedefinitions.json` with
`"name":"web"` and the unique tag — matching the ECS container name the deploy
action expects.

The preserved security posture is intact: CloudFront fronts the ALB, the ALB
security group's auto-created `0.0.0.0/0` ingress is overridden to admit only the
CloudFront origin-facing prefix list, the ECR repo is kept, and the VPC is
imported via `Fn::ImportValue` with zero `AWS::EC2::VPC` resources synthesized.

The bootstrap chicken-and-egg (empty ECR vs. a service that needs an image) is
documented in code comments, `README.md`, and `FACILITATOR-RUNBOOK.md`, and the
Act 4 runbook now walks the real student-verifiable flow. The coder's verification
evidence (tsc clean, synth of both stacks clean, YAML parse, template greps) is
present and consistent with the diff.

<details>
<summary>Issues (1)</summary>

1. **Runbook zip cwd (non-blocking)** — Act 4 step 3 runs `zip -r /tmp/source.zip
   container/` without a preceding `cd` into `session4-coffee-ship`, unlike
   `deploy.sh`. Works if the facilitator is already in that directory; consider
   adding an explicit `cd` for parity. Not a correctness blocker.

</details>

<details>
<summary>Details</summary>

### Fake deploy removed, real EcsDeployAction stages in

Both `S3DeployAction`s and their `deploy/test` / `deploy/prod` object keys are
gone. `Deploy_To_Test` and `Deploy_To_Prod` are now
`codepipeline_actions.EcsDeployAction`s, each targeting `fargateService.service`
and reading the build output artifact (where `imagedefinitions.json` lives).
Deploy-Prod rolls the same single service to the approved image — appropriate for
a one-service demo. No hand-rolled ECS IAM policy is present, correct because
`EcsDeployAction` auto-grants `ecs:UpdateService` / `RegisterTaskDefinition` /
`iam:PassRole`. The verification evidence confirms two `"Provider": "ECS"` actions,
the only `"Provider": "S3"` action being the Source, and zero `deploy/test`/
`deploy/prod` keys in the synthesized template (confirmed).

### Real container image on the ECS service

The service image is `ecs.ContainerImage.fromEcrRepository(repository, 'latest')`
on `containerPort: 8080`, with the container name left at the pattern default
`web`. There is no nginx or amazonlinux reference. Circuit breaker rollback is
`true`, `minHealthyPercent 100` / `maxHealthyPercent 200` are preserved, and the
ALB target group health check stays on `GET /`, which the stdlib app answers with
`{"status":"ok"}` (confirmed from the stack source and verification greps).

### container/buildspec.yml build-and-push contract

The new `container/buildspec.yml` (`version: 0.2`, privileged CodeBuild via
`LinuxBuildImage.STANDARD_7_0`) resolves the account/region, logs into ECR, sets a
unique `IMAGE_TAG` (resolved source version, else build number), runs a real
`python -m py_compile container/app.py` check with no `|| true`, builds the
`container/` context, and pushes BOTH `$REPO_URI:$IMAGE_TAG` and `$REPO_URI:latest`.
`post_build` writes `imagedefinitions.json` as `[{"name":"web","imageUri":"…:<unique
tag>"}]` and lists it as the artifact. The CodeBuild project uses
`BuildSpec.fromSourceFilename('container/buildspec.yml')` and gets
`repository.grantPullPush(buildProject)`. The container name `web` matches the ECS
container name, closing the deploy contract (confirmed).

### Preserved security model

CloudFront fronts the ALB as a `LoadBalancerV2Origin` (HTTP_ONLY, port 80,
REDIRECT_TO_HTTPS, caching disabled, ALL_VIEWER), with `CloudFrontUrl` and
`CloudFrontDistributionId` outputs. The ALB security group's default `0.0.0.0/0`
ingress is overridden to a single rule admitting HTTP only from the CloudFront
origin-facing prefix list (`pl-31a34658`, exposed as an overridable CfnParameter).
The only `0.0.0.0/0` left in the template is the ECS task SG's default egress — not
an ALB ingress. The ECR repo (keep-10 lifecycle) is retained, and the VPC is
imported via `Fn::ImportValue` of VpcId/VpcCidrBlock/PublicSubnetOne-Three with
zero `AWS::EC2::VPC` resources synthesized in either stack. `network-data-stack.ts`
dropped VPC creation and no longer exposes `vpc`; `bin/coffee-ship.ts` stops
passing `vpc` and carries the updated descriptions (confirmed).

### Pipeline shape and docs

The five-stage shape and the versioned-S3 `source.zip` POLL trigger are intact,
with the manual approval wired to the `coffee-ship-approval` SNS topic. `deploy.sh`
now zips `container/` as source.zip, seeds ECR `:latest` once so the service can
stabilize before the first pipeline run (bootstrap), and surfaces the CloudFront
URL instead of the ALB DNS. `README.md` and `FACILITATOR-RUNBOOK.md` describe the
real end-to-end flow, the bootstrap order, and the CloudFront-only entry point;
the remaining "placeholder/no-op/stand-in" phrases are negative assertions
("there is no placeholder…"), not residual fake-deploy instructions.
`app/buildspec.yml` is unchanged and no longer referenced by infra (confirmed).

</details>

<details>
<summary>File map</summary>

- `infra/lib/app-pipeline-stack.ts` — real EcsDeployAction stages, ECR image on
  8080, CloudFront + ALB SG prefix-list lock, imported VPC, buildspec switch.
- `infra/lib/network-data-stack.ts` — drops VPC creation; keeps data resources.
- `infra/bin/coffee-ship.ts` — stops passing `vpc`; updated descriptions.
- `container/buildspec.yml` — NEW: real docker build/push + imagedefinitions.json.
- `deploy.sh` — zips container/ as source.zip, seeds ECR, prints CloudFront URL.
- `README.md`, `FACILITATOR-RUNBOOK.md` — real Act 4 flow + bootstrap order.
- `.agents/tasks/plan.md`, `.agents/tasks/verification.md` — plan + evidence.

Full diff: `git -C /Users/erictole/demo/apcr-dva/.worktrees/real-pipeline diff main`

</details>
