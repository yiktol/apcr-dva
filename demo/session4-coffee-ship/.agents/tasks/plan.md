# Implementation Plan — Real coffee-ship CI/CD pipeline (container path)

All paths are ABSOLUTE under the worktree:
`/Users/erictole/demo/apcr-dva/.worktrees/real-pipeline/demo/session4-coffee-ship`.

## Context discovered during exploration (read this first)

- Build/test tooling for the CDK app lives in
  `/Users/erictole/demo/apcr-dva/.worktrees/real-pipeline/demo/session4-coffee-ship/infra`:
  `aws-cdk-lib 2.160.0`, `aws-cdk 2.160.0`, `typescript ~5.5.4`, `ts-node`.
  Scripts: `npm run build` = `tsc`, `npm run synth` = `cdk synth`.
  `cdk.json` app = `npx ts-node --prefer-ts-exts bin/coffee-ship.ts`.
  THERE IS NO `node_modules` in the worktree infra yet — the first step is `npm install`.
- The CDK CLI reported by the task is 2.1126.0; the repo pins `aws-cdk 2.160.0` as a
  devDependency and runs it via `npx cdk`. Use `npx cdk synth` so the pinned CLI is used.
- `ApplicationLoadBalancedFargateService` (v2.160.0) default container name is **`web`**
  (verified in the installed source: `containerName = taskImageOptions.containerName ?? "web"`).
  We KEEP the default, so `imagedefinitions.json` must use `"name": "web"`.
- `EcsDeployAction` (v2.160.0) AUTO-GRANTS to the pipeline action role:
  `ecs:DescribeServices`, `ecs:DescribeTaskDefinition`, `ecs:DescribeTasks`,
  `ecs:ListTasks`, `ecs:RegisterTaskDefinition`, `ecs:TagResource`,
  `ecs:UpdateService`, and `iam:PassRole`. So NO manual IAM policy is required for the
  deploy actions — do not hand-roll these (a wrong hand-rolled policy is a common failure).
- `container/app.py` is stdlib-only Python 3.12, listens on `PORT` (default 8080),
  `GET /` returns `{"status":"ok"}`. `container/Dockerfile` uses `python:3.12-slim`,
  `EXPOSE 8080`, `CMD ["python","app.py"]`. `container/requirements.txt` is empty by design.

### CRITICAL baseline reconciliation (do not skip)

The worktree branch `real-ecs-pipeline` currently holds the PRE-live-session state:
`infra/lib/network-data-stack.ts` still CREATES a VPC, `infra/lib/app-pipeline-stack.ts`
has NO CloudFront / NO prefix-list lock / NO imported VPC and uses an amazonlinux
placeholder with fake `S3DeployAction`s. The CloudFront + ALB-SG-prefix-list +
imported-VPC security model the task says to "preserve exactly" currently lives ONLY in
the NON-worktree main copy at
`/Users/erictole/demo/apcr-dva/demo/session4-coffee-ship/`.

Therefore the plan must first bring the worktree UP TO the preserved security model
(copying that model verbatim from the main copy), THEN layer the real-pipeline changes on
top. Steps 2–3 establish the baseline; steps 4–7 are the real-pipeline rewrite.

The main copy's app-pipeline-stack.ts still uses an **nginx:stable / port 80** placeholder
and fake S3 deploy actions — those are exactly what we REPLACE, so copy the model but
apply the real-pipeline edits from steps 4–6 (do not carry over nginx/port-80/S3-copy).

### The container-name / imagedefinitions contract (must hold end to end)

- ECS container name: `web` (pattern default; do NOT pass `containerName`).
- ECS container port: `8080` (`taskImageOptions.containerPort: 8080`).
- ECR repo URI: `875692608981.dkr.ecr.ap-southeast-1.amazonaws.com/coffee-ship`.
- `imagedefinitions.json` content: `[{"name":"web","imageUri":"<repoUri>:<uniqueTag>"}]`
  where `<uniqueTag>` is the unique build tag the buildspec also pushed.
- `EcsDeployAction` reads `imagedefinitions.json` from the Build output artifact.

### Bootstrap order (chicken-and-egg; document in code comments + docs)

ECR is empty until the pipeline builds, but the ECS service needs an image to start.
Resolution: service image = `ecs.ContainerImage.fromEcrRepository(repository, 'latest')`.
Required order:
1. `npx cdk deploy --all` creates ECR (empty), ECS service (will not stabilize yet),
   ALB, CloudFront, pipeline. The service task will fail to pull `:latest` until step 2 —
   this is expected on first deploy.
2. Trigger the pipeline once (upload `source.zip` containing `container/` + the new
   `container/buildspec.yml`). Build pushes `:latest` + a unique tag to ECR;
   Deploy-Test runs a real `EcsDeployAction` that registers a new task def pointing at the
   unique tag and the service stabilizes.
3. Approve; Deploy-Prod rolls the same service again to the approved image.
The orchestrator (not this workflow) performs the live deploy + CloudFront curl check.

---

## Plan

- [ ] 1. Install infra dependencies so `tsc` and `cdk synth` can run.
      Files: none (uses existing `infra/package.json` + `infra/package-lock.json`).
      Run: `npm ci` in
      `/Users/erictole/demo/apcr-dva/.worktrees/real-pipeline/demo/session4-coffee-ship/infra`
      (fall back to `npm install` if `npm ci` fails on lockfile drift).
      Verify: `ls node_modules/aws-cdk-lib/package.json` exists and
      `npx tsc --version` prints a 5.5.x version. Leaves the tree buildable.

- [ ] 2. Replace the network/data stack with the imported-VPC (no-VPC-created) version,
      matching the preserved model. Copy the body of
      `/Users/erictole/demo/apcr-dva/demo/session4-coffee-ship/infra/lib/network-data-stack.ts`
      verbatim: it drops the `ec2`/VPC creation, removes `public readonly vpc`, and keeps
      DynamoDB/SQS/SSM/Secrets/AppConfig. The VPC import moves into the pipeline stack
      (step 3), so this stack no longer exposes a `vpc`.
      Files: `/Users/erictole/demo/apcr-dva/.worktrees/real-pipeline/demo/session4-coffee-ship/infra/lib/network-data-stack.ts`
      Verify: deferred to step 7 (`tsc` + `synth`) — this file alone won't compile until
      `bin/coffee-ship.ts` (step 3b) stops passing `vpc`.

- [ ] 3. Rewrite the pipeline stack to the preserved CloudFront + imported-VPC +
      ALB-SG-prefix-list model AND the real pipeline. Start from the main copy
      `/Users/erictole/demo/apcr-dva/demo/session4-coffee-ship/infra/lib/app-pipeline-stack.ts`
      as the base for the security/network portion (imported VPC via `Fn.importValue` of
      `VpcId`/`VpcCidrBlock`/`PublicSubnetOne|Two|Three` across az `1a/1b/1c`; ECR repo
      `coffee-ship` keep-10; `ApplicationLoadBalancedFargateService` serviceName
      `coffee-ship`, cluster `coffee-ship`, cpu256/mem512, desiredCount1, assignPublicIp,
      PUBLIC subnets, `publicLoadBalancer: true`, `minHealthyPercent 100`,
      `maxHealthyPercent 200`, `circuitBreaker {rollback:true}`,
      `healthCheckGracePeriod 120s`; ALB SG `SecurityGroupIngress` override to the
      `CloudFrontPrefixListId` CfnParameter default `pl-31a34658`; CloudFront
      `Distribution` with `LoadBalancerV2Origin` HTTP_ONLY httpPort 80, REDIRECT_TO_HTTPS,
      ALLOW_ALL, CACHING_DISABLED, ALL_VIEWER; the `CloudFrontUrl` + `CloudFrontDistributionId`
      outputs; SNS topic `coffee-ship-approval`; the `coffee-ship-unhealthy-hosts` alarm;
      the versioned S3 `SourceBucket`). Then apply the REAL-pipeline edits below.
      Props: keep `AppPipelineStackProps` with `ordersQueue` + `ordersTable` ONLY
      (the stack imports its own VPC; it must NOT take a `vpc` prop).
      Files: `/Users/erictole/demo/apcr-dva/.worktrees/real-pipeline/demo/session4-coffee-ship/infra/lib/app-pipeline-stack.ts`
      Verify: deferred to step 7.

      Real-pipeline edits inside this same file (all in step 3):
      3a. ECS image: replace the nginx/amazonlinux placeholder with
          `image: ecs.ContainerImage.fromEcrRepository(repository, 'latest')` and
          `containerPort: 8080`. Do NOT set `containerName` (keep default `web`).
          Add a comment documenting the bootstrap order (service unhealthy until first
          pipeline run pushes `:latest`). The ALB health check targets `GET /` by default
          (path `/`), which returns `{"status":"ok"}` — leave the pattern's default target
          group health check path (`/`) in place; add a short comment noting this.
          `repository.grantPull(fargateService.taskDefinition.obtainExecutionRole())` stays.
      3b. CodeBuild project: change
          `buildSpec: codebuild.BuildSpec.fromSourceFilename('app/buildspec.yml')` to
          `codebuild.BuildSpec.fromSourceFilename('container/buildspec.yml')`. Keep
          `privileged: true`, `LinuxBuildImage.STANDARD_7_0`, projectName `coffee-ship-build`.
          The build project needs ECR push rights:
          `repository.grantPullPush(buildProject);` (add after the project is created).
      3c. Deploy stages: delete both `S3DeployAction`s (`deployTestAction`,
          `deployProdAction`) and the `deploy/test` / `deploy/prod` objectKeys. Add:
          ```
          const deployTestAction = new codepipeline_actions.EcsDeployAction({
            actionName: 'Deploy_To_Test',
            service: fargateService.service,
            input: buildOutput,            // imagedefinitions.json lives here
          });
          const deployProdAction = new codepipeline_actions.EcsDeployAction({
            actionName: 'Deploy_To_Prod',
            service: fargateService.service,
            input: buildOutput,
          });
          ```
          Both target the single `fargateService.service` on purpose (one service in this
          demo); Deploy-Prod rolls the same service to the approved image. No manual IAM
          policy — `EcsDeployAction` grants `ecs:UpdateService`/`RegisterTaskDefinition`/
          `iam:PassRole`/etc. automatically (verified). Keep the five-stage shape:
          Source -> Build -> Deploy-Test -> Approval(manual, SNS `coffee-ship-approval`)
          -> Deploy-Prod.
      3d. Also fix `bin/coffee-ship.ts` to stop passing `vpc` (NetworkDataStack no longer
          exposes it) and to carry the preserved descriptions. Copy
          `/Users/erictole/demo/apcr-dva/demo/session4-coffee-ship/infra/bin/coffee-ship.ts`
          verbatim (it already drops `vpc` and has the imported-VPC/CloudFront
          descriptions).
          Files: `/Users/erictole/demo/apcr-dva/.worktrees/real-pipeline/demo/session4-coffee-ship/infra/bin/coffee-ship.ts`

- [ ] 4. Create the REAL container buildspec. New file, used by the CodeBuild project from
      step 3b. It must, in `pre_build`: resolve `ACCOUNT_ID` + region, compute
      `REPO_URI=${ACCOUNT_ID}.dkr.ecr.ap-southeast-1.amazonaws.com/coffee-ship`, set
      `IMAGE_TAG=${CODEBUILD_RESOLVED_SOURCE_VERSION:-$CODEBUILD_BUILD_NUMBER}` (unique),
      and `aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login
      --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.ap-southeast-1.amazonaws.com`.
      In `build`: real check `python -m py_compile container/app.py` (fail on nonzero — NO
      `|| true`), then `docker build -t $REPO_URI:$IMAGE_TAG -t $REPO_URI:latest container/`
      (build context `container/`, Dockerfile `container/Dockerfile`).
      In `post_build`: `docker push $REPO_URI:$IMAGE_TAG` AND `docker push $REPO_URI:latest`,
      then write `imagedefinitions.json` =
      `[{"name":"web","imageUri":"'"$REPO_URI:$IMAGE_TAG"'"}]` (printf/jq, name MUST be
      `web`). `artifacts.files: [imagedefinitions.json]`. `version: 0.2`. No placeholder
      gates, no `|| true`, no `exit 0` escape hatch.
      Files: `/Users/erictole/demo/apcr-dva/.worktrees/real-pipeline/demo/session4-coffee-ship/container/buildspec.yml`
      Verify: `python3 -c "import yaml,sys; yaml.safe_load(open('container/buildspec.yml'))"`
      parses without error (run from the session4-coffee-ship dir); confirm by inspection
      that `name` is `web` and both `:latest` and `:$IMAGE_TAG` are pushed.

- [ ] 5. Leave `app/buildspec.yml` UNCHANGED (serverless path is out of scope). Confirm the
      pipeline no longer references it (step 3b switched to `container/buildspec.yml`).
      Files: none changed.
      Verify: `grep -rn "app/buildspec.yml" infra/` returns no matches (sanity check only;
      real verification is step 7).

- [ ] 6. Update the docs so Act 4 reflects the REAL flow and the bootstrap order, and the
      architecture section shows the real container-image deploy (not S3 copies). In
      `README.md`: update the Architecture block so the container path reads
      "source.zip (container/) -> CodeBuild (docker build/push to ECR + imagedefinitions.json)
      -> EcsDeployAction rolling update behind ALB, fronted by CloudFront"; note the ALB is
      reachable only via CloudFront (SG locked to the CloudFront prefix list); add a
      "Bootstrap order" note (deploy, run pipeline once to populate ECR, service becomes
      healthy); state the VPC is imported from CloudFormation exports (not created).
      In `FACILITATOR-RUNBOOK.md` Act 4: replace the "zip app/ as source.zip" steps with the
      REAL student-verifiable flow — edit `container/app.py` (e.g. change the `/` body),
      `( cd <session4-coffee-ship> && zip -r /tmp/source.zip container/ -x '*__pycache__*' )`,
      `aws s3 cp /tmp/source.zip s3://${SOURCE_BUCKET}/source.zip`, watch
      Source->Build->Deploy-Test->Approval->Deploy-Prod via `aws codepipeline
      get-pipeline-state`, approve, then `curl https://<CloudFrontUrl>/` and SEE the changed
      response (CloudFront URL from the `CoffeeShipAppPipeline` stack output `CloudFrontUrl`;
      the ALB is NOT publicly reachable). Remove placeholder/"no-op gate"/stand-in language
      for the container deploy. Keep Acts 1/2/3/5 and the serverless/Lambda content intact.
      Files:
      `/Users/erictole/demo/apcr-dva/.worktrees/real-pipeline/demo/session4-coffee-ship/README.md`,
      `/Users/erictole/demo/apcr-dva/.worktrees/real-pipeline/demo/session4-coffee-ship/FACILITATOR-RUNBOOK.md`
      Verify: `grep -n "CloudFrontUrl" FACILITATOR-RUNBOOK.md README.md` and
      `grep -n "container/buildspec.yml\|imagedefinitions" README.md` return matches;
      `grep -rn "deploy/test\|deploy/prod\|S3DeployAction" README.md FACILITATOR-RUNBOOK.md`
      returns nothing.

- [ ] 7. Build and synth to prove the whole CDK app compiles and renders real resources.
      Files: none (verification step).
      Run in
      `/Users/erictole/demo/apcr-dva/.worktrees/real-pipeline/demo/session4-coffee-ship/infra`:
      `npx tsc --noEmit` then
      `CDK_DEFAULT_ACCOUNT=875692608981 npx cdk synth > /dev/null`.
      Verify (all must hold):
      - `npx tsc --noEmit` exits 0.
      - `cdk synth` exits 0 (synth works without live AWS; VPC is imported via
        `Fn::ImportValue`, so no context lookup is needed).
      - In the synthesized `CoffeeShipAppPipeline` template:
        `grep -c "AWS::CloudFront::Distribution" cdk.out/CoffeeShipAppPipeline.template.json`
        >= 1; `grep "SourcePrefixListId" cdk.out/CoffeeShipAppPipeline.template.json` present
        (ALB SG locked to the prefix list, no `0.0.0.0/0` ingress on the ALB SG);
        `grep "Fn::ImportValue" cdk.out/CoffeeShipAppPipeline.template.json` present
        (imported VPC); the pipeline has an ECS deploy action
        (`grep -i "\"ECS\"\|UpdateService" cdk.out/CoffeeShipAppPipeline.template.json`
        present) and NO `S3DeployAction`/`deploy/test` artifacts.
      Expected outcome: both commands pass and the greps confirm the real model. This is the
      authoritative verification; NO live deploy happens in this workflow.

## Notes / assumptions

- NO live AWS deploy, curl, or `cdk deploy` runs in this workflow — synth + tsc +
  inspection only. The orchestrator deploys and does the real curl-through-CloudFront
  check after merge.
- The serverless `app/**` path and `app/buildspec.yml` are deliberately untouched.
- `container/requirements.txt` stays empty (stdlib-only); the Dockerfile already copies it.
- If `npm ci` fails due to a lockfile/registry mismatch in the sandbox, use `npm install`;
  record which was used in the implementer's findings.
