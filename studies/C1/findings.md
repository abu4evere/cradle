# C1 findings: routines. Can the child take its turn in a day nobody labels?

**Status:** final. The blind recompute (`recompute_c1.md`): GPT and Gemini both match every number and the reading
(Gemini on its third attempt, with the data pasted inline).

Every number is from `output/results.md` (analyse_c1.py, written before any data) on cloud run 42958035264:
- 5 arms × 16 children, seeds 1–16, 720 days;
- code checks All: PASS, including the gradients through time.

## The answer in one line
**It keeps up, with memory.** A child that remembers the last few steps learns the household's routines, nobody naming
them, and takes its turn right about 9 times in 10. A child without memory manages about 3 in 4, from knowing which
things tend to be used at all.

## The numbers (day 720, clean routines; n = 16 per arm)
| child | anticipates the step | hands the right thing on its turn |
|---|---|---|
| N, no memory | 0.767 | 0.759 |
| P, the last step | 0.860 | 0.858 |
| W, the last 4 steps | 0.905 | 0.903 |
| R, recurrent memory | 0.911 | 0.909 |
| S, recurrent but raised on shuffled routines | 0.730 | 0.734 |

Chance: 0.29 (anticipation), 0.22 (turns).

- **Memory beats no memory on both measures,** in every memory arm:
  - P − N +0.093 [+0.076, +0.110];
  - W − N +0.138;
  - R − N +0.144 [+0.128, +0.161].

  Turns are the same: R − N +0.150.
- **Order is what it learns:** R − S +0.181 [+0.165, +0.197]. Raised on shuffled routines, the same brain is worse
  than one with no memory.
- **More memory helps, because routines share things:**
  - R − P +0.051 [+0.040, +0.062], and W − P +0.046;
  - **R − W +0.005 [−0.001, +0.012]:** a recurrent memory is no better than simply remembering the last 4 steps.
- **On noisy days** (a step skipped, swapped or cut short) everyone does worse: R 0.770, W 0.758, P 0.729 and N 0.687.
  Memory's edge shrinks there (R − N about +0.08).
- **Learning speed:**
  - R is ahead early: day 7 at 0.59 (W 0.54), day 30 at 0.74 (W 0.73);
  - W catches up by day 60;
  - N rises slowly (0.54 to 0.77), from frequency alone.
- **Not at ceiling:** N's clean anticipation is 0.767, below the 0.90 rule.

## What it means (the assistant's reading)
- **The second rung is climbed.** With memory, the child keeps up with an ordinary home's routines that nobody explains.
  Without memory it cannot. This is the first brain part C0 lacked, and ACL's NB2 lacked it too.
- **A short window is enough here,** because these routines are 3–5 steps long. A recurrent memory learns a little
  faster at first, but ends no better. Longer projects, like ACL's multi-week chains, will need to tell the two apart.
- **Surprises still hurt.** On days with a skipped or swapped step, accuracy drops by about 0.14, so the child has
  learned the usual order more than it understands it.
- **For the five projects:**
  - the window and recurrent memories go to the workbench (memory task) and are the memory candidates for ACL's next
    brain;
  - the scorecard's "holding a project" test will use them.
- **The assistant's prior:**
  - R or W keeps up: 60% (yes);
  - N above chance from frequency: 80% (yes);
  - R beats P: 55% (yes);
  - "memory is not enough": 25% (no).
- **Next rungs** (council 4):
  - C1-B, with a neural sibling (the creator's mix);
  - C1.5, word order, so "no" and "first … then" can be understood.
