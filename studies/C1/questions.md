# C1: routines. Can the child take its turn in a day nobody labels? (frozen plan)

**Frozen** as git tag `C1-frozen`, before any code or data.
**Sign-off:**
- the creator, 10 November 2026: "can we also run cradle too";
- their standing instruction "do not ask me go ahead bro";
- earlier, by Telegram, "You can keep cradle go do not stop run both projects".

**The draft** is `docs/C1_draft_2026-11-10.md`, written by the Telegram session. **Council 4**
(`docs/council_4_C1_after_2026-11-10.md`): GPT 65%, DeepSeek 65%. Gemini's tab did not take the question; it will be
asked again, and its answer added as an opinion only.

**The rung:** C1 on the life ladder, ages 1–3. "It takes its turn in a routine no one labels, and anticipates the next
step." It is the first rung that needs **memory**: C0's child carries nothing from one moment to the next.

## The home
- **People:** C0-B's 30 things in 10 look-alike families (level L1 looks); the same two AI parents and C0-A's committed
  corpus.
- **Routines (per child, drawn once from its seed):**
  - 6 routines (waking, breakfast, dressing, going out, bath, bedtime), each an ordered chain of 3–5 steps;
  - each step needs one thing, and is the parent's turn or the child's turn (each with chance ½, and at least one
    child turn per routine);
  - the needed things come from a pool of 12 of the 30, so **the same thing appears in several routines**. What comes
    next therefore depends on which routine one is in, not just on the last thing.
- **A day:** 3–5 routines (equal chance) in a random order. Each routine is run step by step.
  - **Noise, per routine run:** with chance 0.1 a step is skipped; with 0.1 two neighbouring steps swap; with 0.1 it
    is cut short after a random step. At most one of these per run.
- **A step:**
  - 3 or 4 things are in view: the needed one plus others drawn from the other 29;
  - whose turn it is, is shown (a flag);
  - **before anyone acts, the child predicts which of the things in view the step will use** (the anticipation
    read-out).
  - **On the child's turn:** it hands one thing, or waits. The parent answers: the praise frame naming the thing if it
    was right; else the "this one" frame naming the needed thing.
  - **On the parent's turn:** the parent uses the thing and, with chance ½, comments with a naming frame.
  - What the child hears at a step is what was said after the previous step: **nobody names the coming step.**
  - No frame names a routine or uses an order word (then, next, after, before, first, last). A check on the corpus
    drops any frame that does.
- **Life:** 720 days, ages 1–3. The memory is reset at the start of each day (sleep), never at a routine's boundary,
  which the child does not see.

## The child (C0's way of seeing and hearing; arms differ only in memory)
- **Input each step:**
  - the heard sentence as the mean of learned word embeddings (d 16);
  - the turn flag;
  - the arm's memory input.
- **A hidden layer of 32 tanh units:** h.
- **The score of a thing in view:** look · M · h. The prediction is a softmax over the things in view. The act is a
  softmax over those things plus a learned "wait" score (on the parent's turn the right act is to wait).
- **Learning (council 4):**
  1. **next-step prediction:** after each step, cross-entropy on the thing actually used. It trains everything,
     through time for the recurrent arms (backprop over the last 8 steps). Learning rate 0.05.
  2. **the act:** REINFORCE with a running baseline (rate 0.01), with the parent's answer as the reward: 1 for the right
     thing on the child's turn, 0 otherwise. The routine merely continuing is never a reward. Learning rate 0.05.

  These rates are C0's; nothing is tuned.

| arm | memory input | memory |
|---|---|---|
| **N** | none | no state (the sham) |
| **P** | the look of the thing used at the previous step | one step |
| **W** | the looks of the things used at the last 4 steps | a window (council: GPT's W) |
| **R** | the previous thing's look, and its own hidden state fed back (recurrent; backprop over 8 steps) | learned |
| **S** | as R, but each day the order of steps within every routine is shuffled | the order control |

16 children per arm, seeds 1–16, paired: the same routines, days and draws in every arm.

## Tests
- **When:** days 7, 14, 30, 60, 90, 180, 360 and 720.
- **How:** learning frozen; 30 test days drawn from their own stream, the same in every arm. The child's own act is used
  (greedy), but the day runs on as usual.
- **Measured separately on clean steps and on noisy ones** (skipped, swapped, cut short; council 4):
  1. **taking its turn:** on the child's turns, the share where it hands the needed thing;
  2. **anticipating:** on all steps, the share where its top prediction is the needed thing.
- **Chance:** 1 over the things in view (anticipation), and 1 over the things in view plus 1 (the act), averaged over
  the trials. The **frequency baseline** is arm N itself.
- **In S,** anticipation is judged on order only, by R − S.

## Readings at day 720 (exploratory)
- **Statistics:** per-child accuracy; 95% bootstrap intervals over the 16 seeds (10,000 draws,
  `numpy.random.default_rng(20261112)`); differences paired by seed; n = 16 beside every measure.
- **"It keeps up"** needs all of these:
  - for at least one memory arm (P, W or R), both measures on clean steps are above chance (lower bound above chance);
  - its anticipation − N has a lower bound above 0;
  - R − S on anticipation has a lower bound above 0 (order matters).
- **"Memory is not enough":** a memory arm beats N on anticipation, but not on taking its turn.
- **"No improvement shown"** otherwise.
- **Which memory** (secondary, reported with intervals): R − P, W − P and R − W on anticipation.
- **Not at ceiling:** if N's clean anticipation at day 720 is 0.90 or more, the routines are too easy, and the memory
  readings are uninformative.

## Validity (hard stops)
- **No memory leak:** N's prediction cannot depend on anything before the present step (a code check).
- **The checks:**
  - the routines share things across routines;
  - no corpus frame names a routine or an order word;
  - the test days are identical across arms;
  - the gradients of both learning rules equal finite differences, through time for R;
  - the same seed gives the same result twice.
- **The blind recompute** by GPT and Gemini.

## The assistant's prior
- R or W keeps up: about 60%.
- N's anticipation above chance (from frequency alone): about 80%.
- R beats P on anticipation (routines share things): about 55%.
- "Memory is not enough": about 25%.
