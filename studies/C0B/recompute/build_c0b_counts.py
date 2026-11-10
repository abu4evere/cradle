"""C0-B blind recompute: the raw per-child numbers as one CSV for GPT and Gemini (they get this and prompt.txt only).

  python studies/C0B/recompute/build_c0b_counts.py OUT_DIR       (writes OUT_DIR/c0b_children.csv)
"""
import csv
import json
import sys
from pathlib import Path

ARMS = ["A", "B", "C", "H", "D", "P", "G", "E", "F", "K"]
MEASURES = ["request", "new", "alike", "novel", "saying", "repair_with", "repair_without"]
EARLY = [3, 7, 14, 30, 60, 90]

out = Path(sys.argv[1])
with open(out / "c0b_children.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["arm", "seed"] + MEASURES + [f"request_day{d}" for d in EARLY])
    for arm in ARMS:
        for s in range(1, 17):
            res = json.loads((out / f"{arm}_seed_{s}.json").read_text(encoding="utf-8"))["results"]
            r = res["1080"]
            w.writerow([arm, s] + [r[m] for m in MEASURES] + [res[str(d)]["request"] for d in EARLY])
print("wrote", out / "c0b_children.csv")
