# Verification — Session 5 Storefront Frontend

Iteration: FIRST (no `.agents/tasks/review.json` present at start).

Scope shipped: FRONTEND ONLY. Changed files, all under
`demo/session5-secure-assistant/spa/`:
- `index.html` — rewritten into a coffee-shop storefront (navbar, hero, "What
  We Offer" cards, menu/specials, footer) with the chat as a floating widget +
  overlay panel.
- `styles.css` — rewritten self-authored stylesheet (coffee palette + accent
  `#8c4fff`); retains every class `app.js` depends on (`.msg`, `.msg.user`,
  `.msg.bot`, `.msg.sys`, `.pending`, `.receipt`, `.row`, `.chat`).
- `ui.js` — NEW: panel open/close + Esc + focus logic, bound only to the new
  opener/close elements. Does not touch the five chat ids or the chat logic.
- `app.js` — UNCHANGED (git diff empty). All chat/refund/receipt logic and
  fetch calls byte-for-byte intact; the five required ids
  (`log`/`chatForm`/`message`/`orderId`/`receiptBtn`) are present in the panel
  markup before the `<script src="app.js">` tag.

No backend/API/infra/Lambda/SecurityData changes. `destroy.sh` was NOT run.
Changes left staged on disk (not committed per instructions — see note).

## Local checks
- `node --check spa/app.js` → OK
- `node --check spa/ui.js` → OK
- `git status` confirms only `index.html`, `styles.css` modified and `ui.js`
  added under `spa/`; `git diff spa/app.js` is empty (app.js untouched).

## Redeploy (app stack only)
Command run from `demo/session5-secure-assistant/infra`:
```
AWS_REGION=ap-southeast-1 AWS_DEFAULT_REGION=ap-southeast-1 \
CDK_DEFAULT_ACCOUNT=875692608981 CDK_DEFAULT_REGION=ap-southeast-1 \
npx cdk deploy SecureAssistantAppEdgeAI --require-approval never
```
Result: deploy succeeded (Total time ~87s). Re-ran the `SpaDeployment`
BucketDeployment + CloudFront `/*` invalidation; did NOT rebuild the Lambda
image. Stack outputs confirmed:
- CloudFrontUrl = https://d1o0u6nv8iqp83.cloudfront.net
- AssistantApiEndpoint = https://6y7dnxp43k.execute-api.ap-southeast-1.amazonaws.com/prod/

`aws sts get-caller-identity` succeeded (account 875692608981, ap-southeast-1)
before deploy — no SSO re-auth needed.

## Live verification against https://d1o0u6nv8iqp83.cloudfront.net

Method: all checks were **curl-verified** (no real browser available in this
environment). Static assets and the three API contracts were exercised live
through CloudFront. Browser-only interactions (click-to-open, Esc, focus) were
verified by inspecting the shipped markup/CSS/JS that implement them.

### 1. Storefront is live (curl-verified)
`curl https://d1o0u6nv8iqp83.cloudfront.net/?cb=<ts>` and grep:
- "Coffee — Makes you Love" → 3 matches (title/hero/meta)
- `openChatFab` (floating button id) → 1 match
- `chatPanel` → 6 matches
- `ui.js` script tag → 1 match
- `id="log"` → 1 match (chat log present in panel)
Asset HTTP status: `styles.css` 200, `app.js` 200, `ui.js` 200.
=> The NEW storefront markup is live (not the old bare chat page).

### 2. Chat end-to-end — POST /api/chat (curl-verified)
Request `{"message":"where is my order ORD-000123?"}` → HTTP 200. Reply names
the order: "1x Flat White and 1x Croissant", status OK. Proves
Strands → Nova → Bedrock path works through CloudFront `/api/*`.

### 3. Human-in-the-loop refund — POST /api/chat then /api/refunds/confirm (curl-verified)
- `{"message":"Refund the full 12.50 for ORD-000123"}` → HTTP 200 with a
  structured `pendingRefund`:
  `{"token":"717af2ec-...","amountMasked":"12.50","orderMasked":"ORD-000123"}`.
  (Masked order + amount present; the reply text says "No money has moved yet.")
- `POST /api/refunds/confirm` with `{"token":"717af2ec-..."}` (the opaque token
  echoed back unchanged) → HTTP 200 `{"status":"CONFIRMED","token":"717af2ec-..."}`.
  Confirms the opaque-token confirm path. In the UI this renders the
  "Refund confirmed." system message (app.js `confirmRefund`).
- Note: the assistant only emits `pendingRefund` once an amount is given; a bare
  "I want a refund" first asks for the amount (expected agent behavior).

### 4. Receipt — GET /api/receipts/ORD-000123/url (curl-verified)
Request → HTTP 200 `{"url":"https://...receiptsbucket.../receipts/ORD-000123.pdf?...","expiresIn":900}`.
The API returns a presigned S3 URL per the contract; the frontend opens it with
`window.open(data.url, "_blank")`.
Caveat (BACKEND, out of frontend scope): the presigned URL is signed SigV2 and
the receipts bucket is KMS-encrypted in ap-southeast-1, so following S3's 307
regional redirect yields a SigV4-required error. This is a property of the
backend's URL generation (Lambda), which this frontend-only task must not
change, and does not affect the frontend contract (API returns 200 + a url).

### 5. Security re-check (curl-verified on live assets)
- Fetched live `app.js`/`ui.js` + HTML and scanned: NO hardcoded API
  keys/secrets/tokens/passwords (only a comment stating "No secrets ... live in
  the browser").
- All `fetch(...)` targets are relative and same-origin: `/api/chat`,
  `/api/refunds/confirm`, `/api/receipts/.../url`. No absolute or cross-origin
  URLs in the served HTML/JS. No external CDN links.
- The refund token is handled as an opaque string: app.js passes
  `pending.token` straight to `confirmRefund` and sends `{"token":token}` — it
  is never parsed from the reply text. (app.js unchanged.)

## Accessibility (verified by inspecting shipped markup/CSS/JS)
- Floating button `#openChatFab` has `aria-label="Chat with us to order coffee"`.
- Openers have `aria-haspopup="dialog"`, `aria-controls="chatPanel"`,
  `aria-expanded` toggled by `ui.js`.
- Panel is `role="dialog" aria-modal="true" aria-labelledby="chatPanelTitle"`,
  `hidden` when closed (`.chat-panel[hidden]{display:none}`).
- `ui.js` closes the panel on the × button and on `Escape`, moves focus into the
  panel on open and returns focus to the opener on close.
- `#log` keeps `aria-live="polite"`.

## Summary
All three live API contracts return 200 and behave as specified; the new
storefront markup/CSS/JS is confirmed live over HTTPS through CloudFront; no
secrets and all same-origin relative `/api/...` calls preserved; `app.js`
unchanged. The one caveat (presigned-URL S3 redirect signature) is pre-existing
backend behavior outside this frontend-only task's scope.
