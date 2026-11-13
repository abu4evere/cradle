"""Builds the blind-recompute file for C2-S (written before data): one row per child (arm, seed 1-48) with its success
rate at the tests of days 1, 2, 3, 5, 7, 30 and 60.

  python studies/C2S/recompute/build_c2s_counts.py OUT_DIR
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
OUT = Path(sys.argv[1])
DAYS = ["1", "2", "3", "5", "7", "30", "60"]
ARMS = ["T", "I", "Cb", "Co", "Ct", "Cy", "Cp", "Cpx", "Ca", "Cb100", "Cp100"]
rows = ["arm,seed," + ",".join(f"success_d{d}" for d in DAYS)]
for arm in ARMS:
    for s in range(1, 49):
        t = json.loads((OUT / f"{arm}_seed_{s}.json").read_text(encoding="utf-8"))["tests"]
        rows.append(f"{arm},{s}," + ",".join(repr(t[d]["success"]) for d in DAYS))
(HERE / "c2s_children.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
print(len(rows) - 1, "children")
