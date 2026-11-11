"""Builds the blind-recompute file for C1.5 from the children's files (written before data):
  c15_children.csv  one row per child (arm, seed 1-24): day-720 probe results

  python studies/C1_5/recompute/build_c15_counts.py OUT_DIR
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "output"
COLS = ["held_test_first", "held_test_second", "held_test_both", "held_test_neg", "held_test_neg_x", "plain"]
rows = ["arm,seed," + ",".join(COLS)]
for arm in ["B", "P", "K", "Q", "Q-"]:
    for s in range(1, 25):
        f = OUT / f"{arm.replace('-', 'm')}_seed_{s}.json"
        if not f.exists():
            continue
        r = json.loads(f.read_text(encoding="utf-8"))["results"]["720"]
        rows.append(f"{arm},{s}," + ",".join(repr(r[c]) for c in COLS))
(HERE / "c15_children.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
print(len(rows) - 1, "children")
