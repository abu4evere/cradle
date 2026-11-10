# C0-B: independent blind recompute (10 November 2026)

- **Input:** `output/c0b_children.csv` (160 rows), built by `recompute/build_c0b_counts.py`. The builder and
  `recompute/prompt.txt` were committed before the study's data. The CSV was attached as a file.
- **Who** (each a fresh chat; neither saw the analysis script or any earlier result):
  - GPT (Thinking, medium), chat `6af3696c`: Python, 10,000 draws;
  - Gemini 3.6 Flash (High), chat `21a797e9ecbd6a69`: it ran code ("Show code"). The Pro model was not offered today.
- **Recorded only from their actual replies.**

| quantity | analyse_c0b.py | GPT | Gemini |
|---|---|---|---|
| A − 0.25 | 0.735 [0.727, 0.743] | 0.7354 [0.7271, 0.7427] | 0.7354 [0.7271, 0.7427] |
| A − F | 0.733 [0.705, 0.758] | 0.7333 [0.7063, 0.7583] | 0.7333 [0.7052, 0.7583] |
| repair with − without | −0.096 [−0.121, −0.071] | −0.0958 [−0.1208, −0.0708] | −0.0958 [−0.1208, −0.0708] |
| P − 0.25 | 0.743 (P 0.993) | 0.7427 [0.7354, 0.7479] | 0.7427 [0.7354, 0.7479] |
| E, F, A novel | 0.211, 0.252, 0.248 | 0.2115, 0.2521, 0.2479 | 0.2115, 0.2521, 0.2479 |
| speed A / B / H / C / D | 0.517 / 0.376 / 0.484 / 0.361 / 0.360 | 0.5173 / 0.3759 / 0.4843 / 0.3612 / 0.3599 | the same |
| speed P / G / E / F / K | 0.556 / 0.255 / 0.218 / 0.235 / 0.722 | 0.5562 / 0.2552 / 0.2180 / 0.2355 / 0.7222 | 0.5563 / 0.2552 / 0.2180 / 0.2355 / 0.7222 |
| B − A | −0.141 [−0.167, −0.118] | −0.1414 [−0.1666, −0.1180] | −0.1414 [−0.1668, −0.1177] |
| H − A | −0.033 [−0.060, −0.005] | −0.0330 [−0.0607, −0.0061] | −0.0330 [−0.0602, −0.0054] |
| C − H | −0.123 [−0.147, −0.100] | −0.1232 [−0.1472, −0.0997] | −0.1232 [−0.1470, −0.0995] |
| C − B | −0.015 [−0.029, −0.003] | −0.0148 [−0.0285, −0.0034] | −0.0148 [−0.0285, −0.0034] |
| D − A | −0.157 [−0.179, −0.134] | −0.1574 [−0.1788, −0.1348] | −0.1574 [−0.1786, −0.1342] |
| G − A | −0.262 [−0.283, −0.243] | −0.2621 [−0.2835, −0.2435] | −0.2621 [−0.2830, −0.2430] |
| K − A | +0.205 [+0.185, +0.227] | +0.2049 [0.1845, 0.2262] | +0.2049 [0.1848, 0.2272] |
| P − A | +0.039 [+0.021, +0.057] | +0.0389 [0.0208, 0.0567] | +0.0389 [0.0204, 0.0567] |
| A at day 30 | 0.450 | 0.4500 | 0.4500 |
| readings and validity | associates yes; all 8 differences are findings; informative; valid | the same | the same |

**All agree, to the last digit on every point value. C0-B is final.**
