# AutoSkill evaluation cases

Load only when revising AutoSkill itself. Do not load during a normal run.

Judge AutoSkill by the skills it causes the host to load and by later execution
traces, not by how complete its report looks.

## Case 1 — implicit specialist method

**Request.** "Write a literature-backed comparison of these two approaches."

**No-skill failure.** The host synthesizes from general knowledge, weak source
selection, and no claim-to-evidence map.

**Better.** AutoSkill decomposes research vs. synthesis vs. verification,
considers focused candidates or an ephemeral method (search, source quality,
claim mapping), and does *not* emit a `general-research-master-skill`.

## Case 2 — familiar task with a hidden fragile step

**Request.** "Migrate this service to the new framework." The host has done
migrations before.

**No-skill failure.** AutoSkill skips because the agent "can migrate." The
cutover's actual gap (request lifecycle, blocking calls, test strategy) is
never named.

**Better.** Opportunity scan finds the fragile subtask. An existing adequate
skill is reused, or a narrow candidate is written. Routine git/commit work is
classified `No skill`.

## Case 3 — oversupply

**Request.** "Rename this variable."

**Failure.** AutoSkill writes a skill.

**Better.** Skip with one line. Complexity and "professional quality" rhetoric
are not enough.

## Case 4 — candidate vs ephemeral vs persistent

**Request.** A one-off vendor CSV with surprising column semantics.

**Failure.** A persistent library skill is written from an untested first draft.

**Better.** Ephemeral method for this file, or a `lifecycle: candidate` with
evals. Promotion happens only after a trace shows reuse value.

## Case 5 — revision from harm

**Trace.** A candidate added a mandatory three-pass verification pipeline. The
task succeeded no faster and two required output sections were dropped.

**Failure.** AutoSkill keeps or expands the candidate.

**Better.** Diagnose excessive verification, delete the extra procedure, and
discard if nothing remains that beats the baseline.
