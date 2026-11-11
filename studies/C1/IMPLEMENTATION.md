# C1: implementation readings (written before any data)

- **The looks** are C0-B's at level L1: family centres N(0, 1), members + N(0, 0.35²), instance offsets N(0, 0.5²),
  sighting noise 0.2. They come from the child's own seed stream, as in C0-B.
- **Routines:**
  - drawn once per seed (stream [seed, 11]);
  - each step's turn is the child's with chance ½, with at least one child turn per routine;
  - the 12-thing pool is drawn from the 30;
  - the noise (skip, swap, cut short) is drawn per routine run, and a run with any noise counts as "noisy".
- **A step's view:** the needed thing plus 2 or 3 others from the other 29, in a random order; each sighting is a daily
  instance (0–2) with fresh noise.
- **Speech:**
  - after a child turn: praise naming the needed thing if right, else "this one" naming it;
  - after a parent turn, with chance ½: a naming frame with the thing used;
  - the child hears it at the next step, and nothing at a day's first step;
  - C0-A's daily-life frames are used in tests too (the hearing is context here, not the measure);
  - frames with order words or routine names are dropped (none were found).
- **The brain:**
  - 32 tanh units;
  - the hearing is the mean of 16-number word embeddings (learned through the prediction loss);
  - the score of a thing is its look · M · h;
  - the initial numbers are N(0, 0.1²), from stream [seed, 4].
  - For P and W, the memory input is the look of the thing used at the previous step (P), or at the last 4 (W), zeros
    where there is none.
  - For R and S, it is the previous thing's look plus the recurrent state.
- **Learning, at every step:**
  - **Prediction:** the cross-entropy on the used thing, backpropagated through the present step and the 7 before it,
    from the stored states (truncated online backprop through time). The stored states were computed with the
    numbers of their own time.
  - **The act** (child turns only): REINFORCE with a running baseline, through this step only.
  - Both gradients are computed at the same numbers, summed, and **clipped to norm 1.0 before the step** (a safety
    reading for every arm alike, not in the plan's text). Learning rates are 0.05.
- **The day boundary:** the state and the memory inputs reset at each day's start.
- **Arm S:** each life day's routine steps are shuffled (stream [seed, 14, day]) before the noise. Its tests use the
  same unshuffled test days as every arm.
- **Tests:** 30 test days from stream [seed, 13, day, j]; learning frozen; greedy acts.
- **Honest notes:**
  - code tests ran on throwaway seeds 901 and 201–216, never committed and not looked at beyond running;
  - the repeatability check runs arm P on study seed 3 twice and compares the two runs, but prints nothing from them.
