# FEAT-001 verification — expanded AssistantGuardrail CfnGuardrail

## Scope

Expanded the `AssistantGuardrail` `CfnGuardrail` in
`infra/lib/security-data-stack.ts` to exercise the full guardrail feature
surface supported by the **installed** `aws-cdk-lib 2.160.0`, verified against
`infra/node_modules/aws-cdk-lib/aws-bedrock/lib/bedrock.generated.d.ts`. Also
extended the `Bedrock Guardrail ...` assertion in
`infra/test/template.test.ts`. The `CfnGuardrailVersion` wiring and the
`guardrailId` / `guardrailVersion` public-readonly cross-stack contract are
unchanged (still exactly one `AWS::Bedrock::GuardrailVersion`).

## What was added

- **contentPolicyConfig.filtersConfig** — all six content filters:
  HATE, VIOLENCE, INSULTS, MISCONDUCT, SEXUAL at `inputStrength: HIGH /
  outputStrength: HIGH`, plus PROMPT_ATTACK at `inputStrength: HIGH /
  outputStrength: NONE` (PROMPT_ATTACK is input-filtering only — Bedrock
  rejects an output strength for it).
- **wordPolicyConfig** — `managedWordListsConfig: [{ type: PROFANITY }]` and
  three custom `wordsConfig` entries.
- **sensitiveInformationPolicyConfig.piiEntitiesConfig** — kept the existing
  US_BANK_ACCOUNT_NUMBER / US_SOCIAL_SECURITY_NUMBER / EMAIL (ANONYMIZE); added
  BLOCK for CREDIT_DEBIT_CARD_NUMBER, CREDIT_DEBIT_CARD_CVV, PIN, PASSWORD,
  AWS_ACCESS_KEY, AWS_SECRET_KEY; added ANONYMIZE for CREDIT_DEBIT_CARD_EXPIRY,
  PHONE, ADDRESS, NAME, US_BANK_ROUTING_NUMBER, AGE, USERNAME.
- **sensitiveInformationPolicyConfig.regexesConfig** — one `loyalty-card`
  regex (`LOYALTY-[0-9]{8}`, ANONYMIZE).
- **topicPolicyConfig.topicsConfig** — kept legal-advice (DENY) and added
  medical-advice and financial-investment-advice as DENY topics, each with a
  definition and two examples.
- **contextualGroundingPolicyConfig.filtersConfig** — GROUNDING and RELEVANCE
  filters, each `threshold: 0.7`.

## Intentional omission: contentPolicyConfig.tierConfig

`contentPolicyConfig.tierConfig` is **NOT present** in `aws-cdk-lib 2.160.0`.
The installed `CfnGuardrail.ContentPolicyConfigProperty` exposes **only**
`filtersConfig`, so `tierConfig` was intentionally skipped — including it would
be a `tsc --noEmit` error. (Confirmed by reading
`infra/node_modules/aws-cdk-lib/aws-bedrock/lib/bedrock.generated.d.ts`.)

## Included because supported: contextualGroundingPolicyConfig

`contextualGroundingPolicyConfig` (`ContextualGroundingPolicyConfigProperty`
with `filtersConfig` of `ContextualGroundingFilterConfigProperty { type,
threshold }`) **is** supported in 2.160.0 and was included.

## Known-failing, deliberately-unchanged test

The pre-existing template assertion
**`raw Bedrock invocation-logging config on CMK-encrypted destinations`**
fails on the baseline and was deliberately left unchanged. It asserts an
`AWS::Bedrock::ModelInvocationLoggingConfiguration` CloudFormation resource,
but this stack provisions model-invocation logging via an `AwsCustomResource`
(the Bedrock control-plane `PutModelInvocationLoggingConfiguration` API), not a
CFN resource type — so no such resource is synthesized. This is out of scope
for FEAT-001; it must stay the single known failure.

## Verification results

Run from `infra/`:

1. `npx tsc --noEmit` — **clean** (no errors).
2. `CDK_DEFAULT_ACCOUNT=875692608981 JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=1 npx cdk synth SecureAssistantSecurityData` — **synthesizes without error**. The `AWS::Bedrock::Guardrail` resource contains all six content filters (PROMPT_ATTACK with OutputStrength NONE), the word policy (PROFANITY + custom words), the expanded PII entities + loyalty regex, three DENY topics, and the contextual-grounding GROUNDING + RELEVANCE filters.
3. `npm test` — **exactly 1 failure**, the pre-existing `raw Bedrock invocation-logging config on CMK-encrypted destinations` assertion. Every other assertion passes, including the extended Guardrail assertion and `published Guardrail version` (`AWS::Bedrock::GuardrailVersion` count still 1).

### Test-authoring note

`Match.arrayWith` matches its patterns **positionally** (in array order), not as
an unordered subset. The extended PII assertion therefore lists its patterns in
the order the entities appear in the synthesized `PiiEntitiesConfig` array (the
BLOCK `CREDIT_DEBIT_CARD_NUMBER` first, then the ANONYMIZE entities). Nested
policy-config objects in the assertion are wrapped in `Match.objectLike` so that
only the asserted keys are required.
