"""C0-A: generate the parents' sentences once (questions.md, "The sentences"). Runs on the cloud with qwen2.5:7b through
Ollama (workflow c0a-corpus); the output corpus.json is committed before any run.

  python studies/C0A/make_corpus.py qwen2.5:7b out
"""
from __future__ import annotations

import json
import random
import re
import sys
import time
import urllib.request
from pathlib import Path

NAMES = ["ball", "cup", "spoon", "bread", "apple", "banana", "shoe", "hat", "book", "duck"]
PLURALS = ["balls", "cups", "spoons", "breads", "apples", "bananas", "shoes", "hats", "books", "ducks"]
NONCE = ["dax", "wug", "blicket", "toma", "fep", "zib", "kiv", "modi", "pilk", "gazzer"]
SLOT_KINDS = ["naming", "asking", "praise", "no", "this", "handing"]
OTHER_KINDS = ["confusion", "whatwant", "background"]
MINIMUM = {**{k: 40 for k in SLOT_KINDS}, "confusion": 10, "whatwant": 10, "background": 150}
SPLIT_SEED = 20261108

ASK = {
    "naming": "a parent shows a thing to their toddler and tells the child its name, like \"Look, a {X}!\"",
    "asking": "a parent asks their toddler to hand them a thing, like \"Can you give me the {X}?\"",
    "praise": "a parent praises their toddler for handing over the right thing, like \"Yes, that's the {X}! Well done!\"",
    "no": "a parent gently tells their toddler that the thing the child handed over is the wrong one, naming that thing, "
          "like \"No, that's the {X}.\"",
    "this": "a parent points to the right thing and tells their toddler this is the one they meant, like \"This one, the {X}.\"",
    "handing": "a parent hands their toddler the thing the child asked for, like \"Here's your {X}!\"",
    "confusion": "a parent tells their toddler kindly that they did not understand what the child said, like "
                 "\"Hmm, I don't understand.\"",
    "whatwant": "a parent asks their toddler what the child wants, like \"What do you want, sweetie?\"",
    "background": "a parent says something everyday at home near their toddler, about the weather, cooking, the day, "
                  "feelings or family, like \"It's sunny today.\"",
}


def chat(model: str, prompt: str) -> str:
    body = {"model": model, "stream": False, "options": {"temperature": 0.9, "num_predict": 1500},
            "messages": [{"role": "user", "content": prompt}]}
    req = urllib.request.Request("http://localhost:11434/api/chat", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=1200) as r:
        return json.loads(r.read())["message"]["content"]


def prompt_for(kind: str) -> str:
    if kind in SLOT_KINDS:
        rule = ("IMPORTANT: every sentence must contain the exact characters {X} once, in the place where the thing's "
                "name would go. {X} is a blank to be filled in later. Never write the name of any object or animal "
                "(no ball, cup, toy, teddy and so on), only {X}. Vary the wording a lot; do not copy the example. "
                "Good: \"Oh look, it's a {X}!\" Bad: \"Oh look, it's a ball!\"")
    else:
        rule = "Do not mention any object by name, and do not use the placeholder {X}."
    return (f"Write 40 different short sentences for this moment: {ASK[kind]}. {rule} Use plain everyday English, 2 to 14 words, no "
            "numbers. Write one sentence per line, with no numbering, no quotes and nothing else.")


def tokens(s: str) -> list:
    return re.findall(r"[a-z']+", s.lower())


def clean(line: str) -> str:
    line = line.strip().strip("-*•").strip()
    line = re.sub(r"^\d+[.)]\s*", "", line)
    line = line.strip().strip('"“”').strip()
    # the model's ways of writing the placeholder, read as the placeholder (IMPLEMENTATION.md, "The sentences")
    return re.sub(r"\{\{\s*[xX]\s*\}\}|\{\s*[xX]\s*\}|\[\s*[xX]\s*\]|<\s*[xX]\s*>", "{X}", line)


def valid(kind: str, s: str) -> bool:
    if kind in SLOT_KINDS:
        if s.count("{X}") != 1:
            return False
    elif "{X}" in s:
        return False
    words = tokens(s.replace("{X}", " "))
    if any(w in NAMES or w in PLURALS for w in words):
        return False
    if any(w in NONCE for w in words):
        return False
    if re.search(r"\d", s):
        return False
    n = len(tokens(s.replace("{X}", " slot ")))
    return 2 <= n <= 14


def main():
    model, out = sys.argv[1], Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    frames = {k: [] for k in SLOT_KINDS + OTHER_KINDS}
    seen = {k: set() for k in frames}
    log, raw = [], []
    for rnd in range(1 + 3):                      # the first round and up to 3 extra rounds (questions.md)
        short = [k for k in frames if len(frames[k]) < MINIMUM[k]]
        if rnd > 0 and not short:
            break
        for kind in (frames if rnd == 0 else short):
            asks = 4 if kind == "background" else 1
            for _ in range(asks):
                t0 = time.time()
                text = chat(model, prompt_for(kind))
                raw.append({"round": rnd, "kind": kind, "text": text})
                kept = 0
                for line in text.splitlines():
                    s = clean(line)
                    if not s:
                        continue
                    key = s.lower()
                    if key in seen[kind]:
                        continue
                    if valid(kind, s):
                        seen[kind].add(key)
                        frames[kind].append(s)
                        kept += 1
                log.append({"round": rnd, "kind": kind, "kept": kept, "seconds": round(time.time() - t0, 1)})
                print(f"round {rnd} {kind}: kept {kept}, total {len(frames[kind])}", flush=True)
    ok = all(len(frames[k]) >= MINIMUM[k] for k in frames)
    rng = random.Random(SPLIT_SEED)
    split = {}
    for kind in SLOT_KINDS:
        order = list(frames[kind])
        rng.shuffle(order)
        cut = round(0.2 * len(order))
        split[kind] = {"test": order[:cut], "life": order[cut:]}
    for kind in OTHER_KINDS:
        split[kind] = {"life": frames[kind]}
    vocab = sorted({w for k in frames for s in frames[k] for w in tokens(s.replace("{X}", " "))} | set(NAMES))
    assert not set(vocab) & set(NONCE)
    corpus = {"model": model, "minimums_met": ok, "names": NAMES, "nonce": NONCE, "split_seed": SPLIT_SEED,
              "frames": split, "vocabulary": vocab, "log": log}
    (out / "corpus.json").write_text(json.dumps(corpus, indent=1), encoding="utf-8")
    (out / "raw.json").write_text(json.dumps(raw, indent=1), encoding="utf-8")       # every reply as the model wrote it
    print("minimums met:", ok, {k: len(v) for k, v in frames.items()}, "vocabulary", len(vocab))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
