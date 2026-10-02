# Implementation Plan — Session 5 Storefront Frontend (chat as a widget)

Turn the bare chat page at `demo/session5-secure-assistant/spa/` into a
Session-4-style coffee-shop STOREFRONT, with the existing secure chat assistant
opening as a floating widget/overlay panel from it.

**Scope: FRONTEND ONLY.** Every change lives under
`/Users/erictole/demo/apcr-dva/demo/session5-secure-assistant/spa/`. No
backend, API, infra, or CDK code changes. One redeploy of the already-deployed
app stack ships the new `spa/` folder, then live verification.

## Grounding facts (read before starting — discovered from the code, do not re-decide)

- **How `spa/` ships.** `infra/lib/app-edge-ai-stack.ts` has a
  `s3deploy.BucketDeployment` (`SpaDeployment`) whose source is
  `Source.asset(.../spa)` and whose `distributionPaths: ['/*']` invalidates the
  CloudFront cache on deploy. Anything placed in `spa/` is uploaded verbatim;
  adding new asset files under `spa/` is safe and they ship too. CloudFront's
  default behavior serves the SPA with `ALLOW_GET_HEAD` and
  `defaultRootObject: index.html`; `/api/*` is a separate CACHING_DISABLED
  behavior to API Gateway. Both are same-origin from the viewer's perspective.
- **How `app.js` binds to the DOM (critical constraint).** `spa/app.js` is loaded
  with a plain `<script src="app.js"></script>` at the end of `<body>`, so it
  runs after the HTML is parsed. At module load it calls
  `document.getElementById(...)` for exactly these five ids and stores them in
  module constants: `log`, `chatForm`, `message`, `orderId`, `receiptBtn`. It
  also, at load time, attaches a `submit` listener to `chatForm` and a `click`
  listener to `receiptBtn`. **Therefore all five ids MUST exist in the markup
  before the `app.js` `<script>` tag, with the same roles** (`#log` a container
  it appends message divs to and scrolls; `#chatForm` a `<form>`; `#message` the
  text input inside it; `#orderId` the receipt text input; `#receiptBtn` the
  receipt button). We keep the ids identical and keep the script tag last, so
  `app.js` needs **no changes to its element lookups**.
- **CSS classes `app.js` depends on.** `append(cls, text)` creates
  `div.msg.<cls>` where `<cls>` is `user` / `bot` / `sys`. `renderPendingRefund`
  creates `div.pending` containing a `<button>` and the exact strings
  "Refund pending confirmation", "Order … — amount …", "No money has moved yet.",
  and a "Confirm refund" button. These classes/strings must keep working, so the
  new `styles.css` must retain `.msg`, `.msg.user`, `.msg.bot`, `.msg.sys`, and
  `.pending` (+ its button). Do not rename them.
- **Security facts that must stay true (unchanged by this work).** No
  secrets/keys/tokens in the browser; `pendingRefund.token` stays an opaque
  string only echoed back to `/api/refunds/confirm`, never parsed from reply
  text; all fetches stay same-origin relative `/api/...` (they already are, in
  `app.js` — we do not touch them); the human-in-the-loop confirm card and the
  download-receipt capability are preserved. The simplest way to guarantee all
  of this: **leave `app.js`'s functions and fetch calls byte-for-byte intact**
  and only change markup + CSS (plus a tiny, additive open/close script).
- **No CDN dependencies.** The reference Session 4 page pulls jQuery / Bootstrap
  / font-awesome from `static/`; those assets are NOT in `spa/` and must not be
  added or linked from a CDN (a strict CSP/edge setup may block CDNs). Build a
  single self-authored `styles.css` and use inline SVG for icons/illustrations.
- **Verification is live.** There is no local dev server for the SPA; it is
  served by CloudFront. "Does it work" is verified in two layers: (1) static
  HTML/JS validity + a local file open for layout/behavior sanity, then (2) a
  real redeploy of the app stack and a check against the live CloudFront URL.
- **Redeploy command.** Re-running the `BucketDeployment` = deploy the app stack
  only: from `infra/`, `AWS_REGION=ap-southeast-1 AWS_DEFAULT_REGION=ap-southeast-1
  CDK_DEFAULT_ACCOUNT=875692608981 CDK_DEFAULT_REGION=ap-southeast-1 npx cdk
  deploy SecureAssistantAppEdgeAI --require-approval never`. This re-uploads
  `spa/` and invalidates `/*`; it does NOT rebuild the assistant container image
  (that is a separate deploy.sh step) because the image is imported by tag. The
  CloudFront URL is stack output `CloudFrontUrl`.

## Design decisions (made here; one-liners with rationale)

1. **Single-page storefront, chat in an overlay panel — not a route change.**
   The task calls for a floating "Chat with us" button plus a nav/hero "Order"
   button that both open the SAME panel. A single `index.html` with a
   `role="dialog"` panel that is shown/hidden via a CSS class is the lightest
   approach and keeps the five required ids on the page at parse time (so
   `app.js` binds correctly). Rejected: a separate `chat.html` page — it would
   split the ids off the landing page and need `app.js` rewiring.
2. **Keep `app.js` logic intact; add a separate tiny inline/script block for
   open/close + Esc.** Satisfies "REUSE sendMessage/confirmRefund/
   downloadReceipt/renderPendingRefund … keep those functions and fetch calls
   intact." The toggle logic touches only new elements (button + panel) and does
   not reference the five bound ids, so it cannot regress chat behavior. We add
   it as a second `<script>` (either a new `spa/ui.js` file or an inline block
   placed BEFORE `app.js`); choose a new file `spa/ui.js` for cleanliness and
   load it after `app.js` so both are present. Either order is safe because the
   two scripts bind disjoint elements.
3. **Self-authored CSS, coffee palette + existing accent `#8c4fff`.** One
   `styles.css`, no external deps. Reuse the current CSS custom properties and
   accent, add coffee-tone variables (warm browns/cream) for the storefront
   chrome. Rationale: matches "dependency-light like the current SPA" and the
   explicit palette instruction.
4. **Inline SVG for the three offer icons (Coffee/Tea/Cakes) and the hero.** No
   binary images required, nothing to host. Rationale: avoids adding assets and
   avoids any CDN/icon-font dependency.
5. **Panel open/close is accessible.** Toggle button has `aria-label` and
   `aria-expanded`; the panel has `role="dialog"`, `aria-modal="true"`,
   `aria-labelledby`, is `hidden` when closed, and closes on `Esc` and on a
   close (×) button; focus moves into the panel on open and back to the opener on
   close. The `#log` keeps `aria-live="polite"`. Rationale: explicit
   accessibility requirement in the task.

---

## Phase 1 — Storefront + chat-panel markup

- [ ] 1. Rewrite `spa/index.html` into the storefront landing page with an
      embedded (hidden) chat panel that preserves the five required ids.
      Structure, top to bottom:
      - `<head>`: keep `charset`, `viewport`, update `<title>` (e.g. "Coffee —
        Makes you Love"), keep `<link rel="stylesheet" href="styles.css">`. No
        CDN links.
      - **Navbar** (`<header class="site-nav">`): brand/logo (inline SVG cup +
        shop name), and a nav with an **"Order with Assistant"** button —
        `<button type="button" id="openChat" class="btn-order" aria-haspopup="dialog"
        aria-controls="chatPanel" aria-expanded="false">`. Anchor links to the
        in-page sections (`#offer`, `#menu`) are optional but nice.
      - **Hero** (`<section class="hero">`): headline "Coffee — Makes you Love",
        a tagline, and a secondary hero CTA button that ALSO opens the panel —
        give it `class="btn-order"` and `data-open-chat` (the toggle script binds
        all `.btn-order` / `[data-open-chat]` openers to one handler) so both the
        nav and hero buttons open the SAME panel.
      - **"What We Offer"** (`<section id="offer">`): heading plus three cards
        (Coffee / Tea / Cakes), each with an inline SVG icon, a title, and a
        short blurb.
      - **Menu / specials** (`<section id="menu">`): a heading and a few items
        (name + short description + price), e.g. Flat White, Latte, Croissant,
        Coco Cake — static content, coffee-shop themed.
      - **Footer** (`<footer class="site-footer">`): shop name, a line of fake
        contact info, copyright.
      - **Floating button** (bottom-right): `<button type="button"
        id="openChatFab" class="chat-fab btn-order" aria-haspopup="dialog"
        aria-controls="chatPanel" aria-expanded="false" aria-label="Chat with us
        to order coffee">` with an inline chat/cup SVG. Also carries the shared
        opener hook so it opens the same panel.
      - **Chat panel overlay** (`<div id="chatPanel" class="chat-panel" role="dialog"
        aria-modal="true" aria-labelledby="chatPanelTitle" hidden>`), containing,
        in order: a header bar with `<h2 id="chatPanelTitle">` ("Order with our
        assistant") and a close button `<button type="button" id="closeChat"
        class="chat-close" aria-label="Close chat">`; then the EXACT existing
        chat controls, with ids unchanged —
        `<section id="log" class="log" aria-live="polite"></section>`,
        the receipt block (`<label for="orderId">Download my receipt</label>` +
        `<div class="row"><input id="orderId" …><button id="receiptBtn"
        type="button">Download receipt</button></div>`),
        and `<form id="chatForm" class="chat"><input id="message" … required>
        <button type="submit">Send</button></form>`.
      - **Scripts at end of `<body>`**, in this order: `<script src="app.js"></script>`
        then `<script src="ui.js"></script>`. `app.js` runs first and finds all
        five ids already in the DOM; `ui.js` binds only the new opener/close
        elements.
      Files: `spa/index.html`
      Verify: `cd demo/session5-secure-assistant && node --check spa/app.js`
      (unchanged file still parses) and open `spa/index.html` in a browser
      (`open demo/session5-secure-assistant/spa/index.html`): the storefront
      renders (navbar, hero, offer cards, menu, footer); clicking the nav button,
      the hero CTA, and the floating button each opens the chat panel; the panel
      shows the log, receipt row, and chat input. (Chat/refund/receipt network
      calls will error against `file://` — that is expected; they are verified
      live in Phase 3.)

## Phase 2 — Styling and open/close behavior

- [ ] 2. Rewrite `spa/styles.css` as a single self-contained stylesheet: a
      coffee-shop storefront theme plus the chat-panel styles, reusing the accent
      `#8c4fff` and KEEPING the classes `app.js` depends on.
      Must include: CSS variables (coffee browns/cream + `--accent: #8c4fff`);
      base/body/reset; `.site-nav` + `.btn-order`; `.hero` banner; `#offer`
      cards grid; `#menu` list; `.site-footer`; `.chat-fab` fixed bottom-right;
      `.chat-panel` overlay/drawer with a visible vs `hidden`/closed state
      (panel is shown by removing the `hidden` attribute — ensure
      `.chat-panel[hidden]{display:none}` is honored and the open state is a
      positioned panel), a backdrop if used, `.chat-panel .chat-close`.
      MUST retain (ported from the current file): `.log` (bordered, scrollable
      container), `.msg` + `.msg.user` + `.msg.bot` + `.msg.sys`, `.pending`
      (+ its button), `.receipt` + `.receipt label`, `.row`, `.chat`, and the
      shared button + `input[type="text"]` styling. Keep `.pending button`,
      `.receipt button`, `.chat button` on the accent color and
      `.pending button[disabled]` dimmed, matching current behavior.
      Files: `spa/styles.css`
      Verify: reload `spa/index.html` in the browser — storefront is styled
      (coffee palette, accent purple on primary buttons), the floating button
      sits bottom-right, the panel opens as a styled overlay/drawer, and inside
      the panel the message log, a sample `.msg.user`/`.msg.bot` bubble (type a
      message to render a user bubble even if the network call fails), the
      receipt row, and the chat form are all styled correctly.

- [ ] 3. Create `spa/ui.js` with the panel open/close + Esc + focus logic, bound
      only to the new elements (no reference to the five chat ids).
      Behavior: query `#chatPanel`, `#closeChat`, and all openers (`#openChat`,
      `#openChatFab`, and any `[data-open-chat]`/`.btn-order` opener). `openPanel()`
      removes `hidden`, sets each opener's `aria-expanded="true"`, moves focus to
      the panel (e.g. focus `#closeChat` or `#message`), and remembers the opener
      that was clicked. `closePanel()` sets `hidden`, resets `aria-expanded` to
      `"false"`, and returns focus to the last opener. Wire: click on any opener
      → `openPanel`; click on `#closeChat` → `closePanel`; `keydown` Escape while
      open → `closePanel`; optional click on backdrop → `closePanel`. Guard every
      lookup against `null` so a missing element never throws. Do NOT redefine or
      call `sendMessage`/`confirmRefund`/`downloadReceipt`/`renderPendingRefund`
      and do NOT touch `#log`/`#chatForm`/`#message`/`#orderId`/`#receiptBtn`.
      Files: `spa/ui.js`
      Verify: `cd demo/session5-secure-assistant && node --check spa/ui.js`
      passes; reload `spa/index.html` — opening via each of the three buttons
      works, `Esc` closes the panel, the × button closes it, `aria-expanded`
      flips, and no console errors appear on open/close.

## Phase 3 — Ship and verify live

- [ ] 4. Redeploy the already-deployed app stack to upload the new `spa/` and
      invalidate CloudFront. This re-runs the `SpaDeployment` BucketDeployment;
      it does not rebuild the assistant image.
      Command (run from `demo/session5-secure-assistant/infra`):
      `AWS_REGION=ap-southeast-1 AWS_DEFAULT_REGION=ap-southeast-1
      CDK_DEFAULT_ACCOUNT=875692608981 CDK_DEFAULT_REGION=ap-southeast-1
      npx cdk deploy SecureAssistantAppEdgeAI --require-approval never`
      (run `npm install` first only if `infra/node_modules` is absent). This hits
      REAL AWS and may invalidate the CloudFront cache — expected and in scope for
      "a redeploy and live verification"; it is not destructive. If AWS
      credentials for account 875692608981 / ap-southeast-1 are not available in
      the environment, STOP and report that the build is complete but the live
      redeploy/verification could not run, rather than guessing.
      Files: none (deploys existing infra with new `spa/` assets)
      Verify: the deploy completes and prints the `CloudFrontUrl` output
      (also retrievable via `aws cloudformation describe-stacks --stack-name
      SecureAssistantAppEdgeAI --region ap-southeast-1 --query
      "Stacks[0].Outputs[?OutputKey=='CloudFrontUrl'].OutputValue | [0]"
      --output text`).

- [ ] 5. Live-verification checklist against the `CloudFrontUrl` from item 4
      (hard-reload to bypass any cached assets). Confirm each:
      1. **Storefront loads over HTTPS**: navbar, hero ("Coffee — Makes you
         Love"), "What We Offer" cards, menu/specials, footer all render; no
         console errors; no requests to any external/CDN origin (check
         DevTools → Network: every request is same-origin, assets are
         `index.html` / `styles.css` / `app.js` / `ui.js`, API calls are
         relative `/api/...`).
      2. **Panel opens from all three entry points** (nav button, hero CTA,
         floating bottom-right button) and shows the log + receipt row + chat
         form.
      3. **Accessibility**: `Esc` closes the panel; the × button closes it; the
         floating button has an accessible name; focus moves into the panel on
         open; `#log` has `aria-live="polite"`.
      4. **Chat works**: send a message about `ORD-000123`; a user bubble and a
         bot reply render; `POST /api/chat` is 200 and same-origin.
      5. **Human-in-the-loop refund**: ask for a refund; the pending card appears
         with title "Refund pending confirmation", the masked order + amount, and
         "No money has moved yet."; the Confirm button disables itself while in
         flight and `POST /api/refunds/confirm` is called with the opaque token
         (verify in DevTools the request body is `{"token":"…"}` echoing the
         server-provided value, not anything parsed from the reply text); on
         success a "Refund confirmed." system message appears.
      6. **Receipt download**: enter `ORD-000123`, click Download receipt;
         `GET /api/receipts/ORD-000123/url` returns a URL and it opens in a new
         tab.
      7. **Security re-check**: view source / Network — no API keys, tokens, or
         secrets in `index.html` / `app.js` / `ui.js`; all `/api/...` calls are
         relative and same-origin; no absolute or cross-origin URLs added.
      Files: none (observation only)
      Verify: all seven checks pass. Record pass/fail (and the CloudFront URL
      used) in `.agents/tasks/verification-notes.md`.

---

## Dependency order & buildable-state notes

- Item 1 (markup) must land before items 2–3 so the CSS/JS have real elements to
  target. After item 1 the page already renders and opens the panel (openers can
  be wired by item 3; before that the page is still valid, just non-interactive
  for open/close).
- Items 2 and 3 are independent of each other (CSS vs JS) and both depend only on
  item 1; do 2 then 3 (either order is fine).
- Item 4 (redeploy) depends on items 1–3 being complete. Item 5 depends on 4.
- After each of items 1–3 the `spa/` folder is a valid static site (HTML parses,
  `node --check` passes on both JS files, `styles.css` is valid), so the project
  stays shippable at every step.

## Assumptions / gaps

- The backend (`/api/chat`, `/api/refunds/confirm`, `/api/receipts/{id}/url`) is
  already deployed and working; this task does not touch it. Seeded demo order
  `ORD-000123` exists (deploy.sh seeds it), so the live checklist uses it.
- `ui.js` vs inline script: chose a new `spa/ui.js` file for clarity; it ships
  automatically because the whole `spa/` folder is uploaded. If a stricter CSP
  were ever added that blocks separate scripts, an inline block is the fallback —
  but no CSP header is configured in the current CloudFront distribution, so a
  separate file is fine.
- Live verification requires AWS access to account 875692608981 in
  ap-southeast-1. If unavailable, items 4–5 cannot run; the frontend work
  (items 1–3) is still complete and verifiable locally by opening the page.
