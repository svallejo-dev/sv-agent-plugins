#!/usr/bin/env python3
"""Ejecuta mutantes (bugs inyectados a propósito) contra la suite de aceptación.

Cada mutante es un parche (diff unificado). Para cada uno: crea un git worktree temporal con
el estado actual del repositorio (cambios sin commitear y archivos no rastreados incluidos),
aplica el parche, ejecuta el comando de la suite y decide si la suite lo detectó. El
repositorio original nunca se modifica.

Analogía: calibrar una balanza con pesas patrón. Si pones 1 kg y marca 0, la balanza no
sirve, aunque siempre haya marcado "bien".

Contrato con el comando de la suite (variables de entorno que recibe):
  QA_REPORTES      directorio vacío, propio de esa ejecución, donde DEBE escribir sus JUnit
  QA_IMAGEN_TAG    tag único para la imagen que construya desde el directorio actual
  QA_MUTANTE       ID del mutante ("base" en la ejecución sin mutantes)

Un mutante cuenta como DETECTADO solo si el comando termina en rojo Y al menos un caso JUnit
con ID de escenario (ESC-NN) falló. Un rojo sin escenario fallido (no compila, el harness no
arranca, puerto ocupado) es "error-harness" y no cuenta como detectado.

Uso:
  mutantes.py huella   [--repo DIR]
  mutantes.py base     --cmd "COMANDO" [--repo DIR] [--timeout SEG]
  mutantes.py ejecutar --cmd "COMANDO" [--repo DIR] [--timeout SEG] [--salida resultados.json]
                       [--prohibidas RUTA ...] [--limpieza "COMANDO"] PARCHE...

Códigos de salida: 0 todos detectados, 1 algún mutante no detectado (sobrevive, timeout,
error-harness, no-aplica, rechazado), 2 error (incluida una base que no pasa).
Solo usa la biblioteca estándar y git.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from trazabilidad import ErrorDeFormato, leer_junit  # noqa: E402


class ErrorDeMutacion(Exception):
    pass


def _git(repo: Path, *args: str, check: bool = True, texto: bool = True) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=texto)
    if check and r.returncode != 0:
        err = r.stderr if texto else r.stderr.decode(errors="replace")
        raise ErrorDeMutacion(f"git {' '.join(args)} falló: {err.strip()}")
    return r


def _sha(datos: bytes) -> str:
    return hashlib.sha256(datos).hexdigest()


def no_rastreados(repo: Path) -> list[str]:
    salida = _git(repo, "ls-files", "--others", "--exclude-standard", "-z").stdout
    return [p for p in salida.split("\0") if p]


def huella(repo: Path) -> dict:
    """Identifica el código evaluado: HEAD + diff sin commitear + no rastreados."""
    if _git(repo, "rev-parse", "--is-inside-work-tree", check=False).returncode != 0:
        raise ErrorDeMutacion(f"{repo} no es un repositorio git")
    head = _git(repo, "rev-parse", "HEAD").stdout.strip()
    diff = _git(repo, "diff", "HEAD", "--binary", texto=False).stdout
    h = hashlib.sha256(diff)
    for rel in sorted(no_rastreados(repo)):
        p = repo / rel
        h.update(rel.encode())
        if p.is_file():
            h.update(p.read_bytes())
    return {"head": head, "cambios": h.hexdigest()}


def instantanea(repo: Path) -> str:
    stash = _git(repo, "stash", "create").stdout.strip()
    return stash or _git(repo, "rev-parse", "HEAD").stdout.strip()


class Worktree:
    """git worktree temporal que siempre se elimina, pase lo que pase."""

    def __init__(self, repo: Path, commit: str, extras: list[str]):
        self.repo, self.commit, self.extras = repo, commit, extras
        self.dir: Path | None = None
        self.omitidos: list[str] = []

    def __enter__(self) -> "Worktree":
        padre = Path(tempfile.mkdtemp(prefix="qa-mutante-"))
        self.dir = padre / "wt"
        _git(self.repo, "worktree", "add", "--detach", str(self.dir), self.commit)
        for rel in self.extras:
            origen, destino = self.repo / rel, self.dir / rel
            if not origen.is_file():
                self.omitidos.append(rel)  # p. ej. un repositorio anidado
                continue
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(origen, destino)
        return self

    def __exit__(self, *exc) -> None:
        if self.dir is not None:
            _git(self.repo, "worktree", "remove", "--force", str(self.dir), check=False)
            shutil.rmtree(self.dir.parent, ignore_errors=True)
            _git(self.repo, "worktree", "prune", check=False)


def correr(cmd: str, cwd: Path, timeout: int, env_extra: dict[str, str]) -> dict:
    """Ejecuta en su propio grupo de procesos; en timeout mata el grupo entero."""
    env = {**os.environ, **env_extra}
    with tempfile.TemporaryFile() as salida:
        inicio = time.monotonic()
        proc = subprocess.Popen(cmd, shell=True, cwd=cwd, env=env, stdout=salida, stderr=subprocess.STDOUT,
                                start_new_session=True)
        try:
            codigo = proc.wait(timeout=timeout)
            estado = "pasa" if codigo == 0 else "falla"
        except subprocess.TimeoutExpired:
            codigo, estado = None, "timeout"
        finally:
            try:
                os.killpg(proc.pid, signal.SIGKILL)  # limpia descendientes, también tras terminar
            except (ProcessLookupError, PermissionError):
                pass
            proc.wait()
        segundos = time.monotonic() - inicio
        salida.seek(0)
        cola = salida.read()[-3000:].decode(errors="replace")
    return {"estado": estado, "codigo": codigo, "segundos": round(segundos, 1), "salida": cola}


def _escenarios_rojos(reportes: Path) -> tuple[list[str], int]:
    xmls = sorted(reportes.rglob("*.xml"))
    if not xmls:
        return [], 0
    try:
        resultados, _, _ = leer_junit(xmls)
    except ErrorDeFormato:
        return [], 0
    rojos = sorted(i for i, rs in resultados.items() if "failed" in rs)
    return rojos, len(resultados)


def _ejecucion(repo: Path, commit: str, extras: list[str], cmd: str, timeout: int, ident: str,
               parche: Path | None, limpieza: str | None) -> dict:
    with Worktree(repo, commit, extras) as wt, tempfile.TemporaryDirectory(prefix="qa-reportes-") as rep:
        if parche is not None:
            chequeo = _git(wt.dir, "apply", "--check", str(parche), check=False)
            if chequeo.returncode != 0:
                return {"resultado": "no-aplica", "detalle": chequeo.stderr.strip()[-500:]}
            _git(wt.dir, "apply", str(parche))
        env = {"QA_REPORTES": rep, "QA_IMAGEN_TAG": f"qa-mut-{ident.lower()}-{os.getpid()}", "QA_MUTANTE": ident}
        r = correr(cmd, wt.dir, timeout, env)
        r["escenarios_rojos"], r["escenarios_ejecutados"] = _escenarios_rojos(Path(rep))
        r["omitidos"] = wt.omitidos
        if limpieza:
            correr(limpieza, wt.dir, 300, env)
    return r


def _objetivos(parche: Path) -> list[str]:
    rutas = set()
    for linea in parche.read_text(encoding="utf-8", errors="replace").splitlines():
        if linea.startswith(("+++ ", "--- ")):
            ruta = linea[4:].split("\t")[0].strip()
            if ruta != "/dev/null":
                rutas.add(ruta[2:] if ruta.startswith(("a/", "b/")) else ruta)
    return sorted(rutas)


def base(repo: Path, cmd: str, timeout: int) -> dict:
    commit = instantanea(repo)
    r = _ejecucion(repo, commit, no_rastreados(repo), cmd, timeout, "base", None, None)
    r["commit"] = commit
    return r


def ejecutar(repo: Path, cmd: str, parches: list[Path], timeout: int, con_base: bool = True,
             prohibidas: list[str] | None = None, limpieza: str | None = None) -> dict:
    if not parches:
        raise ErrorDeMutacion("indica al menos un parche")
    for p in parches:
        if not p.is_file():
            raise ErrorDeMutacion(f"no existe el parche {p}")
    prohibidas = [Path(x).as_posix().rstrip("/") for x in (prohibidas or [])]
    resumen: dict = {"huella": huella(repo), "base": None, "mutantes": []}
    commit = instantanea(repo)
    extras = no_rastreados(repo)
    if con_base:
        b = _ejecucion(repo, commit, extras, cmd, timeout, "base", None, limpieza)
        resumen["base"] = b
        if b["estado"] != "pasa":
            raise ErrorDeMutacion(f"la suite no pasa sin mutantes (estado: {b['estado']}); "
                                  f"los resultados no significarían nada.\n{b['salida']}")
        if b["escenarios_ejecutados"] == 0:
            raise ErrorDeMutacion("la ejecución base no dejó ningún JUnit con escenarios ESC-NN en $QA_REPORTES; "
                                  "sin reportes no se puede distinguir un bug detectado de un harness roto")
    for parche in parches:
        datos = parche.read_bytes()
        entrada = {"parche": parche.name, "sha256": _sha(datos), "objetivos": _objetivos(parche)}
        tocadas = [o for o in entrada["objetivos"] if any(o == p or o.startswith(p + "/") for p in prohibidas)]
        if tocadas:
            entrada.update(resultado="rechazado", detalle=f"toca rutas prohibidas (oráculo o harness): {', '.join(tocadas)}")
            resumen["mutantes"].append(entrada)
            continue
        ident = re.sub(r"[^a-z0-9-]", "-", parche.stem.lower())[:40]
        r = _ejecucion(repo, commit, extras, cmd, timeout, ident, parche.resolve(), limpieza)
        if r.get("resultado") == "no-aplica":
            entrada.update(r)
        elif r["estado"] == "timeout":
            entrada.update(r, resultado="timeout")
        elif r["estado"] == "pasa":
            entrada.update(r, resultado="sobrevive")
        elif r["escenarios_rojos"]:
            entrada.update(r, resultado="detectado")
            entrada["salida"] = ""
        else:
            entrada.update(r, resultado="error-harness")
        resumen["mutantes"].append(entrada)
    return resumen


def _tabla(resumen: dict) -> str:
    filas = ["| Parche | Resultado | Escenarios en rojo | Segundos |", "|---|---|---|---|"]
    for m in resumen["mutantes"]:
        rojos = ", ".join(m.get("escenarios_rojos", [])) or "—"
        filas.append(f"| {m['parche']} | {m['resultado']} | {rojos} | {m.get('segundos', '—')} |")
    total = len(resumen["mutantes"])
    detectados = sum(1 for m in resumen["mutantes"] if m["resultado"] == "detectado")
    filas.append(f"\nDetectados: {detectados}/{total}")
    filas.append(f"Huella: HEAD {resumen['huella']['head'][:12]} · cambios {resumen['huella']['cambios'][:12]}")
    return "\n".join(filas)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Ejecuta mutantes contra la suite de aceptación")
    sub = ap.add_subparsers(dest="cmd_", required=True)
    h = sub.add_parser("huella")
    h.add_argument("--repo", type=Path, default=Path("."))
    for nombre in ("base", "ejecutar"):
        p = sub.add_parser(nombre)
        p.add_argument("--cmd", required=True, help="comando de la suite; exit 0 = verde; escribe JUnit en $QA_REPORTES")
        p.add_argument("--repo", type=Path, default=Path("."))
        p.add_argument("--timeout", type=int, default=1800)
        if nombre == "ejecutar":
            p.add_argument("--salida", type=Path)
            p.add_argument("--prohibidas", nargs="*", default=[], help="rutas que un mutante no puede tocar")
            p.add_argument("--limpieza", help="comando tras cada ejecución (p. ej. borrar la imagen $QA_IMAGEN_TAG)")
            p.add_argument("parches", nargs="+", type=Path)
    a = ap.parse_args(argv)
    repo = a.repo.resolve()
    try:
        if a.cmd_ == "huella":
            print(json.dumps(huella(repo), indent=2))
            return 0
        if a.cmd_ == "base":
            b = base(repo, a.cmd, a.timeout)
            print(f"Base: {b['estado']} en {b['segundos']} s; escenarios en JUnit: {b['escenarios_ejecutados']}")
            ok = b["estado"] == "pasa" and b["escenarios_ejecutados"] > 0
            if not ok:
                print(b["salida"])
            return 0 if ok else 2
        resumen = ejecutar(repo, a.cmd, a.parches, a.timeout, prohibidas=a.prohibidas, limpieza=a.limpieza)
    except ErrorDeMutacion as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if a.salida:
        a.salida.parent.mkdir(parents=True, exist_ok=True)
        a.salida.write_text(json.dumps(resumen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(_tabla(resumen))
    return 0 if all(m["resultado"] == "detectado" for m in resumen["mutantes"]) else 1


if __name__ == "__main__":
    sys.exit(main())
