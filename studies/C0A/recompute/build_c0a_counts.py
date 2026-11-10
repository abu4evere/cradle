"""C0-A blind recompute: the raw per-child numbers as one CSV for GPT and Gemini (they get this and prompt.txt only).

  python studies/C0A/recompute/build_c0a_counts.py OUT_DIR       (writes OUT_DIR/c0a_children.csv)
"""
import csv
import json
import sys
from pathlib import Path

ARMS = ["A", "B", "C", "H", "D", "P", "G", "E", "F", "K"]
MEASURES = ["request", "new", "novel", "saying", "repair_with", "repair_without"]

out = Path(sys.argv[1])
with open(out / "c0a_children.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["arm", "seed"] + MEASURES)
    for arm in ARMS:
        for s in range(1, 17):
            r = json.loads((out / f"{arm}_seed_{s}.json").read_text(encoding="utf-8"))["results"]["1080"]
            w.writerow([arm, s] + [r[m] for m in MEASURES])
print("wrote", out / "c0a_children.csv")
