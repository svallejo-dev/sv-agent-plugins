#!/usr/bin/env python3
"""Trazabilidad criterio → escenario → test ejecutable → resultado.

Lee criterios.md y escenarios.md (formato de referencias/formatos.md), y opcionalmente
las fuentes de los tests y los reportes JUnit de UNA ejecución. Reporta cada hueco de la
cadena. Es la defensa determinista contra: el criterio que nadie prueba, el test que
"pasa" porque no se ejecutó, el reporte viejo o ajeno y el test que dice cubrir varios
escenarios a la vez.

Uso:
  trazabilidad.py --criterios criterios.md --escenarios escenarios.md
                  [--fuentes DIR ...] [--junit REPORTE.xml ...] [--desde EPOCH]
                  [--peldanos 1,2] [--ids ESC-01,ESC-04] [--esperar-rojo] [--json]

Reglas estrictas:
  - Un escenario saltado (skipped) o no ejecutado NO cuenta como verde.
  - Un caso JUnit con más de un ID de escenario es un hueco: un test, un escenario.
  - Con --junit, cada criterio en alcance necesita al menos un escenario verde ejecutado
    en esta corrida; si sus escenarios están todos fuera de los peldaños pedidos, es un
    hueco ("sin evidencia en el alcance"), nunca un verde.
  - Un alcance vacío es un error.
  - Con --desde, un reporte modificado antes de esa marca de tiempo es un error.
  - --esperar-rojo (antes de implementar): un escenario rojo es lo esperado y un verde se
    reporta para investigar; lo no implementado o no ejecutado sigue siendo hueco.

Códigos de salida: 0 cadena completa (y en verde), 1 huecos o fallos, 2 error de formato.
Solo usa la biblioteca estándar.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

ID_AC = r"AC-\d{2,}"
ID_ESC = r"ESC-\d{2,}"
RE_AC = re.compile(rf"(?<![A-Za-z0-9]){ID_AC}(?!\d)")
RE_ESC = re.compile(rf"(?<![A-Za-z0-9]){ID_ESC}(?!\d)")
RE_ESC_CUALQUIERA = re.compile(r"(?<![A-Za-z0-9])ESC-\d+(?!\d)")
RE_AC_CUALQUIERA = re.compile(r"(?<![A-Za-z0-9])AC-\d+(?!\d)")
RE_AC_ENCABEZADO = re.compile(r"^#{2,3}\s+(AC-\d+)\b(.*)$")
RE_TITULO = re.compile(
    r"(Escenario|Esquema del escenario|Ejemplo|Scenario Outline|Scenario|Example)\s*:"
    r"|\b(test|it|describe)\s*(\.\w+)?\s*\("
    r"|\bt\.Run\s*\(", re.IGNORECASE)
ESTADOS_VALIDOS = {"activo", "bloqueado-testabilidad", "descartado"}
EXT_FUENTES = {".feature", ".hurl", ".go", ".ts", ".js", ".mjs", ".py", ".java", ".kt", ".http", ".robot"}


class ErrorDeFormato(Exception):
    pass


@dataclass
class Escenario:
    id: str
    criterios: list[str]
    peldanos: list[int]
    estado: str
    archivos: list[str] = field(default_factory=list)
    resultados: list[str] = field(default_factory=list)  # passed | failed | skipped

    @property
    def resultado(self) -> str:
        if not self.resultados:
            return "no-ejecutado"
        if "failed" in self.resultados:
            return "rojo"
        if "skipped" in self.resultados:
            return "saltado"
        return "verde"


def _sin_bloques_de_codigo(texto: str) -> list[str]:
    lineas, dentro = [], False
    for linea in texto.splitlines():
        if linea.strip().startswith(("```", "~~~")):
            dentro = not dentro
            lineas.append("")
            continue
        lineas.append("" if dentro else linea)
    return lineas


def leer_criterios(texto: str) -> tuple[list[str], list[str]]:
    """(criterios vigentes, criterios descartados)."""
    vigentes, descartados, actual = [], [], None
    vistos: list[str] = []
    for n, linea in enumerate(_sin_bloques_de_codigo(texto), 1):
        m = RE_AC_ENCABEZADO.match(linea)
        if m:
            ident = m.group(1)
            if not re.fullmatch(ID_AC, ident):
                raise ErrorDeFormato(f"línea {n}: ID de criterio inválido '{ident}' (se espera AC-NN, dos dígitos mínimo)")
            if ident in vistos:
                raise ErrorDeFormato(f"criterio duplicado: {ident}")
            vistos.append(ident)
            actual = ident
            vigentes.append(ident)
            continue
        if linea.startswith("#"):
            actual = None
        if actual and re.match(r"^\s*-\s*Estado\s*:\s*descartado\b", linea, re.IGNORECASE):
            vigentes.remove(actual)
            descartados.append(actual)
            actual = None
    if not vistos:
        raise ErrorDeFormato("no se encontró ningún criterio con encabezado '## AC-NN:'")
    return vigentes, descartados


def _celdas(linea: str) -> list[str]:
    s = linea.strip()
    s = s[1:] if s.startswith("|") else s
    s = s[:-1] if s.endswith("|") and not s.endswith("\\|") else s
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", s)]


def _normal(c: str) -> str:
    return c.lower().replace("ñ", "n").strip()


def _peldanos(texto: str, n: int, ident: str) -> list[int]:
    partes = [p.strip() for p in re.split(r"[,\s]+", texto) if p.strip()]
    if not partes or not all(p.isdigit() and 1 <= int(p) <= 5 for p in partes):
        raise ErrorDeFormato(f"línea {n}: {ident} tiene un peldaño inválido '{texto}' (1 a 5, varios separados por coma)")
    return sorted({int(p) for p in partes})


def leer_escenarios(texto: str) -> list[Escenario]:
    escenarios: list[Escenario] = []
    columnas: dict[str, int] | None = None
    for n, linea in enumerate(_sin_bloques_de_codigo(texto), 1):
        if not linea.strip().startswith("|"):
            columnas = None
            continue
        celdas = _celdas(linea)
        normal = [_normal(c) for c in celdas]
        if "id" in normal:
            alias = {"criterios": "criterio", "peldanos": "peldano"}
            normal = [alias.get(c, c) for c in normal]
            requeridas = {"id", "criterio", "peldano", "estado"}
            faltan = requeridas - set(normal)
            if faltan:
                raise ErrorDeFormato(f"línea {n}: a la tabla le faltan columnas: {', '.join(sorted(faltan))}")
            columnas = {nombre: normal.index(nombre) for nombre in requeridas}
            continue
        if columnas is None or set(linea.replace("|", "").strip()) <= set("-: "):
            continue
        if len(celdas) <= max(columnas.values()):
            raise ErrorDeFormato(f"línea {n}: fila con menos columnas que el encabezado")
        ident = celdas[columnas["id"]]
        if not re.fullmatch(ID_ESC, ident):
            raise ErrorDeFormato(f"línea {n}: ID de escenario inválido '{ident}' (se espera ESC-NN, dos dígitos mínimo)")
        celda_crit = celdas[columnas["criterio"]]
        criterios = RE_AC_CUALQUIERA.findall(celda_crit)
        malos = [c for c in criterios if not re.fullmatch(ID_AC, c)]
        if malos or not criterios:
            raise ErrorDeFormato(f"línea {n}: {ident} debe referenciar criterios AC-NN válidos (encontrado: '{celda_crit}')")
        estado = celdas[columnas["estado"]].lower()
        if estado not in ESTADOS_VALIDOS:
            raise ErrorDeFormato(f"línea {n}: {ident} tiene un estado inválido '{estado}'")
        escenarios.append(Escenario(ident, criterios, _peldanos(celdas[columnas["peldano"]], n, ident), estado))
    ids = [e.id for e in escenarios]
    duplicados = sorted({i for i in ids if ids.count(i) > 1})
    if duplicados:
        raise ErrorDeFormato(f"escenarios duplicados: {', '.join(duplicados)}")
    if not escenarios:
        raise ErrorDeFormato("no se encontró ninguna tabla de escenarios con columnas ID, Criterio, Peldaño y Estado")
    return escenarios


def escanear_fuentes(dirs: list[Path]) -> dict[str, list[str]]:
    """{ESC-NN: [archivos]} buscando el ID en el nombre del archivo o en líneas de título de test."""
    menciones: dict[str, set[str]] = {}
    for d in dirs:
        if not d.exists():
            raise ErrorDeFormato(f"no existe el directorio de fuentes {d}")
        archivos = [d] if d.is_file() else sorted(p for p in d.rglob("*") if p.is_file())
        for p in archivos:
            if p.suffix.lower() not in EXT_FUENTES:
                continue
            ids = set(RE_ESC_CUALQUIERA.findall(p.name))
            try:
                for linea in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                    if RE_TITULO.search(linea):
                        ids |= set(RE_ESC_CUALQUIERA.findall(linea))
            except OSError:
                continue
            for i in ids:
                menciones.setdefault(i, set()).add(p.as_posix())
    return {k: sorted(v) for k, v in menciones.items()}


def leer_junit(rutas: list[Path], desde: float | None = None) -> tuple[dict[str, list[str]], list[str], list[str]]:
    """({ESC-NN: [resultados]}, [casos sin ID], [casos con varios IDs])."""
    if not rutas:
        raise ErrorDeFormato("no se indicó ningún reporte JUnit (¿la ejecución no produjo reportes?)")
    resultados: dict[str, list[str]] = {}
    sin_id: list[str] = []
    multiples: list[str] = []
    for ruta in rutas:
        if desde is not None and ruta.stat().st_mtime < desde:
            raise ErrorDeFormato(f"el reporte {ruta} es anterior al inicio de la ejecución: no se acepta")
        try:
            arbol = ET.parse(ruta)
        except (ET.ParseError, OSError) as e:
            raise ErrorDeFormato(f"no se pudo leer el JUnit {ruta}: {e}") from e
        for caso in arbol.iter("testcase"):
            nombre = " ".join(filter(None, (caso.get("classname"), caso.get("name"), caso.get("file"))))
            if caso.find("failure") is not None or caso.find("error") is not None:
                res = "failed"
            elif caso.find("skipped") is not None:
                res = "skipped"
            else:
                res = "passed"
            ids = sorted(set(RE_ESC_CUALQUIERA.findall(nombre)))
            if not ids:
                sin_id.append(nombre)
            elif len(ids) > 1:
                multiples.append(nombre)
            else:
                resultados.setdefault(ids[0], []).append(res)
    return resultados, sin_id, multiples


def analizar(criterios: list[str], escenarios: list[Escenario], peldanos: set[int] | None,
             fuentes: dict[str, list[str]] | None,
             junit: tuple[dict[str, list[str]], list[str], list[str]] | None,
             ids: set[str] | None = None, esperar_rojo: bool = False,
             descartados: list[str] | None = None) -> dict:
    declarados = {e.id for e in escenarios}
    huecos: list[str] = []
    avisos: list[str] = []
    descartados = descartados or []

    if ids:
        desconocidos = sorted(ids - declarados)
        if desconocidos:
            raise ErrorDeFormato(f"--ids incluye escenarios no declarados: {', '.join(desconocidos)}")

    for e in escenarios:
        for c in e.criterios:
            if c in descartados and e.estado != "descartado":
                huecos.append(f"{e.id} está activo pero referencia {c}, que está descartado")
            elif c not in criterios and c not in descartados:
                huecos.append(f"{e.id} referencia {c}, que no existe en criterios.md")

    vivos = [e for e in escenarios if e.estado != "descartado"]

    def en_filtro(e: Escenario) -> bool:
        return (peldanos is None or bool(set(e.peldanos) & peldanos)) and (ids is None or e.id in ids)

    en_alcance = [e for e in vivos if e.estado == "activo" and en_filtro(e)]
    if not en_alcance:
        raise ErrorDeFormato("el alcance está vacío: ningún escenario activo cumple los filtros (peldaños o IDs)")

    considerados = criterios if ids is None else sorted({c for e in en_alcance for c in e.criterios if c in criterios})

    for c in considerados:
        suyos = [e for e in vivos if c in e.criterios]
        if not suyos:
            huecos.append(f"{c} no tiene ningún escenario")
        elif all(e.estado == "bloqueado-testabilidad" for e in suyos):
            huecos.append(f"{c} solo tiene escenarios bloqueados por testabilidad: sin cobertura ejecutable")

    for e in vivos:
        if e.estado == "bloqueado-testabilidad":
            avisos.append(f"{e.id} bloqueado por testabilidad (deuda abierta)")

    if fuentes is not None:
        for e in en_alcance:
            e.archivos = fuentes.get(e.id, [])
            if not e.archivos:
                huecos.append(f"{e.id} no está implementado en las fuentes (el ID debe ir en el título del test o en el nombre del archivo)")
        for i in sorted(set(fuentes) - declarados):
            huecos.append(f"{i} aparece en {', '.join(fuentes[i])} pero no está declarado en escenarios.md")

    if junit is not None:
        resultados, sin_id, multiples = junit
        for e in en_alcance:
            e.resultados = resultados.get(e.id, [])
            r = e.resultado
            if r == "no-ejecutado":
                huecos.append(f"{e.id} no aparece en ningún reporte JUnit: no ejecutado")
            elif r == "saltado":
                huecos.append(f"{e.id} fue saltado (skipped): no cuenta como verde")
            elif r == "rojo" and not esperar_rojo:
                huecos.append(f"{e.id} falló")
            elif r == "verde" and esperar_rojo:
                avisos.append(f"{e.id} está en VERDE antes de implementar: o el comportamiento ya existía o el test es vacuo; investígalo")
        for i in sorted(set(resultados) - declarados):
            huecos.append(f"{i} se ejecutó pero no está declarado en escenarios.md")
        for nombre in multiples:
            huecos.append(f"caso JUnit con varios IDs de escenario (un test, un escenario): {nombre}")
        for nombre in sin_id:
            avisos.append(f"caso sin ID de escenario en el JUnit: {nombre}")
        if not esperar_rojo:
            for c in considerados:
                suyos = [e for e in vivos if c in e.criterios and e.estado == "activo"]
                if suyos and not any(e in en_alcance for e in suyos):
                    fuera = ", ".join(f"{e.id}(p{'/'.join(map(str, e.peldanos))})" for e in suyos)
                    huecos.append(f"{c} sin evidencia en el alcance: sus escenarios están en otros peldaños ({fuera})")

    cobertura = []
    for c in considerados:
        estados = []
        for e in (x for x in vivos if c in x.criterios):
            if e.estado == "bloqueado-testabilidad":
                estados.append(f"{e.id}:bloqueado")
            elif e not in en_alcance:
                estados.append(f"{e.id}:fuera-de-alcance(p{'/'.join(map(str, e.peldanos))})")
            elif junit is not None:
                estados.append(f"{e.id}:{e.resultado}")
            elif fuentes is not None:
                estados.append(f"{e.id}:{'implementado' if e.archivos else 'sin-implementar'}")
            else:
                estados.append(f"{e.id}:declarado")
        cobertura.append({"criterio": c, "escenarios": estados})

    return {"completo": not huecos, "huecos": huecos, "avisos": avisos, "cobertura": cobertura,
            "en_alcance": len(en_alcance), "declarados": len(vivos), "esperar_rojo": esperar_rojo}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Trazabilidad criterio → escenario → test → resultado")
    ap.add_argument("--criterios", required=True, type=Path)
    ap.add_argument("--escenarios", required=True, type=Path)
    ap.add_argument("--fuentes", nargs="*", type=Path)
    ap.add_argument("--junit", nargs="*", type=Path)
    ap.add_argument("--desde", type=float, help="epoch del inicio de la ejecución; rechaza reportes anteriores")
    ap.add_argument("--peldanos", help="peldaños en alcance, por ejemplo 1,2")
    ap.add_argument("--ids", help="escenarios en alcance, por ejemplo ESC-01,ESC-04 (ritmo por rebanada)")
    ap.add_argument("--esperar-rojo", action="store_true", help="antes de implementar: el rojo es lo esperado")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        criterios, descartados = leer_criterios(a.criterios.read_text(encoding="utf-8"))
        escenarios = leer_escenarios(a.escenarios.read_text(encoding="utf-8"))
        peldanos = ids = None
        if a.peldanos:
            try:
                peldanos = {int(x) for x in a.peldanos.split(",") if x.strip()}
            except ValueError as e:
                raise ErrorDeFormato(f"--peldanos inválido: {a.peldanos}") from e
        if a.ids:
            ids = {x.strip() for x in a.ids.split(",") if x.strip()}
        fuentes = escanear_fuentes(a.fuentes) if a.fuentes else None
        junit = leer_junit(a.junit, a.desde) if a.junit is not None else None
        r = analizar(criterios, escenarios, peldanos, fuentes, junit, ids, a.esperar_rojo, descartados)
    except (ErrorDeFormato, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        alcance = ", ".join(filter(None, [f"peldaños {a.peldanos}" if a.peldanos else "",
                                           f"escenarios {a.ids}" if a.ids else ""])) or "todo"
        print(f"Trazabilidad (alcance: {alcance}): {r['en_alcance']} escenarios activos en alcance de {r['declarados']} vigentes.")
        for c in r["cobertura"]:
            print(f"  {c['criterio']}: {', '.join(c['escenarios']) or '—'}")
        if r["huecos"]:
            print(f"\nHUECOS ({len(r['huecos'])}):")
            for h in r["huecos"]:
                print(f"  - {h}")
        if r["avisos"]:
            print(f"\nAvisos ({len(r['avisos'])}):")
            for av in r["avisos"]:
                print(f"  - {av}")
        if r["completo"]:
            print("\nCadena completa." + (" Rojo esperado antes de implementar." if a.esperar_rojo else ""))
        else:
            print("\nCadena con huecos.")
    return 0 if r["completo"] else 1


if __name__ == "__main__":
    sys.exit(main())
