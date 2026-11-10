# C0-B: a harder home. Do brain size, growth and joint attention matter when words are hard? (frozen plan)

**Frozen** as git tag `C0B-frozen`, before any code or data.
**Sign-off:** the creator's standing instruction, 10 November 2026: "do not ask me go ahead bro" (recorded with NB2), after council 3 (`docs/council_3_C0B_after_2026-11-10.md`).

**Why:** C0-A (final, recomputed by GPT and Gemini) found the child associates words (A − F = 0.734 [0.691, 0.775]),
but every learning arm was at 0.99 or above by day 90, the first test. So the arm questions are unanswered: a small
against a large brain (B, H against A), a growing brain (C), no joint attention (D) and reward only (G). C0-B is the
same child and the same parents' sentences in a harder home, tested from the first days.
- **The rung:** C0 on the life ladder (`docs/life_ladder_draft_2026-11-10.md`).
- **What it measures:** learning speed, not just the end point. That is where children differ.

## What changes from C0-A (everything else is C0-A's frozen design and code)
1. **More things:** 30 categories instead of 10. Each name is one everyday word for a toddler's world, fixed here
   before any run. There are 10 families of 3, C0-A's ten included:
   - cup, mug, glass
   - spoon, fork, ladle
   - apple, orange, peach
   - banana, carrot, corn
   - bread, cookie, cracker
   - shoe, boot, sock
   - hat, cap, helmet
   - book, card, letter
   - duck, chicken, goose
   - ball, balloon, bubble

   **The sentences:** any corpus frame that holds one of the 30 names (or a plural) outside the slot is dropped, so
   that no name is heard except as a name. A check on the committed corpus finds 6 of 288 background frames to drop,
   and none elsewhere.
2. **Look-alikes:**
   - the 30 categories come in 10 families of 3;
   - a family's centre is drawn N(0, 1²) per number, and each member's centre is the family centre plus N(0, 0.35²);
   - so members of a family look alike (a cup, a mug, a glass).
3. **Fewer hearings:** a day has 6 moments, not 20 (level L1 below; the difficulty check may choose an easier level). Act shares are unchanged. So each name is heard about 10 times
   less often per day than in C0-A (a third of the moments, three times the things).
4. **In view:** 3 or 4 things (equal chance). The never-together pairs become 30 of the 435.
5. **Tests early and often:** days 3, 7, 14, 30, 60, 90, 180, 360, 720 and 1,080. Trials and kinds are as in C0-A.
   - **New: a "look-alike" request test**, 60 trials: the 4 things include the target's two family members. Chance
     0.25.
6. **Brain sizes:** as C0-A (8, 32, 64, and growing 8 → 16 → 32). Growth comes at days 360 and 720 (between tests).

The sentences are C0-A's committed corpus (the frames use {X}, so any name fits). The 30 names are slotted in. The
learning rates, sizes and rules are C0-A's, unchanged; nothing is tuned.

## The difficulty check, before the study (council 3: GPT, DeepSeek)
- **The ladder,** from hardest to easiest. Every level has 30 things and 3–4 in view:

  | level | moments a day | member spread σ |
  |---|---|---|
  | L1 | 6 | 0.35 |
  | L2 | 10 | 0.50 |
  | L3 | 14 | 0.65 |
  | L4 | 20 | 0.65 |

- **Run:** arms A, P and E only, seeds 101–104 (never used in the study), up to day 90.
- **The hardest level that meets all three criteria is used:**
  - P's mean request accuracy at day 90 is ≥ 0.60 (it is learnable);
  - A's mean request accuracy at day 30 is within [0.35, 0.90] (between floor and ceiling);
  - E's mean request accuracy at day 90 is within [0.17, 0.33].

  If none meets them, L4 is used, and this is reported. The choice reads only A, P and E, never an arm difference.
- **Feasibility of the looks** (GPT): a nearest-centroid classifier is given the true labels of the daily instances and
  classifies the kept-back instances (30 classes). Its accuracy is reported for the chosen level.

## Arms (16 children each, seeds 1–16, paired by scene stream)
A, B, C, H, D, P, G, E, F and K, as in C0-A. There is no GL.

## Outcomes and decision rule (exploratory)
- **Learning speed** (primary for the arm questions; council 3):
  - the area under the request-accuracy curve over days 3–90, by the trapezoid over the real test days, divided by 87;
  - per child.
- **Days to 0.80** (secondary): the first test day whose request accuracy is ≥ 0.80 and stays ≥ 0.80 at the next test.
  A child who never gets there is censored at 1,080 and reported as such.
- **The end point:** request accuracy at day 1,080.
- **Look-alikes:** look-alike accuracy at day 1,080.
- **Statistics:** as C0-A. Per-child accuracy; 95% intervals by bootstrap over the 16 seeds (10,000 draws,
  `numpy.random.default_rng(20261111)`); differences paired by seed; n = 16 beside every measure.
- **Readings:**
  1. **"Associates words in a hard home":** at day 1,080, A − 0.25 and A − F both have lower bounds above 0.
  2. **"Size matters"** (B − A, H − A), **"growth matters"** (C − H; C − B), **"joint attention matters"** (D − A) and
     **"association matters"** (G − A), on learning speed: an interval that excludes 0 is a finding. One that does not
     is "not shown".
- **Not at ceiling** (stated in advance): if A's request accuracy at day 30 is 0.95 or more, C0-B is still too easy,
  and its arm readings are reported as uninformative.

## Validity (hard stops, as C0-A)
- **P learns:** the lower bound of P − 0.25 at day 1,080 is above 0.
- **E and F at chance:** their request intervals lie within [0.17, 0.33].
- **A's novel word at chance:** its interval lies within [0.17, 0.33].
- **The code checks pass,** C0-A's plus: the 30 names and families; the look-alike trials hold the target's family; the
  scene stream is identical across arms.
- **The blind recompute** by GPT and Gemini.

## Limits, stated in advance (council 3)
- **These are C0-A's child, unchanged,** because C0-B changes the home, not the child:
  - one learning rate for every brain size;
  - hearing as the mean of the words;
  - dot-product scores.
- **If size or growth shows no effect,** these are the first suspects. A null result for size is "not shown with this
  learning rule", not "size does not matter".
- **The growing brain's matched fixed brain is H** (d = 32 from birth).

## The assistant's prior
- A associates words in the hard home: about 80%.
- A not at ceiling by day 30: about 75%.
- Size matters on learning speed (B or H against A): about 45%.
- Growth matters: about 25%.
- Joint attention matters (D slower than A): about 55%.
- Reward only is slower (G − A < 0): about 85%.
