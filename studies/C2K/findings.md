# C2-K findings: skills that build on each other (final, 13 November 2026)

**Run:** c2k-run 43554099349.
- Valid: checks All: PASS, 672 of 672 children.
- Frozen analysis: `output/results.md`.
- Blind recompute: GPT and Gemini, matching (`recompute_c2k.md`).
- n = 48 per condition.

## The frozen readings: the task was too hard (a floor)
- **No child in any arm fully opened a box by day 30.** That holds for the oracle too. Cb's cumulative day-30 success
  was 0.000.
- **The frozen floor guard (below 0.05) applies:** readings 1–3 are **not readable**. Reading 4 is formally "no" (0
  against 0), but it is just as uninformative.
- **Why:** in 60 days the children rarely got past the first lid. On average they reached about 1.15 lids per try in
  the cumulative condition, and lid 3 was copied fewer than once per child. Three lids, each with 16 possible pairs and
  learned from one try a day, ask too much of this brain in this time.

## Exploratory (after the data, labelled; partial score = lids opened / 3, at day 30)
The partial score is above the floor, and it hints at what the full test was meant to ask:
- **With the amount of copying matched, choosing the right person helps in the cumulative condition:**
  - Ctk − Cyk +0.027 [+0.008, +0.045];
  - Cok − Cr +0.034 [+0.014, +0.053].
- **…but not in the flat condition:**
  - Ctk − Cyk +0.001 [−0.014, +0.016];
  - Cok − Cr +0.005 [−0.014, +0.023].
- **Copying everyone is still as good as choosing:**
  - Cok − Cb −0.005 (G), +0.004 (U);
  - Ctk − Cb −0.014 (G).

These are not readings. They suggest that when steps build on each other, whom you copy matters *for the same amount of
copying*. Copying more still makes up for it.

## What it means (the assistant's reading)
1. **The first honest lesson is about the brain:** a small network learning from one try a day cannot climb a 3-step
   skill in 60 days, even with perfect teachers. Real children get far more practice and more help (being shown step
   by step, being corrected). Cumulative skills need either much more time or richer teaching.
2. **The partial scores point the same way as C2-E's day-60 result:** choosing the right model leaves the child further
   along than choosing at random, but not further than copying everyone.
3. **The next rung for cumulative skills should be learnable:**
   - 2 lids, or more days;
   - or teaching step by step (a demonstration before each lid);
   - with a pilot difficulty check before freezing, as C0-B did, so the floor is ruled out in advance.

**The assistant's prior was:** 40%, 60%, 35%, 50%. No reading could be drawn.
