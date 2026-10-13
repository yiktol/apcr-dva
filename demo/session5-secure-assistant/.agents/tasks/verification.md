# Verification — in-chat receipt download fix (Tasks A + B + C)

## Iteration note

`.agents/tasks/review.json` was present with `{"verdict": "APPROVED"}`, but its
companion `review.md` describes a *different, already-approved* task (the coffee
storefront landing page) and contains **no findings** about the receipt-download
work. The current source (`app/assistant/tools.py`, etc.) did **not** yet contain
Tasks A/B, so this was implemented as a first pass for the receipt fix. The stale
review surfaced nothing to fix for this feature.

## Root cause (given, confirmed)

A receipt PDF object only existed for the deploy-seeded `ORD-000123`. No code
wrote a receipt when a NEW order was placed, so in-session orders had no
`receipts/{orderId}.pdf`. The assistant role had `s3:GetObject` but not
`s3:ListBucket`, so a missing object returned **403 AccessDenied** (mentioning
`s3:ListBucket`) instead of 404. Confirmed live before the fix.

## Files changed

- `app/presign/handler.py` — added `make_s3_client(region)` (plain SigV4 regional
  S3 client for in-process head/put calls) and `receipt_key(order_id)` so the
  `receipts/{id}.pdf` layout has ONE definition. `generate_url` now calls
  `receipt_key`. The presign/signing client (`make_s3_presign_client`) is
  unchanged. This module remains the SINGLE owner of S3 client construction.
- `app/assistant/tools.py`
  - **Task A**: `make_place_order(orders_table, req_ctx, receipts_bucket=None, region=None)`
    (backward-compatible defaults). After a successful DynamoDB write (right where
    it appends to `req_ctx['placed_orders']`), it uploads a minimal receipt PDF via
    `presign_handler.make_s3_client(region).put_object(...)`. New `build_receipt_pdf`
    helper produces a tiny valid ASCII `%PDF-1.4` body carrying the order id,
    masked summary, and total. `ContentType='application/pdf'`. The upload is
    wrapped in `try/except` and is best-effort — a failed upload never changes the
    `RECEIVED` result (order is already committed).
  - **Task B**: `make_get_receipt_url` now calls `head_object(Bucket, receipt_key)`
    on the shared plain client BEFORE presigning. Any exception
    (403/404/NoSuchKey/ClientError) is treated as missing → returns
    `{"status": "NOT_FOUND", "orderId": ...}` and appends NOTHING to
    `req_ctx['receipts']`. Only when the object exists is the presigned URL
    generated and the side-channel entry appended. Existing order-id format
    validation and optional `orders_table` existence check are preserved. No
    top-level botocore import (defensive pattern retained).
- `app/assistant/handler.py` — `_build_agent` wires the real bucket + region into
  `make_place_order(orders_table, req_ctx, bucket, region)` from
  `os.environ['RECEIPTS_BUCKET']` and `AWS_REGION_PINNED`.
- `infra/lib/app-edge-ai-stack.ts` — **Task C**: the assistant role's
  `ReadReceipts` statement actions extended to `['s3:GetObject', 's3:PutObject']`,
  still scoped to `receiptsBucket.arnForObjects('*')`. No `s3:ListBucket`, no other
  bucket. KMS write (`GenerateDataKey*/Encrypt`) is already covered by the existing
  `kmsKey.grantEncryptDecrypt(assistantRole)`.
- `app/tests/test_tools.py` — added `_FakeS3Client` (records `put_object`, answers
  `head_object` from an existing-keys set) and new tests:
  - `test_get_receipt_url_ok_populates_side_channel` (now asserts head_object was
    consulted) and `test_get_receipt_url_missing_object_returns_not_found`.
  - `test_place_order_writes_receipt_object`,
    `test_place_order_still_received_when_receipt_upload_fails`,
    `test_place_order_no_bucket_skips_upload`.

## How the PDF is written + encrypted

A plain `put_object` with **no SSE params** is used. The receipts bucket has
default encryption `aws:kms` with the CMK
(`arn:aws:kms:ap-southeast-1:875692608981:key/26c3f7fe-9a27-4b49-a6ba-3a7bc0e7de38`)
and `BucketKeyEnabled`, confirmed live via `get-bucket-encryption`. Relying on
bucket default encryption means the object is CMK-encrypted automatically without
hardcoding the CMK ARN in app code; the role's existing
`kms:GenerateDataKey*/Encrypt` grant covers the write. Verified live: the uploaded
`ORD-086516.pdf` object exists and downloads 200.

## Task B missing-object handling

`head_object` with only `s3:GetObject` (no `s3:ListBucket`) returns 403 for a
missing key; the code treats any `head_object` error as "not found" and returns
`NOT_FOUND` with nothing appended to the side channel. No `s3:ListBucket` added.

## IAM grant path

Applied via **`cdk deploy SecureAssistantAppEdgeAI --exclusively --require-approval never`**
— the EarlyValidation CFN hook did NOT block the IAM change (deploy succeeded in
~49s). The `put-role-policy` fallback was not needed. Live confirmation:
`get-role-policy` on `AssistantFnServiceRoleDefaultPolicy9630C8FC` shows
`ReadReceipts -> ['s3:GetObject', 's3:PutObject']` and no `s3:ListBucket`.

## Build / test results

- `python3 -m py_compile $(find app -name '*.py')` → OK.
- `python3 -m pytest app/tests -q` → **53 passed**.
- `cd infra && npx tsc --noEmit` → clean.
- `cdk synth SecureAssistantAppEdgeAI` → OK. Synthesized template confirms the
  assistant role `ReadReceipts` statement = `['s3:GetObject', 's3:PutObject']`
  (presign role stays GetObject-only).
- `npm test` → **2 pre-existing failures only**, both in the SecurityData stack and
  OUT OF SCOPE (guardrail config untouched):
  1. "Bedrock Guardrail with full feature surface"
  2. "raw Bedrock invocation-logging config on CMK-encrypted destinations"
  Both reproduce on the unmodified tree (verified via `git stash`), so neither is
  caused by this change. Not fixed per constraints.

## Image rebuild / push / update

- `docker login` to ECR OK.
- `docker buildx build --platform linux/amd64 --provenance=false --sbom=false … --push app` OK.
- New digest: `sha256:e81f1eac2cef7949130e42a4ffd907f29015036c9887a244fb78a06a198cd84f`.
- `aws lambda update-function-code … --image-uri …@<digest>` → InProgress, then
  `aws lambda wait function-updated` → done.

## Live end-to-end (https://cafe-nova.aws.yikyakyuk.com)

1. Warm-up `POST /api/chat {"message":"hello"}` → 200.
2. **New order** (5a): after an explicit confirm message, envelope returned
   `placedOrder.orderId = **ORD-086516**`, total 7.75, status RECEIVED. (The first,
   less explicit phrasing made Nova Micro ask to confirm instead of calling the
   tool; the explicit retry placed it — expected model non-determinism.)
3. **S3 object** (5b): `aws s3 ls .../receipts/` lists `ORD-086516.pdf` (107 bytes)
   plus `ORD-000123.pdf` (48 bytes).
4. **New-order receipt link** (5c): envelope has a `receipt` object; curl of the
   presigned URL → **HTTP 200, SIZE 107**.
5. **Regression** (5d): ORD-000123 receipt link → **HTTP 200, SIZE 48**.
6. **Graceful missing** (5e): asking for `ORD-999999` → envelope has **NO
   `receipt`** key (NOT_FOUND path); assistant replies no receipt available.
7. **Custom domain** (5f): `GET https://cafe-nova.aws.yikyakyuk.com/` → **HTTP 200**
   (custom domain + WAF intact).

All checks were verified **live** against the deployed stack and image (no reliance
on model prose — order id and receipt pulled from the JSON envelope).

## Commit

- Single commit on `main` (HEAD), message:
  `fix: write receipt PDF on order placement and head-check before presign (A/B/C)`.
  (The commit's own short hash is `e97a674` at the time this note was written;
  because this file is part of that commit, the final hash after this edit was
  amended in may differ by the trailing documentation line. Resolve the exact
  hash via `git log -1 --oneline`.)
