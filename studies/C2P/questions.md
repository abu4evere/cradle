# C2-P: whom to copy when mistakes hurt (frozen plan)

**Frozen** as git tag `C2P-frozen`, before any code or data.
- **Sign-off:** the creator, 17 November 2026: "You can work on project yourself" (and the standing "do not ask me go
  ahead bro").
- **Draft:** `docs/C2P_draft_2026-11-17.md`.
- **Council:** `docs/C2P_council_2026-11-17.md` (GPT chat 6afce450; Gemini chat e55ab34c).

## The council, in short (taken unless said)
- **Both:**
  - calibrate the pain before freezing its level, on non-confirmatory seeds;
  - make the tests pain-free and identical in every arm;
  - measure pain per lid tried, not in total, so a child who stops trying cannot "win";
  - G is the fixed-budget reference for GS, since a broken box changes how much a child practises; tries taken are
    reported.
- **GPT:**
  - keep I;
  - report copying of the expert against the non-expert;
  - add the interaction **(Ctk − Cyk)GP − (Ctk − Cyk)G**, which tests whether pain raises the value of *choosing*
    rather than of copying less;
  - reading 1 is the only primary.
- **Gemini:**
  - add **Ch** (copy everyone at w = 0.5), so that a Ctk win cannot be just "copying at half strength";
  - the REINFORCE baseline must track the reward including pain. It does: C2-K3's running baseline is updated with
    the step's reward.
  - It would drop I; **not taken**, since I is cheap and GPT keeps it.

## The design: C2-K3's (WS's memory brain, boxes, demonstrators, showings, trust, level K2), with three conditions
| condition | in learning, what a wrong lid costs |
|---|---|
| **G** | the try ends (C2-K3's G) |
| **GP** | the try ends, and the reward at that lid is −p instead of 0 |
| **GS** | the try ends, and that kind's remaining tries that day are lost (a broken box) |

- **Arms:** T, I, Cb, Ch (new: w = 0.5 for everyone), Ctk, Cyk, Cok.
- **Children:** 48 per arm and condition, seeds 1–48.
- **Tests:** learning off, no pain, no broken boxes; C2-K3's test on days 1, 2, 3, 5, 7, 10, 15, 30, 45, 60.

## The pain level (chosen before the study; pilot seeds 1001–1024; arm Cb only)
- **Candidates,** strongest first: p = 1.0, 0.5, 0.25.
- **Chosen:** the first p where Cb's GP day-30 full-box success is at least half of Cb's G day-30 success on the same
  pilot seeds. Pain must leave learning possible.
- **If none qualifies, C2-P stops.** Saved in `pain.json`.

## Readings (day-30 full-box success; paired bootstrap over seeds, 10,000 draws, numpy seed 20261117; n = 48)
1. **PRIMARY:** (Ctk − Cb) in GP, lower bound above 0.
2. **Secondary, each with its interval:**
   - (Ctk − Cb) in GS;
   - (Ctk − Cb)GP − (Ctk − Cb)G;
   - **(Ctk − Cyk)GP − (Ctk − Cyk)G** (GPT);
   - Ctk − Ch in GP (Gemini);
   - **pain per lid tried** over days 1–30 in GP, Ctk − Cb, upper bound below 0.
3. **Guards:**
   - Cb's G day-30 success below 0.05 makes reading 1 not readable;
   - T's success in G at 0.90 or more means no reading.
- **Reported:**
  - day 60;
  - Cok − Cb;
  - tries taken in GS;
  - wrong-lid rates;
  - copy weight given to the expert and the non-expert;
  - Ctk's trust.

## Validity
- **Code checks before data:**
  - G reproduces C2-K3's G exactly for the same seed and arm;
  - GP's reward is −p only on a wrong lid in learning;
  - GS skips exactly that kind's remaining tries that day;
  - tests have no pain and no broken boxes;
  - Ch copies with w = 0.5;
  - the same seed twice is the same.
- **The blind recompute** by GPT and Gemini.

## The assistant's prior (after the council)
- A pain level qualifies: about 85%.
- Reading 1: about 55%.
- Ctk − Ch in GP: about 45%.
- (Ctk − Cyk) interaction: about 40%.
- Pain per lid lower for Ctk: about 60%.
