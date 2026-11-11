# C1.5: word order. Findings (11 November 2026)

**Status:** final. The frozen reading is **not learned.** GPT and Gemini's blind recomputes both match
(`recompute_c15.md`).

- **Run:** c15-run 42982085632. 120 children (5 arms × 24 seeds), checks All: PASS, the same homes in every arm.
- **Plan:** `questions.md` (C1_5-frozen) with correction 1, made before any data.

## What was found (day 720, held-out pairs, test frames)
- **The guard held:** the bag child B learned the names (plain 0.707 [0.674, 0.740] against chance 0.20). So the
  test is informative.
- **Primary: no arm heard order.** First-act order accuracy: B 0.431, P 0.426, K 0.451, Q 0.279, Q− 0.357.
  - Q − B = −0.152 [−0.184, −0.117];
  - Q − Q− = −0.078 [−0.107, −0.047].
  - Every arm stays at or below ½ among the two named things.
- **The recurrent reader Q failed at the root:** it barely learned the names (plain 0.278; 0.236 at day 360). It is
  worse than its own shuffled control (Q− 0.468). Reading a 6–12-word sentence through 16 recurrent units, with C1's
  learning rate and no other help, did not learn in 720 days.
  - **Q's failure was not seen in the stub smoke.** There, one Q child reached plain 0.60 on four short hand-written
    frames. The real corpus's sentences are longer and more varied.
- **P (position added, then the mean) = B.** This was a design flaw (GPT's recompute note, checked): the mean of
  (word + position) is the mean of the words plus a term set by the sentence's length alone, so P could never hear
  order.

## The exploratory surprise: K, words in fixed slots, learned negation
- **K learned negation:** it handed the wanted thing 0.744 [0.735, 0.753] and the negated one 0.194. B can only split
  these 0.417 / 0.417.
  - It also did this on in-life pairs (0.759) and with life frames (0.770). So it is not memorised pairs.
- **But K did not learn order** (first act 0.451, about B's level).
- **K learned a position rule, not the meaning.**
  - On the "after" frames ("the Y after the X": hand X first), K's first act was right only 0.059. It handed Y, the
    thing named first in a frame shaped like "the Y, … not the X".
  - So K reads "which slot the wanted word sits in", and that happens to work for negation.
  - This is exactly the shortcut GPT warned of in council 5.
- **K also learned the names fastest** (plain 0.537 by day 180; B 0.289).

Because Q failed, the frozen "position is enough" rule (P or K within ±0.05 of Q) cannot fire. K's negation is
reported as exploratory only.

## What it means (the assistant's reading)
- **Hearing word order is not free.** A child that averages words cannot do it (by construction). A recurrent reader
  of this size, trained only by these two rules, did not learn even the words.
- **Fixed slots learn fast, but they learn positions:** good enough for "not the X, the Y", and fooled by "the Y
  after the X".
- **Next, for the council:**
  - a reader that learns: a larger or gated recurrent unit, a slower or separate learning rate for the reader, or
    first learning to predict the next word, as real toddlers hear far more speech than requests;
  - and a held-out frame-shape test, so that a slot rule cannot pass.
- **The assistant's prior was wrong:** "it hears order" about 55%: no; "position is enough" 35%: not met;
  "negation learned by Q" 40%: no. GPT 65% and DeepSeek 45% for Q.
