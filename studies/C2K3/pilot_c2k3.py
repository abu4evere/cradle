"""C2-K3's difficulty check (questions.md, frozen): pilot seeds 1001-1024, arms Cb, Cok and T, both conditions; the first
level (K1 then K2) where max(Cb, Cok) in G at day 30 is in [0.15, 0.60] and T is below 0.85 in G and U. -> difficulty.json

  python studies/C2K3/pilot_c2k3.py
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import c2k3  # noqa: E402

rows, chosen = [], None
for name in ("K1", "K2"):
    c2k3.set_level(name)
    m = {}
    for arm in ("Cb", "Cok", "T"):
        for cond in ("G", "U"):
            m[f"{arm}_{cond}"] = float(np.mean([c2k3.run(arm, cond, s)["tests"][30]["success"] for s in range(1001, 1025)]))
    top = max(m["Cb_G"], m["Cok_G"])
    ok = 0.15 <= top <= 0.60 and m["T_G"] < 0.85 and m["T_U"] < 0.85
    rows.append({"level": name, **m, "decided_by": "Cok" if m["Cok_G"] > m["Cb_G"] else "Cb", "qualifies": ok})
    print(rows[-1], flush=True)
    if ok:
        chosen = name
        break
(HERE / "difficulty.json").write_text(json.dumps({"level": chosen, "rows": rows}, indent=1))
print("chosen", chosen)
