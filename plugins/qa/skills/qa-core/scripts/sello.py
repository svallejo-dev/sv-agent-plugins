#!/usr/bin/env python3
"""Sello de integridad del oráculo (criterios, escenarios, tests de aceptación y configuración de QA).

Registra el hash SHA-256 de cada archivo bajo las rutas selladas y detecta cualquier
modificación, eliminación, archivo nuevo o enlace simbólico. Con --base compara además
contra el sello de la rama base (git) y lista TODO re-sellado hecho desde entonces, para
que un humano lo revise: un agente puede editar y volver a sellar, pero no puede hacerlo
sin que quede a la vista en la verificación.

Lo que este script NO hace: impedir la edición ni saber quién re-selló (--autor es
declarativo). La atribución real es la autoría de git y la revisión del PR.

Uso:
  sello.py sellar    --sello RUTA [--raiz DIR] --motivo TEXTO [--autor X] RUTA...
  sello.py resellar  --sello RUTA [--raiz DIR] --motivo TEXTO [--autor X] [RUTA...]
  sello.py verificar --sello RUTA [--raiz DIR] [--base REF] [--requiere RUTA...] [--json]
  sello.py historial --sello RUTA

Códigos de salida: 0 íntegro / operación hecha, 1 sello roto, 2 error de uso.
Solo usa la biblioteca estándar (y git para --base).
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

VERSION = 1
IGNORADOS = {".DS_Store"}
RE_REFERENCIA = re.compile(r"(?<![A-Za-z0-9])[EH]-\d{2,}(?!\d)")


class ErrorDeUso(Exception):
    pass


def _hash(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(65536), b""):
            h.update(bloque)
    return h.hexdigest()


def _rel(p: Path, raiz: Path) -> str:
    return Path(os.path.abspath(p)).relative_to(Path(os.path.abspath(raiz))).as_posix()


def _caminar(base: Path):
    """Recorre sin seguir enlaces simbólicos; devuelve (archivos, enlaces)."""
    archivos, enlaces = [], []
    for dirpath, dirnames, filenames in os.walk(base, followlinks=False):
        for d in list(dirnames):
            if os.path.islink(os.path.join(dirpath, d)):
                enlaces.append(Path(dirpath) / d)
                dirnames.remove(d)
        for f in filenames:
            p = Path(dirpath) / f
            (enlaces if p.is_symlink() else archivos).append(p)
    return sorted(archivos), sorted(enlaces)


def recolectar(rutas: list[str], raiz: Path, sello: Path) -> tuple[dict[str, str], list[str]]:
    """({ruta_relativa: sha256}, [enlaces simbólicos no sellables])."""
    archivos: dict[str, str] = {}
    enlaces: list[str] = []
    sello_abs = os.path.abspath(sello)
    raiz_abs = Path(os.path.abspath(raiz))
    for r in rutas:
        base = raiz / r
        if not base.exists() and not base.is_symlink():
            raise ErrorDeUso(f"la ruta a sellar no existe: {r}")
        try:
            Path(os.path.abspath(base)).relative_to(raiz_abs)
        except ValueError as e:
            raise ErrorDeUso(f"la ruta {r} está fuera de la raíz {raiz}") from e
        if base.is_symlink():
            enlaces.append(_rel(base, raiz))
            continue
        if base.is_file():
            candidatos, ligas = [base], []
        else:
            candidatos, ligas = _caminar(base)
        enlaces.extend(_rel(p, raiz) for p in ligas)
        for p in candidatos:
            if p.name in IGNORADOS or os.path.abspath(p) == sello_abs or p.name.endswith(".qa-sello.json.tmp"):
                continue
            archivos[_rel(p, raiz)] = _hash(p)
    return dict(sorted(archivos.items())), sorted(set(enlaces))


def _digest(archivos: dict[str, str]) -> str:
    h = hashlib.sha256()
    for ruta, sha in archivos.items():
        h.update(f"{ruta}\0{sha}\n".encode())
    return h.hexdigest()


def _validar(datos: dict, origen: str) -> dict:
    if datos.get("version") != VERSION:
        raise ErrorDeUso(f"versión de sello no soportada en {origen}: {datos.get('version')}")
    return datos


def _leer(sello: Path) -> dict:
    if not sello.exists():
        raise ErrorDeUso(f"no existe el sello {sello}")
    return _validar(json.loads(sello.read_text(encoding="utf-8")), str(sello))


def _leer_base(sello: Path, raiz: Path, ref: str) -> dict | None:
    rel = _rel(sello, raiz)
    r = subprocess.run(["git", "-C", str(raiz), "show", f"{ref}:{rel}"], capture_output=True, text=True)
    if r.returncode != 0:
        verif = subprocess.run(["git", "-C", str(raiz), "rev-parse", "--verify", ref], capture_output=True, text=True)
        if verif.returncode != 0:
            raise ErrorDeUso(f"la referencia base '{ref}' no existe")
        return None  # el sello no existía en la base: feature nueva
    return _validar(json.loads(r.stdout), f"{ref}:{rel}")


def _escribir(sello: Path, datos: dict) -> None:
    sello.parent.mkdir(parents=True, exist_ok=True)
    tmp = sello.with_name(sello.name + ".tmp")
    tmp.write_text(json.dumps(datos, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, sello)


def _entrada(accion: str, motivo: str, autor: str, archivos: dict[str, str]) -> dict:
    return {
        "fecha": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "accion": accion,
        "motivo": motivo,
        "autor": autor,
        "n_archivos": len(archivos),
        "digest": _digest(archivos),
    }


def _normalizar(rutas: list[str]) -> list[str]:
    return sorted({Path(r).as_posix().rstrip("/") for r in rutas})


def sellar(sello: Path, raiz: Path, rutas: list[str], motivo: str, autor: str) -> dict:
    if sello.exists():
        raise ErrorDeUso("el sello ya existe; para cambiarlo usa 'resellar' con un motivo")
    if not rutas:
        raise ErrorDeUso("indica al menos una ruta a sellar")
    if not motivo.strip():
        raise ErrorDeUso("el motivo es obligatorio")
    rutas_norm = _normalizar(rutas)
    archivos, enlaces = recolectar(rutas_norm, raiz, sello)
    if enlaces:
        raise ErrorDeUso(f"hay enlaces simbólicos, que no se pueden sellar: {', '.join(enlaces)}")
    if not archivos:
        raise ErrorDeUso("no hay archivos que sellar en las rutas indicadas")
    datos = {"version": VERSION, "rutas": rutas_norm, "archivos": archivos,
             "historial": [_entrada("sellar", motivo, autor, archivos)]}
    _escribir(sello, datos)
    return datos


def comparar(datos: dict, actuales: dict[str, str]) -> dict[str, list[str]]:
    sellados = datos["archivos"]
    return {
        "modificados": sorted(r for r in sellados if r in actuales and actuales[r] != sellados[r]),
        "eliminados": sorted(r for r in sellados if r not in actuales),
        "nuevos": sorted(r for r in actuales if r not in sellados),
    }


def _cubierta(ruta: str, rutas: list[str]) -> bool:
    ruta = Path(ruta).as_posix().rstrip("/")
    return any(ruta == r or ruta.startswith(r + "/") for r in rutas)


def verificar(sello: Path, raiz: Path, base: str | None = None, requeridas: list[str] | None = None) -> dict:
    """Devuelve un informe con 'integro' y todas las causas de rotura."""
    informe: dict = {"integro": True, "modificados": [], "eliminados": [], "nuevos": [], "enlaces": [],
                     "rutas_faltantes": [], "requeridas_sin_sellar": [], "base": base,
                     "resellados_desde_base": [], "problemas_base": []}
    datos_base = _leer_base(sello, raiz, base) if base else None
    if not sello.exists():
        if base and datos_base is not None:
            informe["integro"] = False
            informe["problemas_base"].append("el sello existía en la base y fue eliminado")
            return informe
        raise ErrorDeUso(f"no existe el sello {sello}")
    datos = _leer(sello)
    existentes = [r for r in datos["rutas"] if (raiz / r).exists() or (raiz / r).is_symlink()]
    informe["rutas_faltantes"] = [r for r in datos["rutas"] if r not in existentes]
    actuales, enlaces = recolectar(existentes, raiz, sello) if existentes else ({}, [])
    informe.update(comparar(datos, actuales))
    informe["enlaces"] = enlaces
    informe["requeridas_sin_sellar"] = [r for r in (requeridas or []) if not _cubierta(r, datos["rutas"])]
    if base:
        hist, hist_base = datos["historial"], (datos_base or {}).get("historial", [])
        if hist[:len(hist_base)] != hist_base:
            informe["problemas_base"].append("el historial del sello fue reescrito respecto de la base")
            nuevos = hist
        else:
            nuevos = hist[len(hist_base):]
        informe["resellados_desde_base"] = nuevos
        if datos_base is not None:
            for e in nuevos:
                if e.get("accion") == "resellar" and not RE_REFERENCIA.search(e.get("motivo", "")):
                    informe["problemas_base"].append(
                        f"re-sellado del {e.get('fecha')} sin referencia a un escalamiento o hallazgo (E-NN / H-NN)")
    informe["integro"] = not any(informe[k] for k in ("modificados", "eliminados", "nuevos", "enlaces",
                                                       "rutas_faltantes", "requeridas_sin_sellar", "problemas_base"))
    return informe


def resellar(sello: Path, raiz: Path, rutas: list[str], motivo: str, autor: str) -> tuple[dict, dict]:
    if not motivo.strip():
        raise ErrorDeUso("el motivo es obligatorio para resellar (cita el escalamiento E-NN o el hallazgo H-NN)")
    datos = _leer(sello)
    rutas_norm = _normalizar(datos["rutas"] + rutas)
    archivos, enlaces = recolectar([r for r in rutas_norm if (raiz / r).exists()], raiz, sello)
    if enlaces:
        raise ErrorDeUso(f"hay enlaces simbólicos, que no se pueden sellar: {', '.join(enlaces)}")
    cambios = comparar(datos, archivos)
    entrada = _entrada("resellar", motivo, autor, archivos)
    entrada["cambios"] = cambios
    datos["rutas"], datos["archivos"] = rutas_norm, archivos
    datos["historial"].append(entrada)
    _escribir(sello, datos)
    return datos, cambios


def _imprimir(informe: dict) -> None:
    etiquetas = [("modificados", "MODIFICADO"), ("eliminados", "ELIMINADO"), ("nuevos", "NUEVO SIN SELLAR"),
                 ("enlaces", "ENLACE SIMBÓLICO (no sellable)"), ("rutas_faltantes", "RUTA SELLADA DESAPARECIDA"),
                 ("requeridas_sin_sellar", "REQUERIDA Y NO SELLADA"), ("problemas_base", "BASE")]
    for clave, etiqueta in etiquetas:
        for r in informe.get(clave, []):
            print(f"  {etiqueta}: {r}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Sello de integridad del oráculo de QA")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for nombre in ("sellar", "resellar", "verificar", "historial"):
        p = sub.add_parser(nombre)
        p.add_argument("--sello", required=True, type=Path)
        p.add_argument("--raiz", type=Path, default=Path("."))
        if nombre in ("sellar", "resellar"):
            p.add_argument("--motivo", required=True)
            p.add_argument("--autor", default=os.environ.get("USER", "desconocido"),
                           help="declarativo: la atribución real es la autoría de git")
            p.add_argument("rutas", nargs="*")
        if nombre == "verificar":
            p.add_argument("--base", help="ref de git de la rama base (p. ej. origin/main)")
            p.add_argument("--requiere", nargs="*", default=[], help="rutas que deben estar selladas")
            p.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "sellar":
            datos = sellar(a.sello, a.raiz, a.rutas, a.motivo, a.autor)
            print(f"Sello creado: {len(datos['archivos'])} archivos en {', '.join(datos['rutas'])}")
            return 0
        if a.cmd == "resellar":
            datos, cambios = resellar(a.sello, a.raiz, a.rutas, a.motivo, a.autor)
            print(f"Sello actualizado ({len(datos['archivos'])} archivos). Motivo: {a.motivo}")
            for clave, etiqueta in (("modificados", "cambiado"), ("eliminados", "retirado"), ("nuevos", "añadido")):
                for r in cambios[clave]:
                    print(f"  {etiqueta}: {r}")
            return 0
        if a.cmd == "verificar":
            inf = verificar(a.sello, a.raiz, a.base, a.requiere)
            if a.json:
                print(json.dumps(inf, ensure_ascii=False, indent=2))
            else:
                if inf["integro"]:
                    print("Sello íntegro.")
                else:
                    print("SELLO ROTO:")
                    _imprimir(inf)
                if a.base:
                    print(f"\nSellados y re-sellados desde {a.base} (revisión humana obligatoria): "
                          f"{len(inf['resellados_desde_base'])}")
                    for e in inf["resellados_desde_base"]:
                        print(f"  {e['fecha']}  {e['accion']:<9} {e['n_archivos']:>4} archivos  {e['motivo']}")
            return 0 if inf["integro"] else 1
        if a.cmd == "historial":
            for e in _leer(a.sello)["historial"]:
                print(f"{e['fecha']}  {e['accion']:<9} {e['n_archivos']:>4} archivos  {e['autor']}: {e['motivo']}")
            return 0
    except (ErrorDeUso, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
