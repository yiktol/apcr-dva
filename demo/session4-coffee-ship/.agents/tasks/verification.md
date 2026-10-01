# Verification — Real coffee-ship ECS CI/CD pipeline (container path)

All work on branch `real-ecs-pipeline` in the worktree
`/Users/erictole/demo/apcr-dva/.worktrees/real-pipeline/demo/session4-coffee-ship`.
No live AWS deploy was performed — synth / tsc / inspection only, per the task.

## Commands run and results

### 1. Install infra dependencies
- `npm ci` in `infra/` — **PASS** (added 28 packages, audited 65; `aws-cdk-lib`
  present under `node_modules`). `npm ci` succeeded, so `npm install` fallback
  was not needed.

### 2. TypeScript type-check
- `npx tsc --noEmit` in `infra/` — **PASS** (exit 0, no diagnostics).

### 3. CDK synth (no live AWS)
- `JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=1 CDK_DEFAULT_ACCOUNT=875692608981 npx cdk synth CoffeeShipAppPipeline`
  — **PASS** (exit 0; only informational CDK CLI/notice output on stderr).
- `... npx cdk synth CoffeeShipNetworkData` — **PASS** (exit 0).

### 4. Buildspec YAML parse
- `python3 -c "import yaml; yaml.safe_load(open('container/buildspec.yml'))"`
  — **PASS**. `version: 0.2`, phases pre_build/build/post_build parse cleanly.
  Shell command blocks reviewed by inspection: ECR login, `python -m py_compile`
  (no `|| true`), `docker build` of `container/`, `docker push` of both tags,
  `printf` of imagedefinitions.json. Syntactically sane.

### 5. Script syntax
- `bash -n deploy.sh` — **PASS** (deploy.sh updated to zip `container/` as
  source.zip and surface the CloudFront URL).

## Required-condition confirmations (from the synthesized CoffeeShipAppPipeline template)

Checked against `infra/cdk.out/CoffeeShipAppPipeline.template.json`:

- **(a) CodeBuild privileged/Docker referencing container/buildspec.yml** — CONFIRMED.
  `AWS::CodeBuild::Project` with `PrivilegedMode: true`,
  `BuildSpec: container/buildspec.yml` (via `BuildSpec.fromSourceFilename`).
- **(b) EcsDeployAction(s) present, NO S3 deploy actions** — CONFIRMED.
  Two pipeline actions with `"Provider": "ECS"` (Deploy_To_Test, Deploy_To_Prod);
  the only `"Provider": "S3"` action is `Category: Source` (the S3 source).
  `grep 'deploy/test|deploy/prod'` → 0; `ecs:UpdateService` present (×2, auto-granted
  by EcsDeployAction).
- **(c) ECS task image references the ECR repo (not nginx) on port 8080** — CONFIRMED.
  `image: ecs.ContainerImage.fromEcrRepository(repository, 'latest')`;
  `"ContainerPort": 8080` present; `grep nginx` → 0; `grep amazonlinux` → 0.
- **(d) ALB SG ingress ONLY the CloudFront prefix list, no 0.0.0.0/0** — CONFIRMED.
  ALB SG ingress is a single rule: HTTP 80 with `SourcePrefixListId` =
  `{ "Ref": "CloudFrontPrefixListId" }` (default `pl-31a34658`). The only
  `0.0.0.0/0` in the template is a `SecurityGroupEgress` on the ECS *task* SG
  (default allow-all egress) — NOT an ALB ingress.
- **(e) CloudFront distribution present with the ALB as origin** — CONFIRMED.
  `AWS::CloudFront::Distribution` ×1, origin = `LoadBalancerV2Origin` (HTTP_ONLY,
  httpPort 80) over the Fargate ALB; outputs `CloudFrontUrl` + `CloudFrontDistributionId`.
- **(f) VPC still imported via Fn::ImportValue, no AWS::EC2::VPC created** — CONFIRMED.
  `Fn::ImportValue` appears 13× (VpcId/VpcCidrBlock/PublicSubnetOne-Two-Three);
  `AWS::EC2::VPC` count = 0 in BOTH templates (pipeline and network-data).
- **(g) imagedefinitions.json containerName matches the ECS container name** — CONFIRMED.
  ECS container name is the pattern default `"web"` (synth shows `"Name": "web"`,
  no `containerName` override). buildspec writes
  `[{"name":"web","imageUri":"$REPO_URI:$IMAGE_TAG"}]` — names match.

## Notes

- `review.json` in `.agents/tasks/` is from the PRIOR standalone-scaffold task
  (`task-session4-coffee-ship`, status completed) and describes the pre-rewrite
  baseline (nginx/S3 deploy/created-VPC); its findings are not against this
  real-pipeline change. The worktree held the pre-live-session state, so this is
  effectively the first real-pipeline iteration — implemented per plan.md.
- `app/**` (serverless path) and `app/buildspec.yml` left untouched; the pipeline
  no longer references `app/buildspec.yml` (grep in `infra/lib`,`infra/bin` → none).
- deploy.sh (outside the named scope but required for the documented real flow)
  now zips `container/` as source.zip and prints the CloudFront URL; it still
  seeds ECR `:latest` once so the service can stabilize before the first
  pipeline run (bootstrap), after which the pipeline owns all image builds.
