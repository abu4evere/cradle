"""C1.5: generate the parents' two-thing requests once (questions.md, "The frames"). Runs on the cloud with qwen2.5:7b
through Ollama (workflow c15-corpus); the output corpus_c15.json is committed before any C1.5 run.

Kinds: order ("the {X}, then the {Y}"), neg_first ("not the {X}, the {Y}"), neg_last ("the {Y}, not the {X}"), and the
exploratory after ("the {Y} after the {X}"). Split 3/4 life, 1/4 test.

  python studies/C1_5/make_corpus_c15.py qwen2.5:7b out
"""
from __future__ import annotations

import json
import random
import re
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "C0B"))
from c0b import NAMES, PLURALS, NONCE  # noqa: E402

KINDS = ["order", "neg_first", "neg_last", "after"]
MINIMUM = {"order": 40, "neg_first": 32, "neg_last": 32, "after": 16}
SPLIT_SEED = 20261111
ORDER_WORDS = {"then", "next", "after"}           # order frames need one of these (or "after that") between the slots
NEG_WORDS = {"not", "no", "don't", "dont"}

ASK = {
    "order": "a parent asks their toddler to hand them two things one after the other: first {X}, then {Y}. The first "
             "thing named must be the first to hand, and a word like then or next must come between them. Examples: "
             "\"Give me the {X}, then the {Y}.\" \"First the {X}, and then the {Y}, please.\" \"Can you pass the {X}, "
             "and next the {Y}?\"",
    "neg_first": "a parent asks their toddler for one thing, {Y}, and says it is not the other thing, {X}, saying the "
                 "wrong one FIRST, with not or no right before it. Examples: \"Not the {X}, the {Y}.\" \"No, not the "
                 "{X}, I want the {Y}.\" \"Not that {X}, give me the {Y}.\"",
    "neg_last": "a parent asks their toddler for one thing, {Y}, and then says it is not the other thing, {X}, saying "
                "the wrong one LAST, with not right before it. Examples: \"The {Y}, not the {X}.\" \"Give me the {Y}, "
                "not the {X}.\" \"I want the {Y}, not that {X}.\"",
    "after": "a parent asks their toddler for {Y} after {X}: the child must hand {X} first, but the parent names {Y} "
             "first and uses the word after. Examples: \"The {Y} after the {X}.\" \"Give me the {Y} after you give "
             "me the {X}.\" \"Hand me the {Y}, after the {X}.\"",
}


def chat(model: str, prompt: str) -> str:
    body = {"model": model, "stream": False, "options": {"temperature": 0.9, "num_predict": 1500},
            "messages": [{"role": "user", "content": prompt}]}
    req = urllib.request.Request("http://localhost:11434/api/chat", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=1200) as r:
        return json.loads(r.read())["message"]["content"]


def prompt_for(kind: str) -> str:
    rule = ("IMPORTANT: every sentence must contain the exact characters {X} once and {Y} once, where the two things' "
            "names would go. They are blanks to be filled in later. Never write the name of any object or animal, only "
            "{X} and {Y}. Vary the wording a lot; do not copy the examples.")
    return (f"Write 40 different short sentences for this moment: {ASK[kind]} {rule} Use plain everyday English, 3 to 16 "
            "words, no numbers. Write one sentence per line, with no numbering, no quotes and nothing else.")


def tokens(s: str) -> list:
    return re.findall(r"[a-z']+", s.lower())


def clean(line: str) -> str:
    line = line.strip().strip("-*•").strip()
    line = re.sub(r"^\d+[.)]\s*", "", line)
    line = line.strip().strip('"“”').strip()
    for v in "XY":                                # the model's ways of writing a placeholder, read as the placeholder
        c = f"[{v.lower()}{v}]"
        pat = rf"\{{\{{\s*{c}\s*\}}\}}|\{{\s*{c}\s*\}}|\[\s*{c}\s*\]|<\s*{c}\s*>"
        line = re.sub(pat, "{" + v + "}", line)
    return line


def _words(s: str) -> list:
    """The sentence's words, with the slots kept as the tokens 'xslot' and 'yslot'."""
    return tokens(s.replace("{X}", " xslot ").replace("{Y}", " yslot "))


def valid(kind: str, s: str) -> bool:
    if s.count("{X}") != 1 or s.count("{Y}") != 1:
        return False
    w = _words(s)
    bad = set(NAMES) | set(PLURALS.values()) | set(NONCE)
    if set(w) & bad or re.search(r"\d", s) or not 3 <= len(w) <= 16:
        return False
    ix, iy = w.index("xslot"), w.index("yslot")
    if kind == "order":
        return ix < iy and bool(set(w[ix + 1:iy]) & ORDER_WORDS)
    if kind == "after":
        return iy < ix and "after" in w[iy + 1:ix]
    negs = [i for i, t in enumerate(w) if t in NEG_WORDS]
    if kind == "neg_first":           # the negation comes before X, X before Y, and none between X and Y
        return ix < iy and any(i < ix for i in negs) and not any(ix < i < iy for i in negs)
    if kind == "neg_last":            # Y first, then the negation, then X; no negation before Y
        return iy < ix and any(iy < i < ix for i in negs) and not any(i < iy for i in negs)
    return False


def main():
    model, out = sys.argv[1], Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    frames = {k: [] for k in KINDS}
    seen = {k: set() for k in KINDS}
    log, raw = [], []
    for rnd in range(1 + 5):                      # the first round and up to 5 extra rounds
        short = [k for k in KINDS if len(frames[k]) < MINIMUM[k]]
        if rnd > 0 and not short:
            break
        for kind in (KINDS if rnd == 0 else short):
            t0 = time.time()
            text = chat(model, prompt_for(kind))
            raw.append({"round": rnd, "kind": kind, "text": text})
            kept = 0
            for line in text.splitlines():
                s = clean(line)
                if not s or s.lower() in seen[kind]:
                    continue
                if valid(kind, s):
                    seen[kind].add(s.lower())
                    frames[kind].append(s)
                    kept += 1
            log.append({"round": rnd, "kind": kind, "kept": kept, "seconds": round(time.time() - t0, 1)})
            print(f"round {rnd} {kind}: kept {kept}, total {len(frames[kind])}", flush=True)
    ok = all(len(frames[k]) >= MINIMUM[k] for k in KINDS)
    rng = random.Random(SPLIT_SEED)
    split = {}
    for kind in KINDS:
        order = list(frames[kind])
        rng.shuffle(order)
        cut = round(0.25 * len(order))
        split[kind] = {"test": order[:cut], "life": order[cut:]}
    vocab = sorted({t for k in KINDS for s in frames[k] for t in tokens(s.replace("{X}", " ").replace("{Y}", " "))})
    corpus = {"model": model, "minimums_met": ok, "split_seed": SPLIT_SEED, "frames": split, "vocabulary": vocab,
              "log": log}
    (out / "corpus_c15.json").write_text(json.dumps(corpus, indent=1), encoding="utf-8")
    (out / "raw.json").write_text(json.dumps(raw, indent=1), encoding="utf-8")
    print("minimums met:", ok, {k: len(v) for k, v in frames.items()}, "vocabulary", len(vocab))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
