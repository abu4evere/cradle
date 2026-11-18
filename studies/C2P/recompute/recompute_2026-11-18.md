# C2-P blind recompute (18 November 2026)

Both models got only the per-child CSV and the prompt (`prompt_compact.txt` with `c2p_children_compact.csv`; the compact
file was checked to equal the full one row for row: 0 mismatched rows). Labelled answers below; they are checks, not
sources.

## GPT (chatgpt.com, Instant, code): MATCHES
- All 21 means equal ours to 4 decimals (e.g. Ctk GP 0.1319, Cb GP 0.1632, Cb G 0.1007).
- a. Ctk − Cb (GP) −0.031 [−0.080, +0.017] (ours −0.031 [−0.080, +0.014]): no.
- b. Ctk − Cb (GS) 0.000 [−0.017, +0.017] (ours the same): no.
- c. (Ctk − Cb)GP − (Ctk − Cb)G −0.042 [−0.094, +0.010] (ours [−0.097, +0.010]): no.
- d. (Ctk − Cyk)GP − (Ctk − Cyk)G −0.024 [−0.063, +0.017] (ours [−0.062, +0.017]): no.
- e. Ctk − Ch (GP) +0.097 [+0.052, +0.146] (ours [+0.049, +0.146]): yes.
- f. pain per lid Ctk − Cb (GP) −0.0143 [−0.0241, −0.0046] (ours −0.014 [−0.024, −0.005]): yes.
- The means are exact. The intervals differ only in the third decimal, as different bootstrap draws must. All six
  decisions match.

## Gemini (gemini.google.com): does NOT match; not counted
- Its six decisions match ours, but its cell totals are wrong in several cells. For example, Ctk GP is 35 boxes in its
  answer against 38 in the file (0.1215 against 0.1319), and T G is 11 against 12. It showed no code.
- So it is not a valid independent recompute. The 16 November attempt had failed to send (the 35K file); this was the
  first one that arrived.

## Result
**The blind recompute confirms the frozen analysis** (GPT, exact means; all decisions). C2-P's findings are final.
