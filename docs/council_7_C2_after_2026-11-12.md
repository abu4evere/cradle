# Council 7: C2 (learning how), answers (12 November 2026)

Question: `docs/C2_draft_2026-11-12.md`, attached as a file. DeepSeek was not reached.

## GPT (chat 6af66c1e), labelled as GPT
- **Verdict:** "a strong next step", but it risks measuring short-term memory or supervised copying, not imitation.
- **Q1:** 2 acts of 16 is right for a first rung. Add a harder 3-act transfer test.
- **Q2:** the older sibling, for continuity with C1-B.
- **Q3:** yes, E sees the opening and the treat; only the method is hidden.
- **Biggest risk:**
  - copying the acts without a reusable method;
  - Ic gets an extra supervised signal, so Ic − I may just be more supervision;
  - Iw's "selective" copying may only come from successes being rewarded.
- **Changes:**
  - a retention probe after demonstrations stop;
  - novel boxes that reuse learned sequences;
  - matched exposure across arms;
  - Iw compared on matched box kinds against each sequence's spontaneous rate;
  - a fixed early window and a minimum effect size;
  - check that the act head can condition its second act on its first.
- **Probabilities:** I − E 75%; Ic − I 70%; selective 35%.

## Gemini (chat 84980e0f), labelled as Gemini
- **View:** strong. But I has only memory traces and REINFORCE, while Ic gets a supervised nudge.
- **Q1:** keep 16, but **30 days is too long**: with several tries a day, T and E reach the ceiling within a week.
  Read days 1–7, or the area under the curve over the first 10 days.
- **Q2:** the sibling.
- **Q3:** keep the result visible in E. Then E − T checks whether seeing the goal helps at all.
- **Biggest risk:** the ceiling, plus I has no gradient until it first succeeds by chance (about 16 tries).
- **Changes:**
  - the early window and an E − T check;
  - the memory window must keep the demonstrated acts while the child does its own first act (at least 3–4 slots,
    or demonstration acts kept apart);
  - REINFORCE with a baseline, so failed tries can unlearn blind copying in Iw.
- **Probabilities:**
  - I − E 45% on days 1–30, but 70% on days 1–7;
  - Ic − I 75%;
  - selective 30%.

## To take into the frozen plan (the assistant)
- the sibling as demonstrator;
- the result visible in E;
- E − T as a check;
- the primary window is days 1–7 (as the area under the curve);
- the memory window keeps the demonstrated acts apart from its own;
- the act head sees its own first act when choosing the second;
- REINFORCE with a running baseline (C1's);
- a retention probe (no demonstrations after day 30);
- novel boxes reusing learned sequences, and a 3-act transfer box (exploratory);
- Iw's selectivity against each sequence's spontaneous rate.
