# C1.5: implementation readings (written before any data)

How `c15.py` reads the points that `questions.md` (C1_5-frozen, with correction 1) leaves open.

## The home
- **C1's home** (`c1.Home`) is unchanged: the looks, the routines and the day stream. The routine steps carry no
  requests (correction 1).
- **Asking moments** (correction 1): 24 a day, after the day's routines. Their draws come from their own stream
  (`[seed, 12, day, 99]`), the same in every arm. In each moment:
  - the kind is drawn equally from order, neg_first, neg_last and plain;
  - 4 different things of the 30 are drawn; the first two are X and Y. For any kind but plain, the draw is repeated
    until X–Y is not a held-out pair;
  - the 4 are then shuffled in view.
- **Held-out pairs:** 87 (20% of 435) per child, from `[seed, 15]`.
- **The moment starts from an empty memory.** The request sentence is heard once and held for both acts of an order
  request. The second act has the "second" flag set, and the window then holds X's look (the parent took X, right or
  not).
- **The parent's answer is the reward** (1 if right). It is not heard: the moment ends. In routine steps the child
  hears what it heard in C1.
- **Plain frames** are C0-A's "asking" frames (life or test part). Two-thing frames come from `corpus_c15.json`, made
  by the c15-corpus job (qwen2.5:7b) and committed before any run; every reply is in `corpus_c15_raw.json`.

## The child
- **Input:** the sentence code (B, P and Q 16 numbers; K 128), the child's-turn flag, the second-act flag, and the
  window of 4 looks (C1's W). Then 32 tanh units, scores look·M·h, and a learned "wait".
- **P:** positions past the 12th share the 12th's embedding.
- **K:** words past the 8th are not heard.
- **Q and Q−:** an Elman layer of 16 units, A·e + U·r + c, starting from 0. The gradient runs back through every word.
  - **Q−'s shuffle** is drawn fresh at each hearing: in life from `[seed, 30]`; in the probes from a key fixed per
    probe.
- **Learning:** C1's two rules, learning rate 0.05, baseline rate 0.01, the gradient norm clipped at 1.0 (C1's
  reading). Words not in the vocabulary are skipped.

## The probes
- **For each held-out pair and each kind** (order; negation, both forms; the exploratory "after"), the scene is fixed
  by `[seed, 20, kind tag, pair]`: X, Y and two others, their looks and their order, and the frame index. Both twins use
  the same scene.
- **Acts are greedy** (the arg-max, wait included). Learning is off.
- **Also measured:** test frames vs life frames on the held-out pairs, and test frames on 87 in-life pairs (from
  `[seed, 21]`).
- **Plain probes:** each of the 30 things, one fixed scene.
- **Chance:** the first act 1/5; among the two named things 1/2.
