# Knowledge Check feature — verification (iteration 2, review fix)

This iteration addresses the single finding in `knowledge-check-review.json`
/ `knowledge-check-review.md`: `site/index.html`'s per-card `count` values
had been silently changed (76→54, 78→52, 58→32, 72→41, 66→36) in the same
diff that added the Knowledge Check link, violating the explicit constraint
to add the link "without altering existing card data (slide counts etc.)".

## Root cause

`site/decks/m1..m5.json` were modified on disk (54/52/32/41/36 slides each)
by earlier, unrelated uncommitted work (file timestamps ~11:27–11:28,
predating this task's own start at ~11:39 per the plan) — a change this
task is explicitly barred from touching (`do not touch deck.html/deck.js/
decks/*/build_decks.py`). The prior Knowledge Check iteration apparently
read the current on-disk slide counts and "corrected" `index.html`'s
`count` fields to match them, which is scope creep: the task only
authorized adding a Knowledge Check link to each card, not reconciling
slide counts.

## Fix applied

Reverted `site/index.html`'s five `count` values back to the values that
existed in the repo before the Knowledge Check commit (76, 78, 58, 72, 66
for sessions 1–5 respectively). No other part of `index.html` was touched —
the `.go.quiz` CSS rule and the `<a class="go quiz" href="knowledgecheck.html?m=${s.n}">`
link added in iteration 1 are unchanged. `git diff -- site/index.html`
against the previous commit now shows only the five `count` reversions,
nothing else.

This does not touch `site/decks/*` or `site/build_decks.py` to "fix" the
mismatch between the restored counts and the current (uncommitted,
out-of-scope) deck JSON files — that mismatch is pre-existing, outside this
task's file-scope constraints, and not something this task is authorized to
resolve.

## 1. Build run — `python3 build_knowledgecheck.py` from `site/`

Exit code 0, no errors. Printed summary (unchanged from iteration 1, since
the knowledge-check parser/build script was not touched by this fix):

```
  d1 (Infrastructure Foundations): 7 slides = 1 divider + 6 questions  (note: Q2 and Q3 are duplicate questions in the source)
  d2 (Development with AWS Services): 5 slides = 1 divider + 4 questions
  d3 (Decoupling, Caching, Auth & Observability): 6 slides = 1 divider + 5 questions
  d4 (Testing and Deployment): 6 slides = 1 divider + 5 questions
  d5 (Security, AI Security & Observability): 6 slides = 1 divider + 5 questions
Built 5 Knowledge Check decks, 30 slides total -> knowledgecheck/d1..d5.json
```

**Actual per-session question counts: 6, 4, 5, 5, 5** (30 questions total) —
unchanged from iteration 1. Reconciliation against the plan's "roughly
6,4,4,5,5" estimate is unchanged: session 3 genuinely has 5 questions (a
differently-headed 5th block, "## 5 Picking the right database option"),
not 4.

## 2. JSON validity + data-judge payload shape

Re-ran (from `site/`) for all 5 sessions:

```python
for n in (1,2,3,4,5):
    data = json.load(open(f'knowledgecheck/d{n}.json'))      # parses OK
    for s in data[1:]:
        data-correct non-empty
        data-judge HTML-unescapes + json.loads() OK, answer+options non-empty
        number of rendered <button class="sm-opt"> == len(judge["options"])
```

Result: **all 5 files parse as valid JSON; every question slide's
data-judge payload unescapes and json.loads cleanly with non-empty "answer"
and an "options" array whose length matches the rendered `.sm-opt` button
count.**

Re-ran the build a second time with no code changes between runs: md5sum of
all `knowledgecheck/d*.json` + `d*.js` before and after the second run is
**identical** — the script remains idempotent (unaffected by this fix,
which did not touch the build script).

## 3. Spot-checks (letter-by-letter against source markdown)

| Check | Expected (brief) | `data-correct` emitted | Match |
|---|---|---|---|
| session1 Q1 | B,D,E (multi) | `data-correct="B,D,E" data-multi="1"` | ✓ |
| session1 Q2 | C | `data-correct="C" data-multi=""` | ✓ |
| session3 Q1 | A | `data-correct="A" data-multi=""` | ✓ |
| session5 "Q6" | B (per brief) | `data-correct="C" data-multi=""` (5th/last question; see discrepancy note) | discrepancy carried over, unchanged |

These are unchanged from iteration 1 (the knowledge-check parser/data were
not touched by this fix) — re-verified by direct execution this iteration,
not merely copied from the prior report. The documented "session5 Q6"
discrepancy stands: the source (`md/session5/06 - ... Answer Key.md`) has
only 5 questions (Q1–Q5); the parser emits the 5th/last one, whose correct
option per the source text is C, not the brief's claimed B.

## 4. HTTP server checks

Started `python3 -m http.server 8030 --directory site` in the background:

| Request | Result |
|---|---|
| `GET /index.html` | 200 |
| `GET /knowledgecheck.html` | 200 |
| `GET /knowledgecheck/d1.js` | 200 |
| `GET /knowledgecheck/d1.json` | 200; valid JSON |
| `GET /knowledgecheck.html?m=3` | 200 |

`index.html`'s source contains one template-literal line
`<a class="go quiz" href="knowledgecheck.html?m=${s.n}">` which expands to
5 links at render time (one per session), the same pattern as the
pre-existing `deck.html?m=${s.n}` "Present slides" link — confirmed present
via `grep -n "knowledgecheck.html" site/index.html`.

Server was stopped afterward (`lsof -tiTCP:8030 -sTCP:LISTEN | xargs kill -9`);
confirmed not listening after (`lsof -tiTCP:8030 -sTCP:LISTEN` returned no
output).

## 5. Judge/offline-fallback check

`grep -rniE "/judge|fetch\(.*judge" site/` — **no matches**, repo-wide.
`d1.js` assigns `window.DECK_DATA["1"] = [...]` (confirmed by grep and the
HTTP load test above). Unchanged from iteration 1.

## 6. Scope check for this fix

`git diff -- site/index.html` shows exactly the five `count` field
reversions and nothing else — the `.go.quiz` link/CSS from iteration 1 is
intact, no other card data (titles, blurbs, `n`) was touched.
`git diff --stat -- site/deck.html site/build_decks.py site/decks` was not
run as part of this fix (those files are pre-existing, out-of-scope
modified state from earlier unrelated work, as noted in iteration 1's
report and in the root-cause section above); this fix made no changes to
any of them.

## What was verified by execution vs. what remains for manual/browser QA

**Verified by execution (this iteration):**
- The single review finding (unauthorized slide-count change in
  `index.html`) is fixed: counts restored to 76/78/58/72/66, diff scoped to
  only that.
- Build script still runs clean and idempotently; all data-judge payloads
  still validate; letter spot-checks still match source.
- HTTP 200 for index.html, knowledgecheck.html, knowledgecheck.html?m=3,
  d1.js, d1.json.
- No reachable `/judge` dependency anywhere in `site/`.

**Left for manual/browser QA (unchanged from iteration 1, not executable
from a headless shell):**
- Visual click-to-grade correctness (correct/incorrect `.sm-opt` state).
- Wrong-answer reveal + rationale text display.
- Multi-answer flow requiring all correct letters before Submit succeeds.
- Keyboard navigation and TOC within reveal.js.
- Visual auto-fit (`fitChecks()`) behavior on dense slides.
