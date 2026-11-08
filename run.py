"""Run Cradle.
  python run.py [--years N] [--seed S] [--model mock | ollama:<name>] [--calls-per-day K] [--live] [--save PATH] [--load PATH]
                [--apply EVENT[,EVENT...]] [--note TEXT]
  --live: the ghost is in session; the run stops at each pause point and writes pause.json (plus a save).
  --apply: the ghost's decisions at the pause, applied before the run resumes (with --load).
"""
import argparse
import json
import time

from cradle import world
from cradle.director import Director
from cradle.minds import Minds, MockModel, OllamaModel

ap = argparse.ArgumentParser()
ap.add_argument("--years", type=float, default=10)
ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--model", default="")
ap.add_argument("--calls-per-day", type=int, default=8)
ap.add_argument("--live", action="store_true")
ap.add_argument("--save", default="")
ap.add_argument("--load", default="")
ap.add_argument("--apply", default="")
ap.add_argument("--note", default="")
a = ap.parse_args()

model = None
if a.model == "mock":
    model = MockModel()
elif a.model.startswith("ollama:"):
    model = OllamaModel(a.model.split(":", 1)[1])

if a.load:
    c = world.load(a.load, model)
else:
    c = world.City(a.seed)
    c.pick_focus()
    if model is not None:
        c.minds = Minds(model, a.calls_per_day)
    c.director = Director(a.seed, live=a.live)
if c.director is not None:
    c.director.live, c.director.paused = a.live, False
    for ev in [e for e in a.apply.split(",") if e]:
        print("ghost:", c.director.apply(c, ev, by="ghost", note=a.note))

t0, end = time.time(), c.hour + int(a.years * world.HOURS_PER_YEAR)
while c.hour < end:
    c.step()
    if c.hour % (5 * world.HOURS_PER_YEAR) == 0:
        print(json.dumps(c.census()), flush=True)
    if c.director is not None and c.director.paused:
        print("pause point at year", round(c.hour / world.HOURS_PER_YEAR, 2), "- see pause.json")
        break
if a.save:
    world.save(c, a.save)
print(f"done: year {c.hour / world.HOURS_PER_YEAR:.2f}, {time.time() - t0:.0f}s, model calls "
      f"{getattr(model, 'calls', 0)}, chronicle {len(c.director.chronicle) if c.director else 0}")
if c.director is not None:
    for e in c.director.chronicle[-8:]:
        print(" ", e)
