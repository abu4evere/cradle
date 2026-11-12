"""Builds the blind-recompute file for C1-B (written before data): one row per younger child (arm, seed 1-24) with
clean turn accuracy at days 7, 14, 30, 60, 90 and 720.

  python studies/C1B/recompute/build_c1b_counts.py OUT_DIR
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
OUT = Path(sys.argv[1])
DAYS = ["7", "14", "30", "60", "90", "720"]
rows = ["arm,seed," + ",".join(f"turn_clean_d{d}" for d in DAYS)]
for arm in ["A", "Ym", "Yo", "Y", "Yi"]:
    for s in range(1, 25):
        r = json.loads((OUT / f"{arm}_seed_{s}.json").read_text(encoding="utf-8"))["younger"]
        rows.append(f"{arm},{s}," + ",".join(repr(r[d]["turn_clean"]) for d in DAYS))
(HERE / "c1b_children.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
print(len(rows) - 1, "children")
