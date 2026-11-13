# C2: learning how. Can the child learn a method by watching, when the result alone does not show it? (frozen plan)

**Frozen** as git tag `C2-frozen`, before any code or data.
**Sign-off:** the creator, 12 November 2026: "alr then keep working" (Cradle "all time").
**Draft:** `docs/C2_draft_2026-11-12.md`. **Council 7:** `docs/council_7_C2_after_2026-11-12.md` (GPT, Gemini); the
changes are taken.

## The task
- **6 kinds of toy box.** Each kind has its own look (16 numbers, drawn once per seed; each sight adds noise, sd 0.2).
  Each opens only by its own **ordered pair of acts** from 4 (press, pull, turn, shake): 16 possible pairs. Each kind's
  pair is drawn once per seed, no two kinds the same.
- **A day:** 6 tries, one per kind, in a random order. A try: the child picks a first act, then a second (seeing its
  own first act); the box opens (reward 1) or not (0).
- **Demonstrations (days 1–30, in the arms that have them):** before each try, the older sibling opens a box of the
  same kind with the right pair. In Iw, a third of them use a wrong pair, and the box stays shut.
- **Days 31–60:** no demonstrations (the retention probe).

## The child
- **Input:**
  - the box's look (16);
  - the demonstration as seen, kept apart from the child's own acts: the demonstrated first and second acts (4 + 4,
    one-hot; zeros if not seen) and whether the demonstrated box opened (1 number);
  - its own first act (4, one-hot; zeros when choosing the first act);
  - a step flag.
- **Network:** 30 inputs → 32 tanh → 4 act scores; softmax.
- **Learning:**
  - REINFORCE on its own tries (the reward 1 or 0), with a running baseline (C1's rule, rate 0.01), learning rate 0.05;
  - the copy step (Ic, Iw only): after each demonstration, one cross-entropy step toward the demonstrated acts (first
    act, then second given the first) at half the learning rate. It is blind: it copies failed demonstrations too.

## The arms (24 children each, seeds 1–24, paired: the same boxes, pairs, days and draws)
| arm | demonstration seen | copy step |
|---|---|---|
| **T** | none | no |
| **E** (emulation) | only that the box opened (the acts are zeros) | no |
| **I** (imitation) | the acts in order and that it opened | no |
| **Ic** | as I | yes |
| **Iw** | as Ic, but a third of demonstrations use a wrong pair (the child sees it fail) | yes |

## Tests (learning off; the child's best acts; no demonstration shown)
- **When:** the end of days 1, 2, 3, 5, 7, 10, 15, 30, 45, 60. Each test tries every kind once (and three novel boxes,
  below).
- **Success rate:** the share of the 6 kinds opened.
- **Novel boxes** (exploratory, GPT): three new looks that open with the pairs of kinds 1–3. They test the method
  carried to a new look; they are never shown in life.

## Readings (frozen)
- **Statistics:**
  - early learning = the mean success rate at the tests of days 1, 2, 3, 5, 7 (equal weights; Gemini's early window);
  - differences paired by seed;
  - 95% bootstrap intervals over the 24 seeds (10,000 draws, NumPy seed 20261120).
- **"Watching the method helps"** if I − E has a lower bound above 0.
- **"Copying helps"** if Ic − I has a lower bound above 0.
- **Check:** E − T (does seeing the result alone help?).
- **Retention:** the success rate at day 60 (after 30 days without demonstrations), every arm.
- **Selective copying (Iw, descriptive):**
  - after a failed demonstration, the share of the child's next tries that repeat the failed pair;
  - against the share of that pair in T's tries of the same kind on the same day (its spontaneous rate).
- **Not at ceiling:** if T's early learning is 0.90 or more, the task is too easy, and no reading is drawn.

## Validity (hard stops)
- **Code checks:**
  - the pairs differ across kinds;
  - E never sees acts and T never sees anything;
  - Iw's wrong demonstrations never open the box;
  - the act gradients equal finite differences;
  - the copy step only in Ic and Iw;
  - the same seed gives the same result twice.
- **The blind recompute** by GPT and Gemini.

## The assistant's prior
- Watching the method helps: about 65%.
- Copying helps: about 70%.
- E − T above 0: about 20% (seeing the result shows nothing about the pair).
- Iw repeats failed pairs above their spontaneous rate: about 60% (the copy is blind).
- GPT: 75%, 70%, selective 35%. Gemini (days 1–7): 70%, 75%, selective 30%.
