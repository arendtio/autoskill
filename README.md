# AutoSkill

An [Agent Skill](https://agentskills.io) that runs *before* a task and makes sure the agent has the
specialized skills to execute it at an expert level.

AutoSkill treats every task as a competency assessment: what would an examiner make the agent
demonstrate to certify it can do this work exceptionally well? It decomposes the task into required
capabilities, inspects the skills already installed, generates the ones that are missing or too
shallow, writes them into the user-level skill directory, and returns a short list of skills to
load.

It never performs the task. Discovering, selecting, loading, and applying the recommended skills
stays with the surrounding agent system.

## Install

Clone the repository into a skill directory your agent reads. The directory must be named
`autoskill`, because the Agent Skills specification requires the directory name to match the
skill's `name`.

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

Most agents activate AutoSkill on their own when a task looks specialized, because its description
is written to trigger before non-trivial work. You can also invoke it explicitly — in Claude Code,
`/autoskill` — before starting a task or before a step of a plan.

A run ends with a recommendation like this:

```markdown
## Skill readiness: migrate the billing service from Flask to FastAPI

**Load before starting**
- `migrating-wsgi-to-asgi` (new) — request/response translation, blocking-call detection, and the
  test strategy for a mixed-stack cutover
- `python-dependency-audits` (existing) — pinning and conflict resolution for the new stack

**Gaps left open**
- Writing the migration commits — routine work the agent already does reliably.

No task work has been done. Proceed with the skills above loaded.
```

Producing zero new skills is a normal outcome. AutoSkill only generates a skill when explicit
procedural knowledge, domain expertise, quality criteria, or a specialized method would materially
change the result.

## Contents

| Path | Purpose |
| --- | --- |
| `SKILL.md` | Invocation conditions, boundaries, and the nine-step workflow |
| `references/authoring-skills.md` | Format rules and the depth standard every generated skill must pass |
| `scripts/skill_inventory.py` | Read-only inventory of installed skills, and spec validation of one skill |

There is no registry, database, or daemon. The filesystem skill directories are the registry, which
is what the Agent Skills standard intends.

## The inventory script

```bash
# List every skill visible from here, plus the candidate user-level write targets
python3 scripts/skill_inventory.py

# Include extra directories in the listing
python3 scripts/skill_inventory.py /path/to/other/skills

# Check one skill directory against the specification
python3 scripts/skill_inventory.py --validate /path/to/skill
```

The listing scans `.agents/skills`, `.claude/skills`, and `.cursor/skills` from the working
directory up to the repository root, and the same three under the home directory. Validation checks
frontmatter conformance, name and directory agreement, body length, and whether bundled files and
Markdown references actually resolve. It exits non-zero when it finds an error.

Both modes are read-only.

## Quality standard

A skill counts as adequate only when it enables the capability reliably, not when it merely exists.
AutoSkill accepts an existing skill only if it is direct, operational, grounded in real standards
and specifics, discriminating about what a good result looks like, checkable, and honest about
failure modes. A superficially related skill that lacks the depth to execute well counts as a gap,
because it stops the search without supplying the capability.

## License

MIT. See [LICENSE](LICENSE).
