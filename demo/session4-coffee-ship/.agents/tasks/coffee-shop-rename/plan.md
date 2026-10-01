# Implementation Plan — coffee-ship → coffee-shop rename + prose cleanup

## Scope and ground rules (read first)

ALL edits happen inside the worktree:
`/Users/erictole/demo/apcr-dva/.worktrees/rename/demo/session4-coffee-ship`
(referred to below as `<ROOT>`). Do NOT edit anything outside it. Do NOT rename
the `demo/` folder or the `session4-coffee-ship/` folder. Do NOT touch
`node_modules/`, `dist/`, `cdk.out/`, or `.agents/` (the plan/artifacts live
under `.agents/` and must never be staged into a commit — `.agents/` is NOT in
`.gitignore`, so stage files explicitly, never `git add -A`).

Four kinds of change, applied together:

- **A. Full rename** `coffee-ship` → `coffee-shop` and `CoffeeShip` → `CoffeeShop`
  EVERYWHERE under `<ROOT>` (except the excluded dirs). This is a clean
  destroy+redeploy, so renaming physical resource names (ECR, ECS clusters/
  services, DynamoDB, SQS, SSM, Secrets, SNS, alarms, CodeDeploy app/group, log
  group, task family, CodeBuild project, CodePipeline, CloudFormation stack
  names, Lambda function/alarm names) IS intended.
- **B. UI version string**: `container/app.py` `APP_VERSION = "v3-realapp"` → `"v3"`
  (UI only — leave `realapp` in git history and `.agents/` alone).
- **C. Prose: drop the word "demo"** from descriptions/comments (NOT filenames,
  NOT the folder path). Keep filenames `demo-pipeline.sh` and `DEMO-SCRIPT.md`
  and the folder path unchanged.
- **D. Prose: remove "imported VPC" wording and CloudFront prefix-list /
  CloudFront↔ALB security wording** from docs/comments/description strings ONLY.

### CODE THAT MUST STAY FUNCTIONALLY INTACT (names may change, behavior may not)

These are functional and must keep working — only rename `coffee-ship`→
`coffee-shop` tokens inside them; never delete or weaken the logic:

- `infra/lib/app-pipeline-stack.ts`:
  - `ec2.Vpc.fromVpcAttributes(this, 'ImportedVpc', { ... Fn.importValue(...) })`
    and the three `cdk.Fn.importValue('PublicSubnetOne/Two/Three')`,
    `importValue('VpcId')`, `importValue('VpcCidrBlock')` — KEEP (the VPC import
    code stays; only remove *explanatory text/comments* that call it "imported").
  - `CfnParameter` `CloudFrontPrefixListId` (keep the param; its `description`
    may be softened to a neutral one-liner but the param stays).
  - `ec2.PrefixList.fromPrefixListId(...)`, the `SecurityGroupIngress`
    property override (`SourcePrefixListId: ...`), `prodListener`/
    `prodTestListener` created with `open: false`, and
    `prodListener.connections.allowDefaultPortFrom(ec2.Peer.prefixList(...))` —
    KEEP ALL of these exactly.
  - The `/ecs/coffee-ship-prod` → `/ecs/coffee-shop-prod` log group + the
    `repository.grantPull(prodTaskDef.obtainExecutionRole())` /
    exec-role logs grant — KEEP (rename the log group string only).
  - EventBridge S3 `SourceZipCreatedRule` + `enableEventBridgeNotification()` +
    `S3Trigger.NONE` — KEEP.
  - The two CloudFront distributions, two ALBs, blue/green TGs, CodeDeploy
    canary, SNS approval, alarms — KEEP (rename name strings only).
- `container/buildspec.yml`: must still emit `imagedefinitions.json` +
  `imageDetail.json` (SINGULAR) + `taskdef.json` + `appspec.yaml`. KEEP the
  singular `imageDetail.json`.
- `app/template.yaml`: `AutoPublishAlias: live` + `DeploymentPreference`
  (`Canary10Percent5Minutes`) + alarm rollback — KEEP.
- Region `ap-southeast-1` stays pinned everywhere.

### Build / test commands discovered (used for verification)

- CDK synth (primary gate for the TS rename): from `<ROOT>/infra`:
  `npm install` (first time; `node_modules/` is absent) then
  `CDK_DEFAULT_ACCOUNT=000000000000 npx cdk synth > /dev/null`.
  Expected: synth succeeds, exit 0, no errors.
- Python compile for the container service: from `<ROOT>`:
  `python3 -m py_compile container/app.py` (this is the exact check the
  container buildspec runs). Expected: exit 0.
- SAM app unit tests: from `<ROOT>/app`:
  `python3 -m pip install -r dev-requirements.txt && python3 -m pytest -q`.
  Expected: all tests pass. (These don't assert on names, but confirm the SAM
  app still imports/runs after edits.)
- Diagram regeneration (reproducible SVG): from `<ROOT>`:
  `python3 container/build_diagram.py` then
  `rsvg-convert container/architecture.svg -o architecture.png`.
  (AWS icons at `/Users/erictole/demo/apcr-dva/aws-icons/...` and
  `rsvg-convert` are both present on this machine — verified.)
- Shell scripts: `bash -n deploy.sh destroy.sh demo-pipeline.sh` (syntax only;
  they make live AWS calls and are NOT run here).

Grep is NOT a substitute for these build/test commands, but a final
`grep -rinI 'coffee-ship\|CoffeeShip'` (excluding `node_modules/ dist/ cdk.out/
.agents/`) returning zero matches is a useful completeness check AFTER the real
builds pass.

---

## Ordered steps

- [ ] 1. Decide the `coffee-ship.ts` filename and keep CDK wired.
      DECISION: **leave the file named `infra/bin/coffee-ship.ts`** (do NOT
      rename it) — lower churn and avoids touching `cdk.json`'s `app` and
      `package.json`'s `bin` path. Rationale: the filename is not a deployed
      resource name and renaming it buys nothing while adding two more
      coupling points that could break `cdk synth`. Consequently the string
      `coffee-ship` is ALLOWED to remain ONLY as the literal `bin/coffee-ship.ts`
      filename path inside `infra/cdk.json` (`"app": "npx ts-node
      --prefer-ts-exts bin/coffee-ship.ts"`), `infra/package.json`
      (`"bin": { "coffee-ship": "bin/coffee-ship.ts" }`), and
      `infra/package-lock.json` (the mirrored `"coffee-ship":
      "bin/coffee-ship.ts"` bin entry). Everything ELSE in those files that says
      `coffee-ship` is prose/name and DOES get renamed (see steps 7–8).
      Files: none edited in this step (decision only).
      Verify: no action; recorded here so later grep checks expect the two
      filename references to remain.

- [ ] 2. Rename the CDK entry file `infra/bin/coffee-ship.ts` (contents only).
      Change construct ids `CoffeeShipNetworkData` → `CoffeeShopNetworkData` and
      `CoffeeShipAppPipeline` → `CoffeeShopAppPipeline`. In the two `description`
      strings: `coffee-ship` → `coffee-shop`; and apply prose cleanup C+D:
      remove "demo" ("coffee-ship demo:" → "coffee-shop:"), remove the
      "(VPC is imported, not created)" clause and "Uses the existing VPC
      imported from CloudFormation exports" wording (reword to "the VPC"), and
      remove the "(ALB SGs locked to the CloudFront prefix list)" parenthetical
      and "fronted by CloudFront" security wording — keep it to a neutral
      description of the two ECS environments + pipeline. Keep the
      `region: 'ap-southeast-1'` comment but drop the word "demo" from it.
      Files: `infra/bin/coffee-ship.ts`
      Verify: `cd infra && npx cdk synth > /dev/null` succeeds (run after step 4
      so all three TS files are consistent — this step just makes the edit).

- [ ] 3. Rename and clean `infra/lib/network-data-stack.ts`.
      Rename all 3 `CoffeeShip*` construct ids (`CoffeeShipRepo`,
      `CoffeeShipAppConfig`, `CoffeeShipAppConfigEnv`) → `CoffeeShop*` and all 12
      `coffee-ship` string literals → `coffee-shop`: ECR `repositoryName`
      `coffee-ship`; DynamoDB `tableName` `coffee-ship-orders`; SQS `queueName`
      `coffee-ship-orders`; SSM `parameterName` `/coffee-ship/loyalty/
      points-per-dollar`; Secret `secretName` `coffee-ship/payment-provider-api-key`
      and its description; AppConfig `applicationName` `coffee-ship` + its
      description + the env description; `DeploymentStrategy`
      `deploymentStrategyName` `coffee-ship-staged`. Apply prose cleanup C+D to
      the class JSDoc and inline comments: drop "demo" ("Data layer for the
      coffee-ship demo." → "Data layer for the coffee-shop app."), and reword
      the "The VPC is NOT created here — the pipeline stack imports the existing
      VPC from the account's CloudFormation exports" sentence to not call
      attention to an imported VPC (e.g. "Networking is handled by the pipeline
      stack."). Keep the `secretStringTemplate` value `provider: 'demo-payments'`
      as-is UNLESS trivial — it is a JSON data value, not prose; leave it to
      avoid changing behavior/snapshot. Keep all removalPolicy/billing/lifecycle
      code intact.
      Files: `infra/lib/network-data-stack.ts`
      Verify: covered by the synth in step 4.

- [ ] 4. Rename and clean `infra/lib/app-pipeline-stack.ts` (the big one).
      Rename all 8 `CoffeeShip*` construct ids (`CoffeeShipTestCluster`,
      `CoffeeShipProdCluster`, `CoffeeShipTestService`, `CoffeeShipProdAlb`,
      `CoffeeShipProdService`, `CoffeeShipCdn`, `CoffeeShipTestCdn`,
      `CoffeeShipPipeline`) → `CoffeeShop*`. Rename all 33 `coffee-ship` string
      literals → `coffee-shop`, including: `clusterName` `coffee-ship-test` /
      `coffee-ship-prod`; `serviceName` `coffee-ship-test` / `coffee-ship-prod`;
      task family `coffee-ship-prod`; log group name `/ecs/coffee-ship-prod` and
      `streamPrefix: 'coffee-ship-prod'`; alarm names
      `coffee-ship-prod-unhealthy-hosts` and `coffee-ship-test-unhealthy-hosts`;
      CodeDeploy `applicationName` + `deploymentGroupName` `coffee-ship-prod`;
      SNS `topicName` `coffee-ship-approval` and `displayName` "Coffee Ship …"
      → "Coffee Shop …"; CodeBuild `projectName` `coffee-ship-build`;
      `pipelineName` `coffee-ship`; the two CloudFront distribution `comment`
      strings; the `additionalInformation` approval text; `CfnOutput`
      descriptions; any `coffee-ship:latest` ECR tag references in comments.
      Apply prose cleanup C+D to the class JSDoc, section-banner comments, and
      inline comments:
        - Drop "demo": "Application + delivery layer for the coffee-ship demo."
          → "… for the coffee-shop app."; "this demo" phrasings reworded.
        - Remove "imported VPC" wording: "TWO separate ECS environments in the
          imported VPC" → "… ECS environments"; the whole
          "Import the EXISTING VPC from the account's CloudFormation exports …"
          banner comment reworded to a neutral "Reference the VPC."; "in the
          imported VPC" occurrences → "in the VPC".
        - Remove CloudFront prefix-list / "not public" security EXPLANATION
          text: the "NEITHER ALB is exposed to the public internet directly …
          only CloudFront can reach them (no 0.0.0.0/0). The VPC is imported …"
          paragraph, the "Lock the TEST ALB so ONLY CloudFront can reach it"
          banner and its explanatory body, the "prefix-list-locked" wording in
          the test-CDN comment, the "The ALB is internet-facing at the network
          level so CloudFront can reach it, but its security group … only admits
          the CloudFront prefix list, so the public cannot hit it directly"
          comment. Reword to neutral comments that describe WHAT the code does
          mechanically WITHOUT the "only CloudFront can reach it / not public /
          prefix-list-locked" security narrative.
      CRITICAL — DO NOT CHANGE THE CODE: keep `fromVpcAttributes` +
      `Fn.importValue(...)`; keep the `CloudFrontPrefixListId` CfnParameter
      (its `description` may be shortened to a neutral line but keep the param
      and its `default: 'pl-31a34658'`); keep `PrefixList.fromPrefixListId`, the
      `SecurityGroupIngress` override with `SourcePrefixListId`, `open: false`
      on both listeners, and `allowDefaultPortFrom(Peer.prefixList(...))`. Keep
      the inline comments that document the FUNCTIONAL reason for `open:false`
      only to the extent needed, but strip the "brief forbids ANY 0.0.0.0/0"
      security-narrative phrasing; a short neutral note that `open:false`
      prevents an auto-added world ingress is fine. Keep EventBridge rule, the
      `imageDetail`/`imagedefinitions` comments (rename names only).
      Files: `infra/lib/app-pipeline-stack.ts`
      Verify: `cd infra && npm install && CDK_DEFAULT_ACCOUNT=000000000000 npx cdk
      synth > /dev/null` — synth exits 0 with no errors, confirming steps 2–4 are
      internally consistent (ids/props still resolve, VPC import + SG + listeners
      still compile).

- [ ] 5. Rename the `container/` runtime + build files (code/config).
      Edits:
        - `container/app.py`: rename the 8 `coffee-ship` tokens →
          `coffee-shop` — the module docstring, `ORDERS_TABLE_NAME` default
          `coffee-ship-orders` → `coffee-shop-orders`, `LOYALTY_PARAM_NAME`
          default `/coffee-ship/loyalty/points-per-dollar` →
          `/coffee-shop/...`, the `_serve_index` fallback HTML
          (`<title>coffee-ship</title>` and `<h1>coffee-ship</h1>` →
          `coffee-shop`), and the `print("coffee-ship container listening …")`.
          ALSO apply change B here: `APP_VERSION = "v3-realapp"` → `"v3"`.
          Keep all logic (status thresholds, boto3 guard, handlers) intact.
        - `container/taskdef.json`: `family` `coffee-ship-prod` →
          `coffee-shop-prod`; env `ORDERS_TABLE_NAME` value `coffee-ship-orders`
          → `coffee-shop-orders`; `awslogs-group` `/ecs/coffee-ship-prod` →
          `/ecs/coffee-shop-prod`; `awslogs-stream-prefix` `coffee-ship-prod` →
          `coffee-shop-prod`. Keep `<IMAGE1_NAME>`, `<EXECUTION_ROLE_ARN>`,
          `<TASK_ROLE_ARN>`, `<ORDERS_QUEUE_URL>` placeholders and the X86_64
          runtimePlatform intact. (These MUST stay consistent with the CDK
          log-group name from step 4 and the ECR repo name — same `coffee-shop`.)
        - `container/buildspec.yml`: rename the 3 `coffee-ship` tokens → the
          header comment and the two `REPO_URI=…/coffee-ship` ECR URIs →
          `coffee-shop`. KEEP the `imageDetail.json` (singular) emission and all
          four artifact files. Drop no logic.
        - `container/Dockerfile`: header comment `coffee-ship container image`
          → `coffee-shop …`.
        - `container/requirements.txt`: header comment `coffee-ship …` →
          `coffee-shop …`.
      Files: `container/app.py`, `container/taskdef.json`,
      `container/buildspec.yml`, `container/Dockerfile`,
      `container/requirements.txt`
      Verify: `python3 -m py_compile container/app.py` exits 0; and
      `python3 -c "import json;json.load(open('container/taskdef.json'))"` exits 0
      (valid JSON). Confirm `grep -c 'imageDetail.json' container/buildspec.yml`
      ≥ 1 (singular artifact still emitted).

- [ ] 6. Regenerate the architecture diagram from the renamed generator
      (reproducible SVG + PNG; handles rename A and prose D in the SVG).
      Edit `container/build_diagram.py`: rename its 7 `coffee-ship` tokens →
      `coffee-shop` (the node `sub` labels `coffee-ship-test`,
      `coffee-ship-prod`, `coffee-ship-orders`, the `CodePipeline`
      sub `coffee-ship`, the `ECR` sub `coffee-ship repo`, zone titles
      `coffee-ship-test (rolling)` / `coffee-ship-prod (blue/green)`, docstring).
      ALSO apply prose cleanup D in the generated labels/notes: the
      `Imported-VPC note` line "Both ALBs run in the imported VPC … only
      CloudFront can reach them." → reword to drop "imported" and the
      "only CloudFront can reach them" security clause (e.g. "Both ALBs run in
      the VPC (public subnets, no NAT)."); the `alb` node `sub`
      "SG = CF prefix list" → a neutral label (e.g. "test ALB" with no SG
      sub, or sub "HTTP"); the docstring lane descriptions mentioning
      "imported VPC, SG locked to the CloudFront prefix list" and "prefix list"
      reworded. Then REGENERATE both artifacts rather than hand-editing the SVG:
      run `python3 container/build_diagram.py` (writes
      `container/architecture.svg`), copy it to `<ROOT>/architecture.svg`, and
      run `rsvg-convert container/architecture.svg -o architecture.png`.
      Files edited: `container/build_diagram.py`; files regenerated:
      `container/architecture.svg`, `architecture.svg` (top-level),
      `architecture.png`.
      Verify: `python3 container/build_diagram.py` prints "wrote …" and exits 0;
      then `grep -c 'coffee-ship' container/architecture.svg` returns 0 and
      `grep -ci 'prefix list\|imported vpc' container/architecture.svg` returns 0.
      (If `rsvg-convert`/icons were unavailable the step would note it; both are
      present on this machine.)

- [ ] 7. Rename the `infra/` config files (respecting the step-1 decision).
      - `infra/package.json`: `"name": "coffee-ship-infra"` →
        `"coffee-shop-infra"`; the `description` "CDK v2 infra + pipeline for the
        session4 coffee-ship demo (ap-southeast-1)" → "CDK v2 infra + pipeline
        for the session4 coffee-shop app (ap-southeast-1)" (rename + drop
        "demo"). KEEP the `bin` key `"coffee-ship": "bin/coffee-ship.ts"`
        UNCHANGED (step-1 decision: filename stays). Note: renaming only the
        description/name does not touch the `bin` map key.
      - `infra/cdk.json`: KEEP `"app": "npx ts-node --prefer-ts-exts
        bin/coffee-ship.ts"` UNCHANGED (filename stays). No other `coffee-ship`
        strings exist in this file.
      - `infra/package-lock.json` (generated lockfile): update the two
        `"name": "coffee-ship-infra"` fields → `"coffee-shop-infra"` to match
        `package.json`. KEEP the `bin` map key `"coffee-ship":
        "bin/coffee-ship.ts"` UNCHANGED (mirrors `package.json`'s bin, filename
        stays). Alternatively, after editing `package.json`, running
        `cd infra && npm install` regenerates the lockfile `name` fields
        correctly — either hand-edit the two `name` lines or let `npm install`
        in step 7's Verify refresh them; do NOT otherwise rewrite the lockfile.
      Files: `infra/package.json` (edit), `infra/package-lock.json` (edit the
      two `name` fields), `infra/cdk.json` (no change — verify only).
      Verify: `python3 -c "import json;json.load(open('infra/package.json'));
      json.load(open('infra/package-lock.json'))"` exits 0 (both valid JSON);
      `cd infra && npx cdk synth > /dev/null` still succeeds (the `app` path and
      `bin` entry still point at the real file); `grep -c 'coffee-ship-infra'
      infra/package.json infra/package-lock.json` returns 0.

- [ ] 8. Rename `container/frontend/package.json`.
      `"name": "coffee-ship-frontend"` → `"coffee-shop-frontend"`. Do NOT touch
      `container/frontend/package-lock.json` by hand beyond this — note that the
      lockfile's `"name"` fields still say `coffee-ship-frontend`; update the two
      `name` occurrences in `container/frontend/package-lock.json` to match
      (`coffee-ship-frontend` → `coffee-shop-frontend`) so the lockfile stays
      consistent with package.json. This is a metadata rename only; no install
      is required for the Docker build (which runs `npm ci` fresh in-image, and
      a name mismatch would not break `npm ci`, but we keep them consistent).
      Files: `container/frontend/package.json`,
      `container/frontend/package-lock.json`
      Verify: `python3 -c "import json;json.load(open('container/frontend/package.json'));
      json.load(open('container/frontend/package-lock.json'))"` exits 0 (both
      valid JSON); `grep -rc 'coffee-ship-frontend' container/frontend` returns 0.
      (The `App.jsx` `APP_NAME = 'Coffee Shop'` and `index.html` `<title>Coffee
      Shop</title>` are already "Coffee Shop" and are the demo-script's edit
      target — leave them unchanged.)

- [ ] 9. Rename the `app/` SAM application files (names/strings only).
      - `app/template.yaml`: `Description` "coffee-ship serverless app …" →
        "coffee-shop serverless app …"; both `Default: coffee-ship-orders` →
        `coffee-shop-orders`; `AlarmName: coffee-ship-loyalty-errors` →
        `coffee-shop-loyalty-errors`; `FunctionName: coffee-ship-loyalty` →
        `coffee-shop-loyalty`. KEEP `AutoPublishAlias: live`,
        `DeploymentPreference` canary, alarm wiring intact.
      - `app/appspec.yaml`: `Name: coffee-ship-loyalty` → `coffee-shop-loyalty`;
        hook names `coffee-ship-loyalty-preTrafficHook` /
        `…-postTrafficHook` → `coffee-shop-…`.
      - `app/samconfig.toml`: `stack_name = "coffee-ship-app"` →
        `"coffee-shop-app"`; header comment rename.
      - `app/src/app.py`: docstring `coffee-ship loyalty Lambda handler.` →
        `coffee-shop …`.
      - `app/buildspec.yml`: header comment `coffee-ship serverless app` →
        `coffee-shop …`. (Leave the "placeholder"/headless-gate logic alone.)
      - `app/requirements.txt`, `app/dev-requirements.txt`: header comment
        `coffee-ship loyalty Lambda` → `coffee-shop …`.
      - `app/tests/test_handler.py`: docstring `coffee-ship loyalty Lambda
        handler` → `coffee-shop …`.
      Files: `app/template.yaml`, `app/appspec.yaml`, `app/samconfig.toml`,
      `app/src/app.py`, `app/buildspec.yml`, `app/requirements.txt`,
      `app/dev-requirements.txt`, `app/tests/test_handler.py`
      Verify: from `<ROOT>/app`: `python3 -m pip install -r dev-requirements.txt
      && python3 -m pytest -q` passes; `python3 -c "import json" ` n/a — instead
      confirm YAML/template still parses by running the test suite (it imports
      `app`) and, if `sam` is present, `sam validate --lint` (non-fatal if SAM
      CLI absent). `grep -rc 'coffee-ship' app` returns 0.

- [ ] 10. Rename the `reference/` teaching artifacts (names/strings only).
      - `reference/orders-queue.cfn.json`: `Description` text + `QueueName:
        coffee-ship-orders` + the two output descriptions → `coffee-shop`
        equivalents (keep it valid JSON; the "Teaching artifact only - not
        deployed" line stays, it is not the word "demo").
      - `reference/orders-queue.sam.yaml`: the description + `QueueName:
        coffee-ship-orders` + two output descriptions → `coffee-shop`.
      - `reference/orders-queue-cdk.ts`: the header comment + `queueName:
        'coffee-ship-orders'` → `coffee-shop-orders`.
      - `reference/README.md`: "same coffee-ship orders" and
        "`coffee-ship-orders`" → `coffee-shop`.
      Files: `reference/orders-queue.cfn.json`, `reference/orders-queue.sam.yaml`,
      `reference/orders-queue-cdk.ts`, `reference/README.md`
      Verify: `python3 -c "import json;json.load(open('reference/orders-queue.cfn.json'))"`
      exits 0; `grep -rc 'coffee-ship' reference` returns 0.

- [ ] 11. Rename + clean the shell scripts `deploy.sh` and `destroy.sh`.
      Rename every `coffee-ship` → `coffee-shop` and `CoffeeShip*` →
      `CoffeeShop*` (stack-name vars `NETWORK_STACK`/`PIPELINE_STACK`, `ECR_REPO`,
      `PIPELINE_NAME`, `SAM_STACK` `coffee-ship-app`, the service/cluster names
      in echo lines, URLs, the `coffee-ship-source.XXXXXX` mktemp template).
      Apply prose cleanup C+D to the comments and echoed summary lines:
        - Drop "demo": header "stand up the coffee-ship DVA-C03 testing-and-
          deployment demo" → "… the coffee-shop DVA-C03 testing-and-deployment
          app/project"; "coffee-ship deploy"/"coffee-ship destroy" banners →
          "coffee-shop deploy/destroy"; "coffee-shop demo deployed/destroyed" →
          "coffee-shop app deployed/destroyed"; "cost real money … demo"
          wording reworded to drop "demo"; the "PERMANENTLY DELETE the
          coffee-ship demo" warning → "… the coffee-shop resources".
        - Remove the CloudFront security narrative in `deploy.sh`: the comment
          "Neither ALB is publicly reachable (each SG only admits the CloudFront
          prefix list) …" → neutral "Resolve the CloudFront URLs from the stack
          outputs."; and the summary line
          `" CloudFront URL : ${CLOUDFRONT_URL}  (PROD — use this; the ALB is not
          public)"` → shorten to just a URL label, e.g.
          `" CloudFront URL : ${CLOUDFRONT_URL}  (PROD)"`. Remove the standalone
          "not public" phrasing.
        - KEEP all functional bash: ordering comments can stay but reword the
          "coffee-ship:latest" references to `coffee-shop:latest`; keep the
          `--platform linux/amd64`, stack-resource lookups, EventBridge-trigger
          behavior. Do NOT remove the two-environment / blue-green explanation
          beyond the "demo" word.
      Files: `deploy.sh`, `destroy.sh`
      Verify: `bash -n deploy.sh && bash -n destroy.sh` exit 0 (syntax OK — the
      scripts are NOT executed, they make live AWS calls). `grep -c 'coffee-ship'
      deploy.sh destroy.sh` returns 0; `grep -ci 'not public\|prefix list'
      deploy.sh` returns 0.

- [ ] 12. Rename + clean `demo-pipeline.sh` (keep the FILENAME).
      Rename every `coffee-ship` → `coffee-shop` and `CoffeeShip*` →
      `CoffeeShop*` (the `PIPELINE_STACK` `CoffeeShipAppPipeline`,
      `PIPELINE_NAME`/`CODEDEPLOY_APP` `coffee-ship*`, `coffee-ship-source`
      mktemp template, the "rolling to coffee-ship-test" echoes). Apply prose
      cleanup C: drop "demo" from the comments/echoes that describe it as a
      "demo" ("guided, step-by-step live demo of the Coffee Shop release
      pipeline" → "guided, step-by-step walkthrough of the Coffee Shop release
      pipeline"; "Demo complete." → "Walkthrough complete." or similar). DO NOT
      rename the file. KEEP `OLD_NAME="Coffee Shop"` / `NEW_NAME="BeanThere
      Cafe"` and the whole `sed` edit + poll + approval + CodeDeploy flow intact.
      The user-facing "Coffee Shop" product name stays "Coffee Shop".
      Files: `demo-pipeline.sh`
      Verify: `bash -n demo-pipeline.sh` exits 0; `grep -c 'coffee-ship'
      demo-pipeline.sh` returns 0; confirm `OLD_NAME="Coffee Shop"` and
      `NEW_NAME="BeanThere Cafe"` are unchanged (`grep -c 'BeanThere Cafe'
      demo-pipeline.sh` ≥ 1).

- [ ] 13. Rename + clean `README.md`.
      Rename all 38 `coffee-ship` → `coffee-shop` and all 10 `CoffeeShip*` →
      `CoffeeShop*` (title, the `infra/` table row stacks, all resource names,
      the ASCII architecture block labels, `coffee-ship-orders`,
      `/coffee-ship/loyalty/...`, the ECR repo, pipeline name, log group,
      alarm). Apply prose cleanup C+D:
        - Drop "demo" from the title and body: "# coffee-ship — AWS DVA-C03
          Testing & Deployment demo" → "# coffee-shop — AWS DVA-C03 Testing &
          Deployment project" (or "app"); "A standalone, deployable demo for …"
          → "A standalone, deployable app/project for …"; "this demo", "demo
          volume", "demo is over", "the five-act live demo script" table row,
          "Two gotchas this demo already handles", "demonstrated by this demo",
          "the coffee-shop demo deployed" → reword without "demo". KEEP the
          literal `./demo-pipeline.sh` command and the `DEMO-SCRIPT.md` filename
          references (those are filenames). The "### Demo the pipeline" heading
          → "### Run the pipeline".
        - Remove "imported VPC" wording: "the EXISTING VPC is imported from
          CloudFormation exports (VpcId, …) — this demo does NOT create a VPC."
          and the Deploy-section "(the VPC is imported from CloudFormation
          exports, not created)" and "the VPC uses public subnets only with zero
          NAT gateways" (the NAT/cost line can stay but drop the "imported"
          framing) → reword so the VPC is just "the VPC".
        - Remove CloudFront prefix-list / "not reachable from the public
          internet" security narrative: the `Edge:` block in the ASCII diagram
          caption ("Neither ALB is reachable from the public internet directly …
          each ALB security group only admits the AWS managed CloudFront
          origin-facing prefix list (no 0.0.0.0/0 ingress). Reach each app via
          its CloudFront URL, never the ALB DNS name.") → reword to a neutral
          "CloudFront sits in front of each ALB (CloudFrontUrl → prod,
          TestCloudFrontUrl → test); reach each app via its CloudFront URL.";
          the `(SG = CF prefix list)` labels inside the ASCII art → drop/neutral;
          the Deploy step "Neither ALB is publicly reachable; always use the
          CloudFront URLs." → "Use the CloudFront URLs."; the `(SG = CF prefix
          list only)` art label removed.
      KEEP all factual pipeline/behavior description (two envs, rolling vs
      blue/green, imageDetail.json singular, bootstrap order, log-group gotcha).
      Rename `coffee-ship` inside those passages but keep the passages.
      Files: `README.md`
      Verify: `grep -c 'coffee-ship' README.md` and `grep -c 'CoffeeShip'
      README.md` both return 0; `grep -ci 'imported vpc\|prefix list\|not
      public\|not reachable from the public' README.md` returns 0; the literal
      filename refs `demo-pipeline.sh` / `DEMO-SCRIPT.md` still present
      (`grep -c 'demo-pipeline.sh' README.md` ≥ 1). Markdown is not built; this
      is a prose file.

- [ ] 14. Rename + clean `FACILITATOR-RUNBOOK.md`.
      Rename all 42 `coffee-ship` → `coffee-shop` and 3 `CoffeeShip*` →
      `CoffeeShop*` (stack names in the CLI snippets, `coffee-ship-test`/
      `coffee-ship-prod` clusters/services, `coffee-ship-loyalty`,
      `coffee-ship-approval`, `coffee-ship-prod-unhealthy-hosts`,
      `/coffee-ship/loyalty/...`, `coffee-ship/payment-provider-api-key`, the
      ECR repo, pipeline name). Apply change B inside this doc: the example
      output `# -> {"status": "ok", "version": "v3-realapp"}` → `"version":
      "v3"` (so the runbook matches the new APP_VERSION). Apply prose cleanup
      C+D: title "coffee-ship — Facilitator runbook (five-act live demo)" →
      "coffee-shop — Facilitator runbook (five-act live walkthrough)" or drop
      "demo"; "running the DVA-C03 … demo live" reworded; the "> Blue/green IS
      demonstrated here." note keeps its meaning (that's "demonstrated", not the
      word "demo" as a noun for the project — fine to keep, but change "demo"
      noun usages). Remove the CloudFront prefix-list security narrative: the
      comment "served through CloudFront, NOT the ALB — the ALB SG only admits
      the CloudFront prefix list" → neutral "served through CloudFront"; the
      Act-4 "CloudFront as the single public entry point in front of each
      locked-down ALB" → "CloudFront in front of each ALB". KEEP all the CLI
      commands' behavior; only rename the resource names in them and reword
      prose. KEEP the `./demo-pipeline.sh` / `DEMO-SCRIPT.md` filename refs.
      Files: `FACILITATOR-RUNBOOK.md`
      Verify: `grep -c 'coffee-ship' FACILITATOR-RUNBOOK.md` and `grep -c
      'CoffeeShip' …` both return 0; `grep -c 'realapp' FACILITATOR-RUNBOOK.md`
      returns 0; `grep -ci 'prefix list\|locked-down alb\|only admits' …`
      returns 0.

- [ ] 15. Rename + clean `DEMO-SCRIPT.md` (keep the FILENAME; title may change).
      Rename all 10 `coffee-ship` → `coffee-shop` and 4 `CoffeeShip*` →
      `CoffeeShop*` (`CoffeeShipAppPipeline` in the snippets, `coffee-ship-test`/
      `coffee-ship-prod`, `coffee-ship-prod-unhealthy-hosts`, the pipeline name
      `coffee-ship` in the `--name` flags and `--application-name coffee-ship-prod`).
      Apply prose cleanup C: the title "# Coffee Shop — pipeline demo script
      (copy-paste)" MAY become "# Coffee Shop — pipeline walkthrough
      (copy-paste)" (drop "demo" as the task permits), and "It mirrors
      `demo-pipeline.sh`" keeps the filename ref. "hands-off demo" → "hands-off
      walkthrough". KEEP the product name "Coffee Shop" and the "Coffee Shop" →
      "BeanThere Cafe" rename narrative (that's the headline scenario) and all
      the `sed`/`curl`/`aws` commands' behavior (rename resource names only).
      Files: `DEMO-SCRIPT.md`
      Verify: `grep -c 'coffee-ship' DEMO-SCRIPT.md` and `grep -c 'CoffeeShip'
      …` both return 0; the scenario strings `Coffee Shop` and `BeanThere Cafe`
      still present (`grep -c 'BeanThere Cafe' DEMO-SCRIPT.md` ≥ 1); the
      `demo-pipeline.sh` filename ref still present.

- [ ] 16. Full-tree verification + completeness sweep.
      Run the real build/test gates end to end and the final grep sweep:
        a. `cd infra && npm install && CDK_DEFAULT_ACCOUNT=000000000000 npx cdk
           synth > /dev/null` — exit 0, no errors (proves the renamed CDK still
           synthesizes; names/ids all resolve, VPC import + SG + listeners +
           CodeDeploy still compile).
        b. `cd <ROOT> && python3 -m py_compile container/app.py` — exit 0.
        c. `cd app && python3 -m pip install -r dev-requirements.txt && python3
           -m pytest -q` — all tests pass.
        d. `bash -n deploy.sh destroy.sh demo-pipeline.sh` — exit 0.
        e. `python3 container/build_diagram.py` — exit 0 (SVG regenerated); then
           `rsvg-convert container/architecture.svg -o architecture.png` — exit 0.
        f. Completeness grep (excluding generated/.agents):
           `grep -rinI 'coffee-ship\|CoffeeShip' <ROOT> --exclude-dir=node_modules
           --exclude-dir=dist --exclude-dir=cdk.out --exclude-dir=.agents`
           — the ONLY allowed matches are the `bin/coffee-ship.ts` filename
           references in `infra/cdk.json` (`"app": "… bin/coffee-ship.ts"`),
           `infra/package.json` (`"coffee-ship": "bin/coffee-ship.ts"`), and
           `infra/package-lock.json` (`"coffee-ship": "bin/coffee-ship.ts"`),
           plus the actual filename `infra/bin/coffee-ship.ts` itself. Any OTHER
           match is a miss to fix.
        g. `grep -rinI 'v3-realapp'` under `container/` and the docs returns 0
           (realapp removed from UI + runbook); it may still appear in
           `.agents/` — that's fine, `.agents/` is out of scope.
        h. `grep -rinI 'imported vpc\|prefix-list-locked\|not public\|only
           CloudFront can reach\|not reachable from the public' <ROOT>
           --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=.agents`
           returns 0 (prose D removed). The FUNCTIONAL code tokens
           (`CloudFrontPrefixListId`, `prefixList`, `open: false`,
           `fromVpcAttributes`, `importValue`) MUST still be present in
           `infra/lib/app-pipeline-stack.ts` — spot-check they are
           (`grep -c 'open: false' infra/lib/app-pipeline-stack.ts` ≥ 2,
           `grep -c 'fromVpcAttributes' …` ≥ 1,
           `grep -c 'CloudFrontPrefixListId' …` ≥ 1).
      Files: none edited (verification only; fix regressions in the owning step).
      Verify: all of a–e exit 0; f shows only the three allowed filename matches;
      g, h as specified; the functional-code spot-checks are non-zero.

- [ ] 17. Stage ONLY source files and leave review artifacts out.
      When committing, stage the edited source files explicitly by path (the
      `infra/`, `container/`, `app/`, `reference/` files, the three scripts, the
      three docs, and the regenerated `architecture.svg`/`architecture.png`).
      Do NOT `git add -A` and do NOT stage anything under `.agents/` (not in
      `.gitignore`). `node_modules/`, `dist/`, `cdk.out/`, `*.zip` are already
      git-ignored.
      Files: n/a (git hygiene note for the implementer).
      Verify: `git status --porcelain` shows no `.agents/` paths staged;
      `git diff --cached --name-only` lists only intended source files.

---

## Notes / assumptions

- The product/display name "Coffee Shop" (frontend `APP_NAME`, `<title>`, doc
  headlines, `demo-pipeline.sh` `OLD_NAME`) is the user-facing app name and is
  intentionally NOT renamed to "Coffee Shop app"/"coffee-shop"; only the
  project/resource identifier `coffee-ship`→`coffee-shop` changes. The
  "Coffee Shop" → "BeanThere Cafe" scenario is the demonstration edit and stays.
- `infra/bin/coffee-ship.ts` keeps its filename by decision (step 1); this is
  why two `coffee-ship` strings legitimately survive in `cdk.json` and
  `package.json` as the `app`/`bin` path. If a reviewer prefers zero
  `coffee-ship` tokens anywhere, the alternative is to `git mv` the file to
  `coffee-shop.ts` and update both references — but that is higher churn with no
  functional benefit, so it is deliberately not done.
- `architecture.svg` (top-level and `container/`) are generated; they are fixed
  by regenerating from `build_diagram.py`, not hand-edited, to stay reproducible.
- `app/src/app.py` keeps `POINTS_PER_DOLLAR` env default `'10'` and all logic;
  only its docstring is renamed.
- The `provider: 'demo-payments'` secret template value in network-data-stack.ts
  is a JSON data value, not prose, and is left unchanged to avoid altering the
  generated secret shape.
```
