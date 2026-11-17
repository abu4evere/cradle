"""C2-P's frozen analysis (questions.md), written before any study data.

  python studies/C2P/analyse_c2p.py OUTDIR      -> studies/C2P/results.md, results.json, recompute/c2p_children.csv
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).parent
ARMS = ("T", "I", "Cb", "Ch", "Ctk", "Cyk", "Cok")
CONDS = ("G", "GP", "GS")
SEEDS = range(1, 49)
IDX = np.random.default_rng(20261117).integers(0, 48, (10_000, 48))


def ci(v):
    v = np.asarray(v, float)
    m = v[IDX].mean(axis=1)
    return [round(float(v.mean()), 4), round(float(np.percentile(m, 2.5)), 4), round(float(np.percentile(m, 97.5)), 4)]


def f(t):
    return f"{t[0]:+.3f} [{t[1]:+.3f}, {t[2]:+.3f}]"


def main(outdir):
    out = Path(outdir)
    checks = (HERE / "checks.log").read_text() if (HERE / "checks.log").exists() else ""
    pain = json.loads((HERE / "pain.json").read_text())
    missing = [f"{a}_{c}_seed_{s}" for a in ARMS for c in CONDS for s in SEEDS if not (out / f"{a}_{c}_seed_{s}.json").exists()]
    L = ["# C2-P results (the frozen analysis, analyse_c2p.py)", "",
         f"- Checks All: PASS: **{'yes' if 'All: PASS' in checks else 'NO'}**",
         f"- Pain level (pilot, seeds 1001-1024): **p = {pain['p']}**",
         f"- All {len(ARMS) * len(CONDS) * 48} children present: **{'yes' if not missing else 'NO, missing ' + str(len(missing))}**", ""]
    if missing or pain["p"] is None:
        (HERE / "results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
        print("\n".join(L))
        return
    R = {(a, c): [json.loads((out / f"{a}_{c}_seed_{s}.json").read_text()) for s in SEEDS] for a in ARMS for c in CONDS}

    def succ(a, c, d=30):
        return [r["tests"][str(d)]["success"] for r in R[(a, c)]]

    def pain_per_lid(a, c):
        v = []
        for r in R[(a, c)]:
            tr = [x for x in r["tries"] if x["d"] <= 30 and not x.get("lost")]
            lids = sum(x["reached"] for x in tr)
            v.append(sum(x.get("pain", 0.0) for x in tr) / max(1, lids))
        return v

    def diff(a, b, c, d=30):
        return ci(np.subtract(succ(a, c, d), succ(b, c, d)))

    def inter(a, b, c1, c2):
        return ci(np.subtract(np.subtract(succ(a, c1), succ(b, c1)), np.subtract(succ(a, c2), succ(b, c2))))
    res = {}
    L += ["## Day-30 full-box success (mean over 48 children)", "", "| arm | G | GP | GS |", "|---|---|---|---|"]
    for a in ARMS:
        L.append(f"| {a} | " + " | ".join(f"{np.mean(succ(a, c)):.3f}" for c in CONDS) + " |")
    guard_floor = np.mean(succ("Cb", "G")) < 0.05
    guard_ceiling = np.mean(succ("T", "G")) >= 0.90
    r1 = diff("Ctk", "Cb", "GP")
    res["primary"] = r1
    L += ["", "## Readings", "",
          f"- Guards: Cb's G success {np.mean(succ('Cb', 'G')):.3f} (floor 0.05: {'FAILS' if guard_floor else 'ok'}); "
          f"T's G success {np.mean(succ('T', 'G')):.3f} (ceiling 0.90: {'FAILS' if guard_ceiling else 'ok'})",
          f"- **1. PRIMARY: (Ctk − Cb) in GP:** {f(r1)} -> **"
          f"{'not readable' if guard_floor or guard_ceiling else ('yes' if r1[1] > 0 else 'no')}**"]
    sec = {"(Ctk − Cb) in GS": diff("Ctk", "Cb", "GS"),
           "(Ctk − Cb)GP − (Ctk − Cb)G": inter("Ctk", "Cb", "GP", "G"),
           "(Ctk − Cyk)GP − (Ctk − Cyk)G": inter("Ctk", "Cyk", "GP", "G"),
           "Ctk − Ch in GP": diff("Ctk", "Ch", "GP")}
    pp = ci(np.subtract(pain_per_lid("Ctk", "GP"), pain_per_lid("Cb", "GP")))
    res["secondary"] = {**sec, "pain per lid Ctk − Cb (GP)": pp}
    L += ["", "Secondary (each with its interval):"]
    for k, v in sec.items():
        L.append(f"- {k}: {f(v)} -> {'yes' if v[1] > 0 else 'no'}")
    L.append(f"- Pain per lid tried, days 1-30, Ctk − Cb in GP: {f(pp)} -> {'yes (less)' if pp[2] < 0 else 'no'}")
    L += ["", "## Reported", ""]
    for c in CONDS:
        L.append(f"- {c}: Ctk − Cyk {f(diff('Ctk', 'Cyk', c))}; Cok − Cb {f(diff('Cok', 'Cb', c))}; "
                 f"Ctk − Cb at day 60 {f(diff('Ctk', 'Cb', c, 60))}")
    for a in ("Cb", "Ch", "Ctk", "Cyk", "Cok"):
        lost = np.mean([sum(1 for x in r["tries"] if x.get("lost")) for r in R[(a, "GS")]])
        we = np.mean([r["w_expert_mean"] for r in R[(a, "GP")] if r["w_expert_mean"] is not None])
        wo = np.mean([r["w_other_mean"] for r in R[(a, "GP")] if r["w_other_mean"] is not None])
        L.append(f"- {a}: tries lost in GS {lost:.0f}; GP copy weight to the expert {we:.3f}, to the non-expert {wo:.3f}; "
                 f"pain per lid (GP) {np.mean(pain_per_lid(a, 'GP')):.3f}")
    (HERE / "results.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    (HERE / "results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    # the blind recompute's input: one row per child
    rc = HERE / "recompute"
    rc.mkdir(exist_ok=True)
    with open(rc / "c2p_children.csv", "w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh)
        wr.writerow(["arm", "cond", "seed", "success_day30", "success_day60", "pain_per_lid_d1_30"])
        for a in ARMS:
            for c in CONDS:
                ppl = pain_per_lid(a, c)
                for i, r in enumerate(R[(a, c)]):
                    wr.writerow([a, c, r["seed"], r["tests"]["30"]["success"], r["tests"]["60"]["success"], round(ppl[i], 6)])
    print("\n".join(L))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(HERE / "output"))
