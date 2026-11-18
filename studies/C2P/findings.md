# C2-P findings: whom to copy when mistakes hurt (17 November 2026)

**Plan:** `questions.md` (C2P-frozen; council: GPT and Gemini, `docs/C2P_council_2026-11-17.md`).
- **Checks:** All: PASS (7). G reproduces C2-K3's G exactly; the C2-K3 numbers reappear here, Ctk − Cyk (G) +0.069
  [+0.035, +0.104].
- **The pain level (frozen pilot):** **p = 1.0**, the strongest candidate. Cb in GP 0.167 against G 0.160 on the
  pilot seeds.
- **Run:** locally, 1,008 children (7 arms × 3 conditions × 48). Each child takes about a second.
- **The analysis:** `results.md`.
- **The blind recompute** (GPT and Gemini) is **pending.** Its input is `recompute/c2p_children.csv`, with the prompt
  `recompute/prompt.txt`.

## The frozen readings (day-30 full-box success)
| arm | G | GP | GS |
|---|---|---|---|
| T (no showings) | 0.042 | 0.076 | 0.010 |
| Cb (copy everyone) | 0.101 | **0.163** | 0.014 |
| Ch (copy everyone at half strength) | 0.031 | 0.035 | 0.010 |
| Ctk (copy by learned trust) | 0.111 | 0.132 | 0.014 |
| Cyk (matched copying, random person) | 0.042 | 0.087 | 0.010 |
| Cok (copy only the true expert) | 0.083 | 0.135 | 0.003 |

1. **PRIMARY, "when mistakes hurt, choosing beats copying everyone": no.** (Ctk − Cb) in GP −0.031 [−0.080, +0.014].
2. **Secondary:**
   - (Ctk − Cb) in GS: +0.000 [−0.017, +0.017]. Everyone is at the floor, so this is not informative.
   - (Ctk − Cb)GP − (Ctk − Cb)G: −0.042 [−0.097, +0.010]: no.
   - (Ctk − Cyk)GP − (Ctk − Cyk)G: −0.024 [−0.062, +0.017]: no. Pain does not raise the value of choosing.
   - **Ctk − Ch in GP: +0.097 [+0.049, +0.146]: yes.** Choosing beats copying everyone at half strength.
   - **Pain per lid tried, Ctk − Cb (GP): −0.014 [−0.024, −0.005]: yes.** Ctk hurts a little less per try.

**The priors:**
- a level qualifies, about 85%: yes;
- reading 1, about 55%: no;
- Ctk − Ch, about 45%: yes;
- the Cyk interaction, about 40%: no;
- pain per lid, about 60%: yes.

## What it means (the assistant's reading)
1. **For this brain, pain is not a cost: it is a teacher.**
   - A wrong lid's −1 tells the child exactly which move was wrong.
   - Every arm learns more with pain, even the child with no showings (T 0.042 → 0.076), and the child that copies
     everyone most of all (Cb 0.101 → 0.163).
   - So a wrong habit copied from Ben is quickly un-learned, and copying everyone stays as good as choosing.
   - This matches W3h: pain taught avoidance there too.
2. **Scarce chances (broken boxes) starve everyone:** about 700 of the 1,080 tries are lost, and learning collapses.
   That cost does not favour choosing, because no one learns enough.
3. **Choosing is still worth something:**
   - it beats copying at half strength (+0.097);
   - it beats copying a random person at the same amount (Ctk − Cyk +0.045 in GP);
   - and it costs less pain per try.

   But copying everyone, then correcting by experience, is as good, and with pain a little better.
4. **The open question, now sharper:** selective trust should win when wrong copies are costly *and cannot be
   corrected*: dangerous acts (death, not pain), or no feedback at all. That is the next rung if the creator wants it.
