# C2-S blind recompute (13 November 2026)

- **The data:** `recompute/c2s_children_counts.csv`, the frozen builder's `c2s_children.csv` with each success rate
  times 6 (the number of boxes opened; exact integers, checked). It was pasted inline, and the paste was checked by
  checksum (476878458, 10,781 characters) in both chats.
- **The prompt:** `recompute/prompt.txt`, worded for counts.
- **Neither model saw** the analysis script or the results.

## GPT (chatgpt.com/c/6af776c4-f118-83e9-aab1-57c4cdb41019)
- **First answer:** every arm's early learning matches the analysis to 4 decimals except Cpx (0.1444 against
  0.1451), so Cp − Cpx was −0.0076 against −0.0083.
- **The cause:** GPT's own transcription. Asked to re-read the Cpx rows directly from the data (not given the
  expected number), it found its copy had dropped one count:
  - Cpx total 209 (not 208), Cp total 197;
  - Cp − Cpx −0.0083 [−0.0209, +0.0042] (it used NumPy with seed 20261113, the same draws as the analysis).
- **After the correction, every number matches:**
  - Ca − Cb +0.0403 [+0.0264, +0.0542];
  - Co − Cb −0.0160 [−0.0361, +0.0042];
  - Ct − Cy +0.0014 [−0.0146, +0.0174];
  - Cp − Cb −0.0021 [−0.0111, +0.0069];
  - Cp − Cpx −0.0083 [−0.0209, +0.0042];
  - Cp100 − Cb100 −0.0069 [−0.0208, +0.0069].
- **Readings:** 1 yes; 2–5 not shown.

## Gemini (gemini.google.com/app/5a26eb7acbe7ade6)
**Every arm's early learning matches the analysis exactly**, to 4 decimals:
- T 0.0847, I 0.0958, Cb 0.1389, Co 0.1229, Ct 0.1375, Cy 0.1361;
- Cp 0.1368, Cpx 0.1451, Ca 0.1792, Cb100 0.1486, Cp100 0.1417.

**Every difference matches**, with the intervals within bootstrap noise (its own random draws):
- Ca − Cb +0.0403 [+0.0264, +0.0542];
- Co − Cb −0.0160 [−0.0361, +0.0042];
- Ct − Cy +0.0014 [−0.0146, +0.0181];
- Cp − Cb −0.0021 [−0.0111, +0.0069];
- Cp − Cpx −0.0083 [−0.0215, +0.0042];
- Cp100 − Cb100 −0.0069 [−0.0208, +0.0069].

**Readings:** 1 yes; 2–5 not shown.

## Verdict
**Both recomputes match the frozen analysis**, the primary differences, the intervals and all five readings. GPT's one
disagreement was traced to its own transcription and corrected by its re-reading of the raw data.
