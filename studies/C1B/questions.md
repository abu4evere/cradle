# C1-B: a sibling. Does a younger child learn from an older sibling? (frozen plan)

**Frozen** as git tag `C1B-frozen`, before any code or data.
**Sign-off:** the creator, 11 November 2026: "go ahead with c1-b sibling".
**Draft and council:** `docs/C1B_draft_2026-11-11.md`; council 6 (`docs/council_6_C1B_after_2026-11-11.md`, GPT and
Gemini). Their changes are taken.

## The home
- **C1's home:** the same 30 things, 6 routines over 12 shared things, noise, parents, corpus and day streams.
- **Two children:**
  - **The older** is C1's W child (window of the last 4 things used). It lives 360 days alone, exactly as in C1. Then
    the younger is born, and both live 720 more days. The older keeps learning by C1's rules.
  - **The younger** is a new W child, from its day 0.
- **Turns:**
  - each step that is the child's turn in C1 is given to one child by a fair coin. The coin is drawn from a separate
    stream (`[seed, 40, day]`), the same in every arm;
  - in arm A there is no sibling, so every child's turn is the younger's;
  - the older's own turns and learning follow C1's code.

## The arms (they differ only in what the younger receives from the sibling's turns)
| arm | sees the thing used on the sibling's turns (window + prediction learning) | hears the parent's answer to the sibling | imitates praised acts |
|---|---|---|---|
| **A** | (no sibling: all turns are its own) | – | – |
| **Y−** | no (the sibling's steps happen out of sight) | no | no |
| **Yo** | yes (as if the parent had used it) | no | no |
| **Y** | yes | yes | no |
| **Yi** | yes | yes | yes, at half the learning rate (0.025) |

- **Imitation (Yi):** when the parent praises the sibling, the younger takes one act-learning step toward the thing the
  sibling handed, as if it had handed it and been rewarded (C1's REINFORCE with reward 1 and the same baseline), at
  half the learning rate.
- **24 younger children per arm,** seeds 1–24, paired. The older sibling of seed s is the same child at its day 360 in
  every arm.

## Tests (C1's: the child alone, learning frozen, 30 test days)
- **The younger** at its days 7, 14, 30, 60, 90, 180, 360 and 720: clean and noisy turn-taking and anticipation.
- **The older** at the same moments (the younger's days), so its accuracy can be followed.
- **Turn counts:** the younger's own turns and observed sibling turns, per arm.

## Readings (frozen)
- **The primary statistic:** early learning = the equal-weighted mean of clean turn accuracy at days 7, 14, 30, 60
  and 90.
- **"Imitation helps"** if Yi − Y has a lower bound above 0.
- **"Hearing the sibling's feedback helps"** if Y − Yo has a lower bound above 0.
- **Also reported, with intervals:**
  - Yo − Y− (sequence continuity);
  - Y − Y− (all of watching);
  - day-720 levels against A;
  - a turn-matched comparison (Y and Yi at day t against A at day t/2, for t = 14, 60, 180, 360, 720; descriptive);
  - the older's accuracy before and after the younger's birth;
  - noisy-routine accuracy as the generalisation probe.
- **Statistics:** paired by seed; 95% bootstrap intervals over the 24 seeds (10,000 draws, NumPy seed 20261117).

## Validity (hard stops)
- **Code checks:**
  - in arm A the younger's life equals C1's W child exactly when the sibling is removed (same seed, same results);
  - the coin stream is the same in every arm;
  - Y− never sees or hears a sibling step; Yo sees the thing but hears nothing; Y hears the answer;
  - the imitation step equals C1's act gradient at half the rate;
  - the same seed gives the same result twice.
- **The blind recompute** by GPT and Gemini.

## The assistant's prior
- Imitation helps: about 55%.
- Hearing the feedback helps: about 40%.
- Yo − Y− above 0 (continuity): about 70%.
- Y below A at day 720: about 35%.
- GPT: watching 72%, imitation 58%, Y below A 65%. Gemini: 78%, 68%, 22%.
