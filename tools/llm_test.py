"""First cloud test of Cradle's AI people: can a free open model, run on a GitHub cloud machine, give two NPCs (a mother
and a father) a natural English conversation about their new baby, and how fast?

Talks to a local Ollama server (http://localhost:11434). Writes llm_test.md (the conversation) and llm_test.json (the
timings) to the folder given.

  python tools/llm_test.py <model> <out_dir> [turns]
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

MODEL = sys.argv[1]
OUT = Path(sys.argv[2])
TURNS = int(sys.argv[3]) if len(sys.argv) > 3 else 12
URL = "http://localhost:11434/api/chat"

PEOPLE = {
    "Mira": ("You are Mira, 31, a nurse at the city clinic. You are warm, practical and a little tired. You had your "
             "first baby, a daughter named Lia, three weeks ago. You live in a small house on the east side of the city "
             "with your husband Tomas."),
    "Tomas": ("You are Tomas, 34, a carpenter at the city workshop. You are calm, joking, and quietly nervous about being "
              "a father. Your wife Mira had your first baby, a daughter named Lia, three weeks ago."),
}
SCENE = ("It is 7 in the evening at home. The baby, Lia, is lying in her cot between you, awake and looking at you. "
         "Speak to your partner or to the baby, as people really do. Say one or two short sentences only, in plain "
         "everyday English. Do not describe actions, do not narrate; only what you say aloud.")


def chat(system, history):
    body = {"model": MODEL, "stream": False, "options": {"temperature": 0.8, "num_predict": 60},
            "messages": [{"role": "system", "content": system}] + history}
    req = urllib.request.Request(URL, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=600) as r:
        out = json.loads(r.read())
    return out["message"]["content"].strip(), out.get("eval_count", 0), out.get("eval_duration", 0) / 1e9, time.time() - t0


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    said = []                     # (speaker, text)
    stats = []
    for k in range(TURNS):
        me = "Mira" if k % 2 == 0 else "Tomas"
        hist = [{"role": "assistant" if s == me else "user", "content": f"{s}: {t}"} for s, t in said]
        if not hist:
            hist = [{"role": "user", "content": "(The evening begins.)"}]
        text, ntok, gen_s, wall = chat(PEOPLE[me] + " " + SCENE, hist)
        text = text.split(":", 1)[1].strip() if text.startswith(me + ":") else text
        said.append((me, text))
        stats.append({"turn": k, "speaker": me, "tokens": ntok, "gen_seconds": round(gen_s, 2), "wall_seconds": round(wall, 2)})
        print(f"{me}: {text}   ({ntok} tokens, {wall:.1f}s)", flush=True)
    tok = sum(s["tokens"] for s in stats)
    gen = sum(s["gen_seconds"] for s in stats)
    wall = sum(s["wall_seconds"] for s in stats)
    summary = {"model": MODEL, "turns": TURNS, "tokens": tok, "tokens_per_second": round(tok / gen, 2) if gen else None,
               "seconds_per_turn": round(wall / TURNS, 2), "stats": stats}
    (OUT / "llm_test.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    md = [f"# Cradle cloud test: {MODEL}", "", f"{tok} tokens, {summary['tokens_per_second']} tokens/s, "
          f"{summary['seconds_per_turn']} s per turn (cloud machine, CPU only).", ""]
    md += [f"**{s}:** {t}" for s, t in said]
    (OUT / "llm_test.md").write_text("\n\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "stats"}))


if __name__ == "__main__":
    main()
