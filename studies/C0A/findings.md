# C0-A findings: can a newborn neural child learn ten words by living with two AI parents?

**Status: final.** The blind recompute (`recompute_c0a.md`) matches: GPT and Gemini agree on every number, reading and
validity check.

Every number is from `output/results.md` (analyse_c0a.py, written before any data) on cloud run 42845179399:
- 11 arms × 16 children, seeds 1–16, 1,080 days (GL 4,320);
- the parents' sentences come from corpus job 42841768106;
- code checks All: PASS.

## The answer in one line
**Yes, it associates words. No, it does not use correction.** But the task turned out far too easy: every learning arm
is near perfect by day 90, the first test, so C0-A cannot tell the brains apart.

## The numbers (day 1,080; n = 16 children per arm)
- **Valid:**
  - all 176 files are present, with one scene stream per seed;
  - E's weights never change;
  - P learns (1.000);
  - the controls sit at chance: E request 0.236 [0.210, 0.265], F 0.266 [0.225, 0.309];
  - A's novel word is at chance: 0.219 [0.179, 0.260].
- **Reading 1, associates words: yes.**
  - A's request accuracy is 1.000 in all 16 children: A − 0.25 = 0.750 [0.750, 0.750].
  - A − F = 0.734 [0.691, 0.775].
  - New instances 0.987 [0.979, 0.993]; saying 0.998 [0.994, 1.000].
- **Reading 2, uses correction: no.** With correction minus without: −0.054 [−0.085, −0.029].
  - Hearing the parent's "no, that's the Y" makes the next choice slightly *worse*. This brain hears a sentence as a bag
    of words, so Y's name adds weight to Y. The plan expected "no" (prior 10%).
- **Secondary (no gate):**
  - B, C, H, D and P equal A within 0.001 (all at ceiling);
  - G (reward only) − A = −0.009 [−0.018, −0.002];
  - K (counting) − A = −0.056 [−0.088, −0.027]; K fails new instances (0.257) and saying (0.019).
- **Learning curves** (request accuracy, mean of 16):
  - A, B, C, D, H and P are at 0.99 or above from day 90;
  - G: 0.59 at day 90, 0.87 at 180, 0.96 at 270, 0.99 at 1,080;
  - GL stays at about 0.99 to day 4,320;
  - K: 0.92 → 0.94.
- **Exposure:** about 2,000–2,300 hearings of each name by day 1,080 (about 200 by day 90). Accuracy is 1.0 for
  every word.

## What it means (the assistant's reading, for the creator)
- **The working base works.** A small network that starts knowing no words learns to link ten heard names to the
  right things, in new sentences, new layouts and new instances. It does this without any language model inside, and
  the controls rule out tricks.
- **The world was too easy to test the brain.** Ten clean categories, many hearings and a learning step that is
  probably large mean that even the smallest brain (8 numbers) and the child with no joint attention are perfect by
  the first test. So the questions C0-A also asked are unanswered:
  - "is a bigger brain better";
  - "does a growing brain help";
  - "is joint attention needed".

  Only reward-only learning (G) is visibly slower, and counting (K) visibly worse.
- **The assistant's prior:**
  - A associates words: 85% (yes);
  - D associates words: 45% (yes);
  - B within 0.05 of A: 60% (yes);
  - A's saying beats E: 40% (yes);
  - uses correction: 10% (no);
  - G associates words at 3 years: 25% (yes: G's request accuracy is 0.991 at day 1,080);
  - K matches or beats A: 50% (no).
- **Known weakness:** some of the parents' sentences miss their moment's meaning (`IMPLEMENTATION.md`). The child hears
  sentences as bags of words, so this cannot have helped it.
- **Not decided here (for the creator):** a harder C0-A, with fewer hearings, more things and look-alike things, tested
  earlier (day 10, 30); or moving on to C1, the unlabelled turn-taking routine. Either needs a new frozen plan.
