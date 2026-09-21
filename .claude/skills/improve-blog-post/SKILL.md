---
name: improve-blog-post
description: Turn an existing technical blog post (Jekyll/Chirpy, kramdown, MathJax) into a rigorous, verified, well-designed one. Use when asked to improve, deepen, fix the math of, or fact-check a post in _posts/. Covers provenance audit, math audit, literature sweep from arXiv source, running the deciding experiment, figures, banner, writing, kramdown pitfalls, validation, and commit.
---

# Improve a technical blog post

Read this whole file before touching the post. Work in this order; each step feeds the next.

## 0. Ground rules

- The post's job is to answer the claim in its title. Every section must connect back to that claim in one sentence.
- No number goes into the post unless it can be traced to a file the experiment wrote, a table in a cited paper's source, or a computation done for the post. If it cannot be traced, it comes out.
- The author's own claims get the same scrutiny as anyone else's. If a lemma is wrong, say so in the post and give the statement that holds.
- Read `WRITING-STYLE.md` at the repo root and follow it. Short sentences. No em dashes. No marketing words. No "promise" paragraphs. State the point in the first three paragraphs.

## 1. Read and inventory

```
wc -w _posts/<post>.md
grep -nE '^#{1,4} ' _posts/<post>.md            # structure
grep -oE '<img[^>]+src="[^"]+"|!\[[^]]*\]\([^)]+\)' _posts/<post>.md | sort -u   # images
grep -o '\$' _posts/<post>.md | wc -l          # single-$ math => broken under kramdown
```

Write down: the claim in the title, every quantitative claim, every figure and where it came from, every theorem/lemma and what it rests on, and the sections that are generic filler (textbook primers not used by the argument).

## 2. Provenance audit

For each number and figure, find the source: notebook output, results JSON, a paper's table, a script. Tells that a number is not real:

- Auto-generated tables that disagree with the post (`diff` the generated `.tex` against the prose).
- "Simulation mode", "synthetic results grounded in...", placeholder inequalities (`>0.90`) later hardened into point values.
- A notebook with zero cell outputs.
- A confidence–accuracy curve that *rises* as confidence falls: the low-confidence predictions are being resolved by something other than the score (tie-break, column order, label leak).
- Reported results impossible under the stated procedure (e.g. a "convergence" below a floor the model cannot reach). Compute the floor and check.

Reproduce anything reproducible (an RNG seed, a Monte Carlo floor) and state in the post that it was computed for the post.

## 3. Math audit

For each lemma/theorem: what is assumed, what is derived, what is asserted. Common failures seen in practice:

- "Non-constant function ⇒ nonzero covariance": false (Y² with symmetric Y).
- An argument that applies equally to both directions establishes no asymmetry.
- "Harder landscape ⇒ more steps under PL" needs *equal PL constants* in both directions; that is an unverifiable assumption, not a step in a proof. Name it as an assumption.
- A claimed inequality between loss floors is usually someone else's theorem with conditions (Blöbaum et al. 2018, RECI: small-noise limit, equality iff linear). Cite it; state the conditions.

Write the corrected statements as numbered theorem blocks with proofs or proof sketches.

## 4. Literature sweep, from source

Two alphaXiv searches per message (`discover_papers`, prioritize `recency` for the last 18 months, `historical` for the spine). Then pull source, not abstracts:

```
for id in <ids>; do
  d=lit/$id; mkdir -p $d
  curl -sL -A "Mozilla/5.0 (research; contact <email>)" https://arxiv.org/e-print/$id -o $d/src.bin; sleep 1.5
  (cd $d && (tar -xzf src.bin 2>/dev/null || gunzip -c src.bin > main.tex))
done
```

Extract per paper: abstract, section titles, `\begin{theorem}` headers, every line mentioning the benchmark with a number, every `tabular` containing accuracy/AUROC. Compile a table of reported results **with each paper's protocol** (number of pairs, weighted or not). Different protocols are not comparable; say so under the table.

Look for: (a) the closest prior work the post did not cite, (b) a published counterexample to the post's intuition, (c) a ceiling result (e.g. "40% of benchmark pairs have misleading conditional variance"), (d) the current evaluation conventions (abstention as an outcome, bootstrap CIs, decision-rate curves).

Never copy another paper's figure into the post. Recreate from data or cite.

## 5. Run the deciding experiment

Identify the one experiment that decides the title's claim. Design it so one training pass answers every rule:

- Record the full held-out loss trajectory (every 5 steps) for every run; evaluate any threshold rule post hoc.
- Batch independent runs into one stacked model with one elementwise optimizer (Adam): identical to separate runs, 100× faster on CPU. Benchmark 100 steps first to estimate total time.
- Same seed/initialization in both directions of a pair.
- Standard benchmark protocol (for Tübingen: exclude multivariate pairs 52–55, 71, 105; use `pairmeta.txt` weights; randomly flip orientation before the method sees the pair; report abstentions separately; bootstrap CIs over pairs; check that "always column 1 → column 2" scores ≈ 50%).
- Save per-run summaries as JSON; ship the script and JSON under `assets/code/` and link them.

Report what happened, including results that contradict the post.

## 6. Figures

- Render the paper's TikZ with `pdflatex` (standalone, carry over `\definecolor`s and libraries) and `pdftoppm -r 220 -png -singlefile`.
- New figures in one palette (this site: teal `#0a7c5c`, red `#c0392b`, mid `#666660`, ink `#111118`, gold `#b8860b`, paper `#f0efe9`), serif font, no top/right spines, median + IQR bands over seeds, log axes where the dynamics span decades.
- One figure per finding. A figure that needs a paragraph to read is two figures.
- Every figure gets `![alt](/assets/img/<post>/<file>.png)` followed by an italic `_Figure n. caption._` line; Chirpy renders the italic line as the caption.

## 7. Banner

The banner is a **symbol**, not a data figure. Rules: one idea, no axes, no small text, high contrast, dark background works on this site, unique to the post. Render as TikZ or a 16:9 matplotlib canvas with `axis("off")`. Check it as a 440×240 thumbnail before accepting it. If it needs a legend it is wrong.

## 8. Write

Structure that has worked: hook (2–3 short paragraphs, the point stated directly) → why the problem is hard → the identifiability theory → toolkit (only facts used later, each stated once) → the idea → what is actually asymmetric (corrected lemmas) → the experiment → boundary conditions → related methods table + what the last two years did → the benchmark done properly, with the literature table → what is open → beyond the bivariate case → summary → references.

Design elements: numbered equations `$$ ... \tag{n} $$`; theorem blocks as `> **Lemma n (name).** ...` with proofs; tables with real header rows; captions on every figure and table; citations `[\[n\]](#ref-n)` linking to `n. <a id="ref-n"></a> ...` in the reference list; code links.

Cut: generic primers not used by the argument, comparison tables against unrelated systems, analogies stated as claims, sentences that praise the work, any sentence a reader could skip without losing a fact.

## 9. Kramdown / Chirpy pitfalls (each of these broke a post)

- Inline math must be `$$...$$`, not `$...$`: kramdown italicizes `_` inside single-dollar math. Display math: `$$` on its own line with blank lines around; inside blockquotes prefix every line with `> `. In list items keep math inline and escape a leading `\$$`.
- A `|` anywhere in a paragraph line makes kramdown start a *table*. Inside math use `\mid` or `\vert`, never `|`.
- No `<div>` wrappers: kramdown treats everything inside as raw HTML (tables, math and bold inside stop rendering). pandoc emits `<div class="center">` for `\begin{center}`; strip it.
- Table separator rows must be `|---|`, not `|:---|`; alignment colons become inline `text-align` styles that override site CSS.
- `[27, 100]` in a table cell is parsed as a link reference; write `27 to 100`.
- pandoc 3.x `gfm` emits GitHub-only ```` ```math ```` fences; use `-t gfm+tex_math_dollars-tex_math_gfm`. It leaves `\begin{equation*}` inside `$$`, which MathJax rejects; convert `equation*`/`multline` yourself. `multline` is numbered.
- `\tag{n}` works at the top level of display math; do not put it inside `aligned` (tag the block once instead).
- Chirpy builds its own TOC and title; do not include a TOC list or an H1 in the body. Sections start at `##`.
- Front matter: `math: true`, `image: {path: assets/img/<post>/banner.png, alt: ...}`, `date` with `+04:00`.

## 10. Validate before showing anyone

```
K=vendor/bundle/ruby/3.2.0/gems; G=$(ls -d $K/kramdown-parser-gfm-* | head -1)
ruby -I "$K/kramdown-2.5.2/lib" -I "$G/lib" -e '
require "kramdown"; require "kramdown-parser-gfm"
src = File.read("_posts/<post>.md").sub(/\A---.*?---\n/m, "")
d = Kramdown::Document.new(src, input: "GFM", math_engine: "mathjax"); h = d.to_html
puts "warnings #{d.warnings.size} | inline #{h.scan(/\\\(/).size} | display #{h.scan(/\\\[/).size} | raw $$ #{h.scan(/\$\$/).size} | raw ** #{h.scan(/\*\*/).size} | tables #{h.scan(/<table/).size} | img #{h.scan(/<img /).size}"
d.warnings.each { |w| puts w }'
```

Targets: 0 warnings, 0 raw `$$`, 0 raw `**`. Then: every `/assets/...` path exists; every `#ref-n` cited is defined and every defined one is cited; local serve (`export PATH="$PWD/vendor/bundle/ruby/3.2.0/bin:$PATH"; bundle exec jekyll serve --livereload`) and read the post in the browser, including the card on the home page.

## 11. Commit

Stage only the post, its asset folder, `assets/code/`, and any site CSS override. Leave the author's other uncommitted files alone and say so. Commit message: what the post now claims, in one line. Push only when asked.
