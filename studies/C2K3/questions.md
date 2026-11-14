# C2-K3: whom to copy when skills build on each other, with the memory brain (frozen plan)

**Frozen** as git tag `C2K3-frozen`, before any code or data.
- **Sign-off:** the creator agreed (13 November 2026, "ok go with your suggestion") to return to C2-K's question with
  the memory brain after Mind Lab. Then "keep working … keep it pushin" before sleeping. This is decided under the
  sleep-mode autonomy; estimate of a valid, informative study about 55%.
- **Draft:** `docs/C2K3_draft_2026-11-14.md`.

**Council 12** (opinions, not sign-off):
- **The chats:**
  - GPT: chatgpt.com/c/6af7ec2c-c66c-83e9-bb25-f140518bbac0;
  - DeepSeek: chat.deepseek.com/a/chat/s/d76a2f74-9063-4720-8e5f-f9a00380ff53;
  - Gemini: gemini.google.com/app/30c341bfa8784552.
- **Taken from all three:** the showing fed to memory carries **who showed it** (GPT: otherwise the child may replay
  Ben's wrong showing whatever trust says).
- **The split, resolved:**
  - DeepSeek wanted the showing's input scaled by the arm's weight (trust sets attention);
  - Gemini disagreed: keep perception unscaled and let w gate copying only (otherwise a cold-start trap, and perception
    engineered by trust).
  - **Taken: Gemini's.** Perception is the same in every watching arm. The who-tag lets the network *learn* to
    discount someone. w scales only the copy step.
- **The difficulty rule:**
  - GPT and Gemini: choosing by Cb alone may stop the very case where choosing rescues learning;
  - DeepSeek: use Cok only as a flag.
  - **Taken:** the level qualifies when Cb's or Cok's G day-30 success is in [0.15, 0.60] (the larger of the two),
    and T is below 0.85.
  - **The cost of this (Gemini's own point):** if Cok decides the level, reading 2 (Cok − Cb) is not independent of
    the selection. It is then reported as "selection-dependent". The primary (Ctk − Cyk) does not use Cok.
- **Not taken:** GPT's no-source-label control (the who-tag is the same in all arms; later).

## Design (C2-K's question and arms; WS's brain)
**The boxes:**
- 6 kinds, with L lids opened in order (each lid its own ordered pair of 4 acts);
- 3 tries per kind per day (18 a day), for 60 days.

**The experts, days 1–30, before each try:**
- **Who:** Ann or Ben, an equal-chance draw. Ann is the expert for kinds 0–2, and Ben for 3–5.
- **Per lid:** right with probability 0.85 on own kinds, 0.25 otherwise. Otherwise their own fixed wrong habit.
- **A showing stops at the demonstrator's first wrong lid.**
- **Half the results are hidden.**
- **The fixed draws:** all draws are fixed per seed and day.

**The child (WS's Bm):**
- **The network:** a learned recurrent state, 32 tanh units.
- **The showing:** fed as steps just before the try (each shown act, the lid, and **who**: 2 numbers; plus whether the
  result was seen and the lids opened / L when seen). It is not in view during the try.
- **The try:** steps of look, lid, own first act and step, on the same state.
- **Learning:** REINFORCE (reward 1/L per lid) through time; WS's arithmetic.

**The copy step:** before the try, cross-entropy toward every shown lid's pair (the first act forced to the shown one),
through the showing, at rate 0.05 × 0.5 × w.

**The weights w (C2-K's):**

| arm | w |
|---|---|
| T | no showings |
| I | sees the showing, w = 0 (no copy) |
| Cb | 1 |
| Ctk | per person-and-kind trust from seen results (o = lids opened / L; rate 0.3; t / max(t_Ann,k, t_Ben,k, 0.25)) |
| Cyk | Ctk's current weight for a coin-chosen person |
| Cok | 1 for the expert of the kind, else 0 |
| Cr | a fair coin, 1 or 0 |

**Conditions:**
- **G:** the child's wrong lid ends its try;
- **U:** every lid is tried.

**Children:** 48 per arm and condition, seeds 1–48.

## The difficulty level (chosen before the study; pilot seeds 1001–1024; arms Cb, Cok and T only)
- **Levels, hardest first:** K1 (3 lids) then K2 (2 lids), both with 3 tries per kind per day.
- **Chosen:** the first level where **max(Cb, Cok)** in G at day 30 is in [0.15, 0.60], and T is below 0.85 in G and U.
- **Otherwise stop.** Saved in `difficulty.json`.

## Tests (learning off; no showing; cumulative rules)
- **When:** days 1, 2, 3, 5, 7, 10, 15, 30, 45, 60.
- **Full-box success** and the **partial score**.

## Readings (day-30 full-box success; paired bootstrap, 10,000 draws, seed 20261113; n = 48)
1. **PRIMARY:** Ctk − Cyk (G) has a lower bound above 0.
2. Cok − Cb (G) has a lower bound above 0. It is selection-dependent if Cok decided the level.
3. Ctk − Cb (G) has a lower bound above 0.
4. (Cok − Cb)G − (Cok − Cb)U has a lower bound above 0.

**Guards:**
- **floor:** max(Cb, Cok) in G below 0.05 makes readings 1–3 not readable;
- **ceiling:** T in U at 0.90 or more means no reading.

**Reported:**
- day 60;
- the partial score;
- Cok − Cr;
- Ctk's trust;
- copies per lid.

## Validity
**Code checks:**
- C2-K's (lid pairs, habits, expertise rates, showings stop at the first wrong lid, weights per arm, G and U tries);
- WS's (the showing is never in the try input; gradients through time; the same seed twice);
- the who-tag is present in the showing steps.

**The blind recompute** by GPT and Gemini.

## The assistant's prior
- A level qualifies: about 75%.
- Reading 1: about 40%.
- Reading 2: about 55%.
- Reading 3: about 35%.
- Reading 4: about 45%.
