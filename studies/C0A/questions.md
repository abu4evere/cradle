# C0-A: grounded word association. Can a newborn neural child learn ten words by living with two AI parents?

**Frozen plan** (git tag `C0A-frozen`, before any code or data). From `docs/C0_plan_draft.md` and council 2
(`docs/council_2_C0_2026-11-08.md`).
**Sign-off:** the creator, 8 November 2026, 21:40 ("yessir", in the Claude Code session, answering "shall I freeze C0-A
and build it?").

## The question
A newborn child (a small neural network, **never a language model**, born knowing no words) lives three world-years in
one room with two AI parents and ten things. Afterwards, when a parent asks for a thing:
- in a sentence frame the child has never heard,
- with four things laid out in a combination never seen together,
- and with no looking or pointing,

does the child hand over the right thing?

**What C0-A is and is not.** C0-A is a working base: grounded word association. **It makes no claim about entering a
culture.** That is for C1 (an unlabelled turn-taking routine) and C2 (social reference), which come next.

## The home
- **Ten things** (categories): ball, cup, spoon, bread, apple, banana, shoe, hat, book, duck. Each name is one word.
- **Looks:**
  - each category has a centre: a 16-number vector drawn N(0, 1) per child seed;
  - each instance is the centre plus a fixed offset drawn N(0, 0.5²) per number;
  - each sighting adds noise N(0, 0.2²);
  - daily life uses 3 instances per category, and 2 more per category are kept for the new-instance test;
  - **the child never gets names, labels or ids for the things, only looks.**
- **Days and moments:**
  - a day is 20 moments, and life lasts 1,080 days (3 years of 360 days), so 21,600 moments;
  - in each moment, 2 or 3 things (equal chance) are in view, drawn without replacement;
  - **9 of the 45 pairs** of categories (drawn per seed) never appear together in daily life.
- **The scene stream is fixed in advance per seed**, the same in every arm. It covers:
  - the things and instances in view;
  - the parent's act;
  - the target;
  - the attention draws;
  - the frame for every possible response.

  Only *which* response happens depends on the child's action. **Results report shared scenes and diverging
  interaction histories; the arms are paired by scene stream, not by identical experience.**

## What the parents do (the engine decides; the language model only words it)
**Act shares per moment:** naming 0.35, asking 0.25, want 0.15, background 0.25.

**Naming.** The parent shows a target thing in view and says a naming frame with that thing's name.

**Asking.** "Can you give me the {X}?" (an asking frame), for a target X in view. The parent looks at the child, so
there is no attention cue. The child hands one thing or nothing:
- **right:** a praise frame with X; reward 1;
- **wrong** (it hands Y): a "no" frame with Y, then a "this one" frame with X; reward 0;
- **nothing:** a "this one" frame with X; reward 0.

**Want.** The child wants one thing in view (out of reach) and may say one word it has heard, or stay quiet:
- **the wanted thing's name:** a parent hands it over with a handing frame ("Here's your {X}!"); reward 1;
- **another name of a thing in view:** the parent hands that thing (a handing frame with its name); reward 0;
- **any other word:** a confusion frame (no name); reward 0;
- **quiet:** a "what do you want" frame (no name); reward 0.

**Background.** A sentence with none of the ten names.

**Attention cues, in the arms with joint attention** (an inborn "where is the parent looking" flag on one thing in
view):
- **for every heard frame that names a thing** (naming, praise, "no", "this one", handing), the flag goes:
  - on the named thing with probability 0.75;
  - on another thing in view with 0.10;
  - on no thing with 0.15;
- **background:** on a random thing in view with 0.5, else none;
- **asking:** none.

**Perfect cues (arm P):** always on the named thing; background and asking get none.

**No joint attention (arm D):** never a flag. Nothing else (no place, no "held" mark) singles out a thing.

## The sentences
**Generated once** by qwen2.5:7b through Ollama in a GitHub cloud job (`c0a-corpus`), and committed before the run.

**Frame kinds with a slot {X}:** naming, asking, praise, no, this, handing.

**Kinds without a slot:** confusion, whatwant, background.

**Checks (a script), applied to every sentence:**
- the slot appears exactly once in slot kinds, and not at all elsewhere;
- none of the ten names (or their plurals) appears outside the slot;
- no digits;
- 2–14 words;
- duplicates are dropped (lower case).

**Minimums:**
- each slot kind needs at least 40 valid frames;
- confusion and whatwant need at least 10 each;
- background needs at least 150;
- up to 3 extra rounds of asking the model are allowed.

**The split:**
- per slot kind, 20% of the valid frames (random.Random(20261108) shuffle) are **kept back for tests only**;
- daily life uses the other 80%;
- words are lower-case tokens (`[a-z']+`);
- the child's vocabulary is every token in the corpus;
- ten nonce words (dax, wug, blicket, toma, fep, zib, kiv, modi, pilk, gazzer) must appear nowhere in it.

## The child's brain (inborn mechanisms declared; no inborn knowledge)
**Hearing:** a sentence is the mean of the learned embeddings of its words (dimension d): u = mean E[w]. This is the
declared simplification that words come already separated.

**Seeing:** each thing in view gives z = W·look (W is d×16).

**The shared word–look space:** a thing's score is s = u·z.

**No memory between moments,** except a buffer of the last 20 looks seen (for comparison).

**Learning by association** (all arms except G and E), on every heard sentence:
- loss = −log( Σ_{i∈Pos} e^{s_i} / Σ_{j∈Pos∪Neg} e^{s_j} );
- Pos = the flagged thing, or all things in view if there is no flag;
- Neg = the other things in view plus the 20 buffered looks;
- plain SGD on the heard words' rows of E and on W, learning rate 0.05.

**Learning from inborn rewards** (all arms except E): REINFORCE with a running-mean baseline (rate 0.01, one per action
kind), learning rate 0.05.
- **Handing:** logits are s_i for each thing in view, plus a learned "nothing" logit.
- **Saying:** logits over the vocabulary are E[v]·z_wanted + c_v (a learned bias per word), plus a learned quiet logit.

**Initial weights:** E and W drawn N(0, 0.1²); biases 0. Actions in daily life are sampled; actions in tests are
greedy.

**Brain sizes:**
- d = 64 (large);
- d = 8 (small);
- d = 32 (fixed control);
- growing: 8, then 16 at day 375, then 32 at day 735. Old weights are kept; new columns are drawn N(0, 0.01²). Growth
  is never on a test day.

## Arms (16 children each, seeds 1–16, paired by scene stream)
| Arm | Brain d | Cues | Learning | Names |
|---|---|---|---|---|
| **A** (main) | 64 | joint attention (ambiguous) | association + reward | real |
| B | 8 | ambiguous | association + reward | real |
| C | 8 → 16 → 32 | ambiguous | association + reward | real |
| H | 32 | ambiguous | association + reward | real |
| D | 64 | **none** | association + reward | real |
| P (positive control) | 64 | **perfect** | association + reward | real |
| G (reward only) | 64 | ambiguous | **reward only** | real |
| E (control) | 64 | ambiguous | **none** | real |
| F (control) | 64 | ambiguous | association + reward | **shuffled each day** |
| K (counting baseline) | none | ambiguous (as A) | counts | real |
| GL (exploratory) | as G | as G | as G | real; **12 years** |

**F:** each day the parents' speech uses a fresh random permutation of the ten names. F's tests use the real names.

**K (non-neural):**
- online clusters of looks: a look joins the nearest centre if its distance is under 2.0, else it starts a new cluster;
  the centre is a running mean;
- counts of word × cluster for the flagged thing (or each thing in view, weighted 1/k, without a flag);
- it scores a thing by Σ over the heard words of count(w, c) / count(w);
- it acts greedily in daily life, gets the same parent responses, and says the word with the highest count for the
  wanted thing's cluster.

## Tests
- **When:** at days 90, 180, 270, 360, 540, 720 and 1,080 (GL also at 1,440, 2,160, 2,880, 3,600 and 4,320).
- **Learning is frozen** during tests, and tests never change daily life. Each trial shows 4 things, including at least
  one never-together pair. The parent gives no attention cue, and the child acts greedily.
1. **Request:** 60 trials. Daily instances and a kept-back asking frame. Correct = it hands the target. Chance 0.25.
2. **New instances:** 60 trials, as request but with the never-seen instances.
3. **Novel word:** 30 trials. A kept-back asking frame with a nonce word in the slot. Scored against a random one of
   the four. Chance 0.25.
4. **Saying:** 30 trials. The child wants a thing in view. Correct = it says that thing's name.
5. **Repair:** 30 paired trials. The child has (by construction) just handed a wrong thing Y, which the parent now
   holds, so 3 things remain. Then it chooses again:
   - **with correction:** it hears a kept-back "no" frame with Y together with a kept-back asking frame with X;
   - **without correction:** it hears the asking frame only.

   Chance 1/3.

## Outcomes and decision rule (exploratory)
**Statistics:**
- per-child accuracy;
- 95% intervals by bootstrap over the 16 seeds (10,000 draws, `numpy.random.default_rng(20261108)`, percentiles 2.5
  and 97.5);
- differences between arms are paired, with the same resampled seeds for both arms;
- n = 16 children beside every measure.

**Reading 1, "associates words" (primary):** at day 1,080, A's request accuracy minus 0.25 has a lower bound above 0,
**and** A − F has a lower bound above 0.

**Reading 2, "uses correction":** at day 1,080, A's repair accuracy with correction minus without correction has a
lower bound above 0. **The honest expectation is no:** this brain has no memory between moments. The measure is
pre-registered so that C0-A cannot be over-read (council 2, DeepSeek).

**Secondary (reported with intervals, no gate):**
- B − A, C − A, H − A, C − H, D − A, G − A, K − A and P − A on request accuracy at day 1,080;
- A's new-instance accuracy (a separate endpoint);
- saying accuracy against E;
- learning curves;
- accuracy per word;
- exposure counts (the hearings of each name by day 1,080);
- GL's curve.

## Validity (hard stops; failing any one means C0-A is invalid, not a finding about words)
- **P learns:** the lower bound of P − 0.25 is above 0 at day 1,080. If even perfect cues fail, the learning code or
  its rates are at fault.
- **The controls sit at chance:** E and F request accuracy at day 1,080 has a 95% interval within [0.17, 0.33].
- **A's novel-word accuracy** at day 1,080 has a 95% interval within [0.17, 0.33].
- **Code checks** (`checks_c0a.py`, run before the data):
  - test trials carry no attention cue;
  - kept-back frames and never-together pairs never occur in daily life;
  - the scene stream is identical across arms;
  - a numerical gradient check of both learning rules;
  - E's weights never change;
  - the same seed gives the same result twice;
  - the corpus checks pass.
- **Blind recompute:** GPT and Gemini recompute reading 1 and the validity numbers from the raw per-child files,
  without the analysis script.

## The assistant's prior
- A associates words: about 85%.
- D associates words: about 45%.
- B within 0.05 of A: about 60%.
- A's saying beats E: about 40%.
- Uses correction: about 10%.
- G associates words at 3 years: about 25%.
- K matches or beats A: about 50%.
