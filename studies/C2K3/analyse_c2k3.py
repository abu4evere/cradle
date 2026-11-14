"""C2-K3 analysis (questions.md, C2K3-frozen; C2-K's with the max(Cb, Cok) floor and the selection note). Written before any data.

  python studies/C2K3/analyse_c2k3.py OUT_DIR        (writes OUT_DIR/results.md and summary.json)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
ARMS = ["T", "I", "Cb", "Ctk", "Cyk", "Cok", "Cr"]
CONDS = ["G", "U"]
SEEDS = list(range(1, 49))
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
        for c in CONDS:
            for s in SEEDS:
                fp = out / f"{a}_{c}_seed_{s}.json"
                if fp.exists():
                    data[(a, c, s)] = json.loads(fp.read_text(encoding="utf-8"))
                else:
                    missing.append(fp.name)
    log = HERE / "checks.log"
    checks_ok = log.exists() and log.read_text(encoding="utf-8").strip().endswith("All: PASS")
    same = all(len({json.dumps([data[k]["pairs"], data[k]["habits"]]) for k in data if k[2] == s}) == 1 for s in SEEDS)
    valid = checks_ok and not missing and same
    diff = json.loads((HERE / "difficulty.json").read_text())
    L = ["# C2-K3: whom to copy in cumulative skills, with the memory brain (results)", "",
         "Frozen as `C2K3-frozen`. c2k3.py, analyse_c2k3.py (written before data).", "",
         f"## Difficulty check: level **{diff['level']}**", ""] + [
        f"- {r}" for r in diff["rows"]] + ["", "## Validity", "",
         f"- Code checks (All: PASS): **{'yes' if checks_ok else 'NO'}**",
         f"- All {len(ARMS) * len(CONDS) * len(SEEDS)} runs present: **{'yes' if not missing else 'NO'}**",
         f"- The same boxes, pairs and habits per seed everywhere: **{'yes' if same else 'NO'}**", ""]

    def sc(a, c, d, key="success"):
        return np.array([data[(a, c, s)]["tests"][d][key] for s in SEEDS], float)

    if valid:
        tu = sc("T", "U", "30").mean()
        L += [f"- Not at ceiling (T's day-30 success in U {tu:.3f} below 0.90): **{'yes' if tu < 0.90 else 'NO'}**"]
        valid = tu < 0.90
    L += ["", f"**{'Valid.' if valid else 'NOT VALID: no reading is drawn.'}**", ""]
    if not valid:
        (out / "results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
        print("\n".join(L))
        return
    floor = max(sc("Cb", "G", "30").mean(), sc("Cok", "G", "30").mean()) < 0.05
    sel_dep = [r for r in diff["rows"] if r["level"] == diff["level"]][0]["decided_by"] == "Cok"
    r1 = ci(sc("Ctk", "G", "30") - sc("Cyk", "G", "30"))
    r2 = ci(sc("Cok", "G", "30") - sc("Cb", "G", "30"))
    r3 = ci(sc("Ctk", "G", "30") - sc("Cb", "G", "30"))
    r4 = ci((sc("Cok", "G", "30") - sc("Cb", "G", "30")) - (sc("Cok", "U", "30") - sc("Cb", "U", "30")))

    def word(c, guarded=True):
        if guarded and floor:
            return "not readable (floor)"
        return "yes" if c[1] > 0 else "no"
    L += [f"- Floor guard: max(Cb, Cok) day-30 success in G "
          f"({'BELOW 0.05: readings 1-3 not readable' if floor else 'not below 0.05'}); reading 2 selection-dependent: {'YES' if sel_dep else 'no'}", "",
          "## Readings (frozen; day-30 full-box success; n = 48 per condition)", "",
          f"1. **PRIMARY. Choosing the right expert pays when skills build on each other** (G, Ctk - Cyk): {f(r1)} -> **{word(r1)}**",
          f"2. **The oracle beats copying everyone** (G, Cok - Cb): {f(r2)} -> **{word(r2)}**",
          f"3. **Learned choosing beats copying everyone** (G, Ctk - Cb): {f(r3)} -> **{word(r3)}**",
          f"4. **The chain raises the value of choosing** ((Cok - Cb)G - (Cok - Cb)U): {f(r4)} -> **{word(r4, False)}**", ""]
    L += ["## Reported (no gate)", ""]
    for a, b in (("Cok", "Cr"), ("Ctk", "Cyk"), ("Cok", "Cb"), ("Ctk", "Cb"), ("Ctk", "I"), ("Cb", "I")):
        for c in CONDS:
            L.append(f"- {a} - {b} ({c}): day 30 {f(ci(sc(a, c, '30') - sc(b, c, '30')))}; day 60 "
                     f"{f(ci(sc(a, c, '60') - sc(b, c, '60')))}; partial day 30 "
                     f"{f(ci(sc(a, c, '30', 'partial') - sc(b, c, '30', 'partial')))}")
    L += ["", "## Success by day (full box; mean over 48)", "", "| arm | cond | " + " | ".join(DAYS) + " |",
          "|---|---|" + "---|" * len(DAYS)]
    for a in ARMS:
        for c in CONDS:
            L.append(f"| {a} | {c} | " + " | ".join(f"{sc(a, c, d).mean():.3f}" for d in DAYS) + " |")
    L += ["", "## Partial score by day (lids opened / 3)", "", "| arm | cond | " + " | ".join(DAYS) + " |",
          "|---|---|" + "---|" * len(DAYS)]
    for a in ARMS:
        for c in CONDS:
            L.append(f"| {a} | {c} | " + " | ".join(f"{sc(a, c, d, 'partial').mean():.3f}" for d in DAYS) + " |")
    L += ["", "## Manipulation checks (means over 48)", "", "| arm | cond | copy weight | copies lid 1/2/3 | lids reached per try (days 1-30) |",
          "|---|---|---|---|---|"]
    for a in ARMS:
        for c in CONDS:
            ks = [(a, c, s) for s in SEEDS]
            cl = np.mean([data[k]["copies_by_lid"] for k in ks], axis=0)
            reach = np.mean([np.mean([x["reached"] for x in data[k]["tries"] if x["d"] <= 30]) for k in ks])
            L.append(f"| {a} | {c} | {np.mean([data[k]['copy_weight_sum'] for k in ks]):.1f} | "
                     f"{cl[0]:.1f} / {cl[1]:.1f} / {cl[2]:.1f} | {reach:.2f} |")
    ex, nx = [], []
    for s in SEEDS:
        t = data[("Ctk", "G", s)]["trust"]
        for k in range(6):
            e = 0 if k < 3 else 1
            ex.append(t[e][k])
            nx.append(t[1 - e][k])
    L += [f"- Ctk's final trust per kind: the expert {np.mean(ex):.2f}, the non-expert {np.mean(nx):.2f}", "",
          "Rules (frozen): primary = reading 1; paired by seed; 10,000 draws, seed 20261113; floor and ceiling guards as "
          "in questions.md.", ""]
    (out / "results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps({"r1": r1, "r2": r2, "r3": r3, "r4": r4, "floor": bool(floor)}, indent=1),
                                      encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
