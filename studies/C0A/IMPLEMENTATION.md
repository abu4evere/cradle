# C0-A: implementation readings

The frozen plan (`questions.md`, tag `C0A-frozen`) leaves some small points open. This file records how `c0a.py` reads
each one. It was written before any C0-A data. None of these readings was chosen by looking at results; they were checked
only on a stand-in corpus (in `scratch_test/`, not committed) to confirm that the code runs.

## The scene stream
- **Random streams:** `default_rng([seed, 1])` draws the scene stream: looks, never-together pairs, moments, targets,
  attention draws and frame choices. `[seed, 2]` draws arm F's daily name shuffles. `[seed, 3, arm]` draws the
  child's sampled actions. `[seed, 4]` draws the initial weights, so all neural arms with the same d start alike.
  `[seed, 5, day]` draws growth. `[seed, 9, day, test]` draws the test trials.
- **Every possible response is drawn in advance:** each moment holds six attention draws and six frame choices:
  0 naming/background/asking, 1 praise, 2 "no", 3 "this one", 4 handing/confusion/whatwant. Only the child's action
  picks which one is used.
- **The target** is drawn evenly over the things in view.
- **Instances:** each sighting in daily life picks one of the 3 daily instances at random.
- **Never-together pairs:** a moment's things are redrawn until no never-together pair is in view.
- **GL** lives 4,320 days, so its stream arrays are longer and its fingerprint differs from the other arms'. GL is
  exploratory and is compared with nothing under the decision rule. The "identical across arms" check covers the ten
  1,080-day arms.

## The parents
- **Asking:** the child hears the asking frame first (with no cue), and associates on it like any heard sentence. Then
  it acts, then it gets the reward and the response.
- **Want:** the wanted thing is the moment's target. The child may say any word of its vocabulary, which is every token
  in the corpus (questions.md, "The split"), or stay quiet. If the word is the name of a thing in view, the parent
  hands that thing. If two things in view share the name (the same category), the first one is handed. The reward is 1
  only if the handed thing is the wanted one.
- **Arm F:** each day, category c is called `NAMES[perm[day][c]]` in everything the parents say (naming, asking,
  praise, "no", "this one", handing). The parents also *understand* the child's words through the same day's shuffle,
  so a word the child says is mapped back to the category the parents call by that word that day. F's tests use the
  real names.
- **Background flag:** with probability 0.5, it falls on a random thing in view.
- **The "another thing in view" flag** (0.10): it falls on one of the other things in view, picked by the moment's
  pre-drawn index.

## The child
- **Hearing:** words that are not in the vocabulary are skipped. In tests this means a nonce word is unknown, so the
  novel-word sentence is heard without it. A sentence with no known words gives the zero vector.
- **Association's gradient:** u is the mean of the heard words' rows, so each occurrence of a word gets 1/n of dL/du. A
  word that appears twice gets two such steps.
- **The buffer** holds the looks of the last 20 sightings, added after each moment. The current moment's things are
  therefore never in it as negatives. A buffered look can be another sighting of the same category; the plan does not
  exclude these, so they stay.
- **REINFORCE:** the advantage uses the baseline *before* that action's update. The baseline then moves by
  0.01 × (r − baseline). There is one baseline for handing and one for saying.
- **Saying:** the gradient flows into all of E's rows, the biases c, the quiet logit and W.
- **Growth (arm C):** at the start of 0-based day 375 (16 columns) and day 735 (32 columns). Tests run at the end of
  days 90, 180, … (1-based), so growth never falls on a test day.
- **Learning switches:** G and GL skip association but keep both rewards. E skips both, and its weights are checked to
  be unchanged.

## The counting baseline (K)
- **Clusters:** it clusters every look it sees in a heard sentence's moment. A look that fits no cluster in a test
  scores 0.
- **Ties:** in daily life it hands a thing with the highest score, ties broken at random. It never hands "nothing". In
  tests, ties are broken by the trial's pre-drawn number, so tests stay deterministic.
- **Saying:** it says the word with the highest count for the wanted thing's cluster, or stays quiet if it has none.
  That word can be a common word such as "the". This is the plan's rule taken literally.

## Tests
- **The trials** are the same in every arm: the same things, looks, targets and frames.
- **A never-together pair:** each trial includes one such pair, plus 2 other categories, in shuffled order. New
  instances use instances 3–4; all other tests use daily instances.
- **Novel word:** the "target" is a random one of the four, so chance is 0.25 whatever the child does.
- **Repair with correction:** the child hears the "no" frame with Y and the asking frame with X as one heard input:
  u is the mean over both sentences' words. Y has been removed, so 3 things remain.
- **Request by word:** this is the request trials grouped by the target's name.

## The sentences (added 10 November 2026, before any child ran)
- **First corpus job (run 42789280466) failed the minimums:** naming 0, asking 0, "no" 0, "this one" 0, handing 1
  (praise 52; the kinds without a slot passed). The kept praise frames were near copies of the example. So the model
  most likely wrote real object names instead of {X}, and the check rightly dropped those lines. The raw replies were
  not saved, so this cannot be confirmed.
- **Fixes to `make_corpus.py`:**
  - a firmer instruction for the slot (a good and a bad example, and "do not copy the example");
  - the placeholder's written variants ({x}, {{X}}, [X], <X>) are read as {X};
  - every reply is saved to `raw.json`.

  The checks, the minimums, the split and the model are unchanged.
- **The 3 extra rounds** are counted within each corpus job. The failed job is recorded here, not hidden.
- **Second corpus job (run 42836870786) also failed the minimums:**
  - only "this one" fell short (36 of 40; the others were met);
  - its raw replies show the model repeating the one example ("This one, the {X}.") or padding it with unrelated
    objects;
  - the kept frames also often missed the moment's meaning: asking frames that were not requests, and praise that
    named {X} as if it were the child.
- **Fix:** each moment is now described with what has just happened and 2–4 varied examples. The checks, the minimums,
  the split and the model are unchanged.
- **The child is unaffected either way:** it hears a sentence as a bag of words, and only the name carries the thing.
  The frames' meaning matters for honesty and for later studies.
