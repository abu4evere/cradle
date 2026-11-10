# C0-B findings: in a harder home, do brain size, growth and joint attention matter?

**Status: final.** The blind recompute (`recompute_c0b.md`) matches: GPT and Gemini agree on every number, reading and
validity check.

Every number is from `output/results.md` (analyse_c0b.py, written before the study's data) on cloud run 42879225829:
- level L1 (6 moments a day, look-alike spread 0.35), chosen by the difficulty check (`calibration.md`) on separate
  seeds;
- 10 arms × 16 children, seeds 1–16, 1,080 days;
- code checks All: PASS.

## The answer in one line
**Yes, all three matter, for how fast the child learns.**
- A bigger brain learns faster than a small one.
- A brain that grows late is as slow as the small one it started as.
- Without the parent's attention cue, learning is much slower.

By three years, most of them catch up.

## The numbers (n = 16 children per arm)
- **Valid:**
  - P learns (request 0.993);
  - E (0.211) and F (0.252) sit at chance;
  - A's novel word is at chance (0.248);
  - not at ceiling: A's request at day 30 is 0.450.
- **Reading 1, associates words in a hard home: yes.**
  - A − 0.25 = 0.735 [0.727, 0.743];
  - A − F = 0.733 [0.705, 0.758];
  - A's look-alike test is 0.927, and new instances 0.924.
- **Reading 2, uses correction: no.** −0.096 [−0.121, −0.071]. Hearing "no, that's the Y" makes the next choice worse,
  as in C0-A. This brain hears a sentence as a bag of words, so Y's name pulls toward Y.
- **Learning speed** (area under the request curve, days 3–90, / 87); each difference is paired:

  | comparison | difference | reading |
  |---|---|---|
  | small brain (d 8) − large (d 64), B − A | −0.141 [−0.167, −0.118] | **size matters** |
  | d 32 − d 64, H − A | −0.033 [−0.060, −0.005] | a little, still clear |
  | growing − fixed d 32, C − H | −0.123 [−0.147, −0.100] | **growing late is slower** |
  | growing − small, C − B | −0.015 [−0.029, −0.003] | the growing brain is no faster than the small one it starts as (if anything slower) |
  | no joint attention − A, D − A | −0.157 [−0.179, −0.134] | **joint attention matters** |
  | reward only − A, G − A | −0.262 [−0.283, −0.243] | association matters most |
  | perfect cues − A, P − A | +0.039 [+0.021, +0.057] | better cues help a little |
  | counting baseline − A, K − A | +0.205 [+0.185, +0.227] | see below |

- **Days to 0.80:**
  - A mostly 180 (90–360);
  - B, C and D mostly 360;
  - P mostly 180 or 90;
  - G, E and F never.
- **At day 1,080 most of them catch up:**
  - request: A 0.985, B 0.966, C 0.967, D 0.983;
  - but the look-alike test separates them: A 0.927 and H 0.921, against B 0.805 and C 0.803;
  - saying: A 0.881, B 0.760.

  The small and the growing brains keep a lasting gap on fine distinctions and on speaking.
- **The counting baseline (K)** is the fastest at asking (0.722, reaching 0.80 by day 60). It also gets look-alikes
  right (0.985). But it **fails on new instances (0.241)** and **on saying (0.079)**. It memorises the things it has
  seen and generalises to nothing new. The network child is slower, but it generalises: new instances 0.924.

## What it means (the assistant's reading, for the creator)
- **The brain matters.** In a home that is hard enough:
  - a bigger brain learns words faster, and tells look-alikes apart better for good;
  - a child who cannot follow the parent's gaze learns twice as slowly at first (days to 0.80: 360 against 180),
    though it catches up later;
  - learning only from reward ("you gave the right thing") is far too slow. Hearing and seeing together is the main
    engine.
- **"A growing brain" did not help.** It grew too late (days 360 and 720), when the words were mostly learned. So it
  was as slow as a small brain and kept its weak look-alike score. Human brains grow most before age 2. A growth
  schedule that starts earlier and is matched to what is learned is a question for later.
- **Correction still does not help,** because the child hears a sentence as a bag of words. Hearing "no, that's the cup"
  makes it pick the cup. **For the ladder, a child that understands "no" and word order needs a hearing that keeps
  order.** That is the first brain change C0 points to.
- **The assistant's prior:**
  - A associates words: 80% (yes);
  - not at ceiling: 75% (yes);
  - size matters: 45% (yes);
  - growth matters: 25% (yes, but harmful as built);
  - joint attention: 55% (yes);
  - reward only slower: 85% (yes).
- **Limits** (stated in the plan): one learning rate for every size; hearing as the mean of the words. The size effect
  is "with this learning rule".
