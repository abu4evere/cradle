# C0-A: independent blind recompute (10 November 2026)

- **Input:** `output/c0a_children.csv` (160 rows: 10 arms × 16 children, day 1,080), built by
  `recompute/build_c0a_counts.py`. Both the builder and `recompute/prompt.txt` were committed (b48b9da) before any
  data existed. The CSV was attached as a file.
- **Who** (each a fresh chat; neither saw the analysis script or any earlier result):
  - GPT (Thinking, medium), chat `6af339c2`: Python, 10,000 draws;
  - Gemini 3.1 Pro (High), chat `8ae33169225eb464`: it ran code ("Show code").
- **Recorded only from their actual replies.**

| quantity | analyse_c0a.py | GPT | Gemini |
|---|---|---|---|
| (1) A request − 0.25 | 0.750 [0.750, 0.750] | 0.7500 [0.7500, 0.7500] | 0.7500 [0.7500, 0.7500] |
| (2) A − F request | 0.734 [0.691, 0.775] | 0.7344 [0.6906, 0.7760] | 0.7344 [0.6885, 0.7760] |
| (3) A repair with − without | −0.054 [−0.085, −0.029] | −0.0542 [−0.0854, −0.0292] | −0.0542 [−0.0854, −0.0292] |
| (4) P request − 0.25 | 0.750 [0.750, 0.750] | 0.7500 [0.7500, 0.7500] | 0.7500 [0.7500, 0.7500] |
| E request | 0.236 [0.210, 0.265] | 0.2365 [0.2115, 0.2646] | 0.2365 [0.2104, 0.2646] |
| F request | 0.266 [0.225, 0.309] | 0.2656 [0.2240, 0.3094] | 0.2656 [0.2240, 0.3115] |
| A novel | 0.219 [0.179, 0.260] | 0.2188 [0.1792, 0.2604] | 0.2188 [0.1792, 0.2604] |
| readings | associates: yes; correction: no | the same | the same |
| validity (P learns; E, F at chance; A novel at chance) | all pass | all pass | all pass |

- **GPT's note:** the chance checks "establish that the results meet those bounds, not statistical equivalence to exact
  chance in a broader sense."

**All agree. C0-A is final.**
