# Verification — coffee-ship → coffee-shop rename + prose cleanup

First iteration (no review.json present). All commands run inside the worktree
`/Users/erictole/demo/apcr-dva/.worktrees/rename/demo/session4-coffee-ship`.
No AWS deploy / docker push / cdk deploy performed.

## Completeness grep

`grep -rinI 'coffee-ship\|CoffeeShip' . --exclude-dir=node_modules
--exclude-dir=dist --exclude-dir=cdk.out --exclude-dir=.agents --exclude-dir=.git`
returns only the intended, allowed matches:

- `infra/cdk.json` — `"app": "... bin/coffee-ship.ts"` (filename kept by design)
- `infra/package.json` — `"coffee-ship": "bin/coffee-ship.ts"` (bin key / filename)
- `infra/package-lock.json` — mirrored `"coffee-ship": "bin/coffee-ship.ts"`
- `FACILITATOR-RUNBOOK.md:5` and `:177` — the folder path `demo/session4-coffee-ship`
  (the folder is NOT renamed)

The two regenerated `architecture.svg` files contain only `coffee-shop*` labels
(0 `coffee-ship`). No other `coffee-ship`/`CoffeeShip` occurrences remain.

## Build / test gates (all passed)

- `python3 -m py_compile container/app.py` → OK (exit 0)
- `python3 -c json.load container/taskdef.json` → valid JSON
- `cd container && python3 -m pytest -q` → 4 passed
- `cd app && pip install -r dev-requirements.txt && python3 -m pytest -q` → 5 passed
- `cd container/frontend && npm install && npm run build` → vite build OK, `dist/`
  produced (build banner shows `coffee-shop-frontend@0.0.0`)
- `python3 container/build_diagram.py` → wrote container/architecture.svg (75963 bytes);
  copied to top-level architecture.svg; `rsvg-convert` rebuilt architecture.png
  (top-level). `container/architecture.svg`: 0 `coffee-ship`, 0 `prefix list`/`imported vpc`;
  labels present: coffee-shop, coffee-shop-orders, coffee-shop-prod, coffee-shop-test
- `cd infra && npm install` → OK
- `CDK_DEFAULT_ACCOUNT=875692608981 JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=1
  npx cdk synth CoffeeShopNetworkData CoffeeShopAppPipeline` → exit 0 (new stack names synth clean)
- `npx tsc --noEmit` → exit 0
- `bash -n deploy.sh destroy.sh demo-pipeline.sh` → all OK (exit 0)

## Change B + prose sweeps

- `container/app.py` `APP_VERSION = "v3"` (was `v3-realapp`)
- `grep -rinI 'v3-realapp'` under container/ + docs/scripts → 0 matches
- `grep -rinI 'imported vpc|prefix-list-locked|not public|only cloudfront can reach|
  not reachable from the public|is imported from'` (excl generated/.agents) → 0 matches

## Functional code spot-checks (intact)

In `infra/lib/app-pipeline-stack.ts`: `open: false` ×2, `fromVpcAttributes` ×1,
`CloudFrontPrefixListId` ×1, `prefixList`/`PrefixList` ×5, `importValue` ×5.
`container/buildspec.yml`: `imageDetail.json` (singular) present. The
`OLD_NAME="Coffee Shop"` / `NEW_NAME="BeanThere Cafe"` scenario and the user-facing
"Coffee Shop" product name are unchanged.
