# C2: independent blind recompute (12 November 2026)

- **Input:** `recompute/c2_children.csv` (120 rows), built by `recompute/build_c2_counts.py`. The builder and
  `recompute/prompt.txt` were committed before the data.
- **GPT** (Thinking, medium), chat `6af66d76`: the files were attached and it ran code. It matches every value and both
  readings:
  - early learning T 0.0986, E 0.1139, I 0.1014, Ic 0.1917, Iw 0.1542;
  - I − E −0.0125 [−0.0361, +0.0097];
  - Ic − I +0.0903 [+0.0583, +0.1236];
  - E − T +0.0153;
  - day 60 Ic 0.7986;
  - watching helps **no**, copying helps **yes**.
- **Gemini** (chat `f2af9ea3`, everything in one attached text file): it ran code and **matches every value and both
  readings**: I − E −0.0125 [−0.0360, +0.0107]; Ic − I +0.0903 [+0.0573, +0.1228]; E − T +0.0153.

**Both match. C2 is final:** tag `C2-done`.
