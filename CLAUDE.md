# Cradle: read this first (any assistant, any account)

**Cradle is the creator's second project** (started 8 November 2026), a sister of ACL (`D:\acl`, which has its own
`CLAUDE.md` and handoff). Both share one mission: Bob, a mind with autonomy and a cumulative culture.
- **ACL asks:** can culture appear from nothing?
- **Cradle asks:** can a mind that is not pre-programmed grow up inside an existing culture and become part of it, or
  will it fall short because of its brain?

Read `PLAN.md` (the design, in the creator's own words), then the log at the end of this file.

## What the creator decided (8 November 2026; their words are in ACL's local book notes)
1. **A developed city of AI people:** a doctor, teachers, shopkeepers, workers, families. "Build already developed city
   … our agent will born he/she got ai father and mother just like our normal life."
2. **The Matrix / Neo principle:** "Our agent is Neo inside matrix he does not know about reality and matrix … all
   other people are ai nps and he cannot distinguish."
   - The agent is raised exactly as NPC children are. Nothing is made only for it.
   - It knows only what it senses.
3. **The AI people must be intelligent and speak English:** "they cannot be just nps programmed agents they should be
   more intelligent and we should find free option".
   - **The design:** Generative-Agents-style minds (persona, memory, daily plan, reflection, English speech) for the
     people near the agent; simple routines for the far city, upgraded when they come near (as open-world games do).
4. **The model runs on the cloud only, never on the creator's PC:** "no we should run cloud model not from pc";
   "lets start with github then if its not enough we will switch to better models".
   - **Start:** a free open model through Ollama on GitHub's ubuntu runners (`qwen2.5:3b` first).
   - **Later, if needed:** a free API tier (Gemini or Groq). That needs the creator to make an account and a key and
     store it as a secret. **The assistant never handles keys and never spends money.**
5. **The Director:** "inside cradle their history will be written by you" … "you also live inside that game as ghost
   and control everything what is going to happen".
   - Routine hours run by themselves.
   - Every world month, and at once on notable events, the world pauses and the assistant (the ghost) decides what
     happens next.
   - Between sessions, an autopilot director plays the ghost from the assistant's library of situations.
   - **Every ghost decision goes into a chronicle.**
6. **The agent is a learning neural network, never a language model.** It starts knowing nothing, English included.
7. **Measures,** against NPC children of the same age:
   - daily rhythm;
   - language (understands and uses English words);
   - skills (school, later a job);
   - belonging (friends, asking for and giving help).
   
   Different brains (small, larger, growing with age) test "is it the brain".

## Cradle's mission (the creator, 10 November 2026, after C0-A)
"from cradle main mission is that child to grow up with society have friends explore its world go school sum like
that. Just think about ordinary person life and that child agent should pass the same timeline same pathway just like
humans. Mission is to find out if that child can keep up with society if not find why and try to solve that."
- **The child lives an ordinary human life course:** a baby at home, a toddler, friends and play, exploring, school,
  and later work. Its timeline is the NPC children's timeline.
- **The question at each stage:** does it keep up with the NPC children of its age? If it does not, find why, and try
  to fix the brain.
- **The answer goes back to ACL:** "maybe we find our answer from cradle then we will transform that cradle child
  brain to acl with some edits".
- C0-A (words, at home) is the first rung, and it passed. But it was too easy to tell brains apart.

## Status (16:28, 8 November 2026)
- **Milestone 1 started:** `cradle/world.py` and `cradle/words.py` hold a 2D city of about 55 people (12 founding families) with roles,
  a daily rhythm, school, births, ageing and a small vocabulary. `python run.py 10 1` runs 10 years in about
  7 seconds.
  - **This v0 is scripted.** The creator then asked for intelligent, English-speaking AI people. The scripted city
    stays as the far-city layer.
- **The first cloud test is ready but not yet run:**
  - `.github/workflows/llm-test.yml` installs Ollama on an ubuntu runner and pulls the model;
  - `tools/llm_test.py` has two AI parents (Mira and Tomas) talk in English about their 3-week-old baby, and times it.
- **Resolved 17:09:** the creator created the public repo (github.com/abu4evere/cradle). Earlier: the repository was local only. Creating the **public** GitHub repo was blocked by the app's safety check.
  **The creator must run it themselves:**
  `gh repo create abu4evere/cradle --public --source=D:/cradle --remote=origin --push` (gh at `C:\Users\User\gh\bin\gh.exe`).
  Then: `gh workflow run llm-test.yml -R abu4evere/cradle -f model=qwen2.5:3b -f turns=12`. Read the run page or the
  artifact for speed (tokens per second, seconds per turn) and quality.
- **For GPT:** `docs/intro_for_gpt.md`, an introduction the creator can paste into GPT.

## Next steps (in order)
1. After the repo exists, run the llm-test, and report speed and English quality to the creator simply.
2. **The NPC mind** (`cradle/minds.py`): persona, memory stream, a daily plan by the model, conversations when people
   meet, using the model only for people near the agent.
   - Budget the model calls per world-day from the measured speed.
   - Checkpoint the world state so a long life can span many cloud jobs (each job is at most 6 hours).
3. **The Director** (`cradle/director.py`):
   - the pause points;
   - a library of situations (small daily surprises and big life events);
   - the chronicle;
   - the autopilot.
4. **The agent:** a body, senses (nearby sight, heard words as tokens), and a learning neural network that learns from
   its feelings and by watching and copying.
   - Start small, and compare brains.
   - Plans are written before tests, as in ACL.

## Rules
- The agent never contains a language model.
- No API keys or money handled by the assistant.
- Nothing runs on the creator's PC except light code tests. The model runs on the cloud.
- Public surfaces (repos, posts) only by the creator.
- Talk to the creator simply.
- The creator's ideas go, in their exact words, into ACL's local book notes
  (`D:\acl\drafts\book_rewrite\part2\notes_for_book_<date>.md`).
- Commits: no "Claude" or Co-Authored-By lines (the creator's rule in ACL).

## Log
- 2026-11-08 16:15: project started. `PLAN.md`; city v0; the Neo principle; the Director (a live ghost); cloud-only
  model; the llm-test is ready; the public repo is waiting for the creator; the introduction for GPT is written.
- 2026-11-08 16:34: built and tested with a stand-in model (no AI model; nothing on the PC):
  - `cradle/minds.py`: Generative-Agents-style minds for the focus people (persona, memory stream with recall, speech by the model, a daily call budget, default 8); `OllamaModel` for the cloud, `MockModel` for tests.
  - `cradle/director.py`: the ghost.
    - Pause points monthly and on notable events (births and illnesses near the focus, each noticed once).
    - Live mode writes `pause.json` and stops.
    - Autopilot picks from a library (sick, visit, festival, storm, job change, friend moves, lost toy), with pacing.
    - A chronicle records who decided what.
  - `world.save` and `world.load`: a long life spans many cloud jobs.
  - `run.py`: options --model mock|ollama:<name>, --live, --save, --load, --apply EVENT and --note.
  - Until the agent exists, the focus is the youngest founding couple and their children. Their newborns join it.
  - **Next:** once the creator has created the repo, run llm-test, then set the call budget from the measured speed.
- 2026-11-08 17:13: the creator created github.com/abu4evere/cradle (public) and pushed. Next: the llm-test on the cloud.
- 2026-11-08 17:23: first cloud test (run 42529889010, qwen2.5:3b, ubuntu runner with 4 CPUs and 15 GB of RAM): 18.8 tokens/s, 1.66 s per turn. Natural English, but the conversation drifted from the baby into a repetitive goodnight loop (small models are agreeable and repeat; the council warned of a thin culture). Fixes: world events fed in, memory of the day, a repetition limit, real concerns in the personas. Results in `results/`. Council 1 (GPT, Gemini, DeepSeek) in `docs/council_1_2026-11-08.md`. Recommended to the creator: GPT's C0 (one household, 10 grounded words, three brains, controls) as the first experiment. Awaiting their decision.
- 2026-11-08 20:34: city tests with real AI minds (qwen2.5:3b, 7 world days, 30 calls a day):
  - Test 1 (run 42543817574): everyone talked about the clock and meals, at wrong times; a one-year-old spoke; memory labels leaked.
  - Fixes: time in words, a concern per person, a concrete moment, no AI speech under 4, labels cleaned.
  - Test 2 (run 42544840061): more variety (roof, recipes, drawing, rain, stories), but the 3B model reads the scene description aloud, repeats its one concern (the roof) constantly, and mixes up names and roles; 7.6 s per call.
  - Logs in `results/`.
  - **Next options:** prompts that never echo the scene and give the concern only sometimes; a larger free model (qwen2.5:7b, slower); or a free API tier (the creator must make the key).
- 2026-11-08 20:49: city test 3 (4 world days; the scene as unspoken background, the concern sometimes, a clear speaker and listener):
  - **3B** (run 42546410924), 6.1 s per call: no echoing of the scene, but a repetitive 'how was your day' and some wrong names.
  - **7B** (run 42546418239), 11.8 s per call: the most natural speech (a child shows a butterfly or a leaf; the teacher: 'Want to show it to the class?'), fewer errors; it still mixes up Mom and Dad.
  - **Budget per 6-hour job:** about 3,500 calls (3B) or 1,800 (7B), so a full city childhood is slow.
  - **Direction:** the C0 household first; a free API tier could give better and faster people (the creator's key).
- 2026-11-08 20:56: C0 plan drafted (docs/C0_plan_draft.md; not frozen, waiting for the creator):
  - one home, two AI parents, ten things, a newborn neural child, three years;
  - arms: large, small, growing, blank (no joint attention), learning off, shuffled words;
  - the test: new sentences, new layouts, no cues.
  Research notes on first-word learning are in docs/research_word_learning_2026-11-08.md (records and abstracts only).
- 2026-11-08 21:16: council 2 on the C0 draft (GPT, Gemini, DeepSeek; two rounds; docs/council_2_C0_2026-11-08.md):
  - C0 becomes C0-A, grounded word association, with validity fixes;
  - new: a reward-only arm G, a 32-dim control H, a counting baseline, and novel-word and repair tests;
  - then C1 (routine) and C2 (social reference);
  - the changes are added at the top of docs/C0_plan_draft.md. Still a draft; waiting for the creator.
- 2026-11-10 04:23: C0-A build (sleep mode):
  - frozen plan committed and tagged `C0A-frozen` (the creator's sign-off, 8 November, 21:40);
  - corpus job `c0a-corpus` launched on the cloud (run 42789280466; qwen2.5:7b);
  - `studies/C0A/c0a.py` (the simulation), `checks_c0a.py` (the code checks), `IMPLEMENTATION.md` (readings of open points), `analyse_c0a.py` (written before any data) and the workflow `c0a-run.yml` (checks, then 11 arms × 16 children, then the analysis);
  - on a stand-in corpus (scratch_test/, not committed) every code check passes except the corpus minimums (expected). Arm A learns; E stays at chance.
  - **Next:** commit corpus.json when the job ends, then run c0a-run on the cloud, then the blind recompute.
- 2026-11-10 10:31: C0-A corpus: jobs 1 and 2 failed the minimums (the model wrote object names; then 'this one' collapsed into copies). Prompt fixed twice (recorded in studies/C0A/IMPLEMENTATION.md). Job 3 (42841768106) met them; corpus.json and corpus_raw.json committed; code checks All: PASS on it. Weakness: some frames miss their moment's meaning (reported with the results). **C0-A run launched: c0a-run 42845179399** (11 arms x 16 children, then the analysis).
- 2026-11-10 10:39: **C0-A final** (run 42845179399; recomputed by GPT and Gemini): valid; associates words YES (A request 1.000 in all 16; A - F 0.734 [0.691, 0.775]); uses correction NO (-0.054). But every learning arm is at ceiling by day 90, so the brain-size, growth and joint-attention questions are unanswered; only reward-only (G) is slower and counting (K) worse. Next (harder C0-A or C1) is for the creator. studies/C0A/findings.md.
- 2026-11-10 13:37: Life ladder draft (docs/life_ladder_draft_2026-11-10.md); C0-B plan drafted (studies/C0B/questions.md: 30 things in 10 look-alike families, 6 moments a day, tests from day 3, a look-alike test; learning speed as the arm outcome). Next: council, then freeze and build (the creator: "do not ask me go ahead"). Open question for the creator: who the other children are (AI, neural, or a mix).
- 2026-11-10 13:50: Council 3 on C0-B (GPT 65%, Gemini 85%, DeepSeek 35-45% as drafted): a difficulty check first, learning speed as an area under the curve. C0-B frozen (tag C0B-frozen; the creator's standing go-ahead), built (c0b.py from c0a.py; checks All: PASS), difficulty check chose L1 (6 moments a day, sd 0.35), analysis written before data; run c0b-run 42879225829 on the cloud.
- 2026-11-10 14:01: **C0-B final** (run 42879225829, level L1; recomputed by GPT and Gemini): associates words in a hard home (A - F 0.733); learning speed: size matters (B - A -0.141), growing late is slower (C - H -0.123), joint attention matters (D - A -0.157), reward only far slower; most catch up by day 1,080, but small and growing brains stay weaker on look-alikes (0.80 against 0.93) and saying. Correction hurts (bag-of-words hearing). Counting baseline fastest but fails new instances. studies/C0B/findings.md.
- 2026-11-10: **The creator decided the other children are a mix:** AI adults, plus a few neural children as peers ("i think mix fits better"). Recorded in docs/life_ladder_draft_2026-11-10.md.
- 2026-11-10 23:15: Council 4 on C1 (GPT 65%, DeepSeek 65%; Gemini's tab failed). C1 frozen (tag C1-frozen; the creator: "can we also run cradle too"), built (c1.py: routines over a shared 12-thing pool; arms N, P, W, R, S; prediction through time + REINFORCE act), checks All: PASS (gradients through time), launched on the cloud (c1-run 42958035264).
- 2026-11-11 00:37: **C1 results** (run 42958035264): valid; reading 'it keeps up'. Memory (window W 0.905, recurrent R 0.911) beats no memory (N 0.767) on anticipating and turns; order learned (R - S +0.18); R = W. GPT's blind recompute matches exactly; Gemini pending (could not read the file twice). studies/C1/findings.md.
- 2026-11-11 02:50: Council 5 on C1.5, word order (GPT 65%, DeepSeek 45%; Gemini's tab kept reloading). C1.5 frozen (tag C1_5-frozen; the creator: "keep working i am going sleep keep up all projects"): arms B (bag), P (position), K (fixed slots), Q (recurrent reader), Q- (shuffled); 24 children; matched probes on held-out pairs. Correction 1 before any data: a stub smoke showed no arm learned the names when requests sat inside routines (the window memory answered them), so requests moved to 24 asking moments a day from an empty memory. Corpus made on the cloud (c15-corpus 42980418294, minimums met), checks All: PASS, analysis written before data; launched c15-run 42982085632.
