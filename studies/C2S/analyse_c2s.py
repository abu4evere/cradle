"""C2-S analysis (questions.md, C2S-frozen). Written before any data.

  python studies/C2S/analyse_c2s.py OUT_DIR        (writes OUT_DIR/results.md and summary.json)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
ARMS = ["T", "I", "Cb", "Co", "Ct", "Cy", "Cp", "Cpx", "Ca", "Cb100", "Cp100"]
SEEDS = list(range(1, 49))
EARLY = ["1", "2", "3", "5", "7"]
DAYS = ["1", "2", "3", "5", "7", "10", "15", "30", "45", "60"]
IDX = np.random.default_rng(20261113).integers(0, len(SEEDS), (10_000, len(SEEDS)))


def ci(x):
    x = np.asarray(x, float)
    b = np.nanmean(x[IDX], axis=1)
    return float(np.nanmean(x)), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))


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
    same = all(len({json.dumps([data[(a, s)]["pairs"], data[(a, s)]["habits"]]) for a in ARMS if (a, s) in data}) == 1
               for s in SEEDS)
    valid = checks_ok and not missing and same
    L = ["# C2-S: copy who succeeds (results)", "", "Frozen as `C2S-frozen`. c2s.py, analyse_c2s.py (written before data).",
         "", "## Validity", "", f"- Code checks (All: PASS): **{'yes' if checks_ok else 'NO'}**",
         f"- All {len(ARMS) * len(SEEDS)} runs present: **{'yes' if not missing else 'NO'}**",
         f"- The same boxes, pairs and Ben's habits per seed in every arm: **{'yes' if same else 'NO'}**", ""]

    def succ(a, d, key="success"):
        return np.array([data[(a, s)]["tests"][d][key] for s in SEEDS], float)

    def early(a):
        return np.mean([succ(a, d) for d in EARLY], axis=0)
    if valid:
        ceiling = early("T").mean() >= 0.90
        L += [f"- Not at ceiling (T's early learning {early('T').mean():.3f} below 0.90): **{'yes' if not ceiling else 'NO'}**", ""]
        valid = not ceiling
    L += [f"**{'Valid.' if valid else 'NOT VALID: no reading is drawn.'}**", ""]
    if not valid:
        (out / "results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
        print("\n".join(L))
        return
    d = {}
    for name, (a, b) in {"Ca_Cb": ("Ca", "Cb"), "Co_Cb": ("Co", "Cb"), "Ct_Cy": ("Ct", "Cy"), "Ct_Co": ("Ct", "Co"),
                         "Cp_Cb": ("Cp", "Cb"), "Cp_Cpx": ("Cp", "Cpx"), "Cp100_Cb100": ("Cp100", "Cb100"),
                         "Cb_I": ("Cb", "I"), "I_T": ("I", "T"), "Ct_Cb": ("Ct", "Cb")}.items():
        d[name] = ci(early(a) - early(b))
    sd = {}
    for name, (a, b) in {"Ca_Cb": ("Ca", "Cb"), "Co_Cb": ("Co", "Cb"), "Ct_Cy": ("Ct", "Cy"), "Cp_Cb": ("Cp", "Cb"),
                         "Cp_Cpx": ("Cp", "Cpx"), "Cp100_Cb100": ("Cp100", "Cb100")}.items():
        diff = early(a) - early(b)
        sd[name] = float(diff.mean() / diff.std(ddof=1)) if diff.std(ddof=1) > 0 else float("nan")
    r1 = d["Ca_Cb"][1] > 0
    r4 = d["Cp_Cb"][1] > 0 and d["Cp_Cpx"][1] > 0
    L += ["## Readings (frozen; early learning = mean success at days 1, 2, 3, 5, 7; n = 48 children per arm)", "",
          f"1. **A consistently wrong model harms blind copying** (Ca - Cb): {f(d['Ca_Cb'])}, effect size {sd['Ca_Cb']:.2f}"
          f" -> **{'yes' if r1 else 'not shown'}**",
          f"2. **Copying only what was seen to work helps** (Co - Cb): {f(d['Co_Cb'])}, effect size {sd['Co_Cb']:.2f} -> "
          f"**{'yes' if d['Co_Cb'][1] > 0 else 'no'}**",
          f"3. **Trust from seen results helps, beyond the amount of copying** (Ct - Cy): {f(d['Ct_Cy'])}, effect size "
          f"{sd['Ct_Cy']:.2f} -> **{'yes' if d['Ct_Cy'][1] > 0 else 'no'}** (Ct - Co, reported: {f(d['Ct_Co'])})",
          f"4. **Trust from own experience helps** (Cp - Cb {f(d['Cp_Cb'])}, effect size {sd['Cp_Cb']:.2f}; Cp - Cpx "
          f"{f(d['Cp_Cpx'])}, effect size {sd['Cp_Cpx']:.2f}) -> **{'yes' if r4 else 'no'}**",
          f"5. **...even with every result hidden** (Cp100 - Cb100): {f(d['Cp100_Cb100'])}, effect size "
          f"{sd['Cp100_Cb100']:.2f} -> **{'yes' if d['Cp100_Cb100'][1] > 0 else 'no'}**",
          f"- Checks: copying blind helps over watching (Cb - I) {f(d['Cb_I'])}; watching over nothing (I - T) "
          f"{f(d['I_T'])}; Ct - Cb {f(d['Ct_Cb'])}", ""]
    L += ["## Success rate by day (mean over 48 children)", "", "| arm | " + " | ".join(DAYS) + " | early |",
          "|---|" + "---|" * (len(DAYS) + 1)]
    for a in ARMS:
        L.append(f"| {a} | " + " | ".join(f"{succ(a, dd).mean():.3f}" for dd in DAYS) + f" | {early(a).mean():.3f} |")
    L += ["", "## Retention and novel boxes", "", "| arm | day 30 | day 60 | novel day 30 | novel day 60 |", "|---|---|---|---|---|"]
    for a in ARMS:
        L.append(f"| {a} | {succ(a, '30').mean():.3f} | {succ(a, '60').mean():.3f} | {succ(a, '30', 'novel').mean():.3f} | "
                 f"{succ(a, '60', 'novel').mean():.3f} |")

    def per_child(a, fn):
        return np.array([fn(data[(a, s)]) for s in SEEDS], float)

    def habit_share(res):
        t = [x for x in res["tries"] if x["d"] <= 30]
        return np.mean([x["pair"] == x["habit"] for x in t])

    def fidelity(res, who):
        t = [x for x in res["tries"] if x["d"] <= 30 and x["who"] == who]
        return np.mean([x["pair"] == x["shown"] for x in t]) if t else np.nan

    def succ_after(res, seen_flag):
        t = [x for x in res["tries"] if x["d"] <= 30 and x["seen"] is seen_flag]
        return np.mean([x["r"] for x in t]) if t else np.nan

    def weight_by(res, who):
        t = [x for x in res["tries"] if x["d"] <= 30 and x["who"] == who]
        return np.mean([x["w"] for x in t]) if t else np.nan
    L += ["", "## Descriptive (days 1-30)", "",
          "| arm | uses Ben's habit | copies Ann's pair | copies Ben's pair | success after seen | after hidden | "
          "weight on Ann | weight on Ben |", "|---|---|---|---|---|---|---|---|"]
    for a in ARMS:
        L.append(f"| {a} | {np.nanmean(per_child(a, habit_share)):.3f} | "
                 f"{np.nanmean(per_child(a, lambda r: fidelity(r, 0))):.3f} | {np.nanmean(per_child(a, lambda r: fidelity(r, 1))):.3f} | "
                 f"{np.nanmean(per_child(a, lambda r: succ_after(r, True))):.3f} | "
                 f"{np.nanmean(per_child(a, lambda r: succ_after(r, False))):.3f} | "
                 f"{np.nanmean(per_child(a, lambda r: weight_by(r, 0))):.3f} | {np.nanmean(per_child(a, lambda r: weight_by(r, 1))):.3f} |")
    hab = {a: per_child(a, habit_share) for a in ("Cb", "Co", "Ct", "Cp", "T")}
    L += ["", f"- Adopting Ben's habit, against T (its spontaneous rate): Cb - T {f(ci(hab['Cb'] - hab['T']))}; "
          f"Co - T {f(ci(hab['Co'] - hab['T']))}; Ct - T {f(ci(hab['Ct'] - hab['T']))}; Cp - T {f(ci(hab['Cp'] - hab['T']))}"]
    ben_right = np.array([sum(1 for x in data[("Cb", s)]["tries"] if x["d"] <= 30 and x["who"] == 1 and
                              x["shown"] == list(data[("Cb", s)]["pairs"][x["k"]])) for s in SEEDS])
    ben_all = np.array([sum(1 for x in data[("Cb", s)]["tries"] if x["d"] <= 30 and x["who"] == 1) for s in SEEDS])
    L += [f"- Ben's right demonstrations: {ben_right.mean():.1f} of his {ben_all.mean():.1f} per child (mean)."]
    L += ["", "## Trust (mean over children; Ann / Ben)", "", "| day | Ct (seen results) | Cp (own experience) | Cpx (coin credit) | Cp100 |",
          "|---|---|---|---|---|"]
    for dd in (1, 2, 3, 5, 7, 15, 30):
        row = [f"| {dd} "]
        for a, key in (("Ct", "ct"), ("Cp", "p"), ("Cpx", "p"), ("Cp100", "p")):
            tv = np.array([data[(a, s)]["trust"][dd - 1][key] for s in SEEDS])
            row.append(f"| {tv[:, 0].mean():.2f} / {tv[:, 1].mean():.2f} ")
        L.append("".join(row) + "|")
    L += ["", "Rules (frozen): readings as above; paired by seed; 10,000 draws, seed 20261113; no reading if T's early "
          "learning is 0.90 or more; reading 1 negative reads 'not shown'.", ""]
    (out / "results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (out / "summary.json").write_text(json.dumps({"diffs": d, "effect_sizes": sd}, indent=1), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
