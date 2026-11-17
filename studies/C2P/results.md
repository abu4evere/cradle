# C2-P results (the frozen analysis, analyse_c2p.py)

- Checks All: PASS: **yes**
- Pain level (pilot, seeds 1001-1024): **p = 1.0**
- All 1008 children present: **yes**

## Day-30 full-box success (mean over 48 children)

| arm | G | GP | GS |
|---|---|---|---|
| T | 0.042 | 0.076 | 0.010 |
| I | 0.003 | 0.014 | 0.000 |
| Cb | 0.101 | 0.163 | 0.014 |
| Ch | 0.031 | 0.035 | 0.010 |
| Ctk | 0.111 | 0.132 | 0.014 |
| Cyk | 0.042 | 0.087 | 0.010 |
| Cok | 0.083 | 0.135 | 0.003 |

## Readings

- Guards: Cb's G success 0.101 (floor 0.05: ok); T's G success 0.042 (ceiling 0.90: ok)
- **1. PRIMARY: (Ctk − Cb) in GP:** -0.031 [-0.080, +0.014] -> **no**

Secondary (each with its interval):
- (Ctk − Cb) in GS: +0.000 [-0.017, +0.017] -> no
- (Ctk − Cb)GP − (Ctk − Cb)G: -0.042 [-0.097, +0.010] -> no
- (Ctk − Cyk)GP − (Ctk − Cyk)G: -0.024 [-0.062, +0.017] -> no
- Ctk − Ch in GP: +0.097 [+0.049, +0.146] -> yes
- Pain per lid tried, days 1-30, Ctk − Cb in GP: -0.014 [-0.024, -0.005] -> yes (less)

## Reported

- G: Ctk − Cyk +0.069 [+0.035, +0.104]; Cok − Cb -0.017 [-0.059, +0.021]; Ctk − Cb at day 60 +0.042 [+0.004, +0.080]
- GP: Ctk − Cyk +0.045 [+0.010, +0.083]; Cok − Cb -0.028 [-0.073, +0.017]; Ctk − Cb at day 60 +0.000 [-0.049, +0.049]
- GS: Ctk − Cyk +0.004 [-0.010, +0.017]; Cok − Cb -0.010 [-0.024, +0.004]; Ctk − Cb at day 60 +0.010 [-0.007, +0.028]
- Cb: tries lost in GS 715; GP copy weight to the expert 1.000, to the non-expert 1.000; pain per lid (GP) 0.757
- Ch: tries lost in GS 716; GP copy weight to the expert 0.500, to the non-expert 0.500; pain per lid (GP) 0.780
- Ctk: tries lost in GS 715; GP copy weight to the expert 0.998, to the non-expert 0.300; pain per lid (GP) 0.743
- Cyk: tries lost in GS 716; GP copy weight to the expert 0.639, to the non-expert 0.642; pain per lid (GP) 0.770
- Cok: tries lost in GS 714; GP copy weight to the expert 1.000, to the non-expert 0.000; pain per lid (GP) 0.739
