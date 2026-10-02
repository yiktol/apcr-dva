# Session 5 — Secure Coffee-Shop AI Assistant: Requirements

## Summary

Build a standalone, fully-deployable AWS demo for an **AWS Certified Developer –
Associate (DVA-C03) — Security & Observability** training session (Session 5).
The demo secures a coffee-shop AI customer-support assistant and must exercise
**most** of the session's services for real (deployable to a sandbox account),
organized into **four acts**: (1) Network & data security, (2) Identity &
access, (3) Strands assistant secured, (4) Observability.

The AI agent is built with the **Strands Agents SDK** (`strands-agents`,
`strands-agents-tools`) — explicitly **not** a Bedrock classic Agent and **not**
Bedrock AgentCore. The agent runs inside the assistant compute in private
subnets and invokes **Amazon Nova Micro** via the APAC **inference profile**.

The new project is a self-contained CDK v2 (TypeScript) application plus a chat
SPA and Python 3.12 Lambda source, located at:

```
/Users/erictole/demo/apcr-dva/.worktrees/session5/demo/session5-secure-assistant
```

It reuses established patterns from `demo/session4-coffee-ship` (CDK v2 pinned
at `aws-cdk-lib@2.160.0`, bash `deploy.sh`/`destroy.sh` with `set -euo
pipefail` and region pinned, the base64 icon-embed diagram approach from
`container/build_diagram.py`) but **must not modify** session4-coffee-ship.

### Verification boundary (authoritative, non-negotiable)

Verification is **local only**. There is **NO live AWS deploy, NO `cdk deploy`,
NO `docker push`, NO Bedrock/Guardrail runtime calls** performed inside the
authoring/verification workflow. Allowed verification commands only:

- `npm install` + `tsc` (TypeScript compile) in `infra/`
- `cdk synth` (local synthesis to `cdk.out`, no deploy)
- `python3 -m py_compile` on all Python sources
- `python3 build_diagram.py` (diagram build) + `rsvg-convert` for PNG
- `bash -n` (syntax check) on all shell scripts

`deploy.sh` is authored to be runnable by a facilitator later, but is **not
executed** during this task.

### Assumptions

- A1. The existing VPC and its CloudFormation exports already exist in the
  target account/region; the demo imports them and never creates a VPC.
- A2. Model access to Nova Micro and the Bedrock Guardrails API are already
  enabled in the account; the demo does not request model access.
- A3. CDK bootstrap in the target account/region is the facilitator's
  responsibility at deploy time (handled by `deploy.sh`), not this task.
- A4. The chat SPA is dependency-light (plain HTML/JS or a tiny Vite build);
  plain HTML/JS is the default to keep `cdk synth` self-contained with no npm
  build dependency for the frontend. (Design review may refine this.)
- A5. Account id `875692608981` and region `ap-southeast-1` are fixed facts and
  are pinned everywhere; they are not re-decided.

---

## Functional Requirements

### Project structure & conventions

- FR-1. All deliverables live under
  `.worktrees/session5/demo/session5-secure-assistant` and the project is
  self-contained; session4-coffee-ship is not modified.
- FR-2. CDK app is TypeScript, `aws-cdk-lib@2.160.0`, `constructs@^10.3.0`,
  matching session4's `infra/package.json` toolchain (tsc, cdk synth scripts).
- FR-3. Region is pinned to `ap-southeast-1` in the CDK `env`, in both shell
  scripts (`AWS_REGION`/`AWS_DEFAULT_REGION`), and anywhere a region is
  referenced. Account comes from `CDK_DEFAULT_ACCOUNT` for synth.
- FR-4. The CDK app is split into sensible stacks: a **SecurityData** stack and
  an **AppEdgeAI** stack. Cross-stack references are passed via stack props
  (session4 pattern), not hardcoded.

### Shared infrastructure (VPC import, config, secrets)

- FR-5. Import the existing VPC via `ec2.Vpc.fromVpcAttributes` using the
  verified ids below — do **not** create a VPC:
  - VpcId `vpc-01857e627d800ca7a`, CIDR `10.1.0.0/16`
  - AZs explicitly `[ap-southeast-1a, ap-southeast-1b, ap-southeast-1c]`
  - Private subnets `subnet-031c1ad1112e14559` (1a),
    `subnet-000af0b0c27929d53` (1b), `subnet-09bb34168e90ddd6f` (1c)
  - Public subnets `subnet-05de990ce1677a9b8`, `subnet-029d8307a796a725c`,
    `subnet-03bb2e0d84b125eb0`
  - AZ order must match subnet order. Private subnets have a NAT route.
- FR-6. A **Secrets Manager** secret holds the payment-processor key; the Strands
  agent role has least-privilege **read** on it only.
- FR-7. An **SSM Parameter Store** parameter holds assistant/app config; the
  agent role has least-privilege **read** on it only.

### ACT 1 — Network & data security

- FR-8. A **CloudFront** distribution fronts the app using the **default
  CloudFront domain + default certificate** (no custom domain, no Route 53, no
  ACM cert provisioned by the demo).
- FR-9. A private **S3** bucket hosts the chat SPA; it is served **only** via
  CloudFront **Origin Access Control (OAC)** — no public bucket access.
- FR-10. The API origin is reachable through the **same** CloudFront
  distribution under the `/api/*` path pattern (SPA and API share one
  distribution).
- FR-11. A **WAF Web ACL** is attached with: the **AWS managed common rule set**
  and a **rate-based rule** configured in **COUNT** mode. The WAF is **regional**
  (attached to the API in ap-southeast-1) rather than a us-east-1 CloudFront WAF;
  this tradeoff is documented.
- FR-12. A **presigned-URL receipts** feature: a Lambda generates time-limited
  presigned GET URLs for receipt objects in a receipts S3 bucket; the SPA offers
  a receipt download.
- FR-13. A customer-managed **KMS CMK** encrypts (a) the receipts bucket and (b)
  the Bedrock invocation-log destination.

### ACT 2 — Identity & access

- FR-14. The receipts bucket has a **resource policy that DENY**s access when
  `aws:SecureTransport` is `false` (enforce TLS-only).
- FR-15. An **ABAC** policy gates a support-operator action such that it is
  allowed only when `ResourceTag` equals `PrincipalTag` (tag-based match).
- FR-16. Both an **identity policy** and a **resource policy** are present for at
  least one protected resource (demonstrate the two together).
- FR-17. All IAM roles follow **least privilege** — scoped actions and resource
  ARNs, no wildcards beyond what Bedrock foundation-model ARNs require.

### ACT 3 — Strands assistant secured

- FR-18. The AI agent is a **Strands Agent** (Strands Agents SDK), running inside
  the assistant compute in the **private subnets**. Compute is AWS Lambda (Python
  3.12) by default; design may choose small Fargate if justified, but Lambda is
  the baseline.
- FR-19. Model wiring uses `from strands.models import BedrockModel` with
  `BedrockModel(model_id='apac.amazon.nova-micro-v1:0',
  region_name='ap-southeast-1', guardrail_id=<id>, guardrail_version='<ver>',
  guardrail_trace='enabled')`. The `apac.` inference-profile id **is** the
  `model_id`. Nova Micro is **inference-profile-only** in ap-southeast-1.
- FR-20. The agent role allows `bedrock:InvokeModel` and
  `bedrock:InvokeModelWithResponseStream` on **both**:
  - the inference-profile ARN
    `arn:aws:bedrock:ap-southeast-1:875692608981:inference-profile/apac.amazon.nova-micro-v1:0`
  - the underlying foundation-model ARN
    `arn:aws:bedrock:*::foundation-model/amazon.nova-micro-v1:0`
  Plus `bedrock:ApplyGuardrail` if required by the wiring.
- FR-21. A **Bedrock Guardrail** (`CfnGuardrail`) is defined with: content
  filters **Hate** and **Violence** at **HIGH**, **PII** entities set to **MASK**,
  and at least one **BLOCK** example (e.g. a denied topic or a blocked PII entity),
  and a **published version** (`CfnGuardrailVersion`).
- FR-22. A **PrivateLink interface VPC endpoint** for `bedrock-runtime` is created
  in the private subnets with (a) a restrictive **endpoint policy** and (b) a
  tight **security group** (only the assistant compute SG may reach it on 443).
- FR-23. Strands **tools** are defined with the `@tool` decorator:
  - `look_up_order(order_id)` — read-only.
  - `initiate_refund(order_id, amount)` — **human-in-the-loop**: it returns a
    **PENDING-CONFIRMATION** result, writes a pending-refund record to DynamoDB
    with a **confirmation token**, and moves **no money**.
  - A separate explicit **confirm** step (carrying the token) is the only path
    that executes the refund.
- FR-24. The chat SPA surfaces the pending refund plus a **Confirm** button that
  calls the refund-confirm endpoint with the token.
- FR-25. **Guardrail tool-call blind spot** mitigation: because the Bedrock
  guardrail does **not** inspect or mask PII inside tool-call arguments or tool
  results, the tool handlers **themselves validate and mask PII** (never write a
  raw account number into the pending-refund record or into logs). This is
  enforced in code and explained with code comments and a doc paragraph.
- FR-26. A **Bedrock model-invocation logging configuration**
  (`CfnModelInvocationLoggingConfiguration`) sends invocation logs to a
  **KMS-encrypted destination** (the CMK from FR-13).

### ACT 4 — Observability

- FR-27. **AWS X-Ray** tracing is enabled on **API Gateway** and the assistant
  **Lambda**.
- FR-28. The assistant instruments **Bedrock** and **DynamoDB** calls as X-Ray
  **subsegments**.
- FR-29. **DynamoDB** tables `orders` and `pending-refunds` are **KMS-encrypted**
  (customer-managed CMK).

### Deliverables (artifacts to produce)

- FR-30. Full CDK app under `infra/` (`bin/`, `lib/` with the two stacks,
  `package.json`, `tsconfig.json`, `cdk.json`) — compiles with `tsc` and
  synthesizes with `cdk synth`.
- FR-31. Chat SPA (dependency-light HTML/JS, or tiny Vite) with receipt-download
  and pending-refund Confirm flow, deployed to S3+CloudFront via OAC.
- FR-32. Python 3.12 Lambda source: (a) assistant Strands agent, (b)
  refund-confirm endpoint, (c) presigned-URL generator; plus a `requirements.txt`
  pinning `strands-agents`, `strands-agents-tools`, `boto3`. Include a
  `Dockerfile` if a container-image Lambda is chosen.
- FR-33. `deploy.sh` and `destroy.sh` — bash `set -euo pipefail`, region pinned,
  **destroy guarded** by requiring the user to type `destroy`, correct teardown
  ordering (empty buckets / clear KMS-dependent resources before stack delete),
  matching the session4 script style.
- FR-34. `README.md` and `FACILITATOR-RUNBOOK.md` walking the **four acts** with
  **OLX** and **Clariant** talking points, and the explicit callouts: ACM
  us-east-1 rule, Nova inference-profile requirement, Strands guardrail wiring,
  guardrail tool-call blind spot, human-in-the-loop refund, invocation-logging
  PII trap, and a note that the agent uses the **Strands Agents SDK**.
- FR-35. Architecture diagram reusing the base64 icon-embed approach from
  session4 `build_diagram.py`, pulling icons from
  `/Users/erictole/demo/apcr-dva/aws-icons`, emitting **both** `architecture.svg`
  and `architecture.png` (via `rsvg-convert`).

### Teaching callouts (must appear in docs even though not provisioned)

- FR-36. Docs **teach the us-east-1 ACM rule**: CloudFront custom-domain certs
  must live in us-east-1 — even though the demo uses the default CloudFront
  domain/cert and provisions no ACM cert.
- FR-37. Docs explain the **regional-WAF-vs-us-east-1-CloudFront-WAF tradeoff**
  and why the demo attaches a regional WAF to the API.

---

## Non-Functional Requirements

- NFR-1. **No live deploy during authoring/verification.** Only the local
  commands listed in the Verification boundary run. Any step that would call AWS
  APIs at authoring time is excluded.
- NFR-2. **Pinning:** `aws-cdk-lib` exactly `2.160.0`; region `ap-southeast-1`;
  Nova via the `apac.amazon.nova-micro-v1:0` inference profile only; Python
  dependencies pinned in `requirements.txt`.
- NFR-3. **Least privilege & security defaults:** no public S3, OAC-only
  CloudFront→S3, TLS-only receipts bucket, scoped IAM, KMS CMK on data at rest,
  no secrets in code or logs, no raw PII in records or logs.
- NFR-4. **Reproducibility:** `cdk synth` succeeds offline with a dummy account;
  no network calls or context lookups that require live AWS at synth time (VPC is
  imported by explicit attributes, not `fromLookup`).
- NFR-5. **Pattern consistency** with session4: script structure, numbered-step
  echo output, diagram generator style, doc tone.
- NFR-6. **Testability:** Python tool handlers (PII masking, pending-refund
  token flow, presigned-URL generation) are structured as pure, unit-testable
  functions; infra is validated via `cdk synth` assertions on the synthesized
  template where practical.

---

## Acceptance Criteria (testable, numbered)

1. The directory `.worktrees/session5/demo/session5-secure-assistant` contains
   `infra/`, SPA source, Lambda source, `deploy.sh`, `destroy.sh`, `README.md`,
   `FACILITATOR-RUNBOOK.md`, and a diagram generator; `demo/session4-coffee-ship`
   is unchanged (git diff empty for that path).
2. `infra/package.json` pins `aws-cdk-lib` to exactly `2.160.0`.
3. `cd infra && npm install && npx tsc --noEmit` completes with no errors.
4. `cd infra && npx cdk synth` completes with no errors and produces a
   `cdk.out` template, using a dummy `CDK_DEFAULT_ACCOUNT` and no live AWS calls.
5. The synthesized template contains **no** `AWS::EC2::VPC` resource, and the
   VPC is imported via `fromVpcAttributes` with the six subnet ids and the three
   AZs in the specified order.
6. The synthesized template defines two stacks named per the SecurityData /
   AppEdgeAI intent, and `env.region === 'ap-southeast-1'`.
7. The synthesized template includes a CloudFront distribution with an OAC-backed
   private S3 origin and an `/api/*` behavior routed to the API origin, using the
   default CloudFront domain (no `AWS::CertificateManager::Certificate` and no
   custom domain alias).
8. The synthesized template includes a WAF Web ACL with the AWS managed common
   rule set and a rate-based rule whose action is **Count**, associated regionally
   with the API.
9. The synthesized template includes a KMS CMK that encrypts the receipts bucket
   and the invocation-log destination, and both DynamoDB tables (`orders`,
   `pending-refunds`) specify customer-managed KMS encryption.
10. The receipts bucket resource policy contains a `Deny` statement conditioned
    on `aws:SecureTransport = false`.
11. The template contains an ABAC policy statement comparing `ResourceTag` to
    `PrincipalTag`, and at least one protected resource has both an identity
    policy and a resource policy.
12. The template defines a `CfnGuardrail` with Hate and Violence content filters
    at HIGH, PII entities set to MASK, at least one BLOCK example, and a published
    `CfnGuardrailVersion`.
13. The template defines a `bedrock-runtime` interface VPC endpoint in the private
    subnets with a non-wildcard endpoint policy and a security group that admits
    only the assistant compute SG on 443.
14. The template defines a `CfnModelInvocationLoggingConfiguration` whose
    destination is encrypted with the demo CMK.
15. The agent IAM role grants `bedrock:InvokeModel` and
    `bedrock:InvokeModelWithResponseStream` on **both** the inference-profile ARN
    and the `amazon.nova-micro-v1:0` foundation-model ARN, plus scoped DynamoDB
    RW, Secrets Manager read, SSM read, and X-Ray write — with no broad `*`
    resource on the Bedrock invoke actions beyond the foundation-model ARN form.
16. The assistant Lambda source imports `BedrockModel` from `strands.models` and
    constructs it with `model_id='apac.amazon.nova-micro-v1:0'`,
    `region_name='ap-southeast-1'`, and the guardrail parameters including
    `guardrail_trace='enabled'`; it uses no Bedrock classic Agent or AgentCore
    API.
17. The Lambda `requirements.txt` pins `strands-agents`, `strands-agents-tools`,
    and `boto3` to explicit versions.
18. `initiate_refund` returns a pending-confirmation result and writes a
    pending-refund record with a confirmation token to DynamoDB while moving no
    money; a separate confirm endpoint executes the refund only when supplied the
    matching token. A unit test demonstrates both the pending step and the
    confirm step.
19. The tool handlers validate and mask PII before persisting or logging; a unit
    test asserts that a raw account number never appears in the pending-refund
    record or in a captured log line. Code comments explain the guardrail
    tool-call blind spot.
20. X-Ray tracing is enabled on API Gateway and the assistant Lambda in the
    synthesized template, and the Lambda source creates Bedrock and DynamoDB
    subsegments.
21. The SPA renders a receipt-download control (presigned URL) and a pending-refund
    Confirm button that posts the confirmation token to the confirm endpoint.
22. `python3 -m py_compile` succeeds on every `.py` file; `bash -n deploy.sh` and
    `bash -n destroy.sh` pass; `destroy.sh` aborts unless the operator types
    `destroy`.
23. Running the diagram generator produces both `architecture.svg` and
    `architecture.png` with AWS icons embedded as base64 (no external icon file
    references in the SVG).
24. `README.md` and `FACILITATOR-RUNBOOK.md` contain all seven required callouts
    (ACM us-east-1 rule, Nova inference-profile requirement, Strands guardrail
    wiring, guardrail tool-call blind spot, human-in-the-loop refund,
    invocation-logging PII trap, Strands Agents SDK note) and the regional-WAF
    tradeoff, and reference OLX and Clariant talking points across the four acts.
25. No live-AWS side effects occur during authoring/verification: no `cdk deploy`,
    no `docker push`, no Bedrock/Guardrail runtime invocation is executed.

---

## Out of Scope

- Creating or modifying a VPC, subnets, NAT, or route tables (VPC is imported).
- Any live AWS deployment, CDK bootstrap execution, Docker image push, or Bedrock
  runtime/Guardrail invocation during authoring/verification.
- Custom domains, Route 53 records, and ACM certificate provisioning (the demo
  uses the default CloudFront domain; the us-east-1 ACM rule is taught, not
  provisioned).
- A us-east-1 CloudFront-scoped WAF (the demo uses a regional WAF on the API; the
  tradeoff is documented).
- Using a Bedrock classic Agent or Bedrock AgentCore (the agent is Strands SDK
  only).
- Any changes to `demo/session4-coffee-ship`.
- CI/CD pipeline, multi-environment (test/prod) deployment, or blue/green rollout
  (session4 concerns, not Session 5).
- Production hardening beyond demo scope (e.g. WAF in BLOCK mode, cross-region
  DR, cost optimization) — the rate-based rule stays in COUNT mode by design.
