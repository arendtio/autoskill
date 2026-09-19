# Authoring skills that meet the AutoSkill bar

Read this before writing the first generated candidate of a run. It covers the
format the Agent Skills standard requires, and the design standard that
separates a skill worth loading from extra context that does not change
behavior.

Load [revision.md](revision.md) instead when inspecting traces after execution.

## Contents

- Format requirements
- Discovery contract
- Scope: one coherent capability
- Degrees of freedom
- Body structure
- Rules, examples, and mechanisms
- Quality criteria and verification
- When to add bundled files
- Freshness
- Evaluation files
- Anti-patterns
- Pre-flight checklist

## Format requirements

A skill is a directory whose name equals the frontmatter `name`, containing a
`SKILL.md` with YAML frontmatter and a Markdown body.

```markdown
---
name: source-quality-assessment
description: >-
  Evaluates the reliability, authority, independence, and evidentiary value of
  sources during research and claim verification. Use when selecting sources,
  checking citations, or doing deep research — including when the user never
  asks for source evaluation by name. Do not use it merely to retrieve or
  summarize a source.
metadata:
  generator: autoskill
  lifecycle: candidate
  created: "2026-09-19"
  last_validated: ""
  freshness_sensitive: "false"
---

# Source quality assessment
...
```

| Field | Required | Rules |
| --- | --- | --- |
| `name` | yes | 1–64 characters; lowercase letters, digits, and hyphens only; no leading, trailing, or doubled hyphen; equals the directory name; avoid the reserved words `claude` and `anthropic` |
| `description` | yes | 1–1024 characters; third person; the discovery contract below |
| `license` | no | A license name, or the name of a bundled license file |
| `compatibility` | no | ≤500 characters; only when the skill has real environment requirements |
| `metadata` | no | String-to-string map. Generated skills always set `generator: autoskill` and `lifecycle: candidate` until revision promotes them. Optional: `created`, `last_validated`, `freshness_sensitive`, `tested_against` |
| `allowed-tools` | no | Experimental and client-specific; omit unless there is a concrete reason |

Body rules: keep it under 500 lines and roughly 5,000 tokens, use forward
slashes in every path, reference bundled files with paths relative to the skill
directory, and keep those references one level deep from `SKILL.md`.

**Naming.** Use a gerund phrase (`migrating-postgres-schemas`) or a precise noun
phrase (`terraform-plan-review`). The name should identify the capability, so
`helper`, `utils`, `docs`, and `data` are all too vague to be usable.

## Discovery contract

`description` is the routing contract. It is in the host's context for every
skill and is the only thing the host sees until activation. Optimize for recall
*and* precision.

It must state:

1. **Capability** — what the skill enables
2. **Trigger** — when to use it
3. **Implicit trigger** — cases where it is useful even though the user never
   names it
4. **Exclusion** — important near-misses where it should *not* load

Lean slightly pushy on implicit triggers: agents under-activate useful skills
more often than they over-activate them. Stay in third person; "I can help
you…" degrades matching.

## Scope: one coherent capability

Scope a skill the way you would scope a function. Too narrow and several skills
must load for one task, competing for attention. Too broad and it cannot be
activated precisely.

The test: state what the skill does in one sentence without using "and also".
Querying a warehouse and formatting the results is one capability; querying it
and administering it is two.

Prefer a small composable skill over an exhaustive pack. If the body is growing
into a textbook, split it or move rarely needed detail into `references/`.

Do not teach the model what it already reliably knows. Every paragraph must
change execution.

## Degrees of freedom

Match instruction precision to how narrow the corridor of correct behavior is.

| Fragility | What to write |
| --- | --- |
| Open-ended | Principles, heuristics, decision criteria |
| Semi-structured | Preferred workflow, one default, explicit branches |
| Fragile | Exact sequence, preconditions, guardrails, validators |
| Deterministic | Script or tool; almost no natural-language discretion |

Do not over-constrain work that needs judgment. Do not leave a fragile or
deterministic operation to open-ended prose.

## Body structure

`SKILL.md` is a control plane, not a textbook. Adapt section names to the
domain, but every generated candidate needs the substance behind them.

```markdown
# <Title>

## Purpose
<One to three sentences: the measurable behavioral change this skill should
produce. Not "helps with research" but "forces claim-to-source mapping and
contradiction checks before synthesis.">

## When to use this skill
<Concrete triggering situations.>

## Do not use when
<Important near-misses. Reduces collisions with neighbouring skills.>

## Preconditions
<Inputs, dependencies, permissions, or assumptions that must already be true.>

## Core workflow
<The minimum reliable sequence. Numbered. Each step resolves a decision.>

## Decision points
<IF/THEN branches where execution actually differs. Include the failure path,
not only the happy path.>

## Default
<One recommended approach. Name at most one alternative and the condition that
selects it.>

## Failure handling
<What to do when inputs, tools, or assumptions fail.>

## Verification
<Observable completion criteria. Prefer a deterministic validator. Keep checks
proportional to uncertainty, importance, and error cost.>

## Resources
<When to load each bundled file. Never "see references/ for details.">

## Freshness
<What goes stale, and how to refresh or revalidate it. Omit when nothing dated.>
```

Gotchas that defy reasonable assumptions belong in `SKILL.md` itself: the
endpoint that returns 200 while the database is down, the field named three
things across three services, the flag whose default changed. The agent cannot
know to go looking for them.

## Rules, examples, and mechanisms

Write in this order: **rule → procedure → constraints → verification →
examples**.

State core behavior as explicit rules. Examples clarify style, output shape,
edge cases, and hard decisions. They do not replace the rule. Prefer examples
taken from validated executions over invented demonstrations.

Do not rely on motivational language: "be extremely careful", "make no
mistakes", "think harder", "this is very important", role-play, CAPS LOCK, or
reward rhetoric. Those are testable prompt candidates at best, not process
knowledge. Replace them with mechanisms.

```markdown
<!-- Exhortation: not an instruction -->
Make sure all requirements are satisfied.

<!-- Mechanism -->
Extract the acceptance criteria, map each one to an artifact, and run the
validator before completion.

<!-- Exhortation -->
Carefully inspect the generated JSON.

<!-- Mechanism -->
1. Write result.json.
2. Run `scripts/validate_schema.py result.json`.
3. If it fails, repair only the reported violations.
4. Re-run. Do not finish until it passes or a hard blocker is recorded.
```

Give a default, not a menu. Listing four equal options transfers the decision
back to the agent.

Explain why when the reason is not obvious. Models follow "do X, because Y
causes Z" more reliably than "ALWAYS do X". Use real names: commands, flags,
functions, fields, spec sections, paths, thresholds. Justify any number you
state.

## Quality criteria and verification

State the quality bar in terms someone could check. "Reads well" is unusable;
"every claim traces to a cited source, and no paragraph runs past five
sentences" is checkable.

Where a mechanical check exists, give the exact command, say what its output
means, and wire it into a repair loop. Where none exists, supply a review
checklist of specific statements. For batch or destructive work, use
plan-validate-execute.

Keep verification **risk-proportional**. Targeted checks on uncertain, costly,
or load-bearing claims. Not "verify everything three times." Excessive
verification is a common way skills make agents worse: extra steps, delayed
completion, and new failure modes.

Ask of every instruction: can this be a script? Parsing, schema checks, math,
deduplication, conversion, and other exact operations should not be re-reasoned
in prose each run.

## When to add bundled files

Default to a single `SKILL.md`. Add files only for a concrete reason, and say
*when* to open each one.

- `references/` — material that would push `SKILL.md` past ~500 lines, or that
  is needed in only one branch. Give any reference over 100 lines a table of
  contents. Keep references one level deep.
- `scripts/` — a deterministic operation the agent would otherwise reimplement.
  Scripts handle their own errors with useful messages. State whether to
  execute the script or read it. Document dependencies.
- `assets/` — templates and data files consumed by the output.
- `evals/` — trigger probes and task cases for later revision. The executing
  agent should not load these during normal work.

Never create an empty directory as scaffolding, and never bundle a file that
`SKILL.md` does not mention. A candidate should rarely need more than three
bundled modules besides `evals/`.

## Freshness

APIs, frameworks, and toolchains go stale. Version-incompatible guidance can
lower success rates. For generated skills that depend on evolving interfaces:

```markdown
Dependencies: <tools, libraries, CLIs>
Tested against: <versions, or "unverified">
Freshness-sensitive: <what will rot>
Last validated: <date, or empty for a new candidate>
```

For rapidly changing information, describe *how* to fetch and apply current
docs rather than freezing today's docs into the skill.

Set `metadata.freshness_sensitive: "true"` when stale instructions would actively
mislead.

## Evaluation files

Write these *before* expanding the candidate beyond the minimum that could
close the identified gap.

`evals/triggers.md` — a compact probe set, not a 20-query lab protocol:

- obvious positives
- non-obvious positives (skill never named)
- paraphrases and noisy/casual wording
- the relevant subtask embedded in a larger task
- hard-negative near-misses

`evals/cases.md` — the failure the skill exists to prevent, a no-skill
baseline expectation, and what "better" looks like. Include cost: extra steps
and tokens count against the skill.

Point to both files from `SKILL.md` with an explicit "load only when revising"
note so the executor does not ingest them on every run.

## Anti-patterns

- **Generic advice.** If the sentence would be true of an unrelated task, delete it.
- **A task disguised as a skill.** If it only works for this request, it is a plan.
- **A description that omits trigger or exclusion.** It will under- or over-fire.
- **First- or second-person descriptions.**
- **Option menus.** One default plus a conditional escape hatch.
- **Rigid directives without reasons.** Walls of MUST/NEVER read as noise.
- **Motivational filler.** "Make no mistakes" is not a quality mechanism.
- **Exhaustive master skills.** Split them.
- **Teaching the model its own knowledge.**
- **Prompt hacks without local evaluation.** Do not freeze "take a deep breath"
  or similar into a persistent skill.
- **Nested reference chains.** Link everything from `SKILL.md`.
- **Backslash paths.**
- **Verification theater.** Checks that add cost without changing outcomes.
- **Self-certified quality.** Fluent prose is not evidence the skill works.

## Pre-flight checklist

Before saving a generated candidate:

```
- [ ] Directory name equals a valid frontmatter `name`
- [ ] Description is a discovery contract: capability, trigger, implicit trigger, exclusion; third person
- [ ] metadata.generator is autoskill; metadata.lifecycle is candidate
- [ ] Exactly one coherent capability; no "and also"
- [ ] Degree of freedom matches fragility
- [ ] Purpose states a measurable behavioral change
- [ ] Core workflow, decision branches, and one default are present
- [ ] Verification is observable and risk-proportional
- [ ] Deterministic work is a script or tool where practical
- [ ] Domain specifics are real names, commands, standards, thresholds
- [ ] No exhortations, option menus, or restated general knowledge
- [ ] evals/triggers.md and evals/cases.md exist and are referenced
- [ ] Body under 500 lines; bundled files, if any, are referenced from SKILL.md
- [ ] Freshness notes exist when the domain can rot
```

Then re-read the skill as though someone else wrote it and you had to work from
it alone. If a step would leave you guessing, that step is the one to fix. This
is a form check, not a substitute for execution.
