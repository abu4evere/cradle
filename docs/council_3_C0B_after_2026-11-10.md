# Cradle council 3: C0-B, the answers (10 November 2026)

The question is in `council_3_C0B_question_2026-11-10.md`. Each model got it in a fresh chat. These are opinions, not
sign-off, and are recorded only from the actual replies.

## GPT (Thinking, medium; chat `6af364ae`): approve with changes, 65%
- **Several difficulty settings change at once,** so the ceiling may become a floor, mostly on the look-alike test.
- **A difficulty check before the study:**
  - pre-registered, on separate seeds, with only the main arm, the perfect-cue arm and the controls;
  - its criteria are fixed in advance (P learns clearly; A above chance and below ceiling at day 30), with a fallback
    set beforehand, "not whichever setting produces the largest architecture difference";
  - also check that the categories can be told apart at all (a nearest-centroid classifier on the looks).
- **Learning speed:** the area under the learning curve over days 3–90, by the trapezoid over real days. The draft's
  plain mean over-weights the early tests. Secondary: the days to 0.80, held at the next test (censored if never
  reached); day 1,080; look-alike accuracy.
- **What could hide size or growth:**
  - the mean-of-words hearing;
  - one learning rate for every size;
  - growth coming too late;
  - an attention flag that is too good.
- Keep a fixed-size arm matched to the growing brain's final size.
- **C0-B is the right rung, but C0 must not become an endless benchmark.** Go on to C1 after it, even if C0-B is
  partly unresolved.
- **By mechanism:** joint attention 55%, size 30%, growth 20%.
- "Don't make the child artificially struggle just to reveal differences between brains."

## Gemini (3.6 Flash, high; chat `5c11c4b634495ec9`): 85%
- **The ceiling breaks, but a floor over days 3–30 is a risk:** about 18 hearings of each name by day 90.
- **Its changes:**
  - members closer together (σ 0.20–0.25);
  - 2 things in view for days 1–30;
  - word frequencies following Zipf's law.
- **Learning speed:** the area under the curve against log(1 + day), or the days to 80% from a fitted logistic.
- **What could hide size:**
  - a learning rate fixed across d;
  - dot-product scores that grow with d;
  - the mean of the words.
- **A C0-C (objects that persist and get hidden) before C1.**

## DeepSeek (chat `6cf3b36c`): 35–45% as drafted, 55–65% with fixes
- **A floor is likely:** 6 moments a day plus a σ of 0.35 is too tight.
- **Its changes:**
  - 10–12 moments a day;
  - a member spread of 0.55–0.65;
  - input noise rather than tighter geometry;
  - no curriculum.
- **Learning speed:** days to criterion as the primary, and the area under the whole curve as a secondary.
- **What could hide size or growth:**
  - the same learning rate for every size (scale it, or fix a rule in advance);
  - the mean-of-words hearing;
  - REINFORCE noise;
  - the growing arm needs a matched fixed arm (C0-A's H, d = 32, is that arm).
- **C0-B is the right rung but too aggressive.** Calibrate first, with P and the controls only.

## What the plan takes (the assistant)
- **A difficulty check before the study** (GPT, DeepSeek):
  - pre-registered, on separate seeds 101–104, arms A, P and E only;
  - a ladder of 4 levels fixed now, from hardest to easiest;
  - the hardest level that meets the criteria (P learns; A between floor and ceiling at day 30; E at chance) is used.

  This answers the conflict over closeness (Gemini closer, DeepSeek further apart) by a rule fixed in advance, not by
  the arm results.
- **Learning speed:** the area under the curve over real days (GPT), with the days to 0.80 as a secondary (DeepSeek,
  Gemini).
- **The feasibility check** of the looks (GPT): a nearest-centroid classifier.
- **Kept as C0-A's design, and stated as limits:**
  - one learning rate for every size;
  - the mean-of-words hearing;
  - dot-product scores.

  Changing them would change the child, not the home. They are named as the likely reason if size shows no effect.
- **Not taken:** Zipf frequencies, a curriculum of 2 things in view, and a C0-C rung. They are noted for the ladder.
