#!/usr/bin/env python3
"""Generates every plugin and marketplace manifest from catalog.json.

One source (catalog.json) and one manifest per tool, so they never drift apart:

  Per plugin (plugins/<name>/):
    plugin.json                  Agent Plugins 1.0 (Codex, GitHub Copilot, Cursor, VS Code)
    .claude-plugin/plugin.json   Claude Code
    .codex-plugin/plugin.json    Codex (compatibility with versions before Agent Plugins)
    .cursor-plugin/plugin.json   Cursor (its own format, used by its marketplace)

  At the root:
    .claude-plugin/marketplace.json   Claude Code (Codex and Copilot CLI read it too)
    .agents/plugins/marketplace.json  Codex
    .github/plugin/marketplace.json   GitHub Copilot CLI and VS Code
    .cursor-plugin/marketplace.json   Cursor

Windsurf has no plugin system: it installs the skills with install.sh (see README).

Usage:
  python3 tools/build_manifests.py           writes the manifests
  python3 tools/build_manifests.py --check   fails (exit 1) if any is out of date
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_AGENT_PLUGINS = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
RE_NAME = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")


def _json(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def _validate(cat: dict) -> list[str]:
    errors = []
    if not RE_NAME.match(cat["name"]):
        errors.append(f"invalid marketplace name: {cat['name']}")
    seen = set()
    for p in cat["plugins"]:
        n = p["name"]
        if not RE_NAME.match(n) or "--" in n:
            errors.append(f"invalid plugin name: {n}")
        if n in seen:
            errors.append(f"duplicate plugin: {n}")
        seen.add(n)
        folder = ROOT / "plugins" / n
        if not (folder / "skills").is_dir():
            errors.append(f"plugins/{n}/skills does not exist")
            continue
        for sk in sorted((folder / "skills").iterdir()):
            if sk.is_dir() and not (sk / "SKILL.md").is_file():
                errors.append(f"{sk.relative_to(ROOT)} has no SKILL.md")
    all_skills = [sk.parent.name for p in cat["plugins"]
                  for sk in (ROOT / "plugins" / p["name"] / "skills").glob("*/SKILL.md")]
    repeated = sorted({s for s in all_skills if all_skills.count(s) > 1})
    if repeated:
        errors.append(f"skill names repeated across plugins (they clash in tools without namespaces): {repeated}")
    return errors


def generate(cat: dict) -> dict[Path, str]:
    author = {"name": cat["owner"]["name"], "url": cat["owner"]["url"]}
    files: dict[Path, str] = {}
    for p in cat["plugins"]:
        base = Path("plugins") / p["name"]
        common = {"name": p["name"], "version": p["version"], "description": p["description"]}
        meta = {"homepage": f"{cat['homepage']}/tree/main/plugins/{p['name']}", "repository": cat["repository"],
                "license": cat["license"], "keywords": p["keywords"]}
        files[base / "plugin.json"] = _json({"$schema": SCHEMA_AGENT_PLUGINS, **common, "author": author, **meta})
        files[base / ".claude-plugin/plugin.json"] = _json({**common, "author": {"name": author["name"]}, **meta})
        files[base / ".codex-plugin/plugin.json"] = _json({**common, "author": author, **meta, "skills": "./skills/"})
        files[base / ".cursor-plugin/plugin.json"] = _json({**common, "author": {"name": author["name"]}, **meta})

    owner = {"name": cat["owner"]["name"]}
    files[Path(".claude-plugin/marketplace.json")] = _json({
        "name": cat["name"], "owner": owner, "metadata": {"description": cat["description"]},
        "plugins": [{"name": p["name"], "source": f"./plugins/{p['name']}", "description": p["description"],
                     "version": p["version"], "category": p["category"].lower().replace(" ", "-"),
                     "keywords": p["keywords"]} for p in cat["plugins"]],
    })
    files[Path(".agents/plugins/marketplace.json")] = _json({
        "name": cat["name"], "interface": {"displayName": cat["displayName"]},
        "plugins": [{"name": p["name"], "source": {"source": "local", "path": f"./plugins/{p['name']}"},
                     "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                     "category": p["category"]} for p in cat["plugins"]],
    })
    files[Path(".github/plugin/marketplace.json")] = _json({
        "name": cat["name"], "owner": owner, "metadata": {"description": cat["description"]},
        "plugins": [{"name": p["name"], "source": f"./plugins/{p['name']}", "description": p["description"],
                     "version": p["version"], "keywords": p["keywords"],
                     "category": p["category"].lower().replace(" ", "-")} for p in cat["plugins"]],
    })
    files[Path(".cursor-plugin/marketplace.json")] = _json({
        "name": cat["name"], "owner": owner, "metadata": {"description": cat["description"]},
        "plugins": [{"name": p["name"], "source": f"plugins/{p['name']}", "description": p["description"],
                     "version": p["version"], "category": p["category"].lower().replace(" ", "-")}
                    for p in cat["plugins"]],
    })
    return files


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="does not write; fails if any manifest is out of date")
    a = ap.parse_args(argv)
    cat = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    errors = _validate(cat)
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        return 2
    stale = []
    for path, content in generate(cat).items():
        target = ROOT / path
        current = target.read_text(encoding="utf-8") if target.exists() else None
        if current != content:
            stale.append(path.as_posix())
            if not a.check:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
    if a.check:
        if stale:
            print("Out-of-date manifests (run python3 tools/build_manifests.py):")
            for r in stale:
                print(f"  {r}")
            return 1
        print("Manifests up to date.")
        return 0
    print(f"Wrote {len(stale)} manifests." if stale else "Nothing to change.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
