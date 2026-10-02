# Coffee storefront landing page wrapping the secure chat assistant in a floating panel

The Session 5 secure-assistant SPA gained a full coffee-shop storefront — navbar, hero, "What We Offer" cards, a specials menu, and a footer — and the existing chat UI moved out of the main page flow into a floating dialog panel opened by a bottom-right FAB and two "Order" buttons (navbar + hero). The chat/refund/receipt logic in `app.js` was not touched; a new `ui.js` handles only panel open/close, Escape, and focus. `styles.css` was rewritten into a coffee palette while preserving every class `app.js` renders against. The backend contract, API endpoints, and all infra are untouched.

Watch for: nothing blocking. The frontend keeps all three same-origin API flows, treats the refund token as opaque (app.js is byte-for-byte unchanged — confirmed), introduces no secrets or external CDNs, and preserves the human-in-the-loop refund card and receipt download. (confidence: confirmed)

**Verdict**: APPROVED

## High-level view

The storefront is additive markup around an unchanged chat core. The five DOM ids `app.js` binds at module load (`log`, `chatForm`, `message`, `orderId`, `receiptBtn`) all live inside the chat panel, which is present in the DOM at parse time (`hidden`, not removed), so the `getElementById` lookups resolve and no listener wiring breaks. `app.js` has an empty git diff — the refund token stays an opaque string echoed to `/api/refunds/confirm`, and the three `fetch` targets remain relative same-origin paths.

Panel behavior is isolated in `ui.js`, which binds only to the opener/close controls and the dialog container and never calls into the chat logic, so it structurally cannot regress chat, refund, or receipt behavior. Open/close toggles `hidden`, syncs `aria-expanded`, moves focus into the panel on open, restores it to the opener on close, and closes on Escape.

Accessibility is in good shape: the FAB carries an `aria-label`, all openers advertise `aria-haspopup="dialog"` / `aria-controls` / `aria-expanded`, the panel is a labelled modal dialog, and the log keeps `aria-live="polite"`. No external CDN references, no hardcoded secrets, and the change is confined to `spa/` — no infra, Lambda, or SecurityData edits, and nothing committed.

<details>
<summary>Issues (1)</summary>

1. **No focus trap while dialog open (non-blocking)** — the modal panel is toggled via `hidden` with no focus trap, so keyboard focus can tab out to the storefront behind the open dialog. Consider trapping focus; not required for this task.

</details>

<details>
<summary>Details</summary>

### Storefront is additive; chat core is untouched

`index.html` is rewritten into a storefront, but the chat lives in a `#chatPanel` dialog appended after the footer, carrying the exact ids `app.js` expects: `#log`, `#chatForm`, `#message`, `#orderId`, `#receiptBtn`. Those elements exist in the parsed DOM before `<script src="app.js">` runs — the panel is hidden with the `hidden` attribute, not conditionally rendered — so the module-load `getElementById` calls in `app.js` resolve to real nodes and none of the `addEventListener` wiring hits a null. `git diff` on `app.js` is empty, so `sendMessage`, `confirmRefund`, `downloadReceipt`, and `renderPendingRefund` and their `fetch` calls are intact. (confidence: confirmed)

### Refund token stays opaque; API surface unchanged

Because `app.js` is unchanged, the refund flow still passes `pending.token` straight from the structured `pendingRefund` object into `confirmRefund`, which POSTs `{token}` to `/api/refunds/confirm` — the token is never parsed out of the reply text. The three endpoints remain relative and same-origin (`/api/chat`, `/api/refunds/confirm`, `/api/receipts/{id}/url`); a repo-wide scan of `spa/` found no absolute or cross-origin URLs and no CDN references. The confirm card still renders the title, masked order and amount, "No money has moved yet.", and a Confirm button that disables itself in flight. The receipt path still opens the presigned URL via `window.open(data.url, "_blank", "noopener")`. (confidence: confirmed)

### Panel control is isolated in ui.js

```
openers (#openChat, #openChatFab, [data-open-chat])
   │ click
   ▼
openPanel ──> removeAttribute("hidden"), aria-expanded=true, focus → #message
closeBtn / Escape
   │
   ▼
closePanel ─> setAttribute("hidden"), aria-expanded=false, focus → lastOpener
```

`ui.js` queries openers with a single `querySelectorAll("#openChat, #openChatFab, [data-open-chat]")`; since the FAB and navbar/hero buttons also carry `data-open-chat`, the selector union still returns each element once, so each gets exactly one click listener — no double-binding. `openPanel`/`closePanel` short-circuit on current state, so repeated activations are no-ops. The script bails early if `#chatPanel` is absent and binds nothing to the chat ids, so it cannot regress chat behavior. (confidence: confirmed)

### Accessibility

The FAB has `aria-label="Chat with us to order coffee"`; all three openers set `aria-haspopup="dialog"`, `aria-controls="chatPanel"`, and an `aria-expanded` that `ui.js` keeps in sync. The panel is `role="dialog" aria-modal="true"` labelled by its heading, Escape-closable, with focus moved in on open and returned to the opener on close. `#log` keeps `aria-live="polite"`.

One non-blocking caveat: the panel is only toggled via the `hidden` attribute (`.chat-panel[hidden]{display:none}`), so there is no focus trap while the dialog is open — focus can tab out to the storefront behind it. `display:none` keeps the closed panel out of the tab order, so the gap is limited to the open state; a focus trap would harden the modal but is not required here. (confidence: confirmed)

### Live verification evidence

The coder's `verification.md` records a redeploy of the app stack only (`SecureAssistantAppEdgeAI`, no Lambda rebuild) and curl-based live checks through `https://d1o0u6nv8iqp83.cloudfront.net`: the new storefront markup is served (`openChatFab`, `chatPanel`, `ui.js`, `id="log"` all present; assets 200), `POST /api/chat` returns an order-aware reply, the refund flow returns a structured `pendingRefund` and `POST /api/refunds/confirm` with the echoed opaque token returns `CONFIRMED`, and `GET /api/receipts/ORD-000123/url` returns a presigned URL with HTTP 200. The one documented caveat — the presigned URL's S3 SigV2/regional-redirect behavior — is backend URL-generation detail outside this frontend-only scope and does not affect the frontend contract (API returns 200 + url). Evidence is sufficient; no re-run needed. (confidence: confirmed)

### Scope

`git diff --name-only` plus status shows only `spa/index.html`, `spa/styles.css` modified and `spa/ui.js` added, alongside task docs and a `.DS_Store`. No `infra/*.ts`, `deploy.sh`, `destroy.sh`, Lambda `app/`, or SecurityData changes, and nothing committed — matching the task constraints. (confidence: confirmed)

</details>

<details>
<summary>File map</summary>

- `spa/index.html` — rewritten into storefront (navbar, hero, offer cards, menu, footer) + floating FAB and `#chatPanel` dialog containing the unchanged chat/receipt/form controls; loads `app.js` then `ui.js`.
- `spa/styles.css` — rewritten coffee palette (accent `#8c4fff` retained); preserves `.msg`, `.pending`, `.receipt`, `.row`, `.chat`, `.log` and adds FAB/panel styling.
- `spa/ui.js` — new; panel open/close, Escape, aria-expanded sync, focus management. No chat-id or chat-logic touch.
- `spa/app.js` — unchanged (empty diff).
- `.agents/tasks/plan.md`, `.agents/tasks/verification.md` — task docs.

Full diff: `git diff main -- demo/session5-secure-assistant/spa/` (plus untracked `spa/ui.js`).

</details>
