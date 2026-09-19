# Revising skills from execution evidence

Read this when AutoSkill is running in post-execution mode: the host already
did substantial work with AutoSkill-created candidates or ephemeral methods.
Do not rescan the original task from scratch.

A candidate is not a skill until behavior beats the no-skill baseline. Reading
the text again is not that test. Creator self-critique without traces is how
skills drift: fluent, confident, and worse.

## Contents

- What to collect
- Diagnose the trace
- Revise from evidence
- Promote, keep candidate, or discard
- Library hygiene

## What to collect

Prefer a fresh execution context over the context that wrote the skill. Gather:

- the task outcome (success, acceptance tests, user-visible quality)
- whether the skill triggered, failed to trigger, or triggered on a near-miss
- steps, tool calls, and tokens beyond the no-skill path
- places the executor followed, ignored, or misread the skill
- errors, retries, and dead ends
- model and runtime identifiers, if known

Read the candidate's `evals/cases.md` and `evals/triggers.md` if they exist.
Judge the skill against those probes, not against whether the SKILL.md "looks
complete."

If traces are missing, say what evidence is required and stop. Do not promote
on speculation.

## Diagnose the trace

For each candidate and ephemeral method, mark every issue that applies:

| Observation | Typical defect |
| --- | --- |
| Helped on the targeted gap | Keep; consider promotion |
| Ignored | Trigger too weak, buried, or skill never loaded |
| Misinterpreted | Rule ambiguous; add a constraint or example of the hard case |
| Extra work, same outcome | Procedure too heavy; delete steps, especially extra verification |
| Incorrect behavior | Wrong default, stale guidance, or over-constraint |
| Failed to trigger | Description missing implicit cases |
| Triggered unnecessarily | Description too broad; add exclusions |
| Version or API mismatch | Freshness failure; replace frozen docs with a fetch-and-apply method |
| Ephemeral method clearly recurred | Candidate it, do not leave it as one-off prose |

Ask both:

- What instruction is missing?
- What instruction is unnecessary, over-constraining, ignored, or costly
  without changing the outcome?

Deletion is a valid revision. Focused skills outperform exhaustive packs, and
added context can lower performance even when the extra text is relevant.

## Revise from evidence

Change only what the trace supports. Do not "improve" the prose speculatively.

1. Patch the smallest failing piece: description, a rule, a branch, a validator,
   or a script.
2. Update `evals/` so the observed failure is a probe next time.
3. Re-validate form:

   ```bash
   python3 scripts/skill_inventory.py --validate <target-dir>/<name>
   ```

   Run it from the AutoSkill directory. AutoSkill still does not perform the
   user's original task. If the host can cheaply re-run the failed probe, do
   that after the patch.

Keep SKILL.md a control plane. Move detail that was needed only on one branch
into `references/`. Turn exact operations discovered during execution into
`scripts/`.

Do not modify skills you did not generate. If a third-party skill caused harm,
record it as a gap and write a distinctly scoped candidate instead.

## Promote, keep candidate, or discard

Track at least: task success, correctness, trigger recall, trigger precision,
execution overhead, unnecessary steps, failure modes, tested runtime, and last
validation date.

**Promote** to `metadata.lifecycle: persistent` only when this execution shows
meaningful benefit on the targeted gap without a serious cost or harm
regression. Set `last_validated` and `tested_against`.

**Keep as candidate** when evidence is mixed, the sample is one lucky pass, or
a remaining defect is still cheap to fix. Say what would settle it.

**Discard** when the skill did not beat the baseline, added cost without
improving the result, or caused incorrect behavior you cannot repair simply.
Delete AutoSkill-generated candidates you are discarding. Do not leave dead
skills in the library.

**Candidate an ephemeral method** only when this run showed reuse value. Write
it through the pre-task authoring path as a new candidate, including evals.
Otherwise leave it out of the library.

Report the decision and stop. Do not start the user's next task.

## Library hygiene

While revising, also inspect AutoSkill-generated skills in the inventory:

- overlapping or poorly scoped skills — merge, split, or rename
- candidates that never earned a `last_validated` date across runs — discard
  or schedule a real probe; do not promote them for age
- freshness-sensitive skills after tool, API, or model changes — retest
- instructions that add cost without improving outcomes — delete them
- skills that no longer beat doing nothing — retire them

Optimize the library for precision and coverage, not for skill count.
