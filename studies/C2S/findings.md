# C2-S findings: copy who succeeds (final, 13 November 2026)

**Run:** c2s-run 43503758272.
- Valid: checks All: PASS, 528 of 528 children, T's early learning 0.085.
- Frozen analysis: `output/results.md`.
- Blind recompute: GPT and Gemini, matching (`recompute_c2s.md`).
- n = 48 children per arm.

## The frozen readings (early learning = mean success at days 1, 2, 3, 5, 7)
1. **A consistently wrong model harms blind copying: yes.** Ca − Cb +0.040 [+0.026, +0.054] (effect size 0.80).
2. **Copying only what was seen to work helps: no.** Co − Cb −0.016 [−0.036, +0.004]. The filter throws away every
   hidden demonstration, Ann's included.
3. **Trust from seen results helps, beyond the amount of copying: no.** Ct − Cy +0.001 [−0.015, +0.017].
4. **Trust from own experience helps: no.**
   - Cp − Cb −0.002 [−0.011, +0.007];
   - Cp − Cpx −0.008 [−0.021, +0.004].
5. **…even with every result hidden: no.** Cp100 − Cb100 −0.007 [−0.021, +0.007].

## What the child did (descriptive, days 1–30)
- **Both trust mechanisms learned whom to trust:**
  - from seen results, Ann 1.00 against Ben 0.15 by day 15;
  - **from its own experience, Ann 0.99 against Ben 0.37 by day 30**, with every result hidden too (0.99 against 0.36);
  - the coin-credit control stayed level (0.70 / 0.71).
- **Blind copying picked up Ben's wrong habit a little:** Cb uses it 0.091 of the time, against T's spontaneous
  0.062 (+0.029 [+0.021, +0.036]). The selective children did not (Co −0.002, Ct +0.002, Cp +0.007, against T).
- **Ben's right demonstrations:** 16.8 of his 88.7 per child.

## Exploratory (after the data, labelled; not readings)
The frozen window (days 1–7) is early, while trust is still forming. At days 30 and 60, with the same bootstrap:
- **Choosing the right person matters, given selection:**
  - Ct − Cy +0.073 [+0.028, +0.115] at day 30, +0.080 [+0.028, +0.132] at day 60;
  - Cp − Cpx +0.094 [+0.042, +0.146] at day 60.
- **But selection does not beat copying everyone:**
  - Ct − Cb +0.007 (day 30), −0.035 (day 60);
  - Cp − Cb +0.003 (day 30), +0.038 [−0.017, +0.094] (day 60).
- **The outcome filter falls further behind:** Co − Cb −0.135 [−0.184, −0.083] at day 60.
- **A world without the bad model is far better:** Ca − Cb +0.247 [+0.194, +0.302] at day 60. Ca also gets twice as
  many good demonstrations (GPT's point), so this is the cost of a bad model *and* of fewer good examples.

## What it means (the assistant's reading)
1. **The child can learn whom to trust,** from what it sees work and, more interestingly, from its own results after
   copying, even when it never sees the results.
2. **Here, knowing whom to trust does not make it learn faster than copying everyone.** Own practice already corrects
   blind copies (as in C2). Turning down the bad model also turns down copying itself. The only real gain would come
   from *more* good demonstrations, which selection cannot create.
3. **Later on, the trusted person matters:** a child that trusts the right person beats one that trusts at random
   (Ct − Cy, Cp − Cpx). So the trust signal carries real value. It just does not beat the simple strategy of copying
   everyone and practising.
4. **For Bob:** in a world where your own practice gives fast, honest feedback, blind copying plus practice is hard to
   beat. Selective trust should matter more when practice is costly or slow, or when bad models are common and
   confident. That is a natural next rung: imperfect, varying models, and costly tries (GPT's harder follow-up).

**The assistant's prior was:** 75%, 65%, 45%, 40%, 35%. Reading 1 came true; 2–5 did not.
