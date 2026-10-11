# Knowledge Check feature — verification (iteration 1)

Scope implemented: `site/build_knowledgecheck.py`, `site/knowledgecheck.html`,
`site/knowledgecheck/d1..d5.{js,json}`, and an added "Knowledge Check" action
link on each of the 5 session cards in `site/index.html`. No files under
`md/` or `temp/` were touched; `site/deck.html`, `site/build_decks.py`, and
`site/decks/` were not modified by this work (see note at the end on
pre-existing unrelated uncommitted changes in that area from an earlier,
separate workflow step).

## 1. Build run — `python3 build_knowledgecheck.py` from `site/`

Exit code 0, no errors. Printed summary:

```
  d1 (Infrastructure Foundations): 7 slides = 1 divider + 6 questions  (note: Q2 and Q3 are duplicate questions in the source)
  d2 (Development with AWS Services): 5 slides = 1 divider + 4 questions
  d3 (Decoupling, Caching, Auth & Observability): 6 slides = 1 divider + 5 questions
  d4 (Testing and Deployment): 6 slides = 1 divider + 5 questions
  d5 (Security, AI Security & Observability): 6 slides = 1 divider + 5 questions
Built 5 Knowledge Check decks, 30 slides total -> knowledgecheck/d1..d5.json
```

**Actual per-session question counts: 6, 4, 5, 5, 5** (30 questions total).

Reconciliation against the plan's "roughly 6,4,4,5,5" estimate:
- Session 1 = 6 ✓ (includes the source's verbatim-duplicate Q2/Q3, kept as
  two separate questions per the brief — not de-duplicated).
- Session 2 = 4 ✓ (source has no "Q3" heading at all — only Q1, Q2, Q4, Q5 —
  so 4 is correct, not a parsing gap).
- Session 3 = **5**, not the plan's guessed 4. The source has `## Q1:`
  through `## Q4:` (colon-letter Format A) **plus** a 5th, differently
  headed block, `## 5 Picking the right database option` (bare `A)`/`B)`
  Format D, no "Q" prefix). That block is a genuine 5th question, so 5 is
  the correct, reconciled count for session 3.
- Session 4 = 5 ✓, Session 5 = 5 ✓.

## 2. JSON validity + data-judge payload shape

Ran (from `site/`):
```python
for n in (1,2,3,4,5):
    data = json.load(open(f'knowledgecheck/d{n}.json'))   # parses OK, all 5
    for s in data[1:]:                                     # every question slide
        data-correct non-empty
        data-judge HTML-unescapes + json.loads() OK
        judge["answer"] non-empty, judge["options"] non-empty
        number of rendered .sm-opt buttons == len(judge["options"])
```
Result: **all 5 files parse as valid JSON; every question slide's
data-judge payload unescapes and json.loads cleanly with non-empty "answer"
and an "options" array whose length matches the rendered option-button
count.** First element of every array is the `section-header sm-divider`
slide; remaining elements are `sm-check` question slides.

Re-ran the build a second time with no code changes between runs:
`md5sum` of all `knowledgecheck/d*.json` + `d*.js` before and after the
second run is **identical** — the script is idempotent.

## 3. Spot-checks (letter-by-letter against source markdown)

| Check | Expected (brief) | Found in source | `data-correct` emitted | Match |
|---|---|---|---|---|
| session1 Q1 | B,D,E (multi) | "The correct answers are: **Amazon API Gateway (B)**, **Amazon DynamoDB (D)**, **AWS Lambda (E)**" | `data-correct="B,D,E" data-multi="1"` | ✓ |
| session1 Q2 | C | "The correct answer is **C: Send the JSON files to an Amazon S3 bucket...**" | `data-correct="C" data-multi=""` | ✓ |
| session3 Q1 | A | "A: **Correct.** To deploy an application on EC2 instances, the appspec.yml file must be placed..." | `data-correct="A" data-multi=""` | ✓ |
| session5 "Q6" | B (per brief) | Source has only 5 questions (Q1–Q5); Q5 is "...sam deploy... Invalid (or missing) template file..." whose correct option is **C**: "The developer needs to change the working directory to the root of the application..." | `data-correct="C" data-multi=""` | **Discrepancy** — see below |

Additional spot-checks performed (2+ per session as required):
- session1 Q4: source "The correct answer is **D: Configure the EC2 instance to access the data through a VPC endpoint...**" → `data-correct="D"` ✓
- session1 Q5: source "The correct answers are **A, C, and E**:" (security-group rules) → `data-correct="A,C,E" data-multi="1"` ✓
- session2 Q1: source "**D) Create a layer that contains the missing dependencies...**" (bold-wrapped correct paragraph) → `data-correct="D"` ✓
- session2 Q5 ("Amazon RDS – architecture optimizations", no letter markers in source, positional): source's first paragraph "**Correct. An ElastiCache cluster with a write-through strategy...**" is positionally option A → `data-correct="A"` ✓
- session4 Q3: source "(Select TWO.)" with "B: Correct." and "**D: Correct**." → `data-correct="B,D" data-multi="1"` ✓
- session5 Q4: source "**C: Correct.** Unlike metrics or logs, X-Ray can help users quickly identify..." → `data-correct="C"` ✓

**Documented discrepancy — "session5 Q6":** the task brief's verification
step names a check for "session5 Q6 correct = B," but session 5's answer-key
source (`md/session5/06 - ... Answer Key.md`) contains only five questions,
headed `## Q1:` through `## Q5:` — there is no sixth question in the source
to extract. The plan anticipated this exact mismatch and instructed treating
it as the 5th (last) question slide instead. That question's correct
option, per the source text itself, is **C** ("change the working directory
to the root of the application... sam deploy assumes the current working
directory is the project's root"), not B. `data-correct="C"` is the accurate
reflection of the source material; this is a brief/source mismatch, not a
parser bug — recorded here rather than silently "corrected" to match the
brief, since matching the brief's stated letter would mean emitting a wrong
answer against the actual answer-key text.

## 4. HTTP server checks

Started `./serve.sh 8030` in the background, confirmed via `lsof` that port
8030 was listening, then:

| Request | Result |
|---|---|
| `GET /index.html` | 200; rendered-script simulation confirms exactly 5 `knowledgecheck.html?m=` links and 5 `deck.html?m=` links appear in the generated card markup (one static template literal in the source expands to 5 at runtime, same pattern as the pre-existing "Present slides" link) |
| `GET /knowledgecheck.html` | 200; contains `wireChecks` (2 occurrences: function definition + call site) |
| `GET /knowledgecheck/d1.js` | 200 |
| `GET /knowledgecheck/d1.json` … `d5.json` | 200 each; all parse as valid JSON over HTTP |
| `GET /knowledgecheck.html?m=3` | 200 |

Server was stopped afterward (`lsof -tiTCP:8030 -sTCP:LISTEN \| xargs kill -9`);
confirmed not listening after.

## 5. Judge/offline-fallback check

`grep -rniE "judge" site/knowledgecheck.html` finds only the **local,
offline** judge-JSON payload handling that the plan specifies as the
required fallback mechanism:
- `card.dataset.judge` — reads the slide's own embedded `data-judge` JSON
  attribute (built at compile time by `build_knowledgecheck.py`, never
  fetched from a network).
- One comment block explaining the backend judge call was intentionally
  removed.
- `judgeData.why` used only as a secondary local fallback if
  `data-rationale` is somehow empty.

`grep -n "fetch(" site/knowledgecheck.html` finds exactly **one** `fetch`
call, which is the same-page `knowledgecheck/d{N}.json` static-asset fallback
(mirrors `deck.html`'s existing `decks/m{N}.json` fallback) — not a judge
endpoint. There is no `JUDGE_URL`, no `/judge` string literal, and no
network POST anywhere in the file. `grep -rniE "/judge|fetch\(.*judge" site/`
(repo-wide, matching the brief's exact verification command) returns no
matches. `d1.js` assigns `window.DECK_DATA["1"] = [...]` (confirmed by
grep and by the HTTP load test above).

## What was verified by execution vs. what remains for manual/browser QA

**Verified by execution (this iteration):**
- Build script runs clean, is idempotent, and produces valid dual-emit
  JS/JSON bundles for all 5 sessions.
- Every question's `data-correct`, `data-multi`, and `data-judge` payload
  structurally validates (JSON-parses, non-empty answer/options, option
  count matches rendered buttons).
- Letter-by-letter spot checks against the five source markdown files for
  2+ questions per session, including all four checks named in the task
  brief (with the session5 "Q6" numbering discrepancy documented above).
- HTTP 200 for index.html, knowledgecheck.html, knowledgecheck.html?m=3,
  and all d{N}.js/.json files; index.html's rendered card markup contains
  5 Knowledge Check links.
- No reachable `/judge` dependency and no judge-related `fetch()` call
  anywhere in `site/`.
- `site/deck.html`, `site/build_decks.py`, and files under `md/`/`temp/`
  were not modified by this work.

**Left for manual/browser QA (not executable from a headless shell):**
- Visual click-to-grade correctness on an actual rendered slide (clicking
  the correct vs. an incorrect `.sm-opt` button and seeing the green/red
  state + checkmark/x-mark apply).
- Wrong-answer reveal behavior: confirming the "Not quite — try another
  option" message appears without revealing the answer, and that a
  subsequent correct click still succeeds and locks the slide.
- Multi-answer flow: selecting a partial/incorrect combination of letters
  for a multi-select question, clicking Submit, confirming the selection
  clears with the "adjust your selection" message, then selecting the full
  correct set and confirming Submit succeeds and locks.
- Keyboard navigation (arrow keys / space / Home / End / T for TOC) within
  reveal.js on the rendered deck.
- Visual auto-fit behavior (`fitChecks()` adding `.sm-compact`/
  `.sm-compact-2` on dense slides) at 1280×720.

## Note on pre-existing unrelated uncommitted state

`git diff --stat -- site/deck.html site/build_decks.py site/decks` shows
pre-existing uncommitted changes (file timestamps ~11:27–11:28, before this
task's work began at ~11:39). These were not made by this task and are left
untouched, per the constraint not to modify deck.html/build_decks.py/decks/*.
