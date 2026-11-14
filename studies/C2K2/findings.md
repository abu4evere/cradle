# C2-K2 findings: stopped by the frozen difficulty rule (13 November 2026)

**The difficulty check** (`pilot_c2k2.py`, pilot seeds 1001–1024, arms Cb and T only; `difficulty.json`):

| level | lids | tries per kind per day | Cb, G (day 30) | Cb, U | T, G | T, U | qualifies |
|---|---|---|---|---|---|---|---|
| L1 | 3 | 1 | 0.000 | 0.007 | 0.000 | 0.000 | no |
| L2 | 2 | 1 | 0.007 | 0.014 | 0.000 | 0.000 | no |
| L3 | 2 | 3 | 0.076 | 0.160 | 0.021 | 0.007 | no |

**The rule needed** Cb's G day-30 success in [0.15, 0.60]. **No level qualified, so C2-K2 stops,** as frozen. No study
seeds were run, and no question arm was seen.

## What it means (the assistant's reading)
- **Even with step-by-step teaching,** 2 lids and three tries a day, a child that copies everyone fully opens only
  about 8% of the boxes by day 30.
- **The bottleneck is the brain's speed of learning chained skills,** not the teaching. A small network learning from
  a few tries cannot yet build a two-step skill in a month, even when shown each step.
- **The question itself** (does choosing whom to copy pay when skills build on each other?) **must wait** for one of:
  - a brain that learns chained skills faster (more capacity, a memory, or a better copy step); this is Mind Lab work;
  - or a longer childhood (for example demonstrations over 90 days and tests at day 90), in a new frozen plan with its
    own difficulty check.

**The assistant's prior that a level would qualify was 85%.** It did not.
