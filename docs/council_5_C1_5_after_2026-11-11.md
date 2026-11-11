# Council 5: C1.5 (word order), answers (11 November 2026, sleep mode)

Question: `docs/C1_5_draft_2026-11-11.md` with four open questions, the biggest risk, changes, and a probability.
Gemini was not asked: its tab kept reloading tonight (the same fault as councils 4 and 84).

## GPT (chat 6af41949, Thinking, medium)
- **View:** supports the rung, "but would not freeze it unchanged". The test must tell recognising familiar sentences
  from a rule that carries over to new requests.
- **Open questions:**
  1. keep the three request kinds. Add "no" (stopping) only if the child can really stop an act;
  2. P is a fair rival. Also add a position-binding baseline (word embeddings concatenated in fixed slots), to test
     whether recurrence itself adds anything;
  3. hold out twins: "my strongest recommendation". Train on some object pairs, test on unseen pairings of known things;
  4. keep the correction frame unchanged across arms.
- **Biggest risk:** a shortcut, not order. For example "the first thing named is handed first", or "the last noun
  wins" in negation.
- **Changes:**
  - fix chance for the exact protocol (both-correct under random choice is 0.25, not 0.5);
  - score first and second hands separately;
  - test unseen pairings (primary) and unseen templates (exploratory);
  - negation as both "X, not Y" and "not X, Y";
  - a probe "Y after X" (same order of acts, different word order);
  - an equivalence margin for "P as good as Q".
- **Probability Q passes the draft's rule:** 65%. Also: P equivalent 35%; negation robust 40%; unseen pairings 55%.
- **Its caution:** passing shows order-sensitive behaviour, "not, by itself, compositional understanding".

## DeepSeek (chat 332b1938)
- **View:** the arm set is the right minimal one, and the twin pairs and Q− are necessary.
- **Open questions:**
  1. add "no" alone (stopping an act) as a prerequisite or control, so that stopping does not confound "not X";
  2. P is a fair rival; match capacity, report P − Q;
  3. hold out twins for the primary, and also report twins heard in life;
  4. keep correction, as secondary.
- **Biggest risk:** a false negative. With 16 children, the conjunction of two lower bounds is strict. A second risk:
  if twins are not matched on context and memory, B can use the context.
- **Changes:**
  - a power check, or more children;
  - match the twins;
  - report per-order and both-correct accuracy.
- **Probability:** 45%.

## Taken into the plan (the assistant's reading of both)
1. **Test probes are matched:** each twin pair is tested from the same saved state (same memory, history, parent and
   things in view), with learning off. B then cannot use the context.
2. **Primary on unseen pairings:** a set of object pairs is never requested in order in life. Unseen templates and "Y
   after X" are exploratory.
3. **Chance by the protocol;** first-hand, second-hand and both-correct accuracy all reported.
4. **Negation both ways** ("X, not Y" and "not X, Y"), so "the last noun" cannot pass.
5. **A fifth arm, K:** fixed-slot concatenation (the binding baseline).
6. **"P as good as Q":** an equivalence margin of 0.05, fixed before data.
7. **24 children per arm** (power), after a simulated power check on synthetic effects before the freeze.
8. **Stopping ("no" alone)** is left out of C1.5: the child has no ongoing act to stop yet. It is noted for C2.
9. **Correction** is unchanged, and secondary.

Probabilities: GPT 65%, DeepSeek 45%; the assistant 60% before, 55% after the stricter tests.
