"""C2-K2's difficulty check (questions.md, frozen): pilot seeds 1001-1024, arms Cb and T only, both conditions; the
first level (hardest first) at which Cb's G day-30 full-box success is in [0.15, 0.60] and T's day-30 success is below
0.85 in G and in U. Writes difficulty.json (level null if none qualifies).

  python studies/C2K2/pilot_c2k2.py
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import c2k2  # noqa: E402

PILOT = range(1001, 1025)
rows, chosen = [], None
for name in ("L1", "L2", "L3"):
    c2k2.set_level(name)
    m = {}
    for arm in ("Cb", "T"):
        for cond in ("G", "U"):
            m[f"{arm}_{cond}"] = float(np.mean([c2k2.run(arm, cond, s)["tests"][30]["success"] for s in PILOT]))
    ok = 0.15 <= m["Cb_G"] <= 0.60 and m["T_G"] < 0.85 and m["T_U"] < 0.85
    rows.append({"level": name, **m, "qualifies": ok})
    print(rows[-1], flush=True)
    if ok:
        chosen = name
        break
(HERE / "difficulty.json").write_text(json.dumps({"level": chosen, "pilot_seeds": [1001, 1024], "rows": rows}, indent=1))
print("chosen", chosen)
