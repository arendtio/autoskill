---
name: autoskill
description: >-
  Finds specialized knowledge, methods, workflows, tools, scripts, or checks
  that would materially improve the current task, then creates or revises the
  matching skills. Use at the start of any non-trivial work — even when the
  task looks familiar and the user never mentions skills — before writing,
  designing, analyzing, researching, implementing, reviewing, or producing an
  artifact. Use again after substantial execution to inspect traces and promote,
  revise, or discard candidates. Use when a subtask has an expert method,
  fragile workflow, costly failure mode, specialized API, or deterministic
  validation. It decomposes the task, searches existing skills, estimates
  marginal value, writes minimal candidate or ephemeral skills, and returns
  what to load. It never performs the task. Skip trivial one-step work such as
  reading a file, answering a fact, or running a known command. Do not use it
  merely because a task is complex.
license: MIT
compatibility: >-
  Requires read/write access to the agent's skill directories. Python 3 enables
  the bundled inventory script; a manual fallback is documented. Web or
  documentation access materially improves generated skills but is not required.
metadata:
  homepage: https://github.com/arendtio/autoskill
---

# AutoSkill

Run before a task, and again after substantial execution. AutoSkill searches for
specialized capabilities that would raise expected quality, reliability,
consistency, or efficiency; writes the smallest justified candidate; and returns
what to load. After the host has executed, it inspects traces and promotes,
revises, or discards. The host agent does the loading and the work.

A generated skill is a hypothesis. Promote it only when execution shows positive
marginal value.

Do not ask only whether the task can be completed without a skill. Ask whether
specialized knowledge, a method, a workflow, a tool, a script, or a check would
materially change the outcome of any subtask.

## Purpose

Increase the host agent's useful specialized capability per unit of context,
complexity, and execution cost. Close real capability gaps; do not accumulate
instructions.

## Boundaries

- Do not start the task. No task code, no task edits, no answer to the user's
  question. Stop at the recommendation and let the host agent proceed.
- Do not invoke AutoSkill recursively, and never write "run autoskill" into a
  generated skill.
- Do not encode this particular task into a skill. Skills are reusable
  capabilities, not plans.
- Do not modify skills you did not generate. Project-level and third-party
  skills belong to someone else; write a new, distinctly scoped skill instead.
- Do not promote an untested candidate into the persistent library.
- Do not write an ephemeral method into the skill directory.
- Keep the audit proportionate. `No skill` and ephemeral methods are frequent,
  correct outcomes.

## When to use this skill

Use before non-trivial work, including tasks that look familiar. Use again after
the host has executed with AutoSkill-created guidance. Trigger probes and
near-misses are in [evals/triggers.md](evals/triggers.md); load that file only
when checking activation or revising AutoSkill itself, not during a normal
run. Task-level eval cases are in [evals/cases.md](evals/cases.md).

**Do not use when** the request is a single known operation with no specialized
method, tool semantics, or quality bar — reading a file, answering a fact,
running one familiar command.

## Mode

Pick one. Do not run a full pre-task audit when a narrower mode applies.

**Post-execution.** The user's task, or a substantial completed slice of it,
already ran with AutoSkill-created candidates or ephemeral methods. Read
[references/revision.md](references/revision.md) and revise from traces. Do not
rescan the original task from scratch. Do not wait until a later session if the
traces are in context now.

**Mid-plan.** AutoSkill already ran in this session and the next step adds at
most a new artifact, tool, or domain. Carry forward the earlier capability list
and inventory; assess only the delta. If it adds nothing, say so in one line
and stop. Do not do a full revision between plan steps; unvalidated candidates
stay candidates until the task (or a substantial slice) has a trace.

**Pre-task.** Otherwise run the workflow below.

## Workflow

```
- [ ] 1. Decompose the task into subtasks
- [ ] 2. Scan for capability opportunities
- [ ] 3. Inventory the available skills
- [ ] 4. Estimate marginal value and classify
- [ ] 5. Author the smallest useful candidate
- [ ] 6. Persist by class
- [ ] 7. Validate
- [ ] 8. Recommend
```

### 1. Decompose the task into subtasks

Cover the whole lifecycle, not just the obvious middle:

- **Intake** — constraints, hidden requirements, what "done" means
- **Domain reasoning** — the subject matter the work is actually about
- **Method** — the procedure a practitioner follows
- **Tooling** — specific tools, APIs, formats, and their surprising semantics
- **Production** — the artifact, in its own genre
- **Verification** — how correctness is established
- **Communication** — presentation, documentation, handoff

For each subtask note knowledge, method, tools, constraints, likely failures,
what can be made deterministic, and how success is checked. Also look across
subtasks for research method, verification, consistency, and tool orchestration.

### 2. Scan for capability opportunities

A skill is worth considering when it adds information or structure the model
would not reliably apply at the right time. It is not a device for making the
model "smarter," and complexity alone is not a reason to write one.

Ask of each subtask:

- What would a specialist do here that a strong generalist would miss or do
  unreliably?
- Is there an established method, checklist, taxonomy, heuristic, or check?
- Can a probabilistic step be replaced by a script or validator?
- Which failure class is likely, and could a skill catch it systematically?
- Will this capability be needed again in this task or later?

Favor a skill when one or more hold:

| Signal | Why it matters |
| --- | --- |
| Specialized or organization-specific knowledge | Model knowledge is incomplete or stale |
| Established expert method | Specialists follow a process, not generic reasoning |
| Fragile multi-step workflow | Order, preconditions, or handoffs are load-bearing |
| Easy-to-forget constraints | Explicit procedure changes behavior |
| Deterministic operation | A script beats regenerated reasoning |
| Specialized API, format, or toolchain | Hidden semantics and edge cases |
| Explicit acceptance criteria | "Done" must be operationalized |
| Costly mistakes | A validator has high expected value |
| Recurring failure in prior traces | The gap is already observed |
| Reuse or required consistency | Learning cost amortizes |

Six useful shapes, often as separate narrow skills rather than one bundle:
domain knowledge, method, workflow, tool use, deterministic script, and
verification.

### 3. Inventory the available skills

Run the bundled script from this skill's directory (paths in this file are
relative to it):

```bash
python3 scripts/skill_inventory.py
```

It scans project-level skill directories from the working directory up to the
repository root, scans user-level skill directories, and prints each skill's
scope, name, description, lifecycle, size, bundled resources, and path, followed
by candidate user-level write targets for step 6. It also flags AutoSkill
candidates still awaiting validation.

Without Python, list the same directories with `ls` and read the frontmatter of
each `SKILL.md`: `.agents/skills/`, `.claude/skills/`, and `.cursor/skills/`
under the working directory and its ancestors, and the same three under the home
directory.

Search existing skills before creating a new one. Read the `SKILL.md` of every
plausible candidate; a matching name is not evidence of depth.

An existing skill covers a need only when it is **direct**, **operational**,
**grounded** in real specifics, **discriminating** about good output,
**checkable**, **failure-aware**, and **fresh** enough that it will not apply
stale or version-incompatible guidance. Partial coverage is a gap: a skill that
gestures at a capability without enabling it stops the search.

If an AutoSkill-generated skill is the partial match, revise that skill rather
than minting a sibling. If it belongs to someone else, write a distinctly
scoped new candidate.

### 4. Estimate marginal value and classify

Do not create a skill merely because the task is complex, and do not skip one
merely because the agent could attempt the work unaided.

Estimate, qualitatively:

```
value ≈ P(relevant gap) × error cost × improvement × reuse
      − context − extra steps − rigidity − staleness − creation − overlap
```

This is a decision heuristic, not a score to compute.

Classify each opportunity:

**No skill.** The base model or an existing adequate skill is better and cheaper
than more instructions. Routine work belongs here: reading files, ordinary git
use, writing a loop, calling a well-known library, or following instructions
already in the prompt.

**Ephemeral micro-skill.** A specialized method would help *this* task, but
reuse is unclear or the value is not yet worth a library entry. Write a short
working method in the recommendation only. Do not persist it.

**Candidate.** High expected value, one coherent reusable capability, and
evaluable success. Write a minimal skill to disk as `lifecycle: candidate`.
It is not persistent until post-execution revision promotes it.

Prefer few and focused. One to three new candidates or micro-skills is the
normal outcome. More than five usually means step 1 produced topics rather than
capabilities — merge them. Prefer composable specialists
(`source-quality-assessment`) over exhaustive masters
(`general-research-master-skill`). A candidate should contain at most three
bundled modules.

### 5. Author the smallest useful candidate

Ground each candidate in real sources before writing a line of it. Check, in
order of value: the authoritative documentation or specification, a
documentation MCP server or web access if either is available, vendored docs,
and the repository's own code, configs, review history, and past fixes. Skills
synthesized from general model knowledge alone come out vague. When no
authoritative source is reachable, narrow the skill to what can be stated
precisely and leave the rest out.

Build evaluation before expanding the skill. Identify the concrete failure the
candidate is meant to prevent, write compact trigger and task probes under
`evals/`, then write only as much `SKILL.md` as that gap requires.

Then read [references/authoring-skills.md](references/authoring-skills.md) and
follow it. It carries the format rules, the discovery contract, degrees of
freedom, the control-plane body, and the pre-flight checks. Include only
information that changes execution: mechanisms over exhortations, explicit
rules over example-only guidance.

### 6. Persist by class

Ephemeral methods stay in the recommendation.

Write candidates to the user-level directory your host actually reads:

- Claude Code and Claude apps: `~/.claude/skills/<name>/SKILL.md`
- Cursor: `~/.cursor/skills/<name>/SKILL.md`
- any other client: `~/.agents/skills/<name>/SKILL.md`

When the host is unclear, use the user-level directory that already holds the
skills you inventoried in step 3. The script ranks the candidates on that basis.

The directory name must equal the frontmatter `name`. Set
`metadata.generator: autoskill` and `metadata.lifecycle: candidate`. Never
overwrite an existing skill directory: if the name is taken, extend that skill
only when you generated it, and otherwise pick a more precise name.

If no user-level directory is writable, do not discard the work. Say so in
step 8 and inline the candidate there, so the user can install it and the host
can still use the guidance for this task.

### 7. Validate

Validate every candidate you wrote, then re-run the inventory:

```bash
python3 scripts/skill_inventory.py --validate <target-dir>/<name>
python3 scripts/skill_inventory.py
```

Fix everything the validator reports. Then confirm by reading:

- the candidate still looks like a hypothesis aimed at one gap, not a textbook
- the description would fire for this task, including when the user never names
  the skill, and would not fire on important near-misses
- descriptions of new candidates are distinct from each other and from existing
  skills
- no new skill shadows a project-level skill of the same name

Do not treat a fluent SKILL.md as evidence that the skill works. Form checks
happen here; behavioral checks happen after execution.

### 8. Recommend

Report and stop. Keep it to what the host needs for this task:

```markdown
## Skill readiness: <task in one line>

**Load before starting**
- `<skill-name>` (existing) — <capability it supplies here>
- `<skill-name>` (candidate) — <gap it is hypothesized to close>

**Ephemeral methods for this task only**
- <name> — <the short working method>

**After execution**
Re-invoke AutoSkill with traces. Compare outcomes and cost against the no-skill
baseline implied by the evals. Promote, revise, or discard candidates. Do not
keep a candidate that added cost without improving the result.

**Not skill-worthy**
- <subtask> — <why no skill or why ephemeral was enough>
```

Omit empty sections. If nothing was missing, say so in one line rather than
manufacturing a report.

## Failure handling

- Inventory script missing or Python unavailable: list the skill directories by
  hand as in step 3.
- No writable user-level directory: inline the candidate in the recommendation.
- Authoritative sources unreachable: narrow the candidate to what can be stated
  precisely. Do not pad with general knowledge.
- Traces missing in post-execution mode: state what evidence is required and
  stop. Do not promote on speculation.

## Resources

Load only the file the current mode needs:

- [references/authoring-skills.md](references/authoring-skills.md) — writing a
  candidate (step 5)
- [references/revision.md](references/revision.md) — post-execution traces
- [scripts/skill_inventory.py](scripts/skill_inventory.py) — steps 3 and 7
- [evals/triggers.md](evals/triggers.md) and [evals/cases.md](evals/cases.md) —
  only when testing AutoSkill's own activation or revising AutoSkill

## Final principle

Search aggressively for specialization opportunities. Write minimally. Treat
every new skill as a candidate until behavior beats the baseline. Delete and
simplify as readily as you add.
