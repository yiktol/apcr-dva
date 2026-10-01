# Implementation Plan — coffee-ship REAL app rewrite

Turn the coffee-ship demo into a REAL AWS-backed coffee-ordering app: boto3
backend writing to DynamoDB with an SSM-driven loyalty rate and time-based order
status, a React SPA that shows live order status + the 10 most recent orders, an
IAM grant for `ssm:GetParameter`, and an architecture diagram rebuilt from the
official AWS icon set. Region pinned to **ap-southeast-1**. Verification is LOCAL
ONLY (build + synth); no live AWS, no docker push, no cdk deploy.

All paths below are absolute under the worktree. Worktree root:
`/Users/erictole/demo/apcr-dva/.worktrees/realapp` (branch `coffee-ship-realapp`).
Project dir (abbreviated `<P>` in verify commands):
`/Users/erictole/demo/apcr-dva/.worktrees/realapp/demo/session4-coffee-ship`.
Worktree git commands MUST use `git -C /Users/erictole/demo/apcr-dva/.worktrees/realapp`.

## Design decisions (made here, grounded in the code)

- **SVG icons, not PNG.** session3's `build_diagram.py` embedded `*_64.png`, but
  this icon set ships `*_64.svg` for every service needed (verified: CloudFront,
  Elastic-Load-Balancing, Elastic-Container-Service, AWS-Fargate,
  Elastic-Container-Registry, DynamoDB, AWS-Systems-Manager, CodePipeline,
  CodeBuild, Simple-Storage-Service, EventBridge). Embed as
  `data:image/svg+xml;base64,...` so the output SVG stays self-contained. Reuse
  session3's layout approach (zones, bezier edges, legend, base64 embed).
- **Status is a pure function of time**, not stored/mutated: `status_for(created_at, now)`
  returns RECEIVED (`< 10s`), BREWING (`10–25s`), READY (`>= 25s`). Storing only
  `createdAt` keeps writes simple and makes the function unit-testable with no
  AWS. Thresholds chosen so a facilitator sees all three states within ~30s of
  polling at 3–4s.
- **Loyalty rate from SSM, cached ~60s, fallback 10.** A module-level cache
  `(value, fetched_at)` avoids an SSM call per request; on any `ClientError` or
  missing param the code falls back to `10` (matches the SSM param default and
  the old `POINTS_PER_DOLLAR`). points = `floor(total) * rate`.
- **Scan for GET /orders.** The table has only `orderId` (PK) and no GSI; the
  demo is tiny, so a `Scan` + in-memory sort by `createdAt` desc + top 10 is
  correct and simplest. A code comment states this is a demo-scale choice.
- **boto3 is the ONLY new dependency.** It goes in `requirements.txt`; the
  Dockerfile python stage must `pip install --no-cache-dir -r requirements.txt`.
  `app.py` guards the boto3 import (try/except at module load, lazy client
  creation) so `python3 -m py_compile` and `/health` work even if boto3 or AWS
  is unreachable.
- **Smallest IAM change:** expose the loyalty `ssm.StringParameter` from
  `network-data-stack.ts` as a public readonly field and call
  `loyaltyParam.grantRead(taskRole)` in `app-pipeline-stack.ts`. This adds only
  `ssm:GetParameter*` on that one parameter ARN; nothing else in infra changes.
- **Same-origin API.** The SPA keeps calling relative paths (`/order`, `/orders`,
  `/order/{id}`, `/health`) — no base URL, no CORS — because CloudFront → ALB →
  container serve the SPA and API from one origin.
- **ALB health check stays green:** `GET /` still returns the SPA `index.html`
  (text/html 200) and `/health` returns 200 even when DynamoDB is down, so the
  circuit breaker never trips on a data-plane outage.

## Ordered steps

- [ ] 1. Add boto3 dependency and install it in the Docker python runtime stage.
      Put `boto3` (pinned, e.g. `boto3==1.34.*` or the latest 1.x — pin exact in
      the file) in requirements.txt; in the Dockerfile python stage add
      `RUN pip install --no-cache-dir -r requirements.txt` AFTER `COPY requirements.txt ./`
      and before copying app.py. Keep multi-stage node build, `EXPOSE 8080`,
      `ENV PORT=8080`, `CMD ["python","app.py"]`, and the
      `COPY architecture.svg /app/static/architecture.svg` line.
      Files: `<P>/container/requirements.txt`, `<P>/container/Dockerfile`
      Verify: `grep -q boto3 <P>/container/requirements.txt` and visually confirm
      the Dockerfile pip step; real build verified in step 3's docker build.

- [ ] 2. Rewrite container/app.py as the REAL backend (depends on step 1).
      Region from env `AWS_DEFAULT_REGION`/`AWS_REGION` default `ap-southeast-1`.
      Table from env `ORDERS_TABLE_NAME` default `coffee-ship-orders`. Loyalty
      SSM param name from env (default `/coffee-ship/loyalty/points-per-dollar`),
      cached ~60s TTL, fallback rate 10. Guard boto3 import (try/except) and
      create clients lazily so py_compile and /health survive without boto3/AWS.
      Implement:
      * pure `status_for(created_at, now)` -> RECEIVED (<10s) / BREWING (10–25s)
        / READY (>=25s).
      * `GET /health` -> `{"status":"ok","version":APP_VERSION}` (200 even if
        DynamoDB unreachable).
      * `POST /order`: accept `{items:[{id,name,qty,price}],total}` OR
        `{orderId,total}`; generate orderId if absent; `points = floor(total)*rate`;
        `put_item` with orderId (PK), createdAt (epoch or ISO), total, points,
        items?, status RECEIVED; return `{orderId,status,points,total,createdAt}`.
      * `GET /order/{id}` and `GET /order?id=`: `get_item`, recompute
        `status_for`, 404 if missing. Keep a browsable `GET /order` (no id) as a
        sample if desired, but `/orders` is the list.
      * `GET /orders`: `Scan` + sort by createdAt desc, take 10, recompute
        status each, return `{orders,count}` (comment that Scan is demo-scale).
      * KEEP all SPA static serving: `/`, `/assets/*` content-types,
        `/architecture.svg` as image/svg+xml, SPA fallback, 404 for missing
        assets, path-traversal guard.
      * Robust error handling: boto3 `ClientError` -> JSON 400/500 logged to
        stdout, never crash the server.
      * Bump `APP_VERSION = "v3-realapp"`.
      Files: `<P>/container/app.py`
      Verify: `python3 -m py_compile <P>/container/app.py` exits 0; status_for
      unit test from step 7 passes; runtime smoke from step 8 passes.

- [ ] 3. Build the SPA and the container image to confirm steps 1–2 (depends on 2).
      Files: none (build only).
      Verify: `cd <P>/container/frontend && npm install && npm run build` →
      `dist/index.html` + `dist/assets/*` exist; then
      `cd <P> && docker build -t coffee-ship:realapp-test container/` succeeds
      (this exercises the new pip install). Clean up the test image afterward
      (`docker image rm coffee-ship:realapp-test`).

- [ ] 4. Grant the ECS task role `ssm:GetParameter` on the loyalty parameter.
      In network-data-stack.ts, store the loyalty `ssm.StringParameter` in a
      `public readonly loyaltyParam` field (assign the `new ssm.StringParameter`
      to it). In app-pipeline-stack.ts, add `loyaltyParam: ssm.StringParameter`
      to `AppPipelineStackProps`, pass it from bin/coffee-ship.ts
      (`loyaltyParam: networkData.loyaltyParam`), and call
      `props.loyaltyParam.grantRead(fargateService.taskDefinition.taskRole)`
      next to the existing `ordersTable.grantReadWriteData(...)`. Change NOTHING
      else: no CloudFront edits, ALB-SG prefix-list lock intact (no 0.0.0.0/0),
      VPC still imported (no VPC created), ECR keep-10, EcsDeployAction stages,
      EventBridge S3 trigger all unchanged.
      Files: `<P>/infra/lib/network-data-stack.ts`,
      `<P>/infra/lib/app-pipeline-stack.ts`, `<P>/infra/bin/coffee-ship.ts`
      Verify: step 9 synth + tsc.

- [ ] 5. Extend the React SPA for live status + recent orders (depends on 2 for API shape).
      Keep theme/header/version-badge and the architecture `<details>` section
      and activity log. In App.jsx: on POST /order success, poll `GET /order/{id}`
      every ~3–4s and show a status badge RECEIVED→BREWING→READY, stopping at
      READY. Add a "Recent orders (latest 10)" card that calls `GET /orders` on
      load, after each placed order, and via a manual Refresh button; columns:
      Placed(time), Order ID, Items/Total, Points, Status badge. Update the "AWS
      services in this demo" list text (DynamoDB stores orders; SSM supplies the
      loyalty rate). All fetches stay same-origin relative. In styles.css add
      three visually distinct status-badge styles (RECEIVED/BREWING/READY) and
      recent-orders table styling, matching the coffee theme vars.
      Files: `<P>/container/frontend/src/App.jsx`,
      `<P>/container/frontend/src/styles.css`
      Verify: `cd <P>/container/frontend && npm run build` exits 0 (dist/
      regenerated); runtime smoke in step 8 exercises /orders + /order/{id}.

- [ ] 6. Regenerate the architecture diagram from official AWS icons.
      Add `<P>/container/build_diagram.py` modeled on
      `/Users/erictole/demo/apcr-dva/demo/session3/build_diagram.py`, but reading
      from `Architecture-Service-Icons_04302026` and embedding the `*_64.svg`
      files as `data:image/svg+xml;base64,...`. Icons: CloudFront, Elastic Load
      Balancing, ECS, Fargate, ECR, DynamoDB, Systems Manager, CodePipeline,
      CodeBuild, S3, EventBridge. Depict two lanes:
      runtime (User → CloudFront → ALB [imported VPC, SG locked to CloudFront
      prefix list] → ECS Fargate task → DynamoDB orders + SSM loyalty rate) and
      CI/CD (source.zip in S3 → EventBridge → CodePipeline → CodeBuild docker
      build/push → ECR → EcsDeployAction rolling w/ circuit breaker → ECS
      service). Run it to overwrite `<P>/container/architecture.svg`. Then
      regenerate the top-level `<P>/architecture.svg` (copy of the container SVG
      or a second write) and `<P>/architecture.png` via
      `rsvg-convert <P>/container/architecture.svg -o <P>/architecture.png`.
      Files: `<P>/container/build_diagram.py`, `<P>/container/architecture.svg`,
      `<P>/architecture.svg`, `<P>/architecture.png`
      Verify: `python3 <P>/container/build_diagram.py` exits 0;
      `python3 -c "import xml.dom.minidom as m; m.parse('<P>/container/architecture.svg')"`
      parses; `grep -c "data:image/svg" <P>/container/architecture.svg` ≥ 11;
      `rsvg-convert <P>/container/architecture.svg -o /tmp/arch-check.png` exits 0.

- [ ] 7. Add a unit test for `status_for()` thresholds (depends on 2).
      Add `<P>/container/test_app.py` (pytest-style or a `python -c` script the
      verify step runs) asserting RECEIVED at ~5s, BREWING at ~15s, READY at
      ~30s past createdAt. Guard against boto3 so the test imports app.py
      without AWS.
      Files: `<P>/container/test_app.py`
      Verify: `cd <P>/container && python3 -m pytest -q test_app.py` passes (or
      `python3 test_app.py` exits 0 if written as a script).

- [ ] 8. Runtime smoke test the real backend locally (depends on 2, 5, 6).
      Build the SPA to dist, then run the server against it with env pointing at
      ap-southeast-1 but tolerate no AWS creds (the server must not crash;
      /health must still be 200; order endpoints may return a logged 500 if
      DynamoDB is unreachable — that is acceptable for the smoke, the point is no
      crash). If AWS creds + the real table are available locally, additionally
      confirm POST /order persists and GET /orders returns it; otherwise note AWS
      calls were not exercised.
      Files: none.
      Verify: `STATIC_DIR=<P>/container/frontend/dist PORT=8080 python3 <P>/container/app.py &`
      then curl: `GET /` → text/html 200; `GET /health` → `{"status":"ok","version":"v3-realapp"}`;
      `GET /architecture.svg` → image/svg+xml 200; `GET /nope.js` → 404;
      `GET /spa/route` → text/html 200; server did not crash. Kill the server
      afterward.

- [ ] 9. Synthesize the CDK app and confirm security properties (depends on 4).
      Files: none; writes `<P>/.agents/tasks/verification.md`.
      Verify: `cd <P>/infra && npm install && CDK_DEFAULT_ACCOUNT=875692608981 JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=1 npx cdk synth CoffeeShipAppPipeline`
      exits 0; `cd <P>/infra && npx tsc --noEmit` clean. Record in
      `verification.md`: task role now has `ssm:GetParameter` on the loyalty
      param ARN; ALB SG ingress is ONLY the CloudFront prefix list
      (`SourcePrefixListId`, no `0.0.0.0/0`); CloudFront distribution present;
      VPC imported (no `AWS::EC2::VPC` created); EcsDeployAction Deploy-Test /
      Deploy-Prod stages present; EventBridge `Object Created` rule present.
      (Grep the synthesized template under `cdk.out/` for these, not the source.)

- [ ] 10. Update docs (depends on 2, 5, 6).
      Update README.md and FACILITATOR-RUNBOOK.md to describe the real app:
      order → DynamoDB → status RECEIVED/BREWING/READY → recent-10 list; SSM
      supplies the loyalty rate; boto3 now runs in the container (no longer
      stdlib-only); diagram built from official AWS icons. Keep the ap-southeast-1
      pinning, bootstrap-order and cost sections accurate.
      Files: `<P>/README.md`, `<P>/FACILITATOR-RUNBOOK.md`
      Verify: `grep -n "v3-realapp\|RECEIVED\|boto3\|Recent orders" <P>/README.md`
      shows the new content; prose review for accuracy.

## Constraints (must hold throughout)

- Region ap-southeast-1 pinned everywhere.
- Serverless `app/**` untouched.
- CloudFront, ALB-SG CloudFront-prefix-list lock (no 0.0.0.0/0), imported VPC
  (no VPC created), ECR keep-10, EcsDeployAction stages, EventBridge S3 trigger:
  all preserved.
- boto3 is the ONLY new dependency.
- NO live AWS: no cdk deploy, no docker push, no AWS-mutating calls.
- Commit locally on branch `coffee-ship-realapp`; never push.
