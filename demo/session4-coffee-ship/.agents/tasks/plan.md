# Implementation Plan — Add a real React (Vite) frontend to coffee-ship, served by the container

All paths are absolute under the worktree
`/Users/erictole/demo/apcr-dva/.worktrees/frontend`. The project dir is
`/Users/erictole/demo/apcr-dva/.worktrees/frontend/demo/session4-coffee-ship`
(abbreviated `<S4>` below).

## Design decisions (made here, grounded in the code I read)

- **Option A, SPA baked into the container.** The architecture stays
  CloudFront → ALB → ECS Fargate. The Python container (`<S4>/container/app.py`,
  stdlib `http.server`) additionally serves the built SPA from a baked
  `/app/static` directory. No new runtime pip deps, no infra change.
- **Static layout under `container/` so the Docker build context has everything.**
  The pipeline and `deploy.sh` both run `docker build container/`, so the build
  context is `container/`. I place the SPA source at
  `<S4>/container/frontend/` and copy the diagram to
  `<S4>/container/architecture.svg`. A multi-stage Dockerfile builds the SPA in
  a node stage and copies `frontend/dist` + `architecture.svg` into the python
  stage at `/app/static`. Rationale: everything docker needs lives inside the
  context dir, so `zip -r source.zip container/` (deploy.sh / runbook) already
  includes it with no extra zip paths.
- **Container name stays `web`.** `infra/lib/app-pipeline-stack.ts` uses the
  `ApplicationLoadBalancedFargateService` default container name `web`, and
  `buildspec.yml` writes `imagedefinitions.json` with `name:"web"`. Confirmed by
  reading both. `container/taskdef.json` (name `coffee-ship`) is a reference
  artifact the pipeline does NOT consume — leave it untouched; do not use it to
  justify a container-name change.
- **ALB health check is `GET /` expecting HTTP 200** (confirmed in
  app-pipeline-stack.ts: pattern default path `/`). Today `/` returns JSON 200.
  After the change, `/` returns `index.html` as `text/html` 200 — still 200, so
  the health check is preserved. This is the one hard constraint on the routing.
- **SPA fallback vs 404.** For unknown paths: asset-looking paths (containing a
  dot in the last segment, e.g. `/foo.js`) that are not found return 404 with
  the correct behavior; all other unknown non-API paths fall back to
  `index.html` (SPA client-side routing). Documented in app.py and README.
- **Architecture diagram SVG must reflect THIS demo.** There is NO
  `architecture.svg` in `<S4>` today (verified: the only one in the repo is
  session3's at `demo/session3/frontend/public/architecture.svg`, which shows
  Cognito/ElastiCache — the wrong services). So this task CREATES a new
  session4-specific `<S4>/container/architecture.svg`: a plain hand-authored SVG
  (shapes + text, matching session3's light-card aesthetic — no embedded AWS PNG
  icons required) depicting CodePipeline → CodeBuild → ECR → ECS/Fargate → ALB →
  CloudFront plus DynamoDB/SQS/AppConfig/SSM/Secrets Manager. This is the gap
  called out in the task (which assumed an svg already existed at `<S4>`).
- **APP_VERSION.** A single constant `APP_VERSION` in `app.py` is the source of
  truth. `/health` returns `{"status":"ok","version":APP_VERSION}`. The SPA reads
  it at runtime via `GET /health` and shows it in the header; a build-time
  fallback string is baked into the SPA for the "offline/preview" case.
- **Versions pinned exactly as the task requires:** react ^18.3.1,
  react-dom ^18.3.1, vite ^5.4.0, @vitejs/plugin-react ^4.3.1, `"type":"module"`.
  Same major versions session3 uses (verified), minus `aws-amplify` (no auth).

## Verification toolchain (confirmed present locally)

node v25.6.1, npm 11.9.0, python3 3.13.3, docker 29.7.2, zip present.
CDK infra pins its own toolkit via `<S4>/infra/package.json` (aws-cdk 2.160.0),
run through `npx` as `deploy.sh` does. Verification is LOCAL ONLY — never
`cdk deploy`, never `docker push`, never any AWS-mutating command.

---

## Steps

- [ ] 1. Scaffold the React (Vite) SPA source directory.
      Create the SPA project themed "Coffee Ship" reflecting THIS demo's services
      (CodePipeline, CodeBuild, ECR, ECS/Fargate, ALB, CloudFront, DynamoDB, SQS,
      AppConfig, SSM, Secrets Manager — NOT session3's Cognito/ElastiCache).
      `package.json` pinned: react ^18.3.1, react-dom ^18.3.1, vite ^5.4.0,
      @vitejs/plugin-react ^4.3.1; `"type":"module"`; scripts dev/build/preview.
      `vite.config.js`: react plugin, `build.outDir 'dist'`, `base '/'`.
      Files (create):
      `/Users/erictole/demo/apcr-dva/.worktrees/frontend/demo/session4-coffee-ship/container/frontend/package.json`,
      `/Users/erictole/demo/apcr-dva/.worktrees/frontend/demo/session4-coffee-ship/container/frontend/vite.config.js`,
      `/Users/erictole/demo/apcr-dva/.worktrees/frontend/demo/session4-coffee-ship/container/frontend/index.html`,
      `/Users/erictole/demo/apcr-dva/.worktrees/frontend/demo/session4-coffee-ship/container/frontend/.gitignore` (node_modules/, dist/).
      Verify: `cd /Users/erictole/demo/apcr-dva/.worktrees/frontend/demo/session4-coffee-ship/container/frontend && npm install` succeeds and produces a lockfile (no build yet).

- [ ] 2. Implement the SPA UI (coffee-shop ordering page) matching session3's look/feel.
      Build `src/main.jsx`, `src/App.jsx`, `src/styles.css`. Match the session3
      aesthetic read from `demo/session3/frontend/src/styles.css` (dark cards,
      rounded corners, `.tag` "live", `<details class="diagram">` section, activity
      `.log`), but recolor to a coffee palette. UI requirements:
      header `☕ Coffee Ship` + `live` tag; hardcoded menu (Espresso 3.00,
      Latte 4.50, Cold Brew 4.00, Mocha 5.00) with +/- quantity and a running
      total; a "Place order" button that POSTs same-origin **relative** `/order`
      with JSON `{"orderId":<generated>,"total":<number>}` and shows the returned
      loyalty `points`; an activity log panel; an expandable Architecture diagram
      `<details>` that shows `/architecture.svg` with an "Open full size ↗" link;
      show the app version from `GET /health` (fallback to a baked-in constant).
      No auth, no AWS SDK — API is same-origin unauthenticated.
      Files (create): `.../container/frontend/src/main.jsx`,
      `.../container/frontend/src/App.jsx`, `.../container/frontend/src/styles.css`.
      Verify: `cd /Users/erictole/demo/apcr-dva/.worktrees/frontend/demo/session4-coffee-ship/container/frontend && npm run build` exits 0 and writes `dist/index.html` + `dist/assets/*`.

- [ ] 3. Author a session4-specific architecture diagram SVG and place it in the build context.
      Create a plain hand-authored SVG (no embedded AWS PNG icons needed; shapes +
      labels in the session3 light-card style) depicting the real pipeline/runtime:
      source.zip(S3) → CodePipeline → CodeBuild(docker) → ECR → ECS/Fargate behind
      ALB → CloudFront (ALB SG = CloudFront prefix list), plus DynamoDB, SQS,
      AppConfig, SSM, Secrets Manager. Place it where the Docker context can copy it.
      Files (create): `/Users/erictole/demo/apcr-dva/.worktrees/frontend/demo/session4-coffee-ship/container/architecture.svg`.
      Verify: `python3 -c "import xml.dom.minidom as m; m.parse('/Users/erictole/demo/apcr-dva/.worktrees/frontend/demo/session4-coffee-ship/container/architecture.svg'); print('ok')"` prints ok (well-formed XML).

- [ ] 4. Teach `app.py` to serve the baked SPA while keeping the JSON API byte-for-byte.
      Modify the handler to serve static files from a baked dir (default
      `/app/static`, overridable via a `STATIC_DIR` env for local runs). Routing:
      `GET /health` → JSON `{"status":"ok","version":APP_VERSION}` 200;
      `GET|POST /order` → unchanged loyalty JSON (same shape, same `compute_points`,
      same `POINTS_PER_DOLLAR`/`PORT` behavior); `GET /` → `index.html`
      (`text/html`) 200 (preserves the ALB health check); `GET /architecture.svg`
      → `image/svg+xml`; `GET /assets/...` and other static files → correct
      Content-Type via `mimetypes`; unknown asset-looking path (dot in last
      segment) → 404; any other unknown non-API path → SPA fallback to
      `index.html`. Add a module-level `APP_VERSION` constant. Guard against path
      traversal (resolve within `STATIC_DIR`). Keep `log_message` stdout logging.
      Files (modify): `/Users/erictole/demo/apcr-dva/.worktrees/frontend/demo/session4-coffee-ship/container/app.py`.
      Verify (static + behavior):
      (a) `python3 -m py_compile /Users/erictole/demo/apcr-dva/.worktrees/frontend/demo/session4-coffee-ship/container/app.py` exits 0.
      (b) Build the SPA (step 2) to a temp static dir, then run
      `STATIC_DIR=<dist> PORT=8080 python3 app.py &` and curl: `/health` →
      `{"status":"ok","version":...}` 200; `/` → HTML 200; `POST /order` with
      `{"orderId":"t1","total":12.5}` → `{"orderId":"t1","points":120}` 200;
      `GET /order` → sample loyalty JSON 200; `/architecture.svg` →
      `Content-Type: image/svg+xml` 200; `/nope.js` → 404; `/some/spa/route` →
      HTML 200. Kill the server afterward.

- [ ] 5. Convert the Dockerfile to a multi-stage build (node build → python runtime).
      Stage 1 `node:20-alpine`: `WORKDIR /build`, `COPY frontend/package*.json`,
      `RUN npm ci`, `COPY frontend/ .`, `RUN npm run build` → `/build/dist`.
      Stage 2 `python:3.12-slim`: `WORKDIR /app`, `COPY requirements.txt ./`,
      `COPY app.py ./`, `COPY --from=0 /build/dist /app/static`,
      `COPY architecture.svg /app/static/architecture.svg`, `ENV PORT=8080`,
      `EXPOSE 8080`, `CMD ["python","app.py"]`. stdlib-only runtime (no pip
      install). Document the chosen `container/`-rooted layout in a header comment.
      Files (modify): `/Users/erictole/demo/apcr-dva/.worktrees/frontend/demo/session4-coffee-ship/container/Dockerfile`.
      Verify: `cd /Users/erictole/demo/apcr-dva/.worktrees/frontend/demo/session4-coffee-ship && docker build -t coffee-ship:plantest container/` succeeds; then
      `docker run --rm -d -p 8080:8080 coffee-ship:plantest` and curl `/` (HTML 200),
      `/health` (version JSON), `/architecture.svg` (svg), `POST /order` (points);
      `docker rm -f` the container and `docker image rm coffee-ship:plantest` after.

- [ ] 6. Confirm/adjust `buildspec.yml` for the multi-stage build.
      The current buildspec already does ECR login, `python -m py_compile
      container/app.py`, `docker build ... container/`, push `:latest` + unique
      tag, and `imagedefinitions.json` name `web`. The multi-stage build runs
      `npm ci && npm run build` INSIDE the Docker build (CodeBuild has Docker via
      `privileged:true`), so no new build phase is needed. Keep `py_compile`,
      keep containerName `web`, no `|| true` gates. Update only the header comment
      that enumerates what `source.zip` must contain to add `container/frontend/`
      and `container/architecture.svg`. Make NO behavioral change if none is
      required.
      Files (modify, comment only unless a real need surfaces): `/Users/erictole/demo/apcr-dva/.worktrees/frontend/demo/session4-coffee-ship/container/buildspec.yml`.
      Verify: `python3 -c "import yaml,sys; yaml.safe_load(open('/Users/erictole/demo/apcr-dva/.worktrees/frontend/demo/session4-coffee-ship/container/buildspec.yml')); print('ok')"` prints ok; `grep -n 'py_compile\|name.:.web' <path>` still present.

- [ ] 7. Confirm `deploy.sh` packages the frontend into `source.zip`.
      `deploy.sh` zips the whole `container` dir (`zip -r "$TMP_ZIP" container
      -x '*.pyc' -x '*__pycache__*'`). Since the SPA source now lives under
      `container/frontend/` and the svg under `container/architecture.svg`, the
      existing zip already includes them. Add `-x '*/node_modules/*'` and
      `-x '*/dist/*'` so a developer's local `npm install`/build output is not
      shipped (the image builds the SPA fresh inside Docker). No other change.
      Files (modify): `/Users/erictole/demo/apcr-dva/.worktrees/frontend/demo/session4-coffee-ship/deploy.sh`.
      Verify: `bash -n /Users/erictole/demo/apcr-dva/.worktrees/frontend/demo/session4-coffee-ship/deploy.sh` exits 0; dry-run the zip:
      `cd /Users/erictole/demo/apcr-dva/.worktrees/frontend/demo/session4-coffee-ship && zip -r /tmp/plan-source.zip container -x '*.pyc' -x '*__pycache__*' -x '*/node_modules/*' -x '*/dist/*' >/dev/null && unzip -l /tmp/plan-source.zip | grep -E 'frontend/|architecture.svg'` lists the frontend sources + svg and NOT node_modules/dist; then `rm /tmp/plan-source.zip`.

- [ ] 8. Update docs (README.md and FACILITATOR-RUNBOOK.md).
      In README.md: describe that CloudFront now serves the Coffee Ship web app
      (HTML), the API is same-origin at `/order`, the container is built via a
      multi-stage Dockerfile (node build + python runtime), and the student edit
      loop (edit the React app or `app.py`/`APP_VERSION`, push `source.zip`,
      pipeline rebuilds the image and does a real ECS rolling deploy, the browser
      page changes). Document the `container/frontend/` + `container/architecture.svg`
      layout and the `/` -> HTML health-check note. In FACILITATOR-RUNBOOK.md:
      update Act 4 so the "see the change" step curls the CloudFront URL and sees
      the web page / bumped version change (not just JSON), keeping the real
      pipeline description accurate; keep the existing non-blocking note about an
      explicit `cd` before the Act 4 zip in mind and add the `cd` for parity.
      Files (modify): `/Users/erictole/demo/apcr-dva/.worktrees/frontend/demo/session4-coffee-ship/README.md`,
      `/Users/erictole/demo/apcr-dva/.worktrees/frontend/demo/session4-coffee-ship/FACILITATOR-RUNBOOK.md`.
      Verify: `grep -n 'frontend\|Coffee Ship web\|multi-stage' <both files>` shows the new content; docs reference the real pipeline (no "simulation"/"fake").

- [ ] 9. Cross-cutting integration verification (no AWS deploy).
      With all pieces in place, run the full local gate end to end:
      (1) `cd /Users/erictole/demo/apcr-dva/.worktrees/frontend/demo/session4-coffee-ship/container/frontend && npm ci && npm run build` → dist produced.
      (2) `cd /Users/erictole/demo/apcr-dva/.worktrees/frontend/demo/session4-coffee-ship && docker build -t coffee-ship:planfinal container/` → image builds; smoke-curl `/`, `/health`, `/order`, `/architecture.svg` as in step 5; then remove the container + image.
      (3) `cd /Users/erictole/demo/apcr-dva/.worktrees/frontend/demo/session4-coffee-ship/infra && npm install && CDK_DEFAULT_ACCOUNT=111111111111 CDK_DEFAULT_REGION=ap-southeast-1 npx cdk synth > /dev/null` → synth succeeds (confirms infra untouched/compiling).
      (4) `python3 -m py_compile /Users/erictole/demo/apcr-dva/.worktrees/frontend/demo/session4-coffee-ship/container/app.py` and `bash -n .../deploy.sh` exit 0.
      Clean up any temp containers/images/zips created.
      Files: none (verification only).
      Verify: all four commands above exit 0 with the stated outputs.

## Preserved / out of scope (do NOT touch)

- `app/**` (serverless SAM app) — untouched.
- `infra/**` — prefer NO edits; CloudFront distribution, ALB SG CloudFront
  prefix-list lock, imported-VPC-from-exports wiring, ECR keep-10,
  `EcsDeployAction` stages all stay as-is. Region stays pinned ap-southeast-1.
- `container/taskdef.json` — reference artifact, not consumed by the pipeline;
  leave it. Container name stays `web` (pattern default + imagedefinitions.json).
- The running container stays stdlib-only Python (no new pip deps).
