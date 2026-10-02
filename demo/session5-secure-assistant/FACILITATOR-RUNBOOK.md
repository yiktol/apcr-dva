# Facilitator Runbook — Session 5: Secure Coffee-Shop AI Assistant

A guided, four-act walkthrough for the DVA-C03 **Security & Observability**
session. Region **ap-southeast-1**, account **875692608981**, VPC imported
(never created). The assistant is built with the **Strands Agents SDK** and runs
on **Amazon Nova Micro** via the APAC inference profile, behind a Bedrock
Guardrail, over PrivateLink.

Use the architecture diagram (`diagram/architecture.svg`) on screen throughout.
Deploy with `./deploy.sh`, then open the CloudFront URL it prints.

## Customer talking points

- **OLX** run high-traffic consumer marketplaces where a public chat surface is
  a prime abuse target. The regional WAF (common rule set + rate-based rule),
  the private-subnet compute, and the human-in-the-loop refund map directly to
  how OLX would gate a customer-facing assistant that can touch money.
- **Clariant**, a specialty-chemicals enterprise, cares about data-handling
  controls and auditability: CMK encryption everywhere, PII masking at the tool
  layer, TLS-only data access, and model-invocation logging to an encrypted
  destination are the controls their security review would ask for.

Weave these in as you hit the relevant act.

---

## Act 1 — Network & data security

**Show:** CloudFront in front of a *private* S3 SPA bucket (OAC — the bucket has
no public access; only this distribution can read it), and `/api/*` routed
through a **regional WAF** to API Gateway. Point out the **KMS CMK** encrypting
the receipts bucket, both DynamoDB tables, and the Bedrock invocation-log
destination.

**Callout — the regional-WAF vs CloudFront-WAF tradeoff.** We attach a
**REGIONAL** WebACL to the API Gateway stage, not a CloudFront-scoped one. A
regional ACL filters requests *at the API* (after they traverse CloudFront), so
it protects the mutating `/api/*` surface — which is our threat model — and
keeps the demo single-region. A CloudFront-scoped WebACL would filter earlier,
at the edge, and cover the whole distribution (including the SPA path), but it
**must be created in us-east-1**, forcing a second region. We chose regional for
lower deploy risk; call out that an edge-wide control is the alternative.

**Callout — the ACM us-east-1 rule.** This demo uses the default
`*.cloudfront.net` certificate, so no ACM cert is provisioned. But teach the
rule anyway: **a custom-domain certificate for CloudFront must live in
us-east-1**, regardless of where the rest of the stack runs. It is a sibling
fact to the CloudFront-WAF-in-us-east-1 rule above.

The rate-based WAF rule ships in **COUNT** mode (observe first, don't block). To
enforce, flip `action: { count: {} }` to `action: { block: {} }` in
`infra/lib/app-edge-ai-stack.ts` (there's a comment at the rule).

---

## Act 2 — Identity & access

**Show:** open `infra/lib/app-edge-ai-stack.ts`.

- **TLS-only DENY (resource policy).** The receipts bucket denies all S3 when
  `aws:SecureTransport` is `false`. This is the **resource** half of the
  identity-vs-resource pairing.
- **Identity policy.** The presign Lambda role has a narrow `s3:GetObject`
  identity grant on the receipts objects — both halves must line up for a
  presigned URL to work. The Bedrock interface endpoint pairs the same way: an
  endpoint **resource** policy plus the agent **identity** policy.
- **ABAC.** The refund/operator role carries a statement allowed only when
  `aws:ResourceTag/team` equals `aws:PrincipalTag/team`. Both the role and the
  `pending-refunds` table are tagged `team=support`, so the condition resolves
  true for the demo. Note in the code why the condition is a **single-quoted
  string**, not a backtick literal — `${aws:PrincipalTag/team}` must reach the
  rendered policy verbatim as an IAM variable.
- **Least privilege.** No `Action:'*'`/`Resource:'*'` anywhere except the
  AWS-required `*::foundation-model/...` ARN wildcard form.

---

## Act 3 — The Strands assistant, secured

**Show:** `app/assistant/handler.py` and `app/assistant/tools.py`.

**Callout — the agent uses the Strands Agents SDK.** This is not a Bedrock
classic Agent and not AgentCore. We construct a `strands.Agent` with a
`strands.models.BedrockModel` and register plain `@tool` functions.

**Callout — Nova inference-profile requirement.** Nova Micro is invoked through
the **APAC inference profile** id `apac.amazon.nova-micro-v1:0` — that profile
id *is* the `model_id` passed to `BedrockModel`. The agent IAM role and the
endpoint policy both grant `bedrock:InvokeModel` on **two** ARNs: the
inference-profile ARN **and** the `*::foundation-model/amazon.nova-micro-v1:0`
form. Inference profiles require both.

**Callout — Strands guardrail wiring.** The Bedrock Guardrail (Hate+Violence
HIGH, PII mask for bank-account/SSN/email, a BLOCK topic `legal-advice`,
published version) is attached to the model by passing `guardrail_id`,
`guardrail_version`, and `guardrail_trace='enabled'` to `BedrockModel`. In
`strands-agents==1.23.0` these are forwarded through `**model_config` (not
first-class `__init__` params), configuring the guardrail inline on the
`InvokeModel` request.

**Callout — the guardrail TOOL-CALL blind spot.** The guardrail inspects the
model's prompt and completion only. It does **not** see PII inside tool-call
*arguments* or *results*. So if the model hands a raw account number to
`initiate_refund`, the guardrail never touches it. Mitigation: the tool handlers
mask + validate PII **themselves** (`app/assistant/pii.py`) before persisting to
DynamoDB or logging. There are explicit code comments at the blind spot. This is
the control OLX/Clariant security reviewers will probe.

**Callout — human-in-the-loop refund.** `initiate_refund` moves **no money**. It
writes a `PENDING_CONFIRMATION` record keyed by a server-generated uuid4 token
(with a TTL) and returns a pending result. A **separate** endpoint
`POST /api/refunds/confirm` (the `refund_confirm` Lambda, not a Strands tool) is
the only path that executes the refund. The token reaches the SPA through a
request-scoped side channel in the chat handler — never by parsing model text —
so the model cannot fabricate or leak it. Demo it live: ask for a refund, show
the PENDING card, click **Confirm**.

**Callout — PrivateLink is the private path.** The assistant Lambda sits in
private subnets, but a private subnet with a NAT route would still reach Bedrock
over the public internet. The **bedrock-runtime interface endpoint** (with
private DNS) is what keeps Bedrock traffic on PrivateLink; the endpoint SG admits
443 only from the assistant SG, and the endpoint policy is non-wildcard.

---

## Act 4 — Observability (and the PII trap)

**Show:** X-Ray enabled on the API Gateway stage and all three Lambdas; the
assistant wraps its Bedrock and DynamoDB calls in X-Ray subsegments
(`patch_all()` + `in_subsegment`), so the trace map shows `chat → Bedrock` and
`chat → DynamoDB`.

**Callout — the invocation-logging PII trap.** Bedrock
`ModelInvocationLoggingConfiguration` can capture full request/response
payloads. Treat this as defense in depth, in priority order:
1. **Mask PII at the tool/handler layer** — the only layer that covers tool-call
   data, and the one fully in your control.
2. **Encrypt the invocation-log destination** with the CMK (CloudWatch log group
   + S3), so whatever is captured is encrypted at rest.
3. The guardrail's input/output PII masking is best-effort on the model channel;
   whether the logged payload reflects guardrail-redacted content is a **runtime
   Bedrock behavior to validate at deploy**, not something this demo asserts.

The rule to leave them with: **mask before invoke, never rely on logging to
redact, and encrypt the log destination.**

---

## Teardown

Run `./destroy.sh` and type `destroy`. It removes the Bedrock
invocation-logging configuration (an account/region singleton) first so the CMK
is unpinned, empties the SPA/receipts/log buckets, destroys both stacks, and
sweeps leftover asset buckets and the invocation log group.

## The seven callouts (checklist)

- [x] ACM us-east-1 rule (Act 1)
- [x] Nova inference-profile requirement (Act 3)
- [x] Strands guardrail wiring (Act 3)
- [x] Guardrail tool-call blind spot (Act 3)
- [x] Human-in-the-loop refund (Act 3)
- [x] Invocation-logging PII trap (Act 4)
- [x] The agent uses the Strands Agents SDK (Act 3)

Plus the regional-WAF vs us-east-1-CloudFront-WAF tradeoff (Act 1).
