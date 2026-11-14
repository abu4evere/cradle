"""Builds the blind-recompute file for C2-K (written before data): for each arm and condition, the number of the 6
kinds fully opened at the day-30 test, for seeds 1-48 in order (one line each).

  python studies/C2K/recompute/build_c2k_counts.py OUT_DIR
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
OUT = Path(sys.argv[1])
lines = []
for arm in ["T", "I", "Cb", "Ctk", "Cyk", "Cok", "Cr"]:
    for c in ["G", "U"]:
        vals = []
        for s in range(1, 49):
            v = json.loads((OUT / f"{arm}_{c}_seed_{s}.json").read_text(encoding="utf-8"))["tests"]["30"]["success"] * 6
            assert abs(v - round(v)) < 1e-9
            vals.append(str(int(round(v))))
        lines.append(f"{arm} {c}: " + " ".join(vals))
(HERE / "c2k_day30.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(len(lines), "lines")
