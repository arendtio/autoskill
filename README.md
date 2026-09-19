# AutoSkill

An [Agent Skill](https://agentskills.io) that runs *before* a task — and again
after substantial execution — to raise the specialized capability the agent
brings to the work.

AutoSkill does not ask whether the agent can complete the task unaided. It asks
whether specialized knowledge, methods, workflows, tools, scripts, or checks
would materially improve quality, reliability, consistency, or efficiency. It
decomposes the task, searches installed skills, estimates marginal value, and
then either writes a short ephemeral method, writes a minimal **candidate**
skill, or recommends an existing one.

A generated skill starts as a hypothesis. AutoSkill promotes it into the
persistent library only when later execution traces show positive marginal
value. It never performs the user-visible task. Discovering, selecting,
loading, and applying the recommended skills stays with the surrounding agent.

## Install

Clone the repository into a skill directory your agent reads. The directory
must be named `autoskill`, because the Agent Skills specification requires the
directory name to match the skill's `name`.

```bash
# Claude Code and Claude apps
git clone https://github.com/arendtio/autoskill ~/.claude/skills/autoskill

# Cursor
git clone https://github.com/arendtio/autoskill ~/.cursor/skills/autoskill

# Any other skills-compatible client (cross-client convention)
git clone https://github.com/arendtio/autoskill ~/.agents/skills/autoskill
```

To install it for a single project instead, clone into `.claude/skills/autoskill`,
`.cursor/skills/autoskill`, or `.agents/skills/autoskill` inside the repository.

Verify the installation:

```bash
python3 ~/.claude/skills/autoskill/scripts/skill_inventory.py --validate ~/.claude/skills/autoskill
```

## Use

Most agents activate AutoSkill on their own before non-trivial work, including
tasks that look familiar, because its description is written to trigger on
capability opportunities rather than on explicit "I need a skill" requests. You
can also invoke it explicitly — in Claude Code, `/autoskill` — before starting,
before a step of a plan, or after a run so it can inspect traces.

A run ends with a recommendation like this:

```markdown
## Skill readiness: migrate the billing service from Flask to FastAPI

**Load before starting**
- `migrating-wsgi-to-asgi` (candidate) — request/response translation, blocking
  call detection, and the test strategy for a mixed-stack cutover
- `python-dependency-audits` (existing) — pinning and conflict resolution

**Ephemeral methods for this task only**
- Vendor CSV column map — treat `amt` as minor units, drop `amt_orig`

**After execution**
Re-invoke AutoSkill with traces. Promote, revise, or discard candidates.

**Not skill-worthy**
- Writing the migration commits — routine work the agent already does reliably.
```

Producing zero new library skills is a normal outcome. AutoSkill generates a
**candidate** only when the expected benefit of a reusable, evaluable capability
beats the cost of extra context, rigidity, and staleness. When a method would
help once but reuse is unclear, it stays ephemeral.

## Contents

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Control plane: modes, opportunity scan, classification, recommend |
| `references/authoring-skills.md` | Format, discovery contract, and design bar for new candidates |
| `references/revision.md` | Trace inspection, promotion, discard, and library hygiene |
| `evals/triggers.md` | Activation probes for AutoSkill itself |
| `evals/cases.md` | Behavioral cases for revising AutoSkill |
| `scripts/skill_inventory.py` | Inventory of installed skills, plus spec validation of one skill |

There is no registry, database, or daemon. The filesystem skill directories are
the registry, which is what the Agent Skills standard intends.

## The inventory script

```bash
# List every skill visible from here, plus the candidate user-level write targets
python3 scripts/skill_inventory.py

# Include extra directories in the listing
python3 scripts/skill_inventory.py /path/to/other/skills

# Check one skill directory against the specification
python3 scripts/skill_inventory.py --validate /path/to/skill
```

The listing scans `.agents/skills`, `.claude/skills`, and `.cursor/skills` from
the working directory up to the repository root, and the same three under the
home directory. It prints AutoSkill lifecycle metadata when present and flags
candidates still awaiting validation.

Validation checks frontmatter conformance, name and directory agreement, body
length, and whether bundled files and Markdown references actually resolve. It
exits non-zero when it finds an error.

Both modes are read-only.

## Quality standard

Useful specialized capability per unit of context and cost is the objective,
not skill count and not a complete first draft.

An existing skill counts as coverage only when it enables the capability:
direct, operational, grounded, discriminating, checkable, failure-aware, and
fresh. A generated candidate must also have a precise discovery contract, a
fragility-matched degree of freedom, risk-proportional verification, and eval
probes. Fluent instructions are not evidence. Execution traces are.

## License

MIT. See [LICENSE](LICENSE).
