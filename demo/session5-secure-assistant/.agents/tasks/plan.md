# Implementation Plan — CloudFront custom domain + SPA Clear-chat

Worktree root: `/home/ubuntu/apcr-dva/demo/session5-secure-assistant` (always use absolute paths).
Two independent changes: a CDK edit (TASK 1) and SPA edits (TASK 2). They touch
disjoint files and can be done in either order; this plan does TASK 1 first.

Key findings from exploration (ground truth, do not re-decide):
- CDK v2 monolithic `aws-cdk-lib` 2.160.0. Region pinned ap-southeast-1; account 875692608981.
  CloudFront distribution + SPA `BucketDeployment` live in `infra/lib/app-edge-ai-stack.ts`.
- The ACM cert is in us-east-1; the stack is in ap-southeast-1. `acm.Certificate.fromCertificateArn`
  imports a plain ARN string with NO cross-region lookup and NO `crossRegionReferences` flag needed
  (it is not a stack-to-stack reference). This is exactly the task-mandated approach — not
  `DnsValidatedCertificate`, not a new cert.
- Importing (not creating) the cert means NO `AWS::CertificateManager::Certificate` resource appears
  in the synthesized template, so the existing test assertion that counts that resource == 0 still holds.
- Tests run with `npm test` from `infra/` (`ts-node --prefer-ts-exts test/template.test.ts`); a tiny
  custom assert harness, exits non-zero on failure. Type-check with `npx tsc --noEmit`. Synth with
  `npx cdk synth --all` (set `CDK_DEFAULT_ACCOUNT=875692608981 JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=1`).
- SPA chat: message container is `<section id="log" class="log">`. `app.js` defines `const log =
  document.getElementById("log")` and appends via `append(cls,text)` and `renderPendingRefund`.
  There is NO persistence anywhere (grep found no localStorage/sessionStorage) and NO separate
  in-memory conversation array — chat state lives only in the `#log` DOM. There is NO
  "assistant is typing" indicator in the code. The pending-refund box is a child of `#log`, so
  clearing `#log` removes it too.
- Chat header is `.chat-panel-header` (title `#chatPanelTitle` + close button `#closeChat` styled
  `.chat-close`). Input is `#message` inside `#chatForm.chat`.
- `ui.js`/`diagram.js` deliberately never touch `#log`/`#chatForm`; keep that separation. The
  clear-chat logic belongs in `app.js`, which already owns `log`.

- [ ] 1. Add the custom-domain wiring to the CloudFront distribution in the AppEdgeAI stack.
      Add imports (only if missing) `import * as acm from 'aws-cdk-lib/aws-certificatemanager';`,
      `import * as route53 from 'aws-cdk-lib/aws-route53';`,
      `import * as targets from 'aws-cdk-lib/aws-route53-targets';`. Define constants near the other
      consts: `const CUSTOM_DOMAIN = 'cafe-nova.aws.yikyakyuk.com';`,
      `const CERT_ARN = 'arn:aws:acm:us-east-1:875692608981:certificate/417df345-28ea-4c39-8e5d-d985abb59908';`.
      Before the `new cloudfront.Distribution(...)` call, import the cert:
      `const certificate = acm.Certificate.fromCertificateArn(this, 'CloudFrontCert', CERT_ARN);`.
      Add two props to the existing `Distribution` constructor object (do not remove any existing
      props): `domainNames: [CUSTOM_DOMAIN],` and `certificate,`. The default `*.cloudfront.net`
      domain keeps working automatically.
      Files: infra/lib/app-edge-ai-stack.ts
      Verify: from `infra/`, `npx tsc --noEmit` passes, then
      `CDK_DEFAULT_ACCOUNT=875692608981 JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=1 npx cdk synth SecureAssistantAppEdgeAI`
      succeeds and the synthesized distribution shows `Aliases: [cafe-nova.aws.yikyakyuk.com]` and a
      `ViewerCertificate.AcmCertificateArn` equal to the imported ARN.

- [ ] 2. Add Route53 A + AAAA alias records and the custom-domain CfnOutput in the AppEdgeAI stack.
      After the `Distribution` is created, import the hosted zone:
      `const hostedZone = route53.HostedZone.fromHostedZoneAttributes(this, 'ParentZone', { hostedZoneId: 'Z09170582IZGKC67IAX17', zoneName: 'aws.yikyakyuk.com' });`.
      Add `new route53.ARecord(this, 'CustomDomainA', { zone: hostedZone, recordName: 'cafe-nova', target: route53.RecordTarget.fromAlias(new targets.CloudFrontTarget(distribution)) });`
      and `new route53.AaaaRecord(this, 'CustomDomainAAAA', { zone: hostedZone, recordName: 'cafe-nova', target: route53.RecordTarget.fromAlias(new targets.CloudFrontTarget(distribution)) });`
      (recordName `cafe-nova` resolves to exactly `cafe-nova.aws.yikyakyuk.com` under the zone).
      Add `new cdk.CfnOutput(this, 'CustomDomainUrl', { value: 'https://cafe-nova.aws.yikyakyuk.com', description: 'Custom-domain entry point.' });`.
      Files: infra/lib/app-edge-ai-stack.ts
      Verify: from `infra/`, re-run the synth from item 1; confirm the template contains one
      `AWS::Route53::RecordSet` of Type `A` and one of Type `AAAA`, both Name `cafe-nova.aws.yikyakyuk.com.`
      with an `AliasTarget` to the distribution, and a `CustomDomainUrl` output.

- [ ] 3. Update the template assertion test to cover the custom domain.
      In `infra/test/template.test.ts`, rename/replace the check titled
      `'CloudFront distribution with no ACM cert'`: keep `edge.resourceCountIs('AWS::CertificateManager::Certificate', 0);`
      (the cert is imported, so no cert resource is created) but retitle it to reflect imported cert,
      and add positive assertions: the distribution has `Aliases: Match.arrayWith(['cafe-nova.aws.yikyakyuk.com'])`
      and a `ViewerCertificate` with the imported ARN; and add a new check that the template has one
      `AWS::Route53::RecordSet` with Type `A` and one with Type `AAAA` for Name `cafe-nova.aws.yikyakyuk.com.`.
      Files: infra/test/template.test.ts
      Verify: from `infra/`, `npm test` prints all checks `ok` and exits 0.

- [ ] 4. Add a visible "Clear chat" button to the chat panel header.
      In `spa/index.html`, inside `.chat-panel-header` (the div holding `#chatPanelTitle` and
      `#closeChat`), add BEFORE the close button a
      `<button type="button" id="clearChat" class="chat-clear" aria-label="Clear chat history">Clear chat</button>`.
      Files: spa/index.html
      Verify: open `spa/index.html` in a browser (or confirm by reading the file) — the button renders
      in the chat header, left of the X close button, without breaking the header flex layout. Covered
      functionally by item 6's manual check.

- [ ] 5. Style the Clear-chat button with existing palette variables.
      In `spa/styles.css`, add a `.chat-clear` rule reusing existing variables: transparent background,
      `color: var(--cream)`, small radius, `cursor: pointer`, subtle hover
      `background: rgba(247, 239, 230, 0.15)` (mirrors `.chat-close:hover`), modest font-size (~13px)
      and padding so it sits inline in the espresso header. Do not alter unrelated rules.
      Files: spa/styles.css
      Verify: visually, the button matches the header styling and the hover state works; no layout shift
      of the title or close button.

- [ ] 6. Wire the Clear-chat behavior in app.js (client-side only).
      In `spa/app.js`, after the existing `const` lookups, add
      `const clearBtn = document.getElementById("clearChat");` and a handler:
      on click, set `log.textContent = ""` (removes all `.msg` and any `.pending` refund box from the
      DOM — this is the entire in-memory state since nothing is persisted), clear the input
      (`messageInput.value = ""`), re-enable it if disabled, and return focus to `#message`. Guard with
      `if (clearBtn) { ... }` so the file stays safe if the button is absent. Do NOT call any `/api`
      endpoint and do NOT touch Lambda/API code. No persistence keys exist, so nothing to clear in
      storage; add a one-line comment stating that.
      Files: spa/app.js
      Verify: serve the SPA locally (e.g. `python3 -m http.server` from `spa/`), open it, send a couple
      of messages (or trigger a pending-refund box), click Clear chat; confirm the log empties, the
      pending-refund box is gone, the input is enabled and focused, and no network request fires
      (check the Network tab). Chat still works after clearing (send another message).

- [ ] 7. Full verification sweep before deploy.
      Files: (none — verification only)
      Verify: from `infra/` run `npx tsc --noEmit`, `npm test` (all ok, exit 0), and
      `CDK_DEFAULT_ACCOUNT=875692608981 JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=1 npx cdk synth --all`.
      Confirm no changes leaked into `security-data-stack.ts`, Lambda code, Guardrail config, or
      deploy.sh/destroy.sh.

- [ ] 8. Deploy the AppEdgeAI stack (live, billable — authorized by the task).
      From repo root run the stack deploy exactly as deploy.sh does:
      `cd infra && CDK_DEFAULT_ACCOUNT=875692608981 CDK_DEFAULT_REGION=ap-southeast-1 AWS_REGION=ap-southeast-1 AWS_DEFAULT_REGION=ap-southeast-1 npx cdk deploy SecureAssistantAppEdgeAI --require-approval never`.
      The SPA `BucketDeployment` ships the updated SPA and invalidates `/*`; the CloudFront alias +
      cert + Route53 records are applied. Do NOT run destroy. Do NOT redeploy SecurityData unless CDK
      reports it is required.
      Files: (deployed infra)
      Verify: after the distribution finishes deploying, `curl -sS -o /dev/null -w '%{http_code}' https://cafe-nova.aws.yikyakyuk.com/`
      returns 200 (DNS + cert valid); the default `https://d3h6xnx1499eh1.cloudfront.net/` still returns
      200; and the live SPA shows the Clear-chat button that empties the transcript client-side.
