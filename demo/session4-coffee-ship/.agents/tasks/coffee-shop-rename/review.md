# coffee-ship → coffee-shop rename and prose cleanup

This change renames the project identity from `coffee-ship`/`CoffeeShip` to `coffee-shop`/`CoffeeShop` across CDK construct ids, physical resource names (ECR repo, DynamoDB/SQS, SSM/Secrets, AppConfig, ECS clusters/services, ALBs, log group, CodeDeploy app/group, CodePipeline, CodeBuild, SNS topic, alarms), the SAM reference app, scripts, and docs. It bumps the container `APP_VERSION` from `v3-realapp` to `v3`, and strips three narrative threads from prose/comments only: the word "demo", the "imported VPC" framing, and the CloudFront-prefix-list/ALB-security explanation. The functional security posture (SG ingress restricted to the CloudFront origin-facing prefix list, `open:false` listeners), the VPC import via `Fn.importValue`, and the two-env/blue-green pipeline topology are all preserved. Watch for: nothing blocking — the critical invariants hold (confirmed).

**Verdict**: APPROVED

## High-level view

The rename is clean and complete. Every `coffee-ship`/`CoffeeShip` token outside the allowed carve-outs is gone; the only residual matches are the intentionally-kept `bin/coffee-ship.ts` filename (referenced in cdk.json and package manifests) and the `demo/session4-coffee-ship` folder path in the runbook, both explicitly out of scope.

The security code is intact and was not weakened. The TEST ALB security group still overrides the default `0.0.0.0/0` ingress with `SourcePrefixListId` (CloudFront prefix list), and the prod listeners keep `open:false` with an explicit `allowDefaultPortFrom(Peer.prefixList(...))`. Only the surrounding comments lost their narrative; the CloudFormation shape is unchanged.

The VPC import is intact: `ec2.Vpc.fromVpcAttributes` with five `Fn.importValue` calls (VpcId, VpcCidrBlock, three public subnets) remains in place. The "imported VPC" wording was removed from comments only.

The prose sweeps landed in the files this PR touches. `v3-realapp` is gone everywhere, and the "imported VPC" / "prefix-list-locked" / "only CloudFront can reach" phrasings are removed from the stack comments. Residual uses of the word "demo" live only in `container/frontend/src/App.jsx`, which this PR does not modify — those are pre-existing and out of scope.

<details>
<summary>Issues (0)</summary>

No blocking or non-blocking findings. All critical invariants verified.

</details>

<details>
<summary>Details</summary>

### Rename completeness

A tree-wide grep for `coffee-ship`/`CoffeeShip` (excluding node_modules/dist/cdk.out/.agents/.git) returns only the four expected carve-outs: `infra/cdk.json`, `infra/package.json`, and `infra/package-lock.json` all reference the kept filename `bin/coffee-ship.ts`, and `FACILITATOR-RUNBOOK.md` references the folder path `demo/session4-coffee-ship` (lines 5 and 177). Both the filename and folder path were explicitly designated to stay. Physical resource names flipped consistently — `coffee-shop`, `coffee-shop-orders`, `coffee-shop-test`, `coffee-shop-prod`, `/coffee-shop/loyalty/...`, `/ecs/coffee-shop-prod` — and the matching CDK construct ids (`CoffeeShopRepo`, `CoffeeShopTestCluster`, `CoffeeShopProdService`, `CoffeeShopCdn`, `CoffeeShopPipeline`, etc.) moved in lockstep. Because construct ids changed, these are replacement resources on next deploy, which is the expected consequence of a physical-name rename and consistent with the stacks also being renamed (`CoffeeShopNetworkData`, `CoffeeShopAppPipeline`).

### Security code preserved under reworded comments

The claim worth verifying on a rename like this is whether the comment cleanup quietly loosened the SG rules. It did not. The TEST ALB override still reads:

```ts
cfnTestAlbSg.addPropertyOverride('SecurityGroupIngress', [
  {
    Description: 'Allow HTTP from the CloudFront origin-facing prefix list',
    IpProtocol: 'tcp',
    FromPort: 80, ToPort: 80,
    SourcePrefixListId: cloudFrontPrefixList.prefixListId,
  },
]);
```

`SourcePrefixListId` — not `CidrIp: 0.0.0.0/0`. Both prod listeners keep `open: false` (lines 236, 247), and the prod ingress is added explicitly via `prodListener.connections.allowDefaultPortFrom(ec2.Peer.prefixList(...))` (lines 349-350). The `CloudFrontPrefixListId` CfnParameter (line 111) and `SourcePrefixListId: cloudFrontPrefixList.prefixListId` (line 190) are present. The only edits in this region are comment text: "Allow HTTP only from..." → "Allow HTTP from...", and the removal of the "only CloudFront can reach them" narrative. Functional behavior is byte-for-byte equivalent on the CloudFormation side.

### VPC import preserved

`ec2.Vpc.fromVpcAttributes(this, 'ImportedVpc', { ... })` with `cdk.Fn.importValue('VpcId')`, `VpcCidrBlock`, and `PublicSubnetOne/Two/Three` remains intact at lines 76-83. The comment above it changed from "Import the EXISTING VPC... We do not create a VPC" to "Reference the VPC via CloudFormation exports", which satisfies the "remove the 'imported VPC' text while keeping the code" requirement.

### Version bump and prose sweeps

`APP_VERSION` is now `"v3"` (was `"v3-realapp"`) in `container/app.py`, and a grep for `v3-realapp`/`realapp` across the tree returns nothing. The "imported VPC", "prefix-list-locked", "only cloudfront can reach", and "not reachable from the public" phrasings are gone from the stack comments. The remaining uses of the word "demo" are confined to `container/frontend/src/App.jsx` (comments plus two visible UI strings on lines 207 and 258). That file is not part of this diff — the strings pre-date this PR and are therefore out of scope for this review.

### Pipeline invariants unchanged

The two-environment split (separate `coffee-shop-test` and `coffee-shop-prod` ECS clusters), the prod blue/green CodeDeploy group (canary 10%/5min, auto-rollback on failure and alarm), the two CloudFront distributions, the singular `imageDetail.json` buildspec output (confirmed in `container/buildspec.yml`, with the explanatory note about the exact filename kept), and the `/ecs/coffee-shop-prod` log group matched to `taskdef.json`'s `awslogs-group` all survive the rename. Only names and comments changed in these paths.

### Verification evidence

The coder's `verification.md` records a passing local suite: `py_compile`, container pytest (4), app pytest (5), frontend `npm run build`, `cdk synth CoffeeShopNetworkData CoffeeShopAppPipeline` (exit 0), `tsc --noEmit` (exit 0), `bash -n` on the three scripts, and diagram regeneration. The completeness grep and functional spot-check counts in that file match what I independently re-ran here (`open:false` ×2, `fromVpcAttributes` ×1, `importValue` ×5, prefix-list references present). Evidence is present and consistent; no suite re-run was necessary.

</details>

<details>
<summary>File map</summary>

- `infra/lib/app-pipeline-stack.ts` — construct id / resource-name rename; comment cleanup (imported-VPC, prefix-list narrative); security + VPC code unchanged
- `infra/lib/network-data-stack.ts` — construct id / resource-name rename; comment cleanup
- `infra/bin/coffee-ship.ts` — stack id references renamed (file kept)
- `infra/cdk.json`, `infra/package.json`, `infra/package-lock.json` — bin key / app path still reference kept `bin/coffee-ship.ts` filename
- `container/app.py` — `APP_VERSION` v3-realapp→v3; default resource names and prose updated
- `container/taskdef.json`, `container/buildspec.yml`, `container/Dockerfile`, `container/requirements.txt` — name updates; `imageDetail.json` singular preserved
- `container/build_diagram.py`, `architecture.svg`/`.png` (top-level and container) — diagram labels regenerated to coffee-shop
- `app/*` (SAM reference app: template.yaml, samconfig.toml, buildspec.yml, appspec.yaml, src/app.py, tests, requirements) — name updates
- `reference/*` — orders-queue snippets (cdk.ts, cfn.json, sam.yaml) and README renamed
- `README.md`, `DEMO-SCRIPT.md`, `FACILITATOR-RUNBOOK.md` — prose/name updates; filenames and folder path kept
- `deploy.sh`, `destroy.sh`, `demo-pipeline.sh` — resource-name updates; filenames kept

Full diff: `git -C /Users/erictole/demo/apcr-dva/.worktrees/rename diff main...coffee-shop-rename`

</details>
