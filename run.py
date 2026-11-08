"""Run the Cradle city (milestone 1: the city lives on its own).  python run.py [years] [seed]"""
import sys, time
from cradle.world import run
t0 = time.time()
run(int(sys.argv[1]) if len(sys.argv) > 1 else 30, int(sys.argv[2]) if len(sys.argv) > 2 else 1)
print(f"done in {time.time() - t0:.0f}s")
