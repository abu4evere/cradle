# Cradle council 4: C1, routines, the answers (10 November 2026)

The question is in `council_4_C1_question_2026-11-10.md`. These are opinions, not sign-off, recorded only from the
actual replies. **Gemini:** its browser tab would not accept the question twice (the page did not respond); to be
retried.

## GPT (Thinking, medium; chat `6af3e7ca`): 65%
- **(a) Keep both measures.** Prediction shows what the child knows is coming; the act shows whether it can use that
  knowledge.
  - Test prediction after skipped and swapped steps.
  - Compare it with a simple transition-frequency baseline.
  - Train next-step prediction as its own objective, but judge it on held-out sequences.
- **(b) Use both the parent's response and the body's state, kept separate,** with prediction error as a dense signal.
  - Supervised next-step prediction, plus actor–critic for the act.
  - "Do not automatically reward the child merely because the routine continues", or doing nothing will look like
    success.
- **(c) Memory arms:**
  - N, P (previous step), R (a GRU of 16–32 units), S (shuffled), and **W (the last 4 steps) recommended**;
  - truncated backprop through time over **8 steps**;
  - **reset the memory at the start of each day, not at routine boundaries** (that would give away boundaries the
    child does not see);
  - the prediction loss must train the recurrent weights.
- **(d) Parent first;** a neural sibling in C1-B.
- **(e) Keep word order for a separate rung.**
- **(f) 65%.** The S control may not fall to chance, because what is in view can still give away the next step.
  - Measure chance from the real options and their frequencies.
  - Pre-register separate criteria for clean, skipped, swapped and cut-short days.

## DeepSeek (chat `018ca790`): 65%
- **(a) The act is the gate; prediction confirms.**
  - The no-memory child can sometimes predict from the present step alone, so test anticipation where the present step
    is ambiguous.
  - Judge S on anticipation, since turns can be reactive.
- **(b) "Routine continues" is the natural main reward, and praise a small extra.** The body's state alone will not
  teach social turn-taking. Next-step prediction is the main dense learning signal; actor–critic or REINFORCE with a
  baseline drives the act.
- **(c) Both memories, as separate arms:**
  - P = the last 2–3 steps; R = a small GRU;
  - backprop through time over one day (25 steps at most), truncated to 8–10 if unstable;
  - **no reset at routine boundaries;**
  - the act head learns by REINFORCE or actor–critic.
- **(d) No sibling in the main C1;** it goes in C2 or as an extra arm.
- **(e) Bag-of-words stays in C1;** word order goes in its own rung (C1.5).
- **(f) 65%;** P a little more likely than R. The main risk is "memory is not enough": anticipation improves but turns
  stay reactive.

## Where they agree (the assistant)
- **Both measures.** The act is the gate; prediction is the read-out, judged on held-out, skipped and swapped steps.
  Chance comes from the real frequencies.
- **Learning:** a next-step prediction loss trains the memory (the main dense signal); actor–critic drives the act; the
  parent's response is the act's reward, but "the routine simply continues" alone is not.
- **Memory arms:** N, P, R (a small GRU), S, and a window arm (GPT's W, the last 4 steps; DeepSeek's P of 2–3). Backprop
  through time over 8 steps. The state is reset each day, never at routine boundaries.
- **The parent first.** The sibling (the creator's mix) goes in the next rung, and word order in its own rung.
- **The S control is judged on anticipation.**
- **Both say 65%.**
