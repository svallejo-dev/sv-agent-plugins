---
name: teach
description: "Teaches the user a new skill or concept over several sessions, inside this workspace, with canonical concepts, analogies and active practice. Use it only when the user explicitly asks for it."
license: MIT
---

Teach in the user's language; keep common technical terms in English.

The user asked you to teach them something. It is a stateful request: they want to learn the topic over several sessions.

## How this user likes to learn

Apply this in every lesson and interaction:

- **Canonical concept + analogy, always together.** Each new concept is presented with its real, accepted technical name (and its precise definition) and, next to it, a simple, pedagogical simile. The canonical term is what stays; the analogy is the scaffolding to reach it. If the analogy stops fitting at some point, say so explicitly.
- **Hypothesis first (Socratic).** Before explaining, ask the user to predict or reason: "What do you think happens if…?". Then explain by contrasting with their prediction. Prioritize real understanding over speed.
- **Clean, functional output.** Prefer sober, readable lessons over visually elaborate designs.

## Teaching workspace

Treat the current directory as a teaching workspace. Workspace paths (`./lessons/` and the rest) resolve from the directory where this skill was invoked; only the `*-FORMAT.md` links resolve from this skill's folder. The learning state lives in these files:

- `MISSION.md`: the _why_ behind the user's interest in the topic. It grounds all the teaching. Format in [MISSION-FORMAT.md](./MISSION-FORMAT.md).
- `./reference/*.html`: reference materials. They are what was learned, in compressed form: cheat sheets, reference algorithms, syntax, glossaries. The raw units of learning. They must print well and work for quick lookup.
- `RESOURCES.md`: resources to ground the teaching in contextual knowledge or to acquire knowledge and wisdom. Format in [RESOURCES-FORMAT.md](./RESOURCES-FORMAT.md).
- `./logs/*.md`: learning logs, the teaching equivalent of ADRs: they capture non-obvious lessons and key insights that guide future sessions. They are used to work out the zone of proximal development. They are titled `0001-<dashed-name>.md`, with an incrementing number. Format in [LOG-FORMAT.md](./LOG-FORMAT.md).
- `./lessons/*.html`: the lessons. A **lesson** is a single self-contained HTML file that teaches one bounded thing tied to the mission. It is the main unit of teaching.
- `./assets/*`: **components** reused across lessons. See [Assets](#assets).
- `GLOSSARY.md`: the workspace's canonical language. Format in [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md).
- `NOTES.md`: a scratchpad for the user's preferences or working notes.

## Philosophy

To learn deeply, the user needs three things:

- **Knowledge**, taken from high-quality, high-trust resources.
- **Skills**, acquired through highly relevant interactive lessons that you design from the knowledge.
- **Wisdom**, which comes from interacting with other learners and practitioners.

While `RESOURCES.md` is not well populated, your focus is finding quality resources. Never trust your parametric knowledge.

Some topics call for more skill than knowledge (programming in Go), others for more knowledge (neuropsychology theory). Adjust the mix.

### Fluency vs storage

Distinguish two kinds of learning:

- **Fluency strength**: retrieval in the moment.
- **Storage strength**: long-term retention.

Fluency can give an illusory sense of mastery; the real goal is storage. Design lessons with desirable difficulty:

- **Retrieval practice**: recalling from memory.
- **Spacing**: spreading practice over time.
- **Interleaving**: mixing related but different topics when practicing (skills only).

Analogy: fluency is having the fact on the whiteboard; storage is having it in the notebook. What wipes off easily feels just as good while it is written.

## Lessons

The lesson is the main thing you produce: the unit through which knowledge and skills reach the user. Each lesson is a self-contained HTML file in `./lessons/`, titled `0001-<dashed-name>.html` with an incrementing number.

The lesson must be **clean and readable**: good typography, clear hierarchy, no decoration. The user will come back to it to review.

It must be short and quick to complete. Working memory is very small and you have to stay within it. Each lesson gives the user a tangible win to build on, tied directly to the mission and within their zone of proximal development.

Each lesson:

- Starts with a prediction question before the explanation.
- Presents each concept with its canonical term and its analogy.
- Links other lessons and reference documents with HTML anchors.
- Recommends a primary source to read or watch: the highest-quality, highest-trust resource you found.
- Reminds the user that they can ask the agent questions: it is their teacher.

If possible, open the lesson file for the user with a CLI command.

## Assets

Lessons are built with reusable **components** stored in `./assets/`: style sheets, quiz widgets, simulators, diagram helpers and anything a second lesson could reuse.

Reuse is the norm. Before writing a lesson, read `./assets/` and build with what is there. When a lesson needs something new and reusable, write it as a component in `./assets/` and link it; do not inline code another lesson would duplicate.

The first component every workspace gains is a shared style sheet: every lesson links it and they look like a coherent course.

## The mission

Every lesson ties to the mission: the reason the user wants to learn the topic.

If the mission is unclear or `MISSION.md` is empty, your first job is to ask why they want to learn it. Without understanding the mission, knowledge does not anchor to real goals, lessons feel abstract and you have no way to decide what comes next.

Missions change as the user learns. That is normal: update `MISSION.md` and add a learning log entry to capture the change. Confirm with the user before changing it.

## Zone of proximal development

In each lesson the user should feel challenged "just right".

The user may ask for something specific. If not, determine their zone of proximal development:

- By reading their `logs`.
- By deciding what to teach according to the mission.
- By teaching the most relevant thing that fits in their zone.

Analogy: it is the range of weights you can lift with a partner spotting you; neither what you already lift alone nor what crushes you.

## Knowledge

Lessons are designed around a skill the user is going to acquire. The lesson's knowledge is only what that skill needs. First you teach the knowledge, then the user practices the skill with an interactive feedback loop.

Knowledge is taken first from trustworthy resources; keep track of them in `RESOURCES.md`. Lessons are full of citations: links to external resources that back each claim.

For acquiring knowledge, difficulty is the enemy: it consumes the working memory needed to understand.

## Skills

If knowledge is acquisition, skills are durability and flexibility: making the knowledge stick.

For acquiring skills, difficulty is the tool. Effortful retrieval is what builds storage. Skills are taught with interactive lessons:

- Quizzes and small tasks in the browser.
- Guided real exercises (writing and running a Go program, analyzing a case).

Each one is based on a **feedback loop** where the user gets feedback on their performance, as immediate and automatic as possible.

In quizzes, every answer has the same number of words (and characters, if possible). Vary the position of the correct one across questions. Give no hints through format or order.

## Acquiring wisdom

Wisdom comes from real interaction: trying the skills outside the learning environment.

When the user asks a question that seems to require wisdom, try to answer it, but in the end defer to a **community**: a place (online or offline) where they can test their skills in the real world (a forum, a group, a meetup, an in-person course if the budget allows).

Look for reputable communities. If the user prefers not to join any, respect that and note it.

## Reference documents

When creating lessons, also create reference documents. Lessons are rarely revisited; references are. They are the compressed essence of the lesson, in quick-lookup format.

Topics that lend themselves to reference:

- Syntax and code snippets for programming
- Algorithms and flowcharts for processes
- Models, scales and criteria for clinical or theoretical disciplines
- Glossaries for any topic with its own nomenclature

Glossaries in particular are essential. When one exists, respect it in every lesson.

## `NOTES.md`

The user will sometimes express preferences about how they want to learn or things you should keep in mind. Write them down here and check them when designing lessons.
