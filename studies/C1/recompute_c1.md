# C1: independent blind recompute (11 November 2026)

- **Input:** `output/c1_children.csv` (80 rows), built by `recompute/build_c1_counts.py`. The builder and
  `recompute/prompt.txt` were committed before the data existed. The CSV was attached as a file.
- **GPT** (Thinking, medium), chat `6af3fdd6`: Python, 10,000 draws.
  - It matches the analysis on every value and interval to the last digit: N 0.7670, P 0.8596, W 0.9054, R 0.9106 and
    S 0.7295 (clean anticipation); R − S +0.1811 [+0.1645, +0.1975]; R − W +0.0053 [−0.0008, +0.0116].
  - Reading: "it keeps up".
  - Its notes: "More complex memory is not necessarily better"; and the no-memory child is already well above chance, so
    the data do not show "human-like understanding or generalization beyond these routines".
- **Gemini** (3.6 Flash, High): **two attempts failed to read the attached file.**
  - The first tab would not take the text.
  - The second chat (`e2dae0c434f17ada`) ran code, then asked for the CSV to be pasted, and returned a script.
  - **Pending:** to be retried. Until Gemini matches, C1 is not final.
