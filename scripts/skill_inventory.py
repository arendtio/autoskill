#!/usr/bin/env python3
"""Inventory and validate Agent Skills in the standard skill directories.

Usage:
    python3 skill_inventory.py [extra_dir ...]     List discovered skills and write targets.
    python3 skill_inventory.py --validate <dir>    Check one skill directory against the spec.

The listing scans the project-level skill directories from the working directory up to the
repository root, plus the user-level skill directories, and ends with the candidate user-level
directories ranked as write targets. Extra directories may be given as positional arguments.

Read-only in both modes; nothing is created, modified, or cached.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# The client-native directory names scanned at both project and user level. `.agents` is the
# cross-client convention; the other two cover the clients that populate their own directory.
SKILL_DIR_NAMES = (".agents/skills", ".claude/skills", ".cursor/skills")

# Ancestor directories are searched up to the repository root. The cap keeps the walk bounded when
# the working directory is not inside a repository.
MAX_ANCESTOR_DEPTH = 8

NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_COMPATIBILITY_LENGTH = 500
# The spec recommends keeping SKILL.md bodies short enough to load cheaply on activation.
MAX_BODY_LINES = 500
RESERVED_NAME_WORDS = ("claude", "anthropic")
# Markdown links to bundled files, used to check that references resolve. Skips URLs and anchors.
MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\((?!https?://|#|mailto:)([^)\s]+)\)")


class Skill:
    def __init__(self, directory: Path, scope: str, root: Path):
        self.directory = directory
        self.scope = scope
        self.root = root
        self.name = ""
        self.description = ""
        self.frontmatter: dict[str, str] = {}
        self.body = ""
        self.error = ""


def parse_skill_md(text: str) -> tuple[dict[str, str], str, str]:
    """Split SKILL.md into frontmatter and body.

    Returns (frontmatter, body, error). Values are flattened to strings; nested mappings are
    recorded with dotted keys so `metadata.generator` is reachable without a YAML dependency.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text, "no YAML frontmatter (file must start with ---)"

    closing = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if closing is None:
        return {}, text, "unterminated YAML frontmatter (missing closing ---)"

    fields: dict[str, str] = {}
    raw = lines[1:closing]
    index = 0
    while index < len(raw):
        line = raw[index]
        index += 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())
        match = re.match(r"^\s*([A-Za-z0-9_.-]+)\s*:\s*(.*)$", line)
        if not match:
            continue
        key, value = match.group(1), match.group(2).strip()
        prefix = "" if indent == 0 else f"{_enclosing_key(fields, raw, index - 1)}."

        if value in ("|", ">", "|-", ">-", "|+", ">+"):
            # Block scalar: consume the more-indented lines that follow.
            block: list[str] = []
            while index < len(raw):
                nxt = raw[index]
                if nxt.strip() and (len(nxt) - len(nxt.lstrip())) <= indent:
                    break
                block.append(nxt.strip())
                index += 1
            joiner = "\n" if value.startswith("|") else " "
            fields[prefix + key] = joiner.join(block).strip()
        elif value == "":
            # Either an empty value or the start of a nested mapping; nested keys pick it up
            # through _enclosing_key, so record the bare key as empty.
            fields[prefix + key] = ""
        else:
            fields[prefix + key] = _unquote(value)

    body = "\n".join(lines[closing + 1 :]).strip()
    return fields, body, ""


def _enclosing_key(fields: dict[str, str], raw: list[str], position: int) -> str:
    """Return the nearest top-level key above an indented line, for dotted-key flattening."""
    for i in range(position - 1, -1, -1):
        line = raw[i]
        if line.strip() and not line.startswith((" ", "\t")):
            match = re.match(r"^([A-Za-z0-9_.-]+)\s*:", line)
            if match:
                return match.group(1)
    return ""


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def load_skill(directory: Path, scope: str, root: Path) -> Skill:
    skill = Skill(directory, scope, root)
    skill_md = directory / "SKILL.md"
    try:
        text = skill_md.read_text(encoding="utf-8")
    except OSError as exc:
        skill.error = f"cannot read SKILL.md: {exc}"
        return skill

    fields, body, error = parse_skill_md(text)
    skill.frontmatter = fields
    skill.body = body
    skill.error = error
    skill.name = fields.get("name", "") or directory.name
    skill.description = fields.get("description", "")
    return skill


def candidate_roots(extra: list[Path]) -> list[tuple[str, Path]]:
    """Every directory that may hold skills, as (scope, path) in scan order."""
    roots: list[tuple[str, Path]] = []
    seen: set[Path] = set()

    def add(scope: str, path: Path) -> None:
        resolved = path.expanduser()
        if resolved not in seen:
            seen.add(resolved)
            roots.append((scope, resolved))

    cwd = Path.cwd().resolve()
    ancestors = [cwd, *list(cwd.parents)[:MAX_ANCESTOR_DEPTH]]
    for directory in ancestors:
        for name in SKILL_DIR_NAMES:
            add("project", directory / name)
        if (directory / ".git").exists():
            break

    home = Path.home()
    for name in SKILL_DIR_NAMES:
        add("user", home / name)

    for path in extra:
        add("extra", Path(path).resolve())

    return roots


def discover(roots: list[tuple[str, Path]]) -> list[Skill]:
    skills: list[Skill] = []
    for scope, root in roots:
        if not root.is_dir():
            continue
        for child in sorted(root.iterdir()):
            if child.is_dir() and (child / "SKILL.md").is_file():
                skills.append(load_skill(child, scope, root))
    return skills


def bundled_resources(directory: Path, limit: int = 12) -> list[str]:
    files: list[str] = []
    for path in sorted(directory.rglob("*")):
        if not path.is_file() or path.name == "SKILL.md":
            continue
        relative = path.relative_to(directory)
        if any(part.startswith(".") or part == "__pycache__" for part in relative.parts):
            continue
        files.append(relative.as_posix())
        if len(files) > limit:
            return files[:limit] + [f"... (+{len(files) - limit} more)"]
    return files


def command_list(extra: list[Path]) -> int:
    roots = candidate_roots(extra)
    skills = discover(roots)

    present = [(scope, root) for scope, root in roots if root.is_dir()]
    print(f"Skill directories found: {len(present)} of {len(roots)} candidates")
    for scope, root in present:
        count = sum(1 for s in skills if s.root == root)
        print(f"  [{scope}] {root} — {count} skill(s)")

    print(f"\nSkills discovered: {len(skills)}")
    for skill in skills:
        line_count = len(skill.body.splitlines())
        print(f"\n  [{skill.scope}] {skill.name}")
        print(f"    path: {skill.directory}")
        if skill.name != skill.directory.name:
            print(f"    NOTE: `name` does not match the directory name {skill.directory.name!r}")
        print(f"    body: {line_count} lines")
        generator = skill.frontmatter.get("metadata.generator")
        if generator:
            print(f"    generator: {generator}")
        resources = bundled_resources(skill.directory)
        if resources:
            print(f"    resources: {', '.join(resources)}")
        if skill.error:
            print(f"    PARSE ERROR: {skill.error}")
        description = skill.description or "(no description)"
        if len(description) > 400:
            description = description[:400] + " ..."
        print(f"    description: {description}")

    print("\nUser-level write targets (best first)")
    for scope, root in _ranked_targets(roots, skills):
        count = sum(1 for s in skills if s.root == root)
        if root.is_dir():
            print(f"  {root} — exists, {count} skill(s)")
        else:
            print(f"  {root} — would be created")
    print(
        "\nPrefer a target the host agent is known to read. A user-level directory that already "
        "holds skills is evidence that this host reads it."
    )
    return 0


def _ranked_targets(roots: list[tuple[str, Path]], skills: list[Skill]) -> list[tuple[str, Path]]:
    user_roots = [(scope, root) for scope, root in roots if scope == "user"]

    def rank(item: tuple[str, Path]) -> tuple[int, int]:
        _, root = item
        count = sum(1 for s in skills if s.root == root)
        # Populated directories first, then existing-but-empty, then the rest in scan order.
        return (0 if count else (1 if root.is_dir() else 2), -count)

    return sorted(user_roots, key=rank)


def command_validate(target: Path) -> int:
    directory = target.expanduser().resolve()
    errors: list[str] = []
    warnings: list[str] = []

    if not directory.is_dir():
        print(f"FAIL {directory}\n  - not a directory")
        return 1

    skill_md = directory / "SKILL.md"
    if not skill_md.is_file():
        print(f"FAIL {directory}\n  - no SKILL.md (the file must be named exactly SKILL.md)")
        return 1

    skill = load_skill(directory, "validate", directory.parent)
    if skill.error:
        print(f"FAIL {directory}\n  - {skill.error}")
        return 1

    name = skill.frontmatter.get("name", "")
    if not name:
        errors.append("frontmatter is missing the required `name` field")
    else:
        if len(name) > MAX_NAME_LENGTH:
            errors.append(f"`name` is {len(name)} characters (max {MAX_NAME_LENGTH})")
        if not NAME_PATTERN.match(name):
            errors.append(
                f"`name` {name!r} must be lowercase letters, digits, and single hyphens, "
                "without a leading or trailing hyphen"
            )
        if name != directory.name:
            errors.append(f"`name` {name!r} does not match the directory name {directory.name!r}")
        for word in RESERVED_NAME_WORDS:
            if word in name:
                warnings.append(f"`name` contains the reserved word {word!r}")

    description = skill.frontmatter.get("description", "")
    if not description:
        errors.append("frontmatter is missing a non-empty `description` field")
    elif len(description) > MAX_DESCRIPTION_LENGTH:
        errors.append(
            f"`description` is {len(description)} characters (max {MAX_DESCRIPTION_LENGTH})"
        )

    for field in ("name", "description"):
        value = skill.frontmatter.get(field, "")
        if re.search(r"<[^>]+>", value):
            errors.append(f"`{field}` must not contain XML or HTML tags")

    compatibility = skill.frontmatter.get("compatibility", "")
    if len(compatibility) > MAX_COMPATIBILITY_LENGTH:
        errors.append(
            f"`compatibility` is {len(compatibility)} characters (max {MAX_COMPATIBILITY_LENGTH})"
        )

    if description and " when " not in description.lower():
        warnings.append(
            "`description` may not say when to use the skill, which is what drives activation"
        )
    if re.match(r"^\s*(i |i'|you can|this skill lets you)", description, re.IGNORECASE):
        warnings.append("`description` should be written in third person")

    body_lines = len(skill.body.splitlines())
    if body_lines > MAX_BODY_LINES:
        warnings.append(
            f"body is {body_lines} lines (over {MAX_BODY_LINES}); move detail into references/"
        )
    if not skill.body:
        errors.append("body is empty; a skill needs instructions after the frontmatter")

    for link in MARKDOWN_LINK.findall(skill.body):
        if "\\" in link:
            errors.append(f"reference {link!r} uses backslashes; use forward slashes")
        path = (directory / link.split("#", 1)[0]).resolve()
        if not path.exists():
            errors.append(f"referenced file {link!r} does not exist in the skill directory")

    for sub in ("references", "scripts", "assets"):
        subdir = directory / sub
        if subdir.is_dir():
            for path in sorted(subdir.rglob("*")):
                if path.is_file():
                    relative = path.relative_to(directory).as_posix()
                    if relative not in skill.body:
                        warnings.append(f"bundled file {relative!r} is never referenced in SKILL.md")

    status = "FAIL" if errors else "PASS"
    print(f"{status} {directory}")
    for message in errors:
        print(f"  ERROR   {message}")
    for message in warnings:
        print(f"  WARNING {message}")
    if not errors and not warnings:
        print("  conforms to the Agent Skills specification")
    return 1 if errors else 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Inventory and validate Agent Skills.",
        epilog="With no arguments, lists discovered skills and candidate write targets.",
    )
    parser.add_argument(
        "--validate",
        metavar="DIR",
        help="check one skill directory against the Agent Skills specification",
    )
    parser.add_argument(
        "dirs",
        nargs="*",
        metavar="EXTRA_DIR",
        help="additional skill directories to include in the listing",
    )
    args = parser.parse_args(argv)

    if args.validate:
        return command_validate(Path(args.validate))
    return command_list([Path(d) for d in args.dirs])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
