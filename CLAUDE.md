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

## Status (16:28, 8 November 2026)
- **Milestone 1 started:** `cradle/world.py` and `cradle/words.py` hold a 2D city of about 55 people (12 founding families) with roles,
  a daily rhythm, school, births, ageing and a small vocabulary. `python run.py 10 1` runs 10 years in about
  7 seconds.
  - **This v0 is scripted.** The creator then asked for intelligent, English-speaking AI people. The scripted city
    stays as the far-city layer.
- **The first cloud test is ready but not yet run:**
  - `.github/workflows/llm-test.yml` installs Ollama on an ubuntu runner and pulls the model;
  - `tools/llm_test.py` has two AI parents (Mira and Tomas) talk in English about their 3-week-old baby, and times it.
- **Blocked:** the repository is local only. Creating the **public** GitHub repo was blocked by the app's safety check.
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
