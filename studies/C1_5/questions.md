# C1.5: word order. Does the child hear "X, then Y" differently from "Y, then X"? (frozen plan)

**Frozen** as git tag `C1_5-frozen`, before any code or data.
**Sign-off:** the creator's standing instructions: "do not ask me go ahead bro"; "keep working i am going sleep keep up all
projects" (11 November 2026).

**History:**
- the draft is `docs/C1_5_draft_2026-11-11.md`;
- **council 5** (`docs/council_5_C1_5_after_2026-11-11.md`): GPT 65%, DeepSeek 45%; Gemini not reached. Its nine
  changes are all taken below.

**The rung:** C1 found that a child with memory keeps up with routines. But it hears a sentence as a bag of words (the
mean of word embeddings). So "the cup, then the spoon" and "the spoon, then the cup" are the same to it, and so are "not
the cup, the spoon" and "not the spoon, the cup". This rung asks whether a way of hearing order can learn what order
means, from an ordinary home where parents ask for things.

## The home
As C1 (same things, families, routines, parents, noise, 720 days, memory reset each night), with one thing added.

- **Requests:** at a child's turn, with chance ½, the parent makes a request instead of waiting. Four kinds, equally
  likely:
  - **order:** "the {X}, then the {Y}". The child must hand X first, then Y (two acts in a row; the step's needed
    thing is X);
  - **negation, first:** "not the {X}, the {Y}". The child must hand Y; X is wrong;
  - **negation, last:** "the {Y}, not the {X}". The child must hand Y; X is wrong. (Both forms, so "the last thing
    named" cannot pass);
  - **plain:** "the {X}" (C1's asking frames).
- **X and Y:** both are in view, with one or two other things. In life, X is the routine step's needed thing, and Y is
  another thing drawn from the 30. The pair must not be one of the child's **held-out pairs.**
- **Held-out pairs:** for each child, from its seed, 20% of the unordered pairs of the 30 things are never used
  together in any order or negation request in life.
- **During a request,** the sentence is held in mind for both of the order request's acts, with a flag saying "first"
  or "second" act. After each act the parent answers as in C1: the praise frame naming the thing if it was right, else
  the "this one" frame naming the right one (correction unchanged; council: keep it the same in every arm).
- **The frames** come from a corpus made once by the parents' model (qwen2.5:7b, as C0-A's), checked and committed
  before any run. The checks:
  - each two-thing frame holds {X} and {Y} exactly once;
  - order frames have {X} before {Y} and an order word ("then", "and then", "after that", "next");
  - negation frames have a negation word ("not", "no", "don't") just before the negated slot, in the stated position.
  - Frames are split ¾ life, ¼ test, as C0-A's.
  - An exploratory kind, **after:** "the {Y} after the {X}" (act order X, then Y; the word order reversed).

## The child (C1's arm W memory in every arm; arms differ only in how a sentence is heard)
| arm | hearing a sentence (word embeddings d 16, learned) |
|---|---|
| **B** | the mean of the word embeddings (C1's; the control) |
| **P** | the mean of (word embedding + a learned embedding of its position, positions 1–12) |
| **K** | the first 8 word embeddings in fixed slots, concatenated (zeros where there are fewer); binding by place |
| **Q** | a recurrent reader: an Elman layer of 16 tanh units reads the words in order; its last state is the sentence |
| **Q−** | Q, but the words of every sentence are shuffled (fresh each time it is heard) before reading: the order control |

- **The act** is C1's: a softmax over the things in view plus "wait". It now also takes in the first/second flag.
- **Learning** is C1's two rules, unchanged (next-step prediction, and REINFORCE on the parent's answer, learning rate
  0.05). Gradients reach the hearing parts (P's position embeddings, K's slots, Q's reader through the words).
  Nothing is tuned.
- **24 children per arm,** seeds 1–24, paired: the same homes, days, requests and draws in every arm.

## Tests (learning frozen; matched probes, as council 5 asked)
- **When:** days 30, 90, 180, 360 and 720.
- **How:** each probe starts from the same state for every twin: memory empty, the same 4 things in view (X, Y and two
  others, fixed per probe), the same parent and the same frame.
  - **Order probes:** every held-out pair, both orders ("X, then Y" and "Y, then X"), with test frames.
  - **Negation probes:** every held-out pair, both forms, both ways round.
  - **Plain probes:** each of the 30 things, with test frames.
  - **Exploratory:** in-life pairs (order and negation); "after" frames; life frames instead of test frames.
- **Measures (per child, then per arm):**
  1. **first-act order accuracy** on held-out order probes. This is the primary measure; the second act can be solved
     by "the named one not yet handed";
  2. second-act accuracy, and both acts right;
  3. negation accuracy (Y handed), and the share where X is handed;
  4. plain accuracy.
- **Chance, by the protocol:** first act, 1/5 (4 things plus wait); among the two named things, ½. Both right: the
  product. Reported beside every measure.

## Readings at day 720
- **Statistics:**
  - per-child accuracy; differences paired by seed;
  - 95% bootstrap intervals over the 24 seeds (10,000 draws, `numpy.random.default_rng(20261111)`).
- **"It hears order"** needs both:
  - Q − B on first-act order accuracy has a lower bound above 0;
  - Q − Q− has a lower bound above 0.
- **"Position is enough"** if P or K also beats B (lower bound above 0) and its difference from Q lies wholly within
  ±0.05 (an equivalence margin, fixed now).
- **"Not learned"** otherwise.
- **Negation** is read the same way (Q − B and Q − Q− on negation accuracy). It is a secondary reading.
- **Not informative:** if B's plain accuracy at day 720 is not above chance, the words themselves were not learned. Then
  no order reading is drawn.
- **Caution (GPT):** passing shows order-sensitive behaviour, not compositional understanding.

## Power (before the freeze)
- C1's per-child spread on turn-taking was sd 0.036–0.052.
- With about 170 held-out order probes per child, the probe noise adds at most sd 0.04.
- A paired difference of 0.05 with 24 children has a standard error of about 0.02, so it is found with high power.

## Validity (hard stops)
- **Code checks:**
  - B's sentence input is the same for a twin pair;
  - Q−'s order carries no information (two shuffles of the same sentence are equally likely);
  - held-out pairs never appear in a life request;
  - probes are identical across arms;
  - gradients equal finite differences (Q through the words, P, K);
  - the same seed gives the same result twice.
- **The corpus checks** above.
- **The blind recompute** by GPT and Gemini.

## The assistant's prior
- It hears order: about 55% (60% before council 5's stricter tests).
- Position is enough (P or K): about 35%.
- Negation learned by Q: about 40%.
- B at chance among the two named things on order: about 90% (by construction).
