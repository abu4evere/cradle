# C2: learning how. Findings (12 November 2026)

**Status:** valid. The blind recompute by GPT and Gemini is in progress.
**Run:** c2-run 43347865943; 120 children (5 arms × 24 seeds); checks All: PASS; not at ceiling (T's early learning
0.10).

## The frozen readings
- **Watching the method helps?** **No.** I − E = −0.013 [−0.036, +0.011]. Seeing the demonstrated acts as part of its
  input did not help: the child never learned to use them.
- **Copying helps?** **Yes.** Ic − I = +0.090 [+0.057, +0.124] on early learning.
  - By day 60, the copying child opens 0.80 of the boxes, against I's 0.26 and T's 0.29.
- **Check (E − T):** +0.015 [−0.008, +0.039]. Seeing only the result does not help, as expected.

## What else
- **What it copied stays, and it keeps improving:** Ic's success rose from 0.57 at day 30 (the last demonstrations) to
  0.80 at day 60, on its own practice.
- **A demonstrator who is wrong a third of the time costs a lot** (Iw 0.60 at day 60, against Ic 0.80). But the child
  does not keep repeating the failed pairs: right after a failed demonstration, it repeats the failed pair in 0.069 of
  its next tries, against 0.062 by chance (T on the same tries).
  - The blind copy pulls it the wrong way, and its own failures pull it back.
- **The method does not carry to new-looking boxes** (Ic 0.21 at day 60, near T's 0.15). It learned "this box opens
  like this", not a method that goes with the shape of a problem.

## What it means (the assistant's reading)
1. **Seeing is not enough. The child must have a way to copy.** Information about how something was done sat in its
   input, but trial-and-error learning gives no reason to use it until it first succeeds by chance (about 16 tries per
   box). A copy step turns watching into learning at once. Real children are thought to have something like this:
   over-imitation.
2. **With C1-B, a clear picture:**
   - where the outcome shows what to do (routines), watching alone teaches, and copying adds nothing;
   - where the outcome hides how (methods), watching alone teaches nothing, and copying is what helps.
3. **Copying is blind, and own practice corrects it.** Selective copying, trusting reliable demonstrators, would need
   more: for example, copying only what was seen to work. That is a later rung.
4. **For the brain (Mind Lab):** a copy (imitation) channel is a brain part of its own, separate from reward learning.
   ACL's people have one (NB2's social learning), but there it copied the habit table, not the network. This copy
   step is the kind to bring.

**The assistant's prior:** watching helps 65% (no); copying helps 70% (yes); E − T 20% (no); Iw repeats failures
above chance 60% (no). GPT: 75%, 70%, selective 35%. Gemini: 70%, 75%, selective 30%.
