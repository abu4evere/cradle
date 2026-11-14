# C2-K: skills that build on each other. Does choosing whom to copy pay when a wrong step spoils the rest? (frozen plan)

**Frozen** as git tag `C2K-frozen`, before any code or data.
- **Sign-off:** the creator, 13 November 2026: "go ahead with the next cradle rung" (after C2-E).
- **Draft:** `docs/C2K_draft_2026-11-13.md`.
- **Council 10:** `docs/council_10_C2K_2026-11-13.md` (GPT, Gemini, DeepSeek).

## The task
- **6 kinds of box, each with 3 lids.** Each lid opens only by its own ordered pair of acts (4 acts, 16 pairs), drawn
  per seed; the 3 pairs of a box differ.
- **A try** works the lids in order; reward 1/3 per lid opened.
- 6 tries a day, one per kind; 60 days; demonstrations on days 1–30.

**Two conditions, the second factor:**
- **G (cumulative):** a wrong pair ends the try, so later lids are not tried.
- **U (flat):** every lid is tried whatever happened before.

## Experts (days 1–30, before each try)
- **Who demonstrates:** Ann or Ben, an equal-chance draw.
- **Expertise:** Ann is the expert for kinds 0–2, and Ben for 3–5.
- **Per lid:** the expert shows the right pair with probability 0.85; the non-expert, 0.25. Otherwise they show their
  own fixed wrong habit for that lid (never the right pair).
- **A demonstration stops at the demonstrator's first wrong lid,** in both conditions: the later lids are not shown.
- **The result is seen** with probability 0.5: how many lids the demonstrator opened. It is hidden otherwise.

**The fixed draws:** all draws are fixed per seed and day, the same in every arm and condition.

## The child (C2's network)
- **Input (36):**
  - look 16;
  - who 2;
  - **the demonstrated pair for the current lid** 4 + 4 (zeros if not shown);
  - result seen 1;
  - the lids the demonstrator opened, divided by 3 (0 if hidden);
  - the lid number 3;
  - its own first act on this lid 4;
  - step 1.
- **Network:** 32 tanh units → 4 act scores.
- **Learning:** REINFORCE per lid (reward 1/3 if opened), with C2's baseline and rate.
- **The copy step:** one cross-entropy step per shown lid toward its pair, at 0.05 × 0.5 × w.
  - **G:** lid 1 is copied before the try. Lids 2 and 3 are copied after the try, only if the child reached that lid.
  - **U:** every shown lid is copied before the try.

## Arms (48 children each, seeds 1–48; every arm in G and in U; paired)
| arm | w |
|---|---|
| T | no demonstrations |
| I | watches, no copy |
| Cb | 1 |
| Ctk | per person and kind trust from seen results: o = lids opened / 3; t += 0.3 (o − t); w = t / max(t(Ann,k), t(Ben,k), 0.25), taken before this result |
| Cyk | Ctk's current weight for a coin-chosen person (same kind) |
| Cok | oracle: 1 if the demonstrator is the expert of this kind, else 0 |
| Cr | volume control for Cok: 1 or 0 by a fair coin (fixed draws) |

## Tests
- **When:** days 1, 2, 3, 5, 7, 10, 15, 30, 45, 60.
- **How:** learning off, best acts, no demonstration, cumulative rules.
- **Success:** the share of the 6 kinds fully opened.
- **Partial score:** the mean lids opened / 3.

## Readings (exploratory; day-30 success; n = 48 per condition)
**Statistics:** paired bootstrap over seeds (10,000 draws, `numpy.random.default_rng(20261113)`, percentiles 2.5 and
97.5).
1. **PRIMARY:** "Choosing the right expert pays when skills build on each other": Ctk − Cyk (G) has a lower bound
   above 0.
2. "The oracle beats copying everyone": Cok − Cb (G) has a lower bound above 0.
3. "Learned choosing beats copying everyone": Ctk − Cb (G) has a lower bound above 0.
4. "The chain raises the value of choosing": (Cok − Cb)G − (Cok − Cb)U has a lower bound above 0.

**Guards:**
- **Floor:** if Cb's day-30 success in G is under 0.05, readings 1–3 read "not readable".
- **Ceiling:** no reading if T's day-30 success in U is 0.90 or more.

**Reported:**
- Cok − Cr (G) (the amount of copying);
- the same contrasts at day 60;
- the partial score;
- Ctk's final trust (expert against non-expert);
- copy counts by lid;
- the lids the child reached.

## Validity (hard stops)
**Code checks:**
- the lid pairs differ, and the habits are never right;
- the expertise rates per lid as specified;
- demonstrations stop at the first wrong lid;
- in G, a try stops at the first wrong lid, and lids 2–3 are copied only when reached;
- in U, every lid is tried;
- hidden results carry no result bits;
- weights per arm as defined;
- the gradients equal finite differences;
- the same seed gives the same result twice.

**The blind recompute** by GPT and Gemini.

## The assistant's prior
- Reading 1: about 40%.
- Reading 2: about 60%.
- Reading 3: about 35%.
- Reading 4: about 50%.
