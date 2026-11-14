# C2-K2: skills that build on each other, with a difficulty check first (frozen plan)

**Frozen** as git tag `C2K2-frozen`, before any code or data.
- **Sign-off:** the creator, 13 November 2026: "yes go ahead with the difficulty check first".
- **Draft:** `docs/C2K2_draft_2026-11-13.md`.
- **Council 11 (GPT, DeepSeek, Gemini; their answers are opinions, not sign-off):**
  - GPT: chatgpt.com/c/6af7ddb0-aa54-83ea-8a63-751c4f7bb5ba;
  - DeepSeek: chat.deepseek.com/a/chat/s/c8d341f3-bef6-401d-9f1e-08b5d42742d1;
  - Gemini: gemini.google.com/app/cf02b7d2b78eb0c8.

  All three call the rule fair (pilot seeds kept apart, only Cb and T seen). **Taken:**
  - **The band's top is lowered to 0.60:** 0.70 left little headroom (Gemini, GPT, DeepSeek).
  - **T must also pass:** T under 0.85 in both conditions, so a chosen level cannot trip the ceiling guard (DeepSeek,
    Gemini).
  - **Path dependence is reported:** in step-by-step teaching, how much is copied depends on how far a child gets (GPT,
    DeepSeek). The yoked controls (Cyk, Cr) keep C2-K's per-demonstration form. **Copies per lid, per arm, are reported
    as the check**, and this limit is stated.
  - **The pilot is reported apart from the study**, and comparisons are made within the chosen level only (GPT).
  - **Selecting on Cb's pilot score** may slightly inflate the contrasts against Cb (regression to the mean; Gemini).
    This is noted.

## What changes from C2-K (`studies/C2K/questions.md`; everything not named here is as there)
1. **Step-by-step teaching:**
   - **G:** the copy step for lid j happens just before the child attempts lid j, and only when it reaches lid j.
   - **U:** each lid is copied just before its attempt (every lid is attempted).
2. **The difficulty level, chosen before the study by this rule:**
   - **On the pilot:** pilot seeds 1001–1024 (never used in the study), running **only Cb and T** in both conditions.
   - **The levels, hardest first:**
     - L1: 3 lids, 1 try per kind per day;
     - L2: 2 lids, 1 try per kind per day;
     - L3: 2 lids, 3 tries per kind per day (each try is preceded by its own demonstration on days 1–30).
   - **The chosen level** is the first at which Cb's G day-30 full-box success is between **0.15 and 0.60**, **and**
     T's day-30 success is below **0.85** in both G and U.
   - **If none qualifies, C2-K2 stops** and is reported.
   - **The pilot's numbers** are saved in `difficulty.json` and reported.
3. **Study seeds 1–48**, at the chosen level.

## The arms, readings and guards (as C2-K)
- **Arms:** T, I, Cb, Ctk, Cyk, Cok, Cr × G, U × 48.
- **Readings (day-30 full-box success, paired bootstrap, 10,000 draws, seed 20261113):**
  1. **PRIMARY:** Ctk − Cyk (G) has a lower bound above 0.
  2. Cok − Cb (G) has a lower bound above 0.
  3. Ctk − Cb (G) has a lower bound above 0.
  4. (Cok − Cb)G − (Cok − Cb)U has a lower bound above 0.
- **Guards:**
  - **floor:** Cb (G) below 0.05 makes readings 1–3 not readable;
  - **ceiling:** T (U) at 0.90 or more means no reading.
- **Reported:**
  - Cok − Cr;
  - day 60;
  - the partial score;
  - Ctk's trust;
  - copies per lid per arm;
  - lids reached.

## Validity
- C2-K's code checks, plus:
  - the copy for lid j happens only when lid j is reached, just before it is attempted;
  - the difficulty rule is applied as written.
- **The blind recompute** by GPT and Gemini.

## The assistant's prior
- Reading 1: about 45%.
- Reading 2: about 55%.
- Reading 3: about 35%.
- Reading 4: about 50%.
- A level qualifies: about 85%.
