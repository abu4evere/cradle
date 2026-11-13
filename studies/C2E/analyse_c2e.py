"""C2-E analysis (questions.md, C2E-frozen). Written before any data.

  python studies/C2E/analyse_c2e.py OUT_DIR        (writes OUT_DIR/results.md and summary.json)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
ARMS = ["T", "I", "Cb", "Ct", "Ctk", "Cyk", "Cok", "Cp", "Cpk"]
PR = ["F", "S"]
SEEDS = list(range(1, 49))
EARLY = ["1", "2", "3", "5", "7"]
DAYS = ["1", "2", "3", "5", "7", "10", "15", "30", "45", "60"]
IDX = np.random.default_rng(20261113).integers(0, len(SEEDS), (10_000, len(SEEDS)))


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
        for p in PR:
            for s in SEEDS:
                fp = out / f"{a}_{p}_seed_{s}.json"
                if fp.exists():
                    data[(a, p, s)] = json.loads(fp.read_text(encoding="utf-8"))
                else:
                    missing.append(fp.name)
    log = HERE / "checks.log"
    checks_ok = log.exists() and log.read_text(encoding="utf-8").strip().endswith("All: PASS")
    same = all(len({json.dumps([data[k]["pairs"], data[k]["habits"]]) for k in data if k[2] == s}) == 1 for s in SEEDS)
    valid = checks_ok and not missing and same
    L = ["# C2-E: experts and costly practice (results)", "",
         "Frozen as `C2E-frozen`. c2e.py, analyse_c2e.py (written before data).", "", "## Validity", "",
         f"- Code checks (All: PASS): **{'yes' if checks_ok else 'NO'}**",
         f"- All {len(ARMS) * len(PR) * len(SEEDS)} runs present: **{'yes' if not missing else 'NO'}**",
         f"- The same boxes, pairs and habits per seed everywhere: **{'yes' if same else 'NO'}**", ""]

    def succ(a, p, d):
        return np.array([data[(a, p, s)]["tests"][d]["success"] for s in SEEDS], float)

    def early(a, p):
        return np.mean([succ(a, p, d) for d in EARLY], axis=0)

    if valid:
        tf30 = succ("T", "F", "30").mean()
        ceiling = tf30 >= 0.90
        L += [f"- Not at ceiling (T's day-30 success under full practice {tf30:.3f} below 0.90): "
              f"**{'yes' if not ceiling else 'NO'}**", ""]
        valid = not ceiling
    L += [f"**{'Valid.' if valid else 'NOT VALID: no reading is drawn.'}**", ""]
    if not valid:
        (out / "results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
        print("\n".join(L))
        return

    def s30(a):
        return succ(a, "S", "30")
    r1 = ci(s30("Ctk") - s30("Cyk"))
    r2 = ci(s30("Ctk") - s30("Ct"))
    r3a, r3b = ci(s30("Ctk") - s30("Cb")), ci(s30("Ctk") - s30("I"))
    inter = ci((s30("Ctk") - s30("Cb")) - (succ("Ctk", "F", "30") - succ("Cb", "F", "30")))
    L += ["## Readings (frozen; day-30 success; n = 48 per condition)", "",
          f"1. **PRIMARY. Choosing the right expert per kind pays, beyond the amount of copying** (scarce, Ctk - Cyk): "
          f"{f(r1)} -> **{'yes' if r1[1] > 0 else 'no'}**",
          f"2. **Who is good at what, not just who** (scarce, Ctk - Ct): {f(r2)} -> **{'yes' if r2[1] > 0 else 'no'}**",
          f"3. **Choosing beats copying everyone and only watching** (scarce, Ctk - Cb {f(r3a)}; Ctk - I {f(r3b)}) -> "
          f"**{'yes' if (r3a[1] > 0 and r3b[1] > 0) else 'no'}**",
          f"4. **Scarcity raises the value of choosing** ((Ctk - Cb)S - (Ctk - Cb)F): {f(inter)} -> "
          f"**{'yes' if inter[1] > 0 else 'no'}**", ""]
    L += ["## The same contrasts at day 60 (retention) and early (days 1-7)", "",
          "| contrast | practice | day 60 | early |", "|---|---|---|---|"]
    for a, b in (("Ctk", "Cyk"), ("Ctk", "Ct"), ("Ctk", "Cb"), ("Ctk", "I"), ("Cok", "Ctk"), ("Cp", "Cb"),
                 ("Cpk", "Cb"), ("Cpk", "Cp")):
        for p in PR:
            L.append(f"| {a} - {b} | {p} | {f(ci(succ(a, p, '60') - succ(b, p, '60')))} | "
                     f"{f(ci(early(a, p) - early(b, p)))} |")
    L += ["", "## Day-30 contrasts under full practice", ""]
    for a, b in (("Ctk", "Cyk"), ("Ctk", "Ct"), ("Ctk", "Cb"), ("Cok", "Cb"), ("Cp", "Cb"), ("Cpk", "Cb")):
        L.append(f"- {a} - {b} (F): {f(ci(succ(a, 'F', '30') - succ(b, 'F', '30')))}")
    L += ["", "## Success by day (mean over 48 children)", "", "| arm | practice | " + " | ".join(DAYS) + " |",
          "|---|---|" + "---|" * len(DAYS)]
    for a in ARMS:
        for p in PR:
            L.append(f"| {a} | {p} | " + " | ".join(f"{succ(a, p, d).mean():.3f}" for d in DAYS) + " |")
    L += ["", "## Manipulation checks (means over 48 children)", "",
          "| arm | practice | copy weight sum | copies | own tries | trust updates (Cp, Cpk) |", "|---|---|---|---|---|---|"]
    for a in ARMS:
        for p in PR:
            ks = [(a, p, s) for s in SEEDS]
            L.append(f"| {a} | {p} | {np.mean([data[k]['copy_weight_sum'] for k in ks]):.1f} | "
                     f"{np.mean([data[k]['copies'] for k in ks]):.1f} | {np.mean([data[k]['own_tries'] for k in ks]):.1f} | "
                     f"{np.mean([data[k]['trust_updates'] for k in ks]):.1f} |")
    for a, key in (("Ctk", "ctk"), ("Cpk", "pk")):
        for p in PR:
            ex, nx = [], []
            for s in SEEDS:
                t = data[(a, p, s)]["trust"][-1][key]
                for k in range(6):
                    e = 0 if k < 3 else 1
                    ex.append(t[e][k])
                    nx.append(t[1 - e][k])
            L.append(f"- {a} ({p}), final trust per kind: the expert {np.mean(ex):.2f}, the non-expert {np.mean(nx):.2f}")
    L += ["", "Rules (frozen): primary = reading 1; paired by seed; 10,000 draws, seed 20261113; no reading if T's "
          "day-30 success under full practice is 0.90 or more.", ""]
    (out / "results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps({"r1": r1, "r2": r2, "r3a": r3a, "r3b": r3b, "r4": inter}, indent=1),
                                      encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
