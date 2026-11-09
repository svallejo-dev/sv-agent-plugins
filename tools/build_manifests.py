#!/usr/bin/env python3
"""Genera todos los manifiestos de plugins y marketplaces desde catalogo.json.

Una sola fuente (catalogo.json) y un manifiesto por herramienta, para que no se desincronicen:

  Por plugin (plugins/<nombre>/):
    plugin.json                  Agent Plugins 1.0 (Codex, GitHub Copilot, Cursor, VS Code)
    .claude-plugin/plugin.json   Claude Code
    .codex-plugin/plugin.json    Codex (compatibilidad con versiones anteriores a Agent Plugins)
    .cursor-plugin/plugin.json   Cursor (formato propio, usado por su marketplace)

  En la raíz:
    .claude-plugin/marketplace.json   Claude Code (también lo leen Codex y Copilot CLI)
    .agents/plugins/marketplace.json  Codex
    .github/plugin/marketplace.json   GitHub Copilot CLI y VS Code
    .cursor-plugin/marketplace.json   Cursor

Windsurf no tiene sistema de plugins: instala las skills con install.sh (ver README).

Uso:
  python3 tools/build_manifests.py           escribe los manifiestos
  python3 tools/build_manifests.py --check   falla (exit 1) si alguno está desactualizado
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
SCHEMA_AGENT_PLUGINS = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
RE_NOMBRE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")


def _json(datos: dict) -> str:
    return json.dumps(datos, indent=2, ensure_ascii=False) + "\n"


def _validar(cat: dict) -> list[str]:
    errores = []
    if not RE_NOMBRE.match(cat["name"]):
        errores.append(f"nombre de marketplace inválido: {cat['name']}")
    vistos = set()
    for p in cat["plugins"]:
        n = p["name"]
        if not RE_NOMBRE.match(n) or "--" in n:
            errores.append(f"nombre de plugin inválido: {n}")
        if n in vistos:
            errores.append(f"plugin duplicado: {n}")
        vistos.add(n)
        carpeta = RAIZ / "plugins" / n
        if not (carpeta / "skills").is_dir():
            errores.append(f"plugins/{n}/skills no existe")
            continue
        for sk in sorted((carpeta / "skills").iterdir()):
            if sk.is_dir() and not (sk / "SKILL.md").is_file():
                errores.append(f"{sk.relative_to(RAIZ)} no tiene SKILL.md")
    todas = [sk.name for p in cat["plugins"] for sk in (RAIZ / "plugins" / p["name"] / "skills").glob("*/SKILL.md")
             for sk in [sk.parent]]
    repetidas = sorted({s for s in todas if todas.count(s) > 1})
    if repetidas:
        errores.append(f"nombres de skill repetidos entre plugins (chocan en herramientas sin espacios de nombres): {repetidas}")
    return errores


def generar(cat: dict) -> dict[Path, str]:
    autor = {"name": cat["owner"]["name"], "url": cat["owner"]["url"]}
    archivos: dict[Path, str] = {}
    for p in cat["plugins"]:
        base = Path("plugins") / p["name"]
        comun = {"name": p["name"], "version": p["version"], "description": p["description"]}
        meta = {"homepage": f"{cat['homepage']}/tree/main/plugins/{p['name']}", "repository": cat["repository"],
                "license": cat["license"], "keywords": p["keywords"]}
        archivos[base / "plugin.json"] = _json({"$schema": SCHEMA_AGENT_PLUGINS, **comun, "author": autor, **meta})
        archivos[base / ".claude-plugin/plugin.json"] = _json({**comun, "author": {"name": autor["name"]}, **meta})
        archivos[base / ".codex-plugin/plugin.json"] = _json({**comun, "author": autor, **meta, "skills": "./skills/"})
        archivos[base / ".cursor-plugin/plugin.json"] = _json({**comun, "author": {"name": autor["name"]}, **meta})

    owner = {"name": cat["owner"]["name"]}
    archivos[Path(".claude-plugin/marketplace.json")] = _json({
        "name": cat["name"], "owner": owner, "metadata": {"description": cat["description"]},
        "plugins": [{"name": p["name"], "source": f"./plugins/{p['name']}", "description": p["description"],
                     "version": p["version"], "category": p["category"].lower().replace(" ", "-"),
                     "keywords": p["keywords"]} for p in cat["plugins"]],
    })
    archivos[Path(".agents/plugins/marketplace.json")] = _json({
        "name": cat["name"], "interface": {"displayName": cat["displayName"]},
        "plugins": [{"name": p["name"], "source": {"source": "local", "path": f"./plugins/{p['name']}"},
                     "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                     "category": p["category"]} for p in cat["plugins"]],
    })
    archivos[Path(".github/plugin/marketplace.json")] = _json({
        "name": cat["name"], "owner": owner, "metadata": {"description": cat["description"]},
        "plugins": [{"name": p["name"], "source": f"./plugins/{p['name']}", "description": p["description"],
                     "version": p["version"], "keywords": p["keywords"],
                     "category": p["category"].lower().replace(" ", "-")} for p in cat["plugins"]],
    })
    archivos[Path(".cursor-plugin/marketplace.json")] = _json({
        "name": cat["name"], "owner": owner, "metadata": {"description": cat["description"]},
        "plugins": [{"name": p["name"], "source": f"plugins/{p['name']}", "description": p["description"],
                     "version": p["version"], "category": p["category"].lower().replace(" ", "-")}
                    for p in cat["plugins"]],
    })
    return archivos


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="no escribe; falla si hay manifiestos desactualizados")
    a = ap.parse_args(argv)
    cat = json.loads((RAIZ / "catalogo.json").read_text(encoding="utf-8"))
    errores = _validar(cat)
    if errores:
        for e in errores:
            print(f"error: {e}", file=sys.stderr)
        return 2
    desactualizados = []
    for ruta, contenido in generar(cat).items():
        destino = RAIZ / ruta
        actual = destino.read_text(encoding="utf-8") if destino.exists() else None
        if actual != contenido:
            desactualizados.append(ruta.as_posix())
            if not a.check:
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_text(contenido, encoding="utf-8")
    if a.check:
        if desactualizados:
            print("Manifiestos desactualizados (ejecuta python3 tools/build_manifests.py):")
            for r in desactualizados:
                print(f"  {r}")
            return 1
        print("Manifiestos al día.")
        return 0
    print(f"Escritos {len(desactualizados)} manifiestos." if desactualizados else "Nada que cambiar.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
