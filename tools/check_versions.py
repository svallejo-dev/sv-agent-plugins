#!/usr/bin/env python3
"""Falla si un plugin cambió respecto de la rama base sin subir su versión en catalogo.json.

Claude Code, Codex y Copilot guardan cada plugin por número de versión: un cambio sin
subir la versión nunca llega a quien ya lo tiene instalado.

Uso:
  python3 tools/check_versions.py --base origin/main

Compara el árbol de trabajo (commits y cambios sin commitear) contra la base.
Códigos de salida: 0 todo en orden, 1 hay plugins cambiados sin subir versión, 2 error.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
GENERADOS = {"plugin.json", ".claude-plugin/plugin.json", ".codex-plugin/plugin.json", ".cursor-plugin/plugin.json"}


def _git(*args: str) -> str:
    r = subprocess.run(["git", "-C", str(RAIZ), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def _version(v: str) -> tuple[int, ...]:
    try:
        return tuple(int(x) for x in v.split("-")[0].split("."))
    except ValueError as e:
        raise RuntimeError(f"versión no numérica: {v}") from e


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", required=True, help="ref de git de la rama base, p. ej. origin/main")
    a = ap.parse_args(argv)
    try:
        _git("rev-parse", "--verify", f"{a.base}^{{commit}}")
        base_cat = json.loads(_git("show", f"{a.base}:catalogo.json"))
        cambiados = _git("diff", "--name-only", a.base, "--", "plugins").splitlines()
        cambiados += _git("ls-files", "--others", "--exclude-standard", "--", "plugins").splitlines()
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    actual = {p["name"]: p["version"] for p in json.loads((RAIZ / "catalogo.json").read_text())["plugins"]}
    antes = {p["name"]: p["version"] for p in base_cat["plugins"]}
    problemas = []
    for nombre, version in sorted(actual.items()):
        prefijo = f"plugins/{nombre}/"
        archivos = sorted({f for f in cambiados if f.startswith(prefijo) and f[len(prefijo):] not in GENERADOS})
        if nombre not in antes:
            print(f"  {nombre}: plugin nuevo ({version})")
            continue
        try:
            subio = _version(version) > _version(antes[nombre])
            bajo = _version(version) < _version(antes[nombre])
        except RuntimeError as e:
            print(f"error: {nombre}: {e}", file=sys.stderr)
            return 2
        if bajo:
            problemas.append(f"{nombre}: la versión bajó ({antes[nombre]} → {version})")
        elif archivos and not subio:
            muestra = ", ".join(archivos[:3]) + (f" y {len(archivos) - 3} más" if len(archivos) > 3 else "")
            problemas.append(f"{nombre}: cambió ({muestra}) pero sigue en {version}; súbela en catalogo.json")
        elif archivos:
            print(f"  {nombre}: {antes[nombre]} → {version} ({len(archivos)} archivos cambiados)")
    if problemas:
        print("Plugins con cambios sin subir versión (nadie recibiría la actualización):")
        for p in problemas:
            print(f"  - {p}")
        return 1
    print("Versiones en orden.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
