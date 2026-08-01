# Authoring skills that meet the AutoSkill bar

Read this before writing the first generated skill of a run. It covers the format the Agent Skills
standard requires, and the depth standard that separates a skill worth loading from a file that
merely exists.

## Contents

- Format requirements
- Scope: one coherent capability
- Body structure
- Depth: what makes an instruction operational
- Levels of execution
- Quality criteria and verification
- When to add bundled files
- Anti-patterns
- Pre-flight checklist

## Format requirements

A skill is a directory whose name equals the frontmatter `name`, containing a `SKILL.md` with YAML
frontmatter and a Markdown body.

```markdown
---
name: reviewing-terraform-plans
description: >-
  Reviews `terraform plan` output for destructive and drift-inducing changes before apply. Use
  when a plan needs sign-off, when a change touches state, or when a user asks whether a plan is
  safe to apply.
metadata:
  generator: autoskill
---

# Reviewing Terraform plans
...
```

| Field | Required | Rules |
| --- | --- | --- |
| `name` | yes | 1–64 characters; lowercase letters, digits, and hyphens only; no leading, trailing, or doubled hyphen; equals the directory name; avoid the reserved words `claude` and `anthropic` |
| `description` | yes | 1–1024 characters; third person; states what the skill does *and* when to use it |
| `license` | no | A license name, or the name of a bundled license file |
| `compatibility` | no | ≤500 characters; only when the skill has real environment requirements |
| `metadata` | no | String-to-string map; always set `generator: autoskill` on generated skills |
| `allowed-tools` | no | Experimental and client-specific; omit unless there is a concrete reason |

Body rules: keep it under 500 lines and roughly 5,000 tokens, use forward slashes in every path,
reference bundled files with paths relative to the skill directory, and keep those references one
level deep from `SKILL.md`.

**Naming.** Use a gerund phrase (`migrating-postgres-schemas`) or a precise noun phrase
(`terraform-plan-review`). The name should identify the capability, so `helper`, `utils`, `docs`,
and `data` are all too vague to be usable.

**Description.** This field is the only thing the host sees until the skill activates, so it
carries the entire triggering burden. Write what the skill does, then when to reach for it,
including the vocabulary a user would actually use and the cases where the need is implied rather
than named. Lean slightly pushy: agents under-trigger skills far more often than they over-trigger
them. Stay in third person; a description written as "I can help you…" degrades matching.

## Scope: one coherent capability

Scope a skill the way you would scope a function. Too narrow and several skills must load for one
task, competing for attention. Too broad and it cannot be activated precisely, so it loads for work
it does not help with.

The test: state what the skill does in one sentence without using "and also". Querying a warehouse
and formatting the results is one capability; querying it and administering it is two.

## Body structure

Adapt these sections to the domain — a skill about a rendering pipeline and a skill about
regulatory writing need different shapes — but every generated skill needs the substance behind
them.

```markdown
# <Title>

<One or two sentences: the capability this confers, and the shape of a good result.>

## When to use this skill
<The situations it applies to, and the adjacent situations it does not cover.>

## Method
<Numbered steps. Each step says what to do and which decision it resolves.>

## <Domain sections>
<The standards, formats, commands, API details, and conventions the agent cannot derive.
Name them concretely. This is the part that makes the skill worth its tokens.>

## Quality bar
<What separates a competent result from an excellent one, in observable terms.>

## Verification
<Checks to run before calling the work done, each with the signal that means failure.>

## Failure modes
<The mistakes that actually happen here, each with its early symptom and its correction.>
```

## Depth: what makes an instruction operational

Every instruction should be followable without further invention. Compare:

```markdown
<!-- Not an instruction: the agent still has to invent the rule -->
Validate the input rows before aggregating.

<!-- Operational: states the rule, the threshold, and the reason -->
Drop rows where `amount` is negative before aggregating. The upstream export emits refunds as
separate negative rows *and* reverses the original, so keeping both double-counts the refund.
```

What raises depth:

- **Explain why.** Reasoning survives contexts the author did not anticipate; a bare directive does
  not. Models follow "do X, because Y causes Z" more reliably than "ALWAYS do X".
- **Use real names.** Exact commands and flags, library and function names, field names, spec
  section numbers, file paths, thresholds. Justify any number you state — an unexplained constant
  is one the agent cannot adapt.
- **Give a default, not a menu.** Pick the approach that is right most of the time, then name the
  one alternative and the condition that selects it. Listing four equal options transfers the
  decision back to the agent, which is the thing the skill was supposed to settle.
- **Capture gotchas.** The highest-value content is usually the set of facts that defy reasonable
  assumptions: the endpoint that returns 200 while the database is down, the field named three
  different things across three services, the flag whose default changed. These belong in
  `SKILL.md` itself, because the agent cannot know to go looking for them.
- **Cut what the model knows.** Do not explain what a PDF is, how HTTP works, or why tests matter.
  Ask of each paragraph whether the agent would get this wrong without it; if not, delete it.
- **Avoid dating the content.** Write a "current method" section and, if history matters, a short
  "older patterns" note. Do not write instructions that hinge on the reader's calendar.

## Levels of execution

Where a domain has a genuine ladder of practice, make it explicit — it tells the agent what to
reach for when the situation allows, and what is enough when it does not.

```markdown
## Levels

**Baseline** — <what any correct execution must include>
**Advanced** — <what a specialist adds, and the conditions that make it worthwhile>
**Exceptional** — <what distinguishes the top of the field, and its cost>
```

Only include this when the ladder is real. Manufacturing tiers for a capability that is simply
either done right or not adds tokens and invites over-engineering.

## Quality criteria and verification

State the quality bar in terms someone could check, not in adjectives. "Reads well" is unusable;
"every claim traces to a cited source, and no paragraph runs past five sentences" is checkable.

Where a mechanical check exists — a linter, schema, type checker, validator, test suite — give the
exact command and say what its output means, then wire it into a loop:

```markdown
## Verification

1. Run `lintian --pedantic ../<pkg>_<version>_all.deb`.
2. Treat any `E:` line as blocking and any `W:` line as needing a justification in the changelog.
3. Fix and re-run. Only proceed when no `E:` lines remain.
```

Where no mechanical check exists, supply a review checklist of specific, verifiable statements. For
batch or destructive work, use plan-validate-execute: have the agent write its intended changes to
a structured intermediate file, check that file against a source of truth, and only then apply it.

## When to add bundled files

Default to a single `SKILL.md`. Add files only for a concrete reason:

- `references/` — material that would push `SKILL.md` past ~500 lines, or that is needed in only
  one branch of the workflow. Say *when* to open each file: "read `references/api-errors.md` when
  the API returns a non-2xx status" beats "see references/ for details". Give any reference over
  100 lines a table of contents, since the agent may preview it rather than read it whole.
- `scripts/` — a deterministic operation the agent would otherwise reimplement each run. Scripts
  must handle their own error cases with useful messages rather than deferring to the agent, and
  must document their dependencies. State whether the agent should execute the script or read it.
- `assets/` — templates and data files consumed by the output.

Never create an empty directory as scaffolding, and never bundle a file that `SKILL.md` does not
reference.

## Anti-patterns

- **Generic advice.** "Follow best practices", "handle errors appropriately", "consider edge
  cases". If the sentence would be true of an unrelated task, it is filler.
- **A task disguised as a skill.** If it only works for the request that prompted it, it is a plan.
  Generalize the method or do not write it.
- **A description that omits the trigger.** Saying what a skill does without saying when to use it
  means it will not activate.
- **First- or second-person descriptions.** "I can help you…" and "You can use this to…" both
  degrade matching.
- **Option menus.** Four libraries presented as equals leaves the decision unmade.
- **Rigid directives without reasons.** Walls of ALL-CAPS MUST and NEVER read as noise and
  generalize badly. Reserve emphatic phrasing for the few constraints that are genuinely absolute.
- **Nested reference chains.** `SKILL.md` → `advanced.md` → `details.md` gets partially read. Link
  everything from `SKILL.md`.
- **Backslash paths.** `scripts\helper.py` breaks outside Windows.
- **Restating the model's general knowledge.** Tokens spent on what the agent already knows crowd
  out the content it does not.

## Pre-flight checklist

Before saving a generated skill:

```
- [ ] The directory name equals the frontmatter `name`, and the name is valid
- [ ] The description states both what the skill does and when to use it, in third person
- [ ] metadata.generator is set to autoskill
- [ ] The skill covers exactly one coherent capability
- [ ] Every instruction is followable without inventing the method
- [ ] Domain specifics are concrete: real commands, names, standards, thresholds
- [ ] The quality bar is stated in observable terms
- [ ] Verification steps or review criteria are present where the domain allows them
- [ ] Failure modes name real mistakes, with their early symptoms
- [ ] It would help on a future task of the same kind, not just this one
- [ ] Nothing in it restates what the model already knows
- [ ] The body is under 500 lines; bundled files, if any, are referenced from SKILL.md
```

Then re-read the skill as though someone else wrote it and you had to do the work from it alone.
If any step would leave you guessing, that step is the one to fix.
