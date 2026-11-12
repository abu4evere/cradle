# C1-B: independent blind recompute (11 November 2026)

- **Input:** `recompute/c1b_children.csv` (120 rows), built by `recompute/build_c1b_counts.py`. The builder and
  `recompute/prompt.txt` were committed before the data.
- **GPT** (Thinking, medium), chat `6af53047`: the files were attached and it ran code (its own seed). It matches
  every value and both readings:
  - early learning A 0.6844, Y− 0.5145, Yo 0.6821, Y 0.6822, Yi 0.6789;
  - Yi − Y −0.0032 [−0.0070, +0.0007];
  - Y − Yo +0.0001 [−0.0003, +0.0005];
  - Yo − Y− +0.1676;
  - day-720 Y − A −0.0123;
  - imitation helps **no**, hearing the feedback helps **no**.
- **Gemini** (chat `937e07d8`, everything in one attached text file): pending.
