# C2-E findings: experts and costly practice (final, 13 November 2026)

**Run:** c2e-run 43509652372.
- Valid: checks All: PASS, 864 of 864 children, T's day-30 success under full practice 0.184.
- Frozen analysis: `output/results.md`.
- Blind recompute: GPT and Gemini, matching (`recompute_c2e.md`).
- n = 48 children per condition.

## The frozen readings (day 30)
1. **PRIMARY. "Choosing the right expert per kind pays, beyond the amount of copying": no.** Scarce practice, Ctk −
   Cyk +0.024 [−0.014, +0.066]. The yoke matched the amount of copying almost exactly (copy weight 134.3 against
   134.1).
2. **"Who is good at what, not just who": no.** Ctk − Ct +0.021 [−0.024, +0.066].
3. **"Choosing beats copying everyone and only watching": no.**
   - It beats watching: Ctk − I +0.201 [+0.149, +0.254].
   - It does not beat copying everyone: Ctk − Cb +0.007 [−0.031, +0.049].
4. **"Scarcity raises the value of choosing": no.** +0.024 [−0.031, +0.080].

## Reported, no gate
- **Retention (day 60, scarce practice): the expert-per-kind child keeps more.**
  - Ctk − Cyk +0.063 [+0.021, +0.108];
  - Ctk − Ct +0.076 [+0.031, +0.125];
  - Ctk − Cb +0.024 [−0.021, +0.073] (not clearly).
  - Own-experience trust per kind beats per person: Cpk − Cp +0.063 [+0.017, +0.111].
- **Even the oracle (copy only the expert of each kind) does not beat copying everyone:**
  - Cok − Cb (full practice, day 30) −0.003;
  - Cok − Ctk (scarce) +0.010 [−0.031, +0.052].

  There is little room for choosing to win, in this task.
- **Manipulation checks:**
  - seen-result trust found the experts (expert 0.83, non-expert 0.26 per kind);
  - own-experience trust barely did with scarce practice (0.54 against 0.48; about 3.6 updates per child);
  - scarce practice cut own tries from 360 to 60, and the copies stayed at 180.

## What it means (the assistant's reading)
1. **For the second time, "copy everyone and practise" is as good as choosing whom to copy, by day 30.** This holds
   even when practice is scarce and the people are experts in different things.
   - The oracle shows why: copying only the right expert halves the copying, and the remaining good examples are worth
     no more than all examples plus the child's own practice.
   - In this world, a wrong copy costs little, because a right one quickly outweighs it.
2. **Choosing pays off later.** By day 60, after demonstrations stop, the child who copied the right expert for each
   kind remembers more than the yoked and per-person copiers. Knowing who is good at what seems to give more lasting
   learning, a sign for the "cumulative" side of Bob.
3. **The limit of these toy tasks:** a method is one ordered pair of acts, so bad copies are cheap to undo. Choosing
   should matter most when copies are costly to undo, or dangerous (a bad method that injures). It should also matter
   when methods build on each other, so a wrong step spoils what comes after: cumulative skills. That is a natural next
   rung.

**The assistant's prior was:** 55%, 60%, 45%, 50%. None came true at day 30.
