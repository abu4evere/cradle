# C2-K3 blind recompute (14 November 2026)

**The data:** `recompute/c2k3_day30.txt` (the frozen builder's file), pasted inline. Checksum 826138037, 1,455
characters, matched in the page. Neither model saw the analysis or the results.

- **GPT** (chatgpt.com/c/6af7f047-0508-83ea-bdac-2c345636d9bf; its own seed 20261114):
  - every arm mean matches (for example, Ctk G 0.1111, Cyk G 0.0417, Cb G 0.1007, Cok G 0.0833, T U 0.0694);
  - Ctk − Cyk (G) +0.0694 [+0.0347, +0.1042];
  - Cok − Cb (G) −0.0174 [−0.0556, +0.0208];
  - Ctk − Cb (G) +0.0104 [−0.0208, +0.0417];
  - the interaction +0.0139 [−0.0417, +0.0660];
  - readings: 1 yes, 2–4 no.
- **Gemini** (gemini.google.com/app/9166ba478b41e5a3; its own seed 42):
  - every mean the same;
  - Ctk − Cyk (G) +0.0694 [+0.0347, +0.1042];
  - Cok − Cb (G) −0.0174 [−0.0556, +0.0243];
  - Ctk − Cb (G) +0.0104 [−0.0208, +0.0417];
  - the interaction +0.0139 [−0.0417, +0.0694];
  - readings: 1 yes, 2–4 no.

**Verdict:** both match the frozen analysis (the means exactly; the intervals within bootstrap noise).
