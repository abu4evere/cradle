# C2-E blind recompute (13 November 2026)

- **The data:** the day-30 column of `recompute/c2e_children_counts.csv` (the frozen builder's file), written
  compactly as 18 lists of 48 numbers in `recompute/c2e_day30_compact.txt`. The prompt's quantities are all at day 30.
  It was pasted inline.
- **The prompt:** `recompute/prompt.txt`, worded for the compact form.
- **Neither model saw** the analysis script or the results.

## GPT (chatgpt.com/c/6af77faa-bd74-83e9-abda-dd2b18d5b3ef; NumPy, seed 20261113)
**Every quantity matches the frozen analysis exactly:**
- Ctk − Cyk (S) +0.0243 [−0.0139, +0.0660];
- Ctk − Ct (S) +0.0208 [−0.0243, +0.0660];
- Ctk − Cb (S) +0.0069 [−0.0313, +0.0486];
- Ctk − I (S) +0.2014 [+0.1493, +0.2535];
- the interaction +0.0243 [−0.0313, +0.0799].

The arm means match too (for example, Ctk S 0.2847, Cyk S 0.2604, T F 0.1840).

**Readings:** 0 of 4.

## Gemini (gemini.google.com/app/c6fcf6c5e4ac8e5e)
**Every mean matches exactly.** The intervals agree within bootstrap noise (its own draws):
- Ctk − Cyk (S) +0.0243 [−0.0139, +0.0625];
- Ctk − Ct (S) +0.0208 [−0.0243, +0.0660];
- Ctk − Cb (S) +0.0069 [−0.0313, +0.0451];
- Ctk − I (S) +0.2014 [+0.1493, +0.2535];
- the interaction +0.0243 [−0.0313, +0.0799].

**Readings:** 0 of 4.

## Verdict
Both recomputes match the frozen analysis.
