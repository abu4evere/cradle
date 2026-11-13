"""Builds the blind-recompute file for C2-E (written before data): one row per child (arm, practice, seed 1-48) with
the number of the 6 box kinds opened at the tests of days 1, 2, 3, 5, 7, 30 and 60.

  python studies/C2E/recompute/build_c2e_counts.py OUT_DIR
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
OUT = Path(sys.argv[1])
DAYS = ["1", "2", "3", "5", "7", "30", "60"]
rows = ["arm,practice,seed," + ",".join(f"opened_d{d}" for d in DAYS)]
for arm in ["T", "I", "Cb", "Ct", "Ctk", "Cyk", "Cok", "Cp", "Cpk"]:
    for p in ["F", "S"]:
        for s in range(1, 49):
            t = json.loads((OUT / f"{arm}_{p}_seed_{s}.json").read_text(encoding="utf-8"))["tests"]
            vals = []
            for d in DAYS:
                k = t[d]["success"] * 6
                assert abs(k - round(k)) < 1e-9
                vals.append(str(int(round(k))))
            rows.append(f"{arm},{p},{s}," + ",".join(vals))
(HERE / "c2e_children_counts.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
print(len(rows) - 1, "children")
