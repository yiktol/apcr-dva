# BeanThere — Session 3 Core Services Demo

A **real, functional serverless application** that exercises all eight core AWS services
taught in APCR-DVA Content Review Session 3:

| Service | Role in this demo |
|---|---|
| **Amazon Cognito** | User pool (sign-in) + identity pool (temporary AWS creds) |
| **Amazon ElastiCache** | Serverless Valkey cache in front of the menu (lazy loading + TTL) |
| **Amazon SQS** | Buffers order submissions; a dead-letter queue catches poison messages |
| **Amazon SNS** | Fan-out: one confirmed-order event → several independent subscribers |
| **Amazon EventBridge** | Content-based routing of typed events (`OrderPlaced`, `RefundIssued`, …) |
| **Amazon CloudWatch** | Custom metric `OrderProcessingTime` + alarm → SNS ops topic |
| **Amazon CloudWatch Logs** | Structured JSON logs, filterable by `customerId` / `severity` |
| **AWS CloudTrail** | Records management API calls for auditing |

Deployed with **CloudFormation**, **serverless** compute (Lambda + API Gateway HTTP API),
a **React** front end (S3 + CloudFront), reusing an **existing VPC** via CloudFormation Exports.

## Live deployment (account 875692608981 · ap-southeast-1)

- **App (CloudFront):** https://d1f3hops6xb50j.cloudfront.net
- **API:** https://z8zmoubie0.execute-api.ap-southeast-1.amazonaws.com
- **CloudWatch dashboard:** `beanthere-CoreServices`
  ([open](https://ap-southeast-1.console.aws.amazon.com/cloudwatch/home?region=ap-southeast-1#dashboards/dashboard/beanthere-CoreServices))

### Demo sign-in users

Five email-verified users, **created automatically at deploy** (`./run.sh deploy` runs the
seed step; or run `./run.sh seed-users` on its own). Password for all: **`Superhero123`**

| Hero | Email (username) |
|---|---|
| Superman | `clark.kent@beanthere.demo` |
| Batman | `bruce.wayne@beanthere.demo` |
| Spider-Man | `peter.parker@beanthere.demo` |
| Iron Man | `tony.stark@beanthere.demo` |
| Wonder Woman | `diana.prince@beanthere.demo` |

### What deploy creates automatically

- The **CloudWatch dashboard** is a CloudFormation resource (`CoreServicesDashboard`), so
  it is created and torn down with the stack.
- The **5 demo users** are seeded by `run.sh` right after the stack deploys (CloudFormation
  cannot set a permanent Cognito password, so this step is idempotent shell).
- `./run.sh cleanup` removes the dashboard (with the stack) and deletes the stack; the
  demo users disappear with the user pool.

Last `./run.sh test` result: **11 passed, 0 failed** — all eight core services exercised
end to end (Cognito JWT, ElastiCache cache hit, SQS→worker→CONFIRMED, SNS topic,
EventBridge→Logs, CloudWatch custom metric, filterable JSON logs, SQS DLQ, CloudTrail logging).

---

## Architecture

```
                    ┌──────────────┐
   React SPA  ───►  │ API Gateway  │  (HTTP API, JWT authorizer = Cognito user pool)
 (S3+CloudFront)    └──────┬───────┘
                           │
                    ┌──────▼───────┐   lazy-load    ┌─────────────────────┐
                    │  api Lambda  │ ─────────────► │ ElastiCache (Valkey) │  (in VPC)
                    │  (in VPC)    │ ◄───────────── │  menu cache + TTL    │
                    └──┬────────┬──┘                └─────────────────────┘
              send msg │        │ read/write
                    ┌──▼──┐   ┌─▼──────────┐
                    │ SQS │   │ DynamoDB   │  (orders, menu source of truth)
                    └──┬──┘   └────────────┘
              trigger  │
                　 ┌───▼────────────┐  publish   ┌───────────┐  fan-out  ┌──────────────┐
                    │ worker Lambda  │ ─────────► │ SNS topic │ ────────► │ email/loyalty│
                    │ (custom metric │            └───────────┘           │  subscribers │
                    │  + JSON logs)  │  put event ┌──────────────┐        └──────────────┘
                    └───────┬────────┘ ─────────► │ EventBridge  │ ─rules─► typed handlers
                            │                     └──────────────┘
                   CloudWatch metric ─► Alarm ─► SNS ops topic
                   CloudTrail ─► logs all management API calls
```

## Architecture diagram

`build_diagram.py` generates a self-contained `frontend/public/architecture.svg` that
embeds the official AWS service icons (base64) from `../../aws-icons`. `./run.sh deploy`
regenerates it before the front-end build, and the app shows it in an expandable
**"Architecture diagram"** section at the top of the page (also openable full-size at
`/architecture.svg`).

Regenerate it on its own with:

```bash
python3 build_diagram.py
```

## Layout

```
demo/session3/
├── README.md
├── template.yaml            # CloudFormation: all services + inline Lambda code
├── run.sh                   # end-to-end: deploy | test | cleanup | all
├── build_diagram.py         # generates the architecture SVG from AWS icons
├── frontend/                # React (Vite) single-page app
│   └── public/architecture.svg   # generated diagram (served at /architecture.svg)
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── aws.js           # generated at deploy time (config.js) is loaded at runtime
│       └── styles.css
└── .gitignore
```

## Usage

```bash
cd demo/session3

./run.sh deploy     # package + deploy the CloudFormation stack, build+upload the React app
./run.sh test       # end-to-end test: sign up a user, place orders, assert each service fired
./run.sh cleanup    # empty buckets and delete the stack (full teardown)
./run.sh all        # deploy, then test
```

### Order generator (populate the dashboard)

Two ways to drive random traffic — random coffees from random superhero customers,
with ~1 in 8 designed to fail into the DLQ:

```bash
./generate_orders.sh            # 20 orders, 1s apart
./generate_orders.sh 50 0.3     # 50 orders, 0.3s apart
```

Watch them land in the "All orders" table and light up the CloudWatch dashboard.

All commands target **account 875692608981**, **region ap-southeast-1**, using the
current SSO credentials.

## Cost note

ElastiCache Serverless and CloudTrail are **not** free-tier. The demo is cheap to run for
an hour but **run `./run.sh cleanup` when done** to avoid ongoing charges. ElastiCache
Serverless bills on data stored + ECPUs; a short demo is a few cents, but an idle cache
left running accrues cost.
