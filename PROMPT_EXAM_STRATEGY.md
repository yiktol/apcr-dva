# Comprehensive Prompt: AWS Exam Strategy Materials Generator

Use this prompt to recreate the entire exam strategy materials package from scratch.

---

## Context

I have AWS Partner Certification Readiness (APCR) PowerPoint presentations and Answer Key documents for the **Developer Associate (DVA-C02)** exam. Each session PPT contains lecture content, and separate Answer Key `.docx` files contain the exam-style practice questions with correct answers and explanations.

I need you to:
1. Extract the exam-style questions from each session's Answer Key document (and cross-reference with the PPT if needed)
2. For each question, generate study materials including markdown notes, architecture diagrams, and a standalone PowerPoint presentation

---

## Input Structure

The source files are located in a `ppt/` folder:

**Content Review PPTs:**
- `ppt/02 - APCR-DVA - Content Review Session 1.pptx`
- `ppt/03 - APCR-DVA - Content Review Session 2.pptx`
- `ppt/04 - APCR-DVA - Content Review Session 3.pptx`
- `ppt/05 - APCR-DVA - Content Review Session 4.pptx`
- `ppt/06 - APCR-DVA - Content Review Session 5.pptx`

**Exam Strategy Answer Keys:**
- `ppt/03 - APCR-DVA - Exam Strategy Session 1 - Answer Key.docx`
- `ppt/05 - APCR-DVA - Exam Strategy Session 2 - Answer Key.docx`
- `ppt/07 - APCR-DVA - Exam Strategy Session 3 - Answer Key.docx`
- `ppt/09 - APCR-DVA - Exam Strategy Session 4 - Answer Key.docx`
- `ppt/11 - APCR-DVA - Exam Strategy Session 5 - Answer Key.docx`

AWS architecture icons are available in `aws-icons/` folder with subfolders:
- `Architecture-Service-Icons_04302026/` (service icons by category, sizes 16/32/48/64)
- `Architecture-Group-Icons_04302026/` (VPC, subnet, region groupings)
- `Resource-Icons_04302026/`
- `Category-Icons_04302026/`

---

## Session Topics (DVA-C02 Domains)

- **Session 1**: AWS Global Infrastructure, Compute Services, Container Services, Networking, IAM
- **Session 2**: Serverless Architecture, Database Offering, Messaging Services
- **Session 3**: Application Integration, Database Caching, Web & Mobile Login, Monitoring, SQS, SNS, EventBridge, ElastiCache
- **Session 4**: CI/CD Toolings, Deployment Services, CloudFormation Extensions, Deployment Strategies
- **Session 5**: Security/Identity/Compliance, IAM Policy, Application Monitoring, Amazon S3

---

## Output Structure

For each session (1-5), create the following folder structure:

```
session{N}/exam-strategy/
├── countdown_2min.gif          # Shared 2-minute countdown timer
├── q1/
│   ├── q1.md                   # Markdown with question, options, answers, explanations
│   ├── option_a.png            # Architecture diagram for option A
│   ├── option_b.png            # Architecture diagram for option B
│   ├── option_c.png            # ...
│   ├── option_d.png
│   ├── option_e.png            # (if 5 options)
│   ├── q1_exam_strategy.pptx   # Standalone PowerPoint presentation
│   └── create_diagrams.py      # Script to regenerate diagrams
├── q2/
│   ├── ...
├── q3/
├── q4/
└── q5/
```

---

## Step 1: Extract Questions

Read each Answer Key `.docx` using `python-docx`. These documents contain the exam questions with:
- The question text (scenario + prompt)
- All answer options (A through D or E)
- Which options are correct (marked with "(Correct)" or similar indicators)
- Explanations for why each option is correct or incorrect

Also cross-reference with the corresponding Content Review PPT (`python-pptx`) to identify:
- Slides with "QUESTION" header or containing "Which", "What is", "How should"
- Answer slides containing "(Correct)" markers
- Answer key slides summarizing correct answers

For each question, extract:
- The question text (scenario + prompt)
- All answer options (A through D or E)
- Which options are correct
- Explanations for why each option is correct or incorrect

---

## Step 2: Create Markdown Files

For each question, create `q{N}.md` with this structure:

```markdown
# {Question Title}

{Full question text}

- A) {Option A text}
- B) {Option B text}
- C) {Option C text}
- D) {Option D text}

## Answer

**{Correct letter(s)}**

- **{Letter}) {Correct option text}**
  - {Bullet explanation 1}
  - {Bullet explanation 2}
  - {Bullet explanation 3}

## Why the other options are incorrect

- **{Letter}) {Incorrect option text}**
  - {Bullet explanation 1}
  - {Bullet explanation 2}
  - {Bullet explanation 3}
```

---

## Step 3: Generate Architecture Diagrams

Use the Python `diagrams` library (mingrammer/diagrams) to create a unique architecture diagram for each option of each question.

### Requirements:

- Each diagram must be **unique** and visually illustrate the architecture proposed by that specific option
- Use **horizontal layout** (`direction="LR"`)
- **No title text** on the diagram (empty string for Diagram name)
- **Color-coded clusters**:
  - Correct answers: green background (`#e8f5e9`, border `#2e7d32`)
  - Incorrect answers: red/orange background (`#fbe9e7`, border `#c62828`)
  - Neutral groupings: blue background (`#e3f2fd`, border `#1565c0`)
  - Source/origin: orange background (`#fff3e0`, border `#e65100`)
- **Edge styling**:
  - Green bold arrows for correct flows
  - Red bold/dashed arrows for incorrect/blocked flows
  - Orange for warnings
  - Include descriptive labels on edges explaining the flow
- **Use proper AWS service icons** from the diagrams library:
  - `diagrams.aws.compute` — Lambda, EC2, ElasticBeanstalk, ECS, EKS, Fargate
  - `diagrams.aws.storage` — S3, ElasticFileSystemEFS, ElasticBlockStoreEBS
  - `diagrams.aws.database` — Dynamodb, RDS, ElastiCache, Aurora
  - `diagrams.aws.network` — VPC, NATGateway, CloudFront, ELB, APIGateway, Route53
  - `diagrams.aws.integration` — Eventbridge, SQS, SNS, StepFunctions
  - `diagrams.aws.devtools` — Codepipeline, Codebuild, Codedeploy, Codecommit, Xray
  - `diagrams.aws.security` — IAM, KMS, SecretsManager, Cognito, WAF
  - `diagrams.aws.management` — Cloudwatch, Cloudformation, SystemsManager, CloudTrail
  - `diagrams.aws.analytics` — Kinesis, KinesisDataStreams
  - `diagrams.custom.Custom` — for icons from the `aws-icons/` folder when built-in library doesn't have the specific service icon
- **Graph attributes**:
  ```python
  {"fontsize": "14", "bgcolor": "#fafafa", "pad": "0.8", "splines": "spline",
   "nodesep": "1.0", "ranksep": "1.0", "fontname": "Helvetica"}
  ```

### Diagram content guidelines:

- Show the actual AWS services involved in the option
- Show data flow direction with labeled arrows
- Highlight WHY it's correct (green, "✓" labels) or incorrect (red, warning labels)
- Keep diagrams simple (3-6 nodes max) but informative
- For DVA-C02 topics, emphasize:
  - API Gateway → Lambda → DynamoDB patterns
  - CI/CD pipeline flows (CodeCommit → CodeBuild → CodeDeploy)
  - Event-driven architectures (SQS, SNS, EventBridge)
  - Container orchestration (ECS, EKS, Fargate)
  - Authentication flows (Cognito, IAM)
  - Deployment strategies (Blue/Green, Canary, Rolling)

---

## Step 4: Generate Countdown Timer

Create an animated GIF countdown timer (`countdown_2min.gif`):
- **Size**: 280×280 pixels
- **Background**: Dark navy (`#1a237e`)
- **Ring**: Green progress arc (`#00e676`) on dark gray background ring
- **Text**: Large white numbers (56pt DejaVu Sans Bold) showing `M:SS`
- **Duration**: 121 frames (2:00 down to 0:00), 1 second per frame
- **Loop**: Play once only (`loop=1`)
- **Format**: Optimized GIF with 64-color adaptive palette

---

## Step 5: Generate PowerPoint Presentations

For each question, create a standalone `.pptx` with this structure:

### Slide 1: Question + Options + Timer

- **Slide size**: 10" × 5.625" (16:9 widescreen)
- **Background**: Dark gradient (navy `#0d1b2a` → `#09121c`)
- **Left accent bar**: Thin blue vertical line (`#1e88e5`)
- **Title**: Question title in accent blue, 20pt bold, Segoe UI
- **Question text**: White, 11pt, Segoe UI
- **Options**: Each with a circular blue badge (letter A-E) and option text in light gray, 10pt
- **Timer card** (top right):
  - Rounded rectangle with dark navy background (`#1a237e`)
  - "⏱ TIME" label in green (`#00e676`), 9pt bold, centered
  - Embedded countdown GIF (1.7" × 1.7")
  - No "2 Minutes" text below

### Slides 2+: One per option

- **Background**: Light gray solid (`#f8f9fa`)
- **Top banner**: Full-width dark navy rectangle (0.9" tall)
  - Status badge: Rounded rectangle, green (`#00c853`) for correct or red (`#ff1744`) for incorrect
  - Badge text: "✓ CORRECT" or "✗ INCORRECT", 10pt bold white
  - Option text: "Option {Letter}: {text}", 10pt white
- **Diagram** (left side, ~60% width):
  - Proportionally sized (never stretched)
  - Calculate aspect ratio from actual image dimensions
  - Center vertically in available space
- **Explanation panel** (right side):
  - White rounded rectangle card
  - Colored accent line on left edge (green or red matching status)
  - "Why this is correct/incorrect:" header in status color, 10pt bold
  - Bullet points: "• {explanation}", 9pt dark text, Segoe UI
  - 6pt spacing between bullets

---

## Dependencies

```
pip install python-pptx python-docx diagrams Pillow
apt install graphviz  # Required by diagrams library
```

---

## Key Design Decisions

1. **Images are never stretched** — always calculate proportional dimensions from actual image size
2. **Timer plays once** — not looping, counts down 2:00 → 0:00 and stops
3. **No title/label text on diagrams** — the diagram speaks for itself
4. **Bullet points for explanations** — not paragraphs, for quick scanning during review
5. **Color coding is consistent** — green = correct, red = incorrect, throughout all materials
6. **Each option gets its own unique diagram** — showing the specific architecture proposed, not a generic placeholder
7. **Horizontal layout** for all diagrams — left-to-right flow
8. **Custom AWS icons** from the `aws-icons/` folder used via `diagrams.custom.Custom()` when the built-in library doesn't have the specific service icon needed
9. **Answer Keys are primary source** — the `.docx` Answer Key files are the authoritative source for questions and correct answers; PPTs are secondary/supplementary
10. **DVA-C02 focus** — diagrams emphasize developer-centric patterns: serverless, CI/CD, event-driven, containers, security

---

## Execution Order

```bash
# 1. Generate the countdown timer
python3 session1/exam-strategy/generate_timer.py

# 2. Generate diagrams for session 1
cd session1/exam-strategy/q1 && python3 create_diagrams.py
cd session1/exam-strategy/q2 && python3 create_diagrams.py
# ... repeat for q3, q4, q5

# 3. Generate diagrams for sessions 2-5
python3 generate_diagrams_s2_s5.py

# 4. Generate PPTs for session 1
cd session1/exam-strategy && python3 create_all_pptx.py

# 5. Generate markdown + PPTs for sessions 2-5
python3 build_all_sessions.py
```

---

## Notes

- The `ppt/` and `aws-icons/` folders are already in `.gitignore` (large binary assets)
- Source materials include both `.pptx` (Content Review) and `.docx` (Answer Keys) — use `python-docx` for the Answer Keys
- Answer identification: look for "(Correct)" text in option lines, or dedicated answer sections in the docx
- Some questions have 2 correct answers (Select TWO) — handle multi-select properly in both markdown and PPT
- This project already has Streamlit apps per session — the exam-strategy materials are supplementary study aids, not part of the Streamlit app
- DVA-C02 exam domains to keep in mind:
  - Domain 1: Development with AWS Services (32%)
  - Domain 2: Security (26%)
  - Domain 3: Deployment (24%)
  - Domain 4: Troubleshooting and Optimization (18%)
