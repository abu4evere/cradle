# C2-S: copy who succeeds. Can the child learn whom to copy? (frozen plan)

**Frozen** as git tag `C2S-frozen`, before any code or data.
- **Sign-off:**
  - the creator chose this rung (13 November 2026, "Copy who succeeds");
  - their standing instruction (10 November 2026): "do not ask me go ahead bro".
- **Draft:** `docs/C2S_draft_2026-11-13.md`.
- **Council 8:** `docs/council_8_C2S_2026-11-13.md` (GPT, Gemini and DeepSeek, two rounds; all changes below are
  theirs unless said).

## The task (C2's toy boxes)
- 6 kinds of box, each with its own look (16 numbers, drawn per seed; each sight adds noise sd 0.2).
- Each opens only by its own ordered pair of acts from 4 (16 pairs).
- 6 tries a day, one per kind, in a random order.
- 60 days: demonstrations on days 1–30, none on days 31–60 (retention).

## Two demonstrators (days 1–30, before each try, on a box of the same kind)
**Who:** an equal-chance draw per try.
- **Ann:** always shows the right pair, and it opens.
- **Ben, a consistently wrong model:** each kind has his own fixed wrong pair, drawn per seed and different from the
  right one. He shows it with probability 0.8 (it stays shut), and the right pair with 0.2 (it opens).

**Hidden results:** with probability 0.5 the child sees who and the acts, but not whether the box opened. In the "100"
arms, every result is hidden.

**The fixed draws:** all of these are fixed per seed and day, and the same in every arm:
- who demonstrates;
- Ben's right draw;
- the hidden draw;
- the coins for Cy and Cpx (below).

## The child (C2's network)
- **Input (33):**
  - look 16;
  - who 2 (Ann, Ben; one-hot; recognising people is taken as inborn);
  - the demonstrated first and second acts, 4 + 4;
  - result seen 1;
  - opened 1 (0 when hidden);
  - its own first act 4;
  - step 1.

  With no demonstration, all the demonstration inputs are zeros. **The demonstration stays in view during the child's
  try:** that is what watching means here.
- **Network:** 33 → 32 tanh → 4 act scores; softmax.
- **Learning:**
  - REINFORCE on its own tries: reward 1 or 0, baseline rate 0.01, learning rate 0.05 (C2's);
  - **the copy step:** one cross-entropy step toward the demonstrated acts (first act, then second given the first), at
    learning rate 0.05 × 0.5 × **w**, where w is the arm's copy weight below.

## Copy weights (trust starts at 0.5 for each person; rate 0.3)
**Normalised trust:** n(p) = trust(p) / max(trust(Ann), trust(Ben), 0.25).
- **Cb, Ca and Cb100:** w = 1.
- **Co:** w = 1 if the child saw the box open, else 0.
- **Ct (trust from seen results):**
  - w = n(demonstrator), taken **before** this demonstration's result;
  - then, if the result is seen, trust(demonstrator) += 0.3 · (opened − trust(demonstrator)).
  - Ct's trust depends only on the demonstration stream, not on the child.
- **Cy (the yoked control):** w = Ct's current n(p) for a person p chosen by a fair coin (fixed draws), not for the
  demonstrator. The slot, the time and the box kind are the same as Ct's; only the link to who demonstrated is cut.
- **Cp (trust from the child's own experience):**
  - w = n(demonstrator);
  - after the child's own try on that box, **only if the try used the demonstrated pair**, trust(demonstrator) +=
    0.3 · (reward − trust(demonstrator)).
  - Seen results are not used.
- **Cpx (the credit control):** as Cp, but the trust update goes to a person chosen by a fair coin (fixed draws),
  not to the demonstrator.
- **Cp100:** as Cp, with every result hidden.

## Arms (48 children each, seeds 1–48, paired: the same boxes, habits, demonstrators, draws and days)
| arm | demonstrations | copy |
|---|---|---|
| **T** | none | none |
| **I** | Ann and Ben, half hidden | none (watches only) |
| **Cb** | Ann and Ben, half hidden | blind (w = 1) |
| **Co** | Ann and Ben, half hidden | only seen-open |
| **Ct** | Ann and Ben, half hidden | trust from seen results |
| **Cy** | Ann and Ben, half hidden | Ct's weights, yoked to a coin |
| **Cp** | Ann and Ben, half hidden | trust from own experience |
| **Cpx** | Ann and Ben, half hidden | own-experience trust, credited to a coin |
| **Ca** | **Ann only** (the same draws; Ann every time), half hidden | blind |
| **Cb100** | Ann and Ben, **all hidden** | blind |
| **Cp100** | Ann and Ben, **all hidden** | trust from own experience |

## Tests (learning off; the child's best acts; no demonstration shown; C2's)
- **When:** the end of days 1, 2, 3, 5, 7, 10, 15, 30, 45, 60.
- **Success rate:** the share of the 6 kinds opened. Novel boxes are as C2's.

## Readings (exploratory)
**Statistics:**
- early learning = the mean success at days 1, 2, 3, 5, 7;
- differences are paired by seed;
- 95% bootstrap intervals over the 48 seeds (10,000 draws, `numpy.random.default_rng(20261113)`, percentiles 2.5 and
  97.5);
- n = 48 children per arm beside every measure, and effect sizes reported.

**The readings:**
1. **"A consistently wrong model harms blind copying":** Ca − Cb has a lower bound above 0. If not, it reads "not
   shown" (Ben's right demonstrations may teach the method).
2. **"Copying only what was seen to work helps":** Co − Cb has a lower bound above 0.
3. **"Trust from seen results helps, beyond the amount of copying":** Ct − Cy has a lower bound above 0. Ct − Co is
   reported.
4. **"Trust from own experience helps":** both of:
   - Cp − Cb has a lower bound above 0;
   - Cp − Cpx has a lower bound above 0 (the person matters, not just the update).
5. **"…even with every result hidden":** Cp100 − Cb100 has a lower bound above 0.

**Not at ceiling:** if T's early learning is 0.90 or more, no reading is drawn.

**Descriptive:**
- **Adopting Ben's habit:** the share of tries on days 1–30 that use Ben's wrong pair for that kind, per arm, against T.
- **Copy fidelity:** the share of tries matching the demonstrated pair, after Ann's against after Ben's
  demonstrations.
- Success on tries after hidden against seen demonstrations.
- Trust in Ann and Ben at the end of each day (Ct, Cp, Cpx, Cp100).
- Copy weights by demonstrator and kind (Ct, Cy, Cp).
- The number of Ben's right demonstrations.
- Retention at day 60, and the novel boxes.

## Validity (hard stops)
**Code checks:**
- Ben's habits differ from the right pairs;
- T never sees a demonstration, and Ca only Ann's;
- hidden demonstrations carry no result bits, and the "100" arms are always hidden;
- the copy step only in the copying arms, with Co's weight 0 unless seen open;
- Ct's trust is the same for every child of a seed (independent of the child), and Cy's weights equal Ct's for the
  coin's person;
- Cp updates only when the try used the demonstrated pair;
- Cpx credits the coin's person;
- the act gradients equal finite differences;
- the same seed gives the same result twice.

**The blind recompute** by GPT and Gemini.

## The assistant's prior (after the council)
- Reading 1: about 75%.
- Reading 2: about 65%.
- Reading 3: about 45%.
- Reading 4: about 40%.
- Reading 5: about 35%.
