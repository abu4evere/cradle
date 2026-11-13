"""C2 analysis (questions.md, C2-frozen). Written before any data.

  python studies/C2/analyse_c2.py OUT_DIR        (writes OUT_DIR/results.md and summary.json)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
ARMS = ["T", "E", "I", "Ic", "Iw"]
SEEDS = list(range(1, 25))
EARLY = ["1", "2", "3", "5", "7"]
DAYS = ["1", "2", "3", "5", "7", "10", "15", "30", "45", "60"]
IDX = np.random.default_rng(20261120).integers(0, len(SEEDS), (10_000, len(SEEDS)))


def ci(x):
    x = np.asarray(x, float)
    b = x[IDX].mean(1)
    return float(x.mean()), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


def f(c):
    return f"{c[0]:+.4f} [{c[1]:+.4f}, {c[2]:+.4f}]"


def main():
    out = Path(sys.argv[1])
    data, missing = {}, []
    for a in ARMS:
        for s in SEEDS:
            p = out / f"{a}_seed_{s}.json"
            if p.exists():
                data[(a, s)] = json.loads(p.read_text(encoding="utf-8"))
            else:
                missing.append(p.name)
    log = HERE / "checks.log"
    checks_ok = log.exists() and log.read_text(encoding="utf-8").strip().endswith("All: PASS")
    same_pairs = all(len({json.dumps(data[(a, s)]["pairs"]) for a in ARMS if (a, s) in data}) == 1 for s in SEEDS)
    valid = checks_ok and not missing and same_pairs
    L = ["# C2: learning how (results)", "", "Frozen as `C2-frozen`. c2.py, analyse_c2.py (written before data).", "",
         "## Validity", "", f"- Code checks (All: PASS): **{'yes' if checks_ok else 'NO'}**",
         f"- All {len(ARMS) * len(SEEDS)} runs present: **{'yes' if not missing else 'NO'}**",
         f"- The same boxes and pairs per seed in every arm: **{'yes' if same_pairs else 'NO'}**", ""]

    def succ(a, d, key="success"):
        return np.array([data[(a, s)]["tests"][d][key] for s in SEEDS], float)

    def early(a):
        return np.mean([succ(a, d) for d in EARLY], axis=0)
    if valid:
        ceiling = early("T").mean() >= 0.90
        L += [f"- Not at ceiling (T's early learning {early('T').mean():.3f} below 0.90): "
              f"**{'yes' if not ceiling else 'NO'}**", ""]
        valid = not ceiling
    L += [f"**{'Valid.' if valid else 'NOT VALID: no reading is drawn.'}**", ""]
    if not valid:
        (out / "results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
        print("\n".join(L))
        return
    ie, ci_ = ci(early("I") - early("E")), ci(early("Ic") - early("I"))
    et = ci(early("E") - early("T"))
    L += ["## Readings (frozen)", "",
          f"- **Watching the method helps** (I - E, early learning = mean success at days 1, 2, 3, 5, 7): {f(ie)} -> "
          f"**{'yes' if ie[1] > 0 else 'no'}**",
          f"- **Copying helps** (Ic - I): {f(ci_)} -> **{'yes' if ci_[1] > 0 else 'no'}**",
          f"- Check, seeing the result alone (E - T): {f(et)}", ""]
    L += ["## Success rate by day (mean over 24 children)", "", "| arm | " + " | ".join(DAYS) + " | early |",
          "|---|" + "---|" * (len(DAYS) + 1)]
    for a in ARMS:
        L.append(f"| {a} | " + " | ".join(f"{succ(a, d).mean():.3f}" for d in DAYS) + f" | {early(a).mean():.3f} |")
    L += ["", "## Retention and novel boxes", "",
          "| arm | day 30 (last with demonstrations) | day 60 (30 days without) | novel boxes day 30 | novel boxes day 60 |",
          "|---|---|---|---|---|"]
    for a in ARMS:
        L.append(f"| {a} | {succ(a, '30').mean():.3f} | {succ(a, '60').mean():.3f} | {succ(a, '30', 'novel').mean():.3f} | "
                 f"{succ(a, '60', 'novel').mean():.3f} |")
    # selective copying (Iw): repeats of the failed pair on wrong-demonstration tries, against T on the same tries
    def rep(a):
        vals = []
        for s in SEEDS:
            t = [x for x in data[(a, s)]["tries"] if x["wrong_demo"]]
            vals.append(np.mean([x["pair"] == x["wrong_pair"] for x in t]) if t else np.nan)
        return np.array(vals)
    iw_rep, t_rep = rep("Iw"), rep("T")
    L += ["", "## Selective copying (Iw, descriptive)", "",
          f"- After a failed demonstration, Iw repeats the failed pair in {np.nanmean(iw_rep):.3f} of its next tries; "
          f"T, on the same tries with no demonstration, picks that pair {np.nanmean(t_rep):.3f} of the time "
          f"(Iw - T {f(ci(iw_rep - t_rep))}).", ""]
    L += ["Rules (frozen): 'watching the method helps' if I - E has a lower bound above 0; 'copying helps' if Ic - I has "
          "a lower bound above 0 (paired by seed, 10,000 draws, seed 20261120); no reading if T's early learning is "
          "0.90 or more.", ""]
    (out / "results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps({"I_E": ie, "Ic_I": ci_, "E_T": et}, indent=1), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
