# C0: can the child learn ten words by living with its parents? (DRAFT, not frozen; 8 November 2026)

**Status:** a draft for the creator. Nothing is built or run until the creator agrees (then it is frozen with a git tag
`C0-frozen`, as in ACL). Based on council 1 (`council_1_2026-11-08.md`): GPT's "C0", DeepSeek's blank-slate arm and
pre-registration, Gemini's warning that AI parents invent meaning.

## The question, simply
A newborn child (a small neural network, never a language model) lives in one home with two AI parents and ten
everyday things. The parents talk to it as parents do. **After three years of this life, when a parent says "give me the
cup" in a sentence it has never heard, with the things laid out in a way it has never seen, and with no pointing or
looking to help, does it hand over the cup?**

GPT's words (council 1): the first meaningful success is "a neural agent that initially cannot distinguish two objects,
learns their spoken names through experience … and correctly acts on those words in a new situation."

## The home
- **One room, two parents (Mom and Dad), one child.** No Director in C0 (nothing for it to do in one room); the
  Director is tested as its own condition later.
- **Ten things:** ball, cup, spoon, bread, apple, banana, shoe, hat, book, duck (a toy). Each has a fixed look (a
  random feature vector, like shape and colour) and is seen with small changes each time (light, angle). **The child
  gets looks, never labels or numbers for the things.**
- **A day** is 20 shared moments. In each moment 2 or 3 things are in view, at random places. Three years = about 21,600
  moments.

## What the parents do (the world engine decides; the language model only words it)
Council 1's fix for AI parents who invent meaning: **a stable engine decides every act; the model only supplies the
English sentence.** The parent's act in a moment is drawn from:
1. **Naming:** a parent holds or looks at a thing and talks about it ("Look at this {X}! Isn't it nice?").
2. **Asking:** "Can you give me the {X}?" The child hands one thing (or nothing). Right: praise ("Thank you, that's
   the {X}!"). Wrong: a gentle correction that names both ("No, that's the {Y}. Where's the {X}?").
3. **The child's wants:** the child gets hungry or wants to play (inborn needs). If it says the name of a thing it
   wants, a parent hands it ("Here's your {X}!"). If it says something that fits nothing in view, the parent is
   confused ("Hmm? What do you want, sweetie?"), never pretending to understand (Gemini's point).
4. **Background talk:** sentences with none of the ten words ("I'm so tired today", "Did you call your mother?").

**The sentences:** generated once, in a cloud job, by the open model (qwen2.5:7b through Ollama, free), as frames with
a slot {X}: about 40 frames per act, plus about 200 background sentences. A script checks every frame (the slot appears
exactly once, no other thing's name, plain English). **Frames are split: 80% heard in daily life, 20% kept back for the
test only.** Frames are the same for every thing, so a sentence never hints which thing is meant.

## The child's brain (a neural network, born knowing no words)
- **Hears** each sentence as a sequence of separate words (declared simplification: real babies must also find where
  words begin and end).
- **Sees** the things in view (their looks and places) and, in the arms that have it, **where the parent is looking**
  (joint attention, an inborn mechanism).
- **Feels** its needs (hungry, wants to play).
- **Acts:** hands a thing or not; says one word it has heard, or stays quiet.
- **Inborn mechanisms, declared openly (never inborn knowledge):**
  1. a shared space where heard words and seen things can be matched (a dual encoder: one small network for words,
     one for looks);
  2. learning by association: what it hears is pulled toward what it sees, toward the thing the parent attends to
     (with joint attention) or toward all things in view (without);
  3. learning from inborn rewards: praise, getting the thing it wanted, food when hungry.
- **Brain sizes:** small (an 8-number meaning space), large (64), growing (born small, doubled at 12 and at 24 months).

## Arms (16 children each, the same 16 daily lives in every arm, paired)
| Arm | Brain | Joint attention | Learning | Words |
|---|---|---|---|---|
| A (main) | large | yes | on | real |
| B | small | yes | on | real |
| C | growing | yes | on | real |
| D (blank slate, DeepSeek) | large | **no** | on | real |
| E (control) | large | yes | **off** | real |
| F (control) | large | yes | on | **shuffled each day** (no stable meaning) |

## The test (at 3, 6, 9, 12, 18, 24 and 36 months; learning frozen while testing)
- **60 trials:** 4 things in view (daily life shows 2 or 3), in combinations never seen together in daily life; the
  sentence is a kept-back frame; **no looking or pointing by the parent.** The child hands one thing. Chance = 1 in 4.
- **Saying (secondary):** the child wants a thing that is out of reach, no one speaks first. Does it say that thing's
  name?

## Outcomes and decision rule (exploratory)
- **Primary:** arm A's accuracy at 36 months minus chance (0.25), with a 95% bootstrap interval over the 16 children
  (10,000 draws, a fixed seed). **"Learns words"** = the lower bound is above 0 **and** A's accuracy is above F's (the
  paired difference's lower bound above 0).
- **Secondary:** B, C and D against A (does brain size, growth or joint attention matter?); the learning curve (the first
  test month at which accuracy is 0.6 or more); saying accuracy.
- **Human anchor (descriptive only, never a target):** infants show they know many common nouns at 6–9 months
  (Bergelson and Swingley 2012), and learn word–thing pairs across ambiguous moments within minutes in the lab (Smith
  and Yu 2008). A learning network grounded only in one child's camera and audio learned many word–thing pairs (Vong et
  al. 2024). C0 reports how many hearings of each word the child needed.

## Validity (hard stops)
- **E at chance** (no learning means no words) and **F at chance** (no stable meaning means nothing to learn): the two
  manipulation checks.
- **Code checks:** test trials carry no attention cue; kept-back frames and combinations never occur in daily life; the
  same moment stream in every arm; every frame passes the corpus check.
- **Independent recompute** of the primary from the raw output files (GPT and Gemini, blind), as in ACL.

## Where it runs
Two cloud jobs on GitHub (free; the creator's PC stays off): one Ollama job writes the sentences once (they are saved in
`results/`), then a plain Python job raises all 96 children (small networks, minutes each).

## The assistant's prior (honest)
- **A learns the ten words: about 85%.** With joint attention and a shared word–thing space, this is expected; C0 is
  mostly the working base and the honest controls, not the discovery.
- **D (blank slate) learns them too: about 45%.** This is the interesting arm: can association across moments alone,
  with no one showing what is meant, find the words?
- **B (small) as good as A: about 60%** (ten words need little room).
- **Saying the right name: about 40%** (the reward for speaking is rarer).

## What C0 does not answer (later stages)
Verbs and routines, speaking in sentences, other children, school, the city, and the big question (belonging).
