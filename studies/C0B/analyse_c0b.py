"""C0-B analysis (questions.md, C0B-frozen). Written before the study's data (after the difficulty check, which chose L1).
Built on analyse_c0a.py: C0-A's readings and validity, plus learning speed (the area under the request curve over
days 3-90 by the trapezoid over the real test days, / 87), days to 0.80, the look-alike test, and the ceiling rule.

  python studies/C0B/analyse_c0b.py OUT_DIR

Writes OUT_DIR/summary.json and OUT_DIR/results.md.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
ARMS10 = ["A", "B", "C", "H", "D", "P", "G", "E", "F", "K"]
EARLY = [3, 7, 14, 30, 60, 90]
ALLD = [3, 7, 14, 30, 60, 90, 180, 360, 720, 1080]
SEEDS = list(range(1, 17))
DAY = "1080"
NAMES = ["ball", "cup", "spoon", "bread", "apple", "banana", "shoe", "hat", "book", "duck"]
MEASURES = ["request", "new", "alike", "novel", "saying", "repair_with", "repair_without"]
SECONDARY = [("B", "A"), ("H", "A"), ("C", "H"), ("C", "B"), ("D", "A"), ("G", "A"), ("K", "A"), ("P", "A")]

# one set of resampled seeds for everything, so every difference is paired (questions.md)
IDX = np.random.default_rng(20261111).integers(0, len(SEEDS), (10_000, len(SEEDS)))


def ci(x):
    x = np.asarray(x, dtype=float)
    b = x[IDX].mean(1)
    return {"mean": round(float(x.mean()), 4), "lo": round(float(np.percentile(b, 2.5)), 4),
            "hi": round(float(np.percentile(b, 97.5)), 4), "n": len(x)}


def main():
    out = Path(sys.argv[1])
    data, missing = {}, []
    for arm in ARMS10:
        for s in SEEDS:
            f = out / f"{arm}_seed_{s}.json"
            if f.exists():
                data[(arm, s)] = json.loads(f.read_text(encoding="utf-8"))
            else:
                missing.append(f.name)

    def per_child(arm, measure, day=DAY):
        return [data[(arm, s)]["results"][day][measure] for s in SEEDS]

    # validity: files, one scene per seed, the code checks
    scenes_ok = all(len({data[(a, s)]["scene"] for a in ARMS10 if (a, s) in data}) == 1 for s in SEEDS)
    log = HERE / "checks.log"
    checks_ok = log.exists() and log.read_text(encoding="utf-8").strip().endswith("All: PASS")
    e_still = all(data[("E", s)]["E_unchanged"] is True for s in SEEDS if ("E", s) in data)
    v = {"all_files": not missing, "missing": missing,
         "one_scene_per_seed": scenes_ok, "checks_pass": checks_ok, "E_unchanged": e_still}
    if not v["all_files"]:
        print("missing files:", missing)
        sys.exit(1)

    S = {"validity": v, "arms": {}, "differences": {}, "readings": {}}
    for arm in ARMS10:
        S["arms"][arm] = {m: ci(per_child(arm, m)) for m in MEASURES}
        S["arms"][arm]["curve_request"] = {d: ci([data[(arm, s)]["results"][d]["request"] for s in SEEDS])["mean"]
                                           for d in data[(arm, 1)]["results"]}
        S["arms"][arm]["exposure_mean"] = np.mean([data[(arm, s)]["exposure"] for s in SEEDS], 0).round(1).tolist()
        byw = {}
        for w in NAMES:
            vals = [data[(arm, s)]["results"][DAY]["request_by_word"][w] for s in SEEDS]
            vals = [x for x in vals if x is not None]
            byw[w] = {"mean": round(float(np.mean(vals)), 4), "n": len(vals)} if vals else None
        S["arms"][arm]["request_by_word"] = byw

    def diff(a, b, m="request", m2=None):
        x = np.array(per_child(a, m)) - np.array(per_child(b, m2 or m))
        return ci(x)

    def aulc(arm):
        out = []
        for s in SEEDS:
            ys = [data[(arm, s)]["results"][str(d)]["request"] for d in EARLY]
            out.append(float(np.trapezoid(ys, EARLY)) / (EARLY[-1] - EARLY[0]))
        return np.array(out)

    def days_to(arm):
        out = []
        for s in SEEDS:
            ys = [data[(arm, s)]["results"][str(d)]["request"] for d in ALLD]
            hit = next((ALLD[i] for i in range(len(ALLD) - 1) if ys[i] >= 0.8 and ys[i + 1] >= 0.8), None)
            out.append(hit)
        return out
    S["speed"] = {}
    for arm in ARMS10:
        dt = days_to(arm)
        S["speed"][arm] = {"aulc": ci(aulc(arm)), "days_to_0.8": dt,
                           "never": sum(1 for x in dt if x is None)}
    S["speed_diff"] = {f"{a}-{b}": ci(aulc(a) - aulc(b)) for a, b in SECONDARY}
    a30 = float(np.mean([data[("A", s)]["results"]["30"]["request"] for s in SEEDS]))
    S["ceiling"] = {"A_day30": a30, "uninformative": a30 >= 0.95}
    a_chance = ci(np.array(per_child("A", "request")) - 0.25)
    a_f = diff("A", "F")
    S["readings"]["1_associates_words"] = {"A_minus_chance": a_chance, "A_minus_F": a_f,
                                           "yes": a_chance["lo"] > 0 and a_f["lo"] > 0}
    rep = ci(np.array(per_child("A", "repair_with")) - np.array(per_child("A", "repair_without")))
    S["readings"]["2_uses_correction"] = {"A_with_minus_without": rep, "yes": rep["lo"] > 0}
    for a, b in SECONDARY:
        S["differences"][f"{a}-{b} request"] = diff(a, b)
    S["differences"]["A-E saying"] = diff("A", "E", "saying")

    p = ci(np.array(per_child("P", "request")) - 0.25)
    within = lambda c: c["lo"] >= 0.17 and c["hi"] <= 0.33
    v["P_learns"] = {"P_minus_chance": p, "ok": p["lo"] > 0}
    v["E_at_chance"] = {"ci": S["arms"]["E"]["request"], "ok": within(S["arms"]["E"]["request"])}
    v["F_at_chance"] = {"ci": S["arms"]["F"]["request"], "ok": within(S["arms"]["F"]["request"])}
    v["A_novel_at_chance"] = {"ci": S["arms"]["A"]["novel"], "ok": within(S["arms"]["A"]["novel"])}
    v["valid"] = all([v["all_files"], scenes_ok, checks_ok, e_still, v["P_learns"]["ok"], v["E_at_chance"]["ok"],
                      v["F_at_chance"]["ok"], v["A_novel_at_chance"]["ok"]])

    gl = []
    if gl:
        days = sorted(data[("GL", gl[0])]["results"], key=int)
        S["GL_curve_request"] = {d: {"mean": round(float(np.mean([data[("GL", s)]["results"][d]["request"]
                                                                   for s in gl])), 4), "n": len(gl)} for d in days}

    (out / "summary.json").write_text(json.dumps(S, indent=1), encoding="utf-8")
    fmt = lambda c: f"{c['mean']:.3f} [{c['lo']:.3f}, {c['hi']:.3f}] (n={c['n']})"
    L = ["# C0-B results (level L1; day 1,080 unless stated; 95% bootstrap intervals over 16 children)", "",
         f"**Valid:** {v['valid']}  (all files {v['all_files']}; one scene per seed {scenes_ok}; code checks "
         f"{checks_ok}; E unchanged {e_still}; P learns {v['P_learns']['ok']}; E at chance {v['E_at_chance']['ok']}; "
         f"F at chance {v['F_at_chance']['ok']}; A novel word at chance {v['A_novel_at_chance']['ok']})", "",
         f"**Reading 1, associates words:** {S['readings']['1_associates_words']['yes']}  "
         f"(A - 0.25 = {fmt(a_chance)}; A - F = {fmt(a_f)})", "",
         f"**Reading 2, uses correction:** {S['readings']['2_uses_correction']['yes']}  "
         f"(with - without = {fmt(rep)})", "", "| Arm | " + " | ".join(MEASURES) + " |",
         "|---|" + "---|" * len(MEASURES)]
    for arm in ARMS10:
        L.append(f"| {arm} | " + " | ".join(fmt(S["arms"][arm][m]) for m in MEASURES) + " |")
    L += ["", f"**Ceiling rule:** A's request at day 30 = {a30:.3f}; still at ceiling (>= 0.95, uninformative): "
          f"{S['ceiling']['uninformative']}", "",
          "**Learning speed** (area under the request curve, days 3-90, / 87) and days to 0.80:", "",
          "| Arm | speed | children never reaching 0.80 by day 1,080 | days to 0.80 (per child) |", "|---|---|---|---|"]
    for arm in ARMS10:
        sp = S["speed"][arm]
        L.append(f"| {arm} | {fmt(sp['aulc'])} | {sp['never']} | {sp['days_to_0.8']} |")
    L += ["", "**Arm questions, on learning speed (paired; an interval excluding 0 is a finding):**", ""]
    L += [f"- {k}: {fmt(c)}" for k, c in S["speed_diff"].items()]
    L += ["", "**Secondary differences (paired), request at day 1,080:**", ""]
    L += [f"- {k}: {fmt(c)}" for k, c in S["differences"].items()]
    if gl:
        L += ["", "**GL (exploratory) request curve:** " + ", ".join(f"day {d}: {c['mean']:.3f}"
                                                                     for d, c in S["GL_curve_request"].items())
              + f" (n={len(gl)})"]
    (out / "results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
