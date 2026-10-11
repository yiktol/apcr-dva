# APCR-DVA presentation site — verification note

First iteration (no prior `apcr-dva-site-review.json` existed). Implemented
from scratch per `.agents/tasks/apcr-dva-site-plan.md`. All commands below
were run from the workspace root `/Users/erictole/demo/apcr-dva` unless noted.

## 1. Builder run — slide counts

```
$ cd site && python3 build_decks.py
Built session decks:
  m1: 76 slides (2 hidden) -> decks/m1.js
  m2: 78 slides (2 hidden) -> decks/m2.js
  m3: 58 slides (2 hidden) -> decks/m3.js
  m4: 72 slides (3 hidden) -> decks/m4.js
  m5: 66 slides (2 hidden) -> decks/m5.js
Total: 350
```
Exit code: 0. Counts match the brief exactly (76/78/58/72/66).

Idempotency check (ran the builder twice, compared md5 of m1.json before/after):
```
$ md5sum decks/m1.json > /tmp/a.txt && python3 build_decks.py && md5sum decks/m1.json > /tmp/b.txt && diff /tmp/a.txt /tmp/b.txt
(no diff output -> IDENTICAL)
```

## 2. JSON validity + slide object shape

```
$ python3 -c "import json; [print(n, len(json.load(open(f'decks/m{n}.json')))) for n in range(1,6)]"
1 76
2 78
3 58
4 72
5 66
```
Exit code: 0 (all 5 files parse as valid JSON).

```
$ python3 -c "
import json
for n in range(1,6):
    d = json.load(open(f'decks/m{n}.json'))
    for s in d:
        assert set(s.keys()) == {'n','mode','image','title','hidden','student'}
print('OK keys')
"
OK keys
```
Every slide object across all 5 decks has exactly the keys n/mode/image/title/hidden/student.

## 3. Image path existence

```
$ python3 -c "
import json, os
missing = 0
for n in range(1,6):
    for s in json.load(open(f'decks/m{n}.json')):
        if not os.path.exists(s['image']):
            missing += 1
            print('MISSING', s['image'])
print('missing total:', missing)
"
missing total: 0
```
0 missing images across all 5 decks (350 total).

```
$ find decks/images -name '*.png' | wc -l
350
```

## 4. HTTP smoke test (server started in background, then stopped)

```
$ cd /Users/erictole/demo/apcr-dva
$ ./site/serve.sh 8030 > /tmp/serve.log 2>&1 &
$ sleep 1.5
$ curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8030/index.html
200
$ curl -s -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:8030/deck.html?m=3"
200
$ curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8030/decks/m3.json
200
$ curl -s http://127.0.0.1:8030/decks/m3.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d))"
58
$ curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8030/decks/m1.js
200
$ curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8030/decks/images/session3/slide-01.png
200
$ curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8030/fonts/AmazonEmber_Rg.ttf
200
$ curl -s http://127.0.0.1:8030/index.html | grep -c "sessions = \["
1
$ kill %1; wait
(server terminated cleanly, no leftover process)
```
index.html, deck.html?m=3, decks/m3.json, decks/m1.js, a slide image, and a
font file all returned 200. decks/m3.json round-trips to 58 entries over
HTTP (matches session3's slide count). index.html's embedded `sessions`
array (which renders the 5 session cards client-side, same pattern as the
reference app's `domains` array) is present in the served HTML.

## 5. Static checks on deck.html

```
$ grep -c "JUDGE_URL\|sm-check\|Timer\.\|wireChecks\|fitChecks" site/deck.html
0
```
All judge/check/timer code fully removed.

```
$ grep -c 'DECK_DATA\[m\]\|decks/m${m}\.js\|decks/m${MODULE}\.json' site/deck.html
4
```
The DECK_DATA[m] + decks/m<m>.js + decks/m<MODULE>.json loading contract is
intact (loadDeckScript checks window.DECK_DATA[m] first, falls back to the
decks/m<m>.js script tag, then loadDeck() falls back further to fetching
decks/m<MODULE>.json).

Render-path confirmation (exact lines present verbatim in site/deck.html):
```js
const body = (s.mode === "native" && s.native) ? s.native
  : (s.image ? `<img class="slide-image" src="${s.image}" alt="slide ${s.n}" />` : "");
const notes = s.student
  ? `<aside class="notes">${renderNotes(s.student)}</aside>` : "";
```

reveal.js wiring confirmed: `<script src=".../reveal.js/5.1.0/reveal.min.js">`,
`.../plugin/notes/notes.min.js`, and `Reveal.initialize({ ..., plugins: [RevealNotes] })`
are all present and unchanged from the reference app (version 5.1.0, same CDN).

Spot-check m1.js assigns window.DECK_DATA["1"] with 76 entries:
```
$ python3 -c "
import re, json
text = open('decks/m1.js').read()
m = re.search(r'window.DECK_DATA\[\"1\"\] = (\[.*\]);', text, re.S)
print(len(json.loads(m.group(1))))
"
76
```

## Other checks performed

- `ls -la site/serve.sh` -> `-rwxr-xr-x` (executable bit set).
- `bash -n site/serve.sh` -> no syntax errors.
- `ls site/fonts | wc -l` -> `9`; `diff site/fonts.css aib-c01/fonts.css` -> no output (byte-identical).
- `grep -o 'deck.html?m=\${d.n}'`-style check: index.html's session links are
  rendered client-side via a template literal (`deck.html?m=${s.n}`), the
  same pattern the reference `aib-c01/index.html` uses for its domain cards
  (confirmed identical templating approach in the reference source). The
  live-rendered routing was confirmed working via the `deck.html?m=3` -> 200
  HTTP check above, and all 5 session numbers (1-5) are present in the
  `sessions` array embedded in index.html.
- `grep -c "quiz\|flashcard\|walkthrough\|knowledgecheck\|/judge" site/deck.html site/index.html`
  -> `0` for both files (no out-of-scope features leaked in).
- `git status --short md temp` -> only the pre-existing untracked
  `md/session1,2,4,5/` directories; no modifications to any file under `md/`
  or `temp/`.
- `find site -type f | sort` reviewed: index.html, deck.html, build_decks.py,
  serve.sh, fonts.css, fonts/*.ttf (9), decks/m1..5.js, decks/m1..5.json,
  decks/images/session1..5/slide-*.png (350 total, confirmed above).

## What still needs a human to eyeball in a browser

1. **Visual non-cropping of slide images.** The `.slide-image` CSS rule uses
   `object-fit: contain` with `max-height: 84vh`, which should letterbox
   rather than crop every 2001x1125 PNG, but this needs a real browser
   render to confirm there's no unexpected clipping or distortion at
   different viewport sizes.
2. **Speaker notes view.** Press `S` on `deck.html?m=<N>` (or click the
   "Notes" button) to confirm the reveal.js speaker-notes popup opens and
   renders each slide's `student` text correctly, including the two-URL
   link-ified paragraphs and hidden-slide notes (session1 slides 1-2,
   session4 slide 29, etc.).
3. **Keyboard navigation and TOC overlay.** Arrow keys / space / Home / End
   for slide navigation, and the "Slides" button (or `T`) opening the
   jump-to-slide overlay with search/filter — these are unchanged from the
   reference app's logic but were not clicked through in a real browser.
4. **Fullscreen toggle** (`F` or the Fullscreen button) — browser-only
   behavior, not testable via curl.
5. **Visual accent-color distinction** across the 5 index.html session
   cards (navy/blue/teal/green/magenta) — confirmed present in CSS but not
   visually inspected.
6. **Font rendering** — Amazon Ember / Amazon Ember Display loading
   correctly from the self-hosted `fonts/*.ttf` files (confirmed the files
   serve with 200, but actual glyph rendering needs a browser).
