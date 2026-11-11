"""C1 blind recompute: the raw per-child numbers as one CSV for GPT and Gemini (they get this and prompt.txt only).

  python studies/C1/recompute/build_c1_counts.py OUT_DIR       (writes OUT_DIR/c1_children.csv)
"""
import csv
import json
import sys
from pathlib import Path

ARMS = ["N", "P", "W", "R", "S"]
KEYS = ["ant_clean", "ant_noisy", "turn_clean", "turn_noisy", "chance_ant_clean", "chance_turn_clean"]
out = Path(sys.argv[1])
with open(out / "c1_children.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["arm", "seed"] + KEYS)
    for a in ARMS:
        for s in range(1, 17):
            r = json.loads((out / f"{a}_seed_{s}.json").read_text(encoding="utf-8"))["results"]["720"]
            w.writerow([a, s] + [r[k] for k in KEYS])
print("wrote", out / "c1_children.csv")
