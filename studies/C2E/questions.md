# C2-E: experts and costly practice. When does choosing whom to copy pay? (frozen plan)

**Frozen** as git tag `C2E-frozen`, before any code or data.
- **Sign-off:** the creator, 13 November 2026: "yes go ahead with the next cradle rung" (after C2-S).
- **Draft:** `docs/C2E_draft_2026-11-13.md`.
- **Council 9:** `docs/council_9_C2E_2026-11-13.md` (GPT, Gemini, DeepSeek).

## The task (C2-S's boxes)
- 6 kinds of box, each opened only by its own ordered pair of 4 acts (16 pairs).
- 60 days: demonstrations on days 1–30, none on days 31–60.

## Experts (days 1–30)
**One demonstration per slot:** each day has 6 slots, one per kind, in a random order. Before each slot, Ann or Ben
demonstrates (an equal-chance draw).
- **Ann is the expert for kinds 0–2, and Ben for kinds 3–5.**
- **On their own kinds** they show the right pair with probability 0.85; **on the others**, 0.25. Otherwise each shows
  their own fixed wrong habit for that kind (each person has their own, drawn per seed, never the right pair).
- **Overall** both are right 55% of the time: only per-kind trust can tell them apart.

**Hidden results:** with probability 0.5 a result is hidden (the child sees who and the acts, not whether it opened).

**The fixed draws:** every draw (who, right or habit, hidden, the coin) is fixed per seed and day, the same in every
arm and both practice levels.

## Practice (the second factor; every arm is run at both levels)
- **Full (F):** an own try in every slot (6 a day), as C2-S.
- **Scarce (S):** an own try only in the slot of kind (d − 1) mod 6, so 1 a day and 5 per kind over days 1–30.
  - The demonstrations and copy steps still happen in all 6 slots (watching is cheap, doing is costly).
  - This also changes the ratio of copying to own correction. That is part of the manipulation (council: DeepSeek).
- **Days 31–60:** the same practice level, with no demonstrations.

## The child (C2-S's network and learning)
- **Input (33):** look 16, who 2, the demonstrated acts 4 + 4, result seen 1, opened 1, own first act 4, step 1.
- **Network:** 32 tanh units → 4 act scores.
- **Learning:**
  - REINFORCE on its own tries (rate 0.05, baseline rate 0.01);
  - the copy step at 0.05 × 0.5 × w after each demonstration.

## Copy weights (trust starts at 0.5; rate 0.3; floor 0.25)
- **Cb:** w = 1.
- **Ct (per person, from seen results; C2-S):**
  - w = t(p) / max(t(Ann), t(Ben), 0.25), taken before this result;
  - if seen, t(p) += 0.3 · (opened − t(p)).
- **Ctk (per person and kind, from seen results):** as Ct, with a separate t(p, k) for each kind k, and w = t(p, k) /
  max(t(Ann, k), t(Ben, k), 0.25).
- **Cyk (the yoked control):** w = Ctk's current weight for a coin-chosen person, for the same kind (fixed coins).
- **Cok (the oracle per kind):** w = 1 if p is the expert for kind k, else 0. A ceiling for choosing.
- **Cp and Cpk (own experience; exploratory):**
  - weights as Ct and Ctk, but trust is updated only after an own try that used the pair demonstrated in that slot:
    t += 0.3 · (reward − t), credited to that slot's demonstrator;
  - with scarce practice this happens at most once a day.
- **I** watches with no copy; **T** sees no demonstrations.

## Arms
9 arms (T, I, Cb, Ct, Ctk, Cyk, Cok, Cp, Cpk) × 2 practice levels (F, S) × 48 children (seeds 1–48). Paired: the
same boxes, habits and draws for a seed in every arm and level.

## Tests
- **When:** the end of days 1, 2, 3, 5, 7, 10, 15, 30, 45, 60.
- **How:** learning off, best acts, no demonstration.
- **Success:** the share of the 6 kinds opened.

## Readings (exploratory; n = 48 per condition)
**Statistics:** paired bootstrap over seeds (10,000 draws, `numpy.random.default_rng(20261113)`, percentiles 2.5 and
97.5).

**Primary (one, pre-registered):**
1. **"Choosing the right expert per kind pays, beyond the amount of copying":** at day 30 under scarce practice, Ctk −
   Cyk has a lower bound above 0.

**Secondary:**
2. **"Who is good at what, not just who":** Ctk − Ct (scarce, day 30) has a lower bound above 0.
3. **"Choosing beats both copying everyone and only watching":** under scarce practice at day 30, Ctk − Cb **and**
   Ctk − I both have lower bounds above 0.
4. **"Scarcity raises the value of choosing":** at day 30, (Ctk − Cb)scarce − (Ctk − Cb)full has a lower bound above 0.

**Reported with intervals, no gate:**
- the same contrasts at day 60 (retention) and in the early window (days 1, 2, 3, 5, 7);
- Cok − Ctk (the room left);
- Cp and Cpk against Cb (exploratory) with their update counts;
- **manipulation checks:**
  - Ctk's final trust in the expert against the non-expert per kind;
  - each arm's total copy weight and copy counts;
  - own-try counts.

**Not at ceiling:** if T's day-30 success under full practice is 0.90 or more, no reading is drawn.

## Validity (hard stops)
**Code checks:**
- expertise as specified: right-pair rates by expert and non-expert slot in the draws;
- each person's habits differ from the right pairs;
- scarce practice has own tries only on the cycling kind;
- hidden demonstrations carry no result bits;
- the weights per arm as defined (Ct and Ctk trust independent of the child; Cyk follows the coin; Cok follows
  expertise);
- Cp and Cpk update only after a try that used the shown pair;
- the act gradients equal finite differences;
- the same seed gives the same result twice.

**The blind recompute** by GPT and Gemini.

## The assistant's prior
- Reading 1 (primary): about 55%.
- Reading 2: about 60%.
- Reading 3: about 45%.
- Reading 4: about 50%.
