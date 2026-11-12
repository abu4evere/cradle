# Council 6: C1-B (a sibling), answers (11 November 2026)

Question: `docs/C1B_draft_2026-11-11.md`, attached as a file, with four questions. DeepSeek was not reached.

## GPT (chat 6af52e1f), labelled as GPT
- **Verdict:** "Good design," with three changes.
- **Q1:** Yi is a fair first approximation, but it is reward-gated copying. Update only on praised acts.
- **Q2:** Y− controls the number of own turns. Y − Y− then measures all the benefit of observation together.
- **Q3:** keep the older learning, and record its accuracy throughout.
- **Biggest risk:** the younger may learn from extra routine information (the sibling's steps in its window and its
  prediction learning), not from the sibling's behaviour.
- **Changes:**
  - **a "Y-object" control:** the same things seen, but no sibling act or praise;
  - a precise primary statistic (the equal-weighted mean of days 7, 14, 30, 60, 90);
  - a generalisation probe;
  - report the numbers of own and observed turns.
- **Probabilities:** watching helps 72%; imitation helps 58%; Y below A at day 720 65%.

## Gemini (chat 30e43a6b), labelled as Gemini
- **View:** "clean, well-isolated".
- **Q1:** fair as filtered behavioural cloning.
- **Q2:** Y− controls the number of own turns, but not sequence continuity. Hiding the sibling's turns leaves gaps in
  the younger's 4-item window ("aliasing"), so Y − Y− may measure "intact vs broken sequence".
- **Q3:** keep the older learning.
- **Biggest risk:** that aliasing, and the newborn's early mistakes polluting the older's window.
- **Changes:**
  - compare Y and Yi at day t with A at day t/2 (the same number of own turns);
  - **imitation at half the learning rate**, so that extra updates are not mistaken for social learning;
  - log the older's accuracy at days 7, 14, 30, 90.
- **Probabilities:** watching helps 78%; imitation helps 68%; Y below A at day 720 22%.

## Taken (the assistant)
- **A new arm Yo** (objects only): the younger sees the things used on the sibling's turns, keeping its window
  continuous, but hears nothing about them. It answers both GPT's and Gemini's main concern.
  - **Hearing the sibling's feedback** = Y − Yo.
  - **Imitation** = Yi − Y.
  - **Sequence continuity** = Yo − Y−.
- **Imitation at half the learning rate** (Gemini).
- **The older tested** at the younger's days 7, 14, 30, 90 (and later test days).
- **Turn counts reported.**
- **A turn-matched comparison with A** (descriptive).
- **The noisy-routine tests** stand as the generalisation probe.
