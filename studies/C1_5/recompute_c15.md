# C1.5: independent blind recompute (11 November 2026)

- **Input:** `recompute/c15_children.csv` (120 rows), built by `recompute/build_c15_counts.py`. The builder and the
  prompt were committed before the data. The CSV was pasted in full after the prompt.
- **GPT** (Thinking, medium), chat `6af42546`: it ran code with the same seed (20261111).
  - It matches the analysis **to the last digit**: Q − B −0.1521 [−0.1842, −0.1173]; Q − Q− −0.0781 [−0.1066,
    −0.0465]; K − B +0.0199 [−0.0014, +0.0390]; negation Q − B −0.1455 [−0.1673, −0.1218]; B plain 0.7069 [0.6736,
    0.7403].
  - Readings: order **not learned**, negation not learned.
  - **Its notes:**
    - Q is worse than its shuffled control even on plain requests, "a broader learning or representation failure";
    - K's negation (0.744 vs 0.194) is "descriptive, not proof of compositional negation";
    - **P cannot encode order at all:** the mean of (word + position) equals the mean of the words plus a term that
      depends only on the sentence's length. (The assistant checked this: it is true. P was a flawed arm by design;
      council 5's GPT hinted at it.)
- **Gemini** (chat `c090e5bc`, a fresh tab, the text pasted inline): it ran code.
  - Every mean matches to 4 decimals; the interval ends are within 0.001 (a different random draw). For example, Q −
    B lower bound −0.1839 (analysis −0.1842); negation Q − Q− lower bound −0.0921 (−0.0915).
  - The same readings: **not learned;** negation not learned; the guard passed (B plain lower bound 0.6722).

**Both match. C1.5 is final:** tag `C1_5-done`.
