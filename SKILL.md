---
name: autoskill
description: >-
  Audits and closes the agent's skill gaps before it starts work. Use at the start of any
  non-trivial task and again before each substantial step of a multi-step plan — before writing,
  designing, analyzing, implementing, reviewing, or producing any artifact — and especially when
  the work touches a specialized domain, a specific output format, an unfamiliar tool or API, or a
  professional quality bar. Use it proactively, even when the user never mentions skills and even
  when the task looks familiar. It decomposes the task into required capabilities, inspects the
  local and user-level skill directories, writes the missing skills into the user-level skill
  directory, and returns a short list of skills to load. It never performs the task itself. Skip it
  only for trivial one-step operations such as reading a file, answering a factual question, or
  running a single known command.
license: MIT
compatibility: >-
  Requires read/write access to the agent's skill directories. Python 3 enables the bundled
  inventory script; a manual fallback is documented. Web or documentation access materially
  improves generated skills but is not required.
metadata:
  generator: autoskill
  homepage: https://github.com/arendtio/autoskill
---

# AutoSkill

Run before a task, never instead of it. AutoSkill checks whether the agent already has the
specialized skills to execute the upcoming task at an expert level, writes the ones that are
missing, and hands back a short list of skills to load. The host agent does the loading and the
work.

Treat the task as a competency assessment: **what would an examiner make the agent demonstrate to
certify that it can execute every relevant aspect of this task exceptionally well?** Every item on
that list the agent cannot reliably demonstrate today is a gap.

## Boundaries

- Do not start the task. No task code, no task edits, no answer to the user's question. Stop at the
  recommendation and let the host agent proceed.
- Do not invoke AutoSkill recursively, and never write "run autoskill" into a generated skill.
- Do not encode this particular task into a skill. Skills are reusable capabilities, not plans.
- Do not modify skills you did not generate. Project-level and third-party skills belong to someone
  else; write a new, distinctly scoped skill instead.
- Keep the audit proportionate to the task. Producing zero skills is a frequent and correct outcome.

## Workflow

```
- [ ] 1. Decompose the task into activities
- [ ] 2. Derive the capability requirements
- [ ] 3. Inventory the available skills
- [ ] 4. Assess coverage against the sufficiency bar
- [ ] 5. Decide what is worth generating
- [ ] 6. Research and write the missing skills
- [ ] 7. Persist to the user-level skill directory
- [ ] 8. Re-inspect and validate
- [ ] 9. Recommend
```

### 1. Decompose the task into activities

Cover the whole lifecycle of the work, not just the obvious middle:

- **Intake** — interpreting the request, its constraints, and what "done" means here
- **Domain reasoning** — the subject matter the work is actually about
- **Method** — the procedure a practitioner follows to produce this kind of result
- **Tooling** — the specific tools, libraries, APIs, and formats involved
- **Production** — building the concrete artifact, in its own genre and conventions
- **Verification** — how correctness and quality are established before handoff
- **Communication** — how the result is presented, documented, or handed over

For each activity ask what separates a competent attempt from an expert one. That difference is
where a skill can change the outcome; where there is no difference, there is nothing to add.

### 2. Derive the capability requirements

For each activity with a real competent-to-expert gap, state what the agent must be able to do.
Use these categories as prompts, not as a form to fill in:

| Category | Question it answers |
| --- | --- |
| Procedure | What is the actual step sequence, and where are its decision points? |
| Domain knowledge | Which facts, models, or conventions must be known and cannot be inferred? |
| Tooling | Which exact tools, APIs, and flags, and what is surprising about them? |
| Standards | Which external specs, regulations, or house rules define correct output? |
| Output expertise | What makes this artifact well-formed within its own genre? |
| Quality criteria | How is a good result told apart from a plausible-looking bad one? |
| Failure modes | What goes wrong for non-experts, and how does it show up early? |

Write each requirement as a capability statement, not a topic label. "Write a Debian changelog
entry that passes lintian" is a requirement; "packaging" is not.

### 3. Inventory the available skills

Run the bundled script from this skill's directory (paths in this file are relative to it):

```bash
python3 scripts/skill_inventory.py
```

It scans the project-level skill directories from the working directory up to the repository root,
scans the user-level skill directories, and prints each skill's scope, name, description, size,
bundled resources, and path, followed by the candidate user-level write targets for step 7.

Without Python, list the same directories with `ls` and read the frontmatter of each `SKILL.md`:
`.agents/skills/`, `.claude/skills/`, and `.cursor/skills/` under the working directory and its
ancestors, and the same three under the home directory.

### 4. Assess coverage against the sufficiency bar

Read the `SKILL.md` of every plausible candidate before judging it. A matching name or an
encouraging description is not evidence of depth.

A skill covers a requirement only when all six hold:

1. **Direct** — it targets that capability, not a neighbouring one.
2. **Operational** — a competent agent could follow it without inventing the method.
3. **Grounded** — it carries the real standards, formats, commands, or API details, rather than
   advice that would be true of any task.
4. **Discriminating** — it says how to recognize a good result, in observable terms.
5. **Checkable** — it supplies verification steps or review criteria wherever the domain allows one.
6. **Failure-aware** — it names the mistakes that actually occur here and their early symptoms.

Mark each requirement **Covered**, **Partial**, or **Missing**. Partial is a gap: a skill that
gestures at a capability without enabling it is worse than none, because it stops the search.

### 5. Decide what is worth generating

Generate only when all three are true:

- getting this capability wrong would visibly degrade the result
- explicit procedure, domain knowledge, standards, or quality criteria would change what the agent
  actually produces
- the capability recurs beyond this one task

Skip when any of these apply:

- it is routine work the agent already does reliably — reading files, ordinary git use, writing a
  loop, calling a well-known library
- everything needed is already stated in the task prompt
- the content would amount to general good practice with no domain substance
- an existing skill already clears the bar in step 4

Prefer few and deep. One to three new skills is the normal outcome. More than five usually means
step 2 produced topics rather than capabilities — go back and merge them into coherent units.

### 6. Research and write the missing skills

Ground each skill in real sources before writing a line of it. Check, in order of value: the
authoritative documentation or specification for the domain, a documentation MCP server or web
access if either is available, vendored docs in the repository, and the repository's own code,
configs, review history, and past fixes. Skills synthesized from general model knowledge alone come
out vague, which is the failure this whole workflow exists to prevent. When no authoritative source
is reachable, narrow the skill to what can be stated precisely and leave the rest out.

Then read [references/authoring-skills.md](references/authoring-skills.md) and follow it. It
carries the format rules, the body structure, the depth standard, and the pre-flight checks that
every generated skill has to pass.

### 7. Persist to the user-level skill directory

Write to the user-level directory your host actually reads:

- Claude Code and Claude apps: `~/.claude/skills/<name>/SKILL.md`
- Cursor: `~/.cursor/skills/<name>/SKILL.md`
- any other client: `~/.agents/skills/<name>/SKILL.md`, the cross-client convention

When the host is unclear, use the user-level directory that already holds the skills you
inventoried in step 3 — that is demonstrably a directory this host reads. The script ranks the
candidates on that basis.

The directory name must equal the frontmatter `name`. Never overwrite an existing skill directory:
if the name is taken, extend that skill only when you generated it (its frontmatter carries
`metadata.generator: autoskill`), and otherwise pick a more precise name.

### 8. Re-inspect and validate

Validate every skill you wrote, then re-run the inventory:

```bash
python3 scripts/skill_inventory.py --validate <target-dir>/<name>
python3 scripts/skill_inventory.py
```

Fix everything the validator reports. Then confirm by reading, because the validator only checks
form:

- each new skill still clears the step 4 bar when read as though someone else wrote it
- descriptions are distinct enough that the host can tell the skills apart
- no new skill shadows a project-level skill of the same name

### 9. Recommend

Report and stop. Keep it to the skills that matter for the task at hand:

```markdown
## Skill readiness: <task in one line>

**Load before starting**
- `<skill-name>` (existing) — <the capability it supplies for this task>
- `<skill-name>` (new) — <the capability it supplies for this task>

**Gaps left open**
- <capability> — <why no skill was warranted>

No task work has been done. Proceed with the skills above loaded.
```

Omit the gaps section when there are none. If nothing was missing, say so in one line rather than
manufacturing a report.
