"""Tests de los scripts del plugin qa. Ejecutar: python3 -m unittest discover -s scripts/tests"""

from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import mutantes  # noqa: E402
import sello  # noqa: E402
import trazabilidad  # noqa: E402


def _silencio(fn, *args):
    with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()) as err:
        codigo = fn(*args)
    return codigo, out.getvalue(), err.getvalue()


def _git_init(d: Path) -> None:
    subprocess.run(["git", "init", "-q", "-b", "main", str(d)], check=True)
    for k, v in (("user.email", "t@t"), ("user.name", "t"), ("commit.gpgsign", "false")):
        subprocess.run(["git", "-C", str(d), "config", k, v], check=True)


def _commit(d: Path, msg: str = "c") -> None:
    subprocess.run(["git", "-C", str(d), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(d), "commit", "-qm", msg], check=True)


# ---------------------------------------------------------------- sello

class TestSello(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self.tmp.name)
        (self.raiz / "acceptance/feat").mkdir(parents=True)
        (self.raiz / "acceptance/feat/ESC-01-alta.hurl").write_text("GET {{base_url}}/x\nHTTP 200\n")
        (self.raiz / "acceptance/feat/limites.feature").write_text("Escenario: ESC-02 límite\n")
        (self.raiz / "docs/agentes").mkdir(parents=True)
        (self.raiz / "docs/agentes/qa.md").write_text("comando: make p1\n")
        self.sello = self.raiz / "acceptance/feat/.qa-sello.json"

    def tearDown(self):
        self.tmp.cleanup()

    def _sellar(self):
        return sello.sellar(self.sello, self.raiz, ["acceptance/feat", "docs/agentes/qa.md"], "diseño aprobado", "qa")

    def test_sellar_y_verificar_integro(self):
        datos = self._sellar()
        self.assertTrue(sello.verificar(self.sello, self.raiz)["integro"])
        self.assertEqual(len(datos["archivos"]), 3)
        self.assertNotIn("acceptance/feat/.qa-sello.json", datos["archivos"], "el sello no se sella a sí mismo")

    def test_detecta_modificacion_eliminacion_y_nuevo(self):
        self._sellar()
        (self.raiz / "acceptance/feat/ESC-01-alta.hurl").write_text("GET {{base_url}}/x\nHTTP 404\n")
        (self.raiz / "acceptance/feat/limites.feature").unlink()
        (self.raiz / "acceptance/feat/ESC-09-nuevo.hurl").write_text("x")
        inf = sello.verificar(self.sello, self.raiz)
        self.assertFalse(inf["integro"])
        self.assertEqual(inf["modificados"], ["acceptance/feat/ESC-01-alta.hurl"])
        self.assertEqual(inf["eliminados"], ["acceptance/feat/limites.feature"])
        self.assertEqual(inf["nuevos"], ["acceptance/feat/ESC-09-nuevo.hurl"])

    def test_cambiar_el_comando_de_la_configuracion_rompe_el_sello(self):
        self._sellar()
        (self.raiz / "docs/agentes/qa.md").write_text("comando: make p1 TAGS=~@lento\n")
        self.assertEqual(sello.verificar(self.sello, self.raiz)["modificados"], ["docs/agentes/qa.md"])

    def test_node_modules_y_pycache_no_se_ignoran(self):
        self._sellar()
        (self.raiz / "acceptance/feat/node_modules/@playwright/test").mkdir(parents=True)
        (self.raiz / "acceptance/feat/node_modules/@playwright/test/index.js").write_text("trampa")
        self.assertFalse(sello.verificar(self.sello, self.raiz)["integro"])

    def test_enlace_simbolico_rompe_el_sello(self):
        self._sellar()
        fuera = self.raiz / "fuera"
        fuera.mkdir()
        (fuera / "pasos.go").write_text("x")
        os.symlink(fuera, self.raiz / "acceptance/feat/steps")
        inf = sello.verificar(self.sello, self.raiz)
        self.assertFalse(inf["integro"])
        self.assertEqual(inf["enlaces"], ["acceptance/feat/steps"])
        with self.assertRaises(sello.ErrorDeUso):
            sello.resellar(self.sello, self.raiz, [], "H-01: x", "qa")

    def test_requiere_rutas_selladas(self):
        sello.sellar(self.sello, self.raiz, ["acceptance/feat"], "diseño", "qa")
        inf = sello.verificar(self.sello, self.raiz, requeridas=["docs/agentes/qa.md", "acceptance/feat/limites.feature"])
        self.assertEqual(inf["requeridas_sin_sellar"], ["docs/agentes/qa.md"])
        self.assertFalse(inf["integro"])

    def test_no_permite_sellar_dos_veces_ni_sin_motivo(self):
        with self.assertRaises(sello.ErrorDeUso):
            sello.sellar(self.sello, self.raiz, ["acceptance/feat"], "  ", "qa")
        self._sellar()
        with self.assertRaises(sello.ErrorDeUso):
            sello.sellar(self.sello, self.raiz, ["acceptance/feat"], "otra vez", "qa")

    def test_resellar_exige_motivo_y_deja_historial(self):
        self._sellar()
        (self.raiz / "acceptance/feat/ESC-01-alta.hurl").write_text("cambio")
        with self.assertRaises(sello.ErrorDeUso):
            sello.resellar(self.sello, self.raiz, [], "", "qa")
        datos, cambios = sello.resellar(self.sello, self.raiz, [], "E-02: test corregido", "qa")
        self.assertEqual(cambios["modificados"], ["acceptance/feat/ESC-01-alta.hurl"])
        self.assertEqual([e["accion"] for e in datos["historial"]], ["sellar", "resellar"])
        self.assertTrue(sello.verificar(self.sello, self.raiz)["integro"])

    def test_ruta_fuera_de_la_raiz_es_error(self):
        with self.assertRaises(sello.ErrorDeUso):
            sello.sellar(self.sello, self.raiz, ["../"], "x", "qa")

    def test_cli_codigos_de_salida(self):
        base = ["--sello", str(self.sello), "--raiz", str(self.raiz)]
        self.assertEqual(_silencio(sello.main, ["verificar", *base])[0], 2, "sin sello es error de uso")
        self.assertEqual(_silencio(sello.main, ["sellar", *base, "--motivo", "inicial", "acceptance/feat"])[0], 0)
        self.assertEqual(_silencio(sello.main, ["verificar", *base])[0], 0)
        (self.raiz / "acceptance/feat/limites.feature").write_text("editado por el dev")
        codigo, salida, _ = _silencio(sello.main, ["verificar", *base])
        self.assertEqual(codigo, 1)
        self.assertIn("SELLO ROTO", salida)


class TestSelloContraBase(unittest.TestCase):
    """El agente que edita y vuelve a sellar no pasa desapercibido."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.raiz = Path(self.tmp.name)
        _git_init(self.raiz)
        (self.raiz / "acceptance/feat").mkdir(parents=True)
        (self.raiz / "acceptance/feat/ESC-01.hurl").write_text("HTTP 409\n")
        self.sello = self.raiz / "acceptance/feat/.qa-sello.json"
        sello.sellar(self.sello, self.raiz, ["acceptance/feat"], "diseño aprobado", "qa")
        _commit(self.raiz, "base")
        subprocess.run(["git", "-C", str(self.raiz), "checkout", "-qb", "feature"], check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_resellado_sin_referencia_rompe_contra_la_base(self):
        (self.raiz / "acceptance/feat/ESC-01.hurl").write_text("HTTP 422\n")
        sello.resellar(self.sello, self.raiz, [], "ajuste", "dev")
        self.assertTrue(sello.verificar(self.sello, self.raiz)["integro"], "sin base, el re-sellado pasa…")
        inf = sello.verificar(self.sello, self.raiz, base="main")
        self.assertFalse(inf["integro"], "…pero contra la base queda a la vista")
        self.assertEqual(len(inf["resellados_desde_base"]), 1)

    def test_resellado_con_referencia_se_lista_para_revision(self):
        (self.raiz / "acceptance/feat/ESC-01.hurl").write_text("HTTP 422\n")
        sello.resellar(self.sello, self.raiz, [], "E-03: el criterio cambió", "qa")
        inf = sello.verificar(self.sello, self.raiz, base="main")
        self.assertTrue(inf["integro"])
        self.assertEqual(inf["resellados_desde_base"][0]["motivo"], "E-03: el criterio cambió")

    def test_borrar_y_recrear_el_sello_se_detecta(self):
        self.sello.unlink()
        (self.raiz / "acceptance/feat/ESC-01.hurl").write_text("HTTP 422\n")
        sello.sellar(self.sello, self.raiz, ["acceptance/feat"], "nuevo", "dev")
        inf = sello.verificar(self.sello, self.raiz, base="main")
        self.assertFalse(inf["integro"])
        self.assertIn("historial del sello fue reescrito", " ".join(inf["problemas_base"]))

    def test_borrar_el_sello_se_detecta(self):
        self.sello.unlink()
        inf = sello.verificar(self.sello, self.raiz, base="main")
        self.assertFalse(inf["integro"])

    def test_feature_nueva_sin_sello_en_base(self):
        otro = self.raiz / "acceptance/nueva/.qa-sello.json"
        (self.raiz / "acceptance/nueva").mkdir()
        (self.raiz / "acceptance/nueva/ESC-01.hurl").write_text("x")
        sello.sellar(otro, self.raiz, ["acceptance/nueva"], "diseño", "qa")
        inf = sello.verificar(otro, self.raiz, base="main")
        self.assertTrue(inf["integro"])
        self.assertEqual(len(inf["resellados_desde_base"]), 1, "se lista todo para revisión humana")

    def test_base_inexistente_es_error(self):
        with self.assertRaises(sello.ErrorDeUso):
            sello.verificar(self.sello, self.raiz, base="no-existe")


# ---------------------------------------------------------------- trazabilidad

CRITERIOS = textwrap.dedent("""\
    # Criterios
    Estado: aprobado

    ## AC-01: registrar dispositivo
    - Oráculo: listado

    ## AC-02: límite de dispositivos
    - Oráculo: 409

    ### AC-03: token sirve al SDK
    - Oráculo: SDK inicializado

    ## AC-04: idea vieja
    - Estado: descartado

    ```markdown
    ## AC-99: ejemplo dentro de un bloque de código, no cuenta
    ```
    """)

ESCENARIOS = textwrap.dedent("""\
    # Escenarios

    | ID | Criterio | Técnica | Peldaño | Escenario | Oráculo | Estado |
    |---|---|---|---|---|---|---|
    | ESC-01 | AC-01 | particiones | 1 | alta | listado | activo |
    | ESC-02 | AC-02 | límites | 1, 4 | quinto | 409 \\| listado | activo |
    | ESC-03 | AC-02, AC-01 | límites | 1 | cuarto | 201 | activo |
    | ESC-04 | AC-03 | walking skeleton | 3 | sdk | sdk ok | activo |
    | ESC-05 | AC-02 | fallo | 1 | timeout | 503 | bloqueado-testabilidad |
    | ESC-06 | AC-01 | x | 1 | viejo | x | descartado |
    | ESC-07 | AC-04 | x | 1 | podado por riesgo | x | descartado |

    ### ESC-02
    Detalle con un ESC-99 mencionado en prosa, que no debe parsearse como fila.
    """)


def _junit(casos: list[tuple[str, str]]) -> str:
    partes = ['<?xml version="1.0"?><testsuites><testsuite name="s">']
    for nombre, res in casos:
        hijo = {"failed": "<failure message='x'/>", "skipped": "<skipped/>", "error": "<error/>"}.get(res, "")
        partes.append(f'<testcase classname="acceptance" name="{nombre}">{hijo}</testcase>')
    partes.append("</testsuite></testsuites>")
    return "".join(partes)


VERDES_P1 = [("ESC-01 alta", "passed"), ("ESC-02 quinto #1", "passed"),
             ("ESC-02 quinto #2", "passed"), ("ESC-03 cuarto", "passed")]


class TestTrazabilidad(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        (self.d / "criterios.md").write_text(CRITERIOS)
        (self.d / "escenarios.md").write_text(ESCENARIOS)
        self.src = self.d / "acceptance"
        self.src.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, *extra):
        return _silencio(trazabilidad.main, ["--criterios", str(self.d / "criterios.md"),
                                             "--escenarios", str(self.d / "escenarios.md"), "--json", *extra])

    def _rep(self, casos, nombre="r.xml"):
        rep = self.d / nombre
        rep.write_text(_junit(casos))
        return rep

    def test_parseo_basico(self):
        self.assertEqual(trazabilidad.leer_criterios(CRITERIOS), (["AC-01", "AC-02", "AC-03"], ["AC-04"]))
        esc = trazabilidad.leer_escenarios(ESCENARIOS)
        self.assertEqual([e.id for e in esc], [f"ESC-0{i}" for i in range(1, 8)])
        self.assertEqual(esc[1].peldanos, [1, 4])
        self.assertEqual(esc[2].criterios, ["AC-02", "AC-01"])

    def test_solo_declaracion_completa(self):
        codigo, salida, _ = self._run()
        self.assertEqual(codigo, 0, salida)
        self.assertTrue(any("ESC-05" in a for a in json.loads(salida)["avisos"]))

    def test_criterio_sin_escenario_y_referencia_inexistente(self):
        (self.d / "criterios.md").write_text(CRITERIOS + "\n## AC-05: nuevo\n")
        (self.d / "escenarios.md").write_text(ESCENARIOS.replace("| ESC-01 | AC-01 |", "| ESC-01 | AC-01, AC-09 |"))
        codigo, salida, _ = self._run()
        huecos = json.loads(salida)["huecos"]
        self.assertEqual(codigo, 1)
        self.assertIn("AC-05 no tiene ningún escenario", huecos)
        self.assertTrue(any("AC-09" in h for h in huecos))

    def test_escenario_activo_sobre_criterio_descartado(self):
        (self.d / "escenarios.md").write_text(ESCENARIOS.replace("| x | 1 | podado por riesgo | x | descartado |",
                                                                 "| x | 1 | podado por riesgo | x | activo |"))
        codigo, salida, _ = self._run()
        self.assertEqual(codigo, 1)
        self.assertTrue(any("AC-04, que está descartado" in h for h in json.loads(salida)["huecos"]))

    def test_criterio_solo_bloqueado_no_tiene_cobertura(self):
        esc = ESCENARIOS.replace("| 3 | sdk | sdk ok | activo |", "| 3 | sdk | sdk ok | bloqueado-testabilidad |")
        (self.d / "escenarios.md").write_text(esc)
        codigo, salida, _ = self._run()
        self.assertEqual(codigo, 1)
        self.assertTrue(any("AC-03 solo tiene escenarios bloqueados" in h for h in json.loads(salida)["huecos"]))

    def test_fuentes_solo_cuentan_titulos_y_nombres(self):
        (self.src / "ESC-01-alta.hurl").write_text("x")
        (self.src / "limites.feature").write_text(
            "Escenario: ESC-02 quinto\nEscenario: ESC-77 inventado\n# este paso también cubre ESC-03\n")
        (self.src / "helper.go").write_text("// cubre ESC-03\nfunc x() {}\n")
        (self.src / "mapping.json").write_text('{"ESC-03": true}')
        codigo, salida, _ = self._run("--fuentes", str(self.src), "--peldanos", "1")
        huecos = json.loads(salida)["huecos"]
        self.assertEqual(codigo, 1)
        self.assertTrue(any(h.startswith("ESC-03") and "no está implementado" in h for h in huecos),
                        "un comentario o un JSON no implementan un escenario")
        self.assertTrue(any(h.startswith("ESC-77") for h in huecos))
        self.assertFalse(any(h.startswith("ESC-04") for h in huecos), "ESC-04 es peldaño 3, fuera del alcance")

    def test_fuentes_go_y_playwright(self):
        (self.src / "a_test.go").write_text('t.Run("ESC-01 alta", func(t *testing.T) {})\n')
        (self.src / "b.spec.ts").write_text("test('ESC-02 quinto', async () => {})\ntest.describe('ESC-03 cuarto', () => {})\n")
        self.assertEqual(set(trazabilidad.escanear_fuentes([self.src])), {"ESC-01", "ESC-02", "ESC-03"})

    def test_junit_verde_completo_en_peldano_1(self):
        (self.d / "escenarios.md").write_text(ESCENARIOS.replace("| ESC-04 | AC-03 | walking skeleton | 3 |",
                                                                 "| ESC-04 | AC-03 | walking skeleton | 1, 3 |"))
        rep = self._rep(VERDES_P1 + [("ESC-04 sdk", "passed")])
        codigo, salida, _ = self._run("--junit", str(rep), "--peldanos", "1")
        self.assertEqual(codigo, 0, salida)

    def test_criterio_cuyos_escenarios_estan_en_otro_peldano_no_es_verde(self):
        """El caso PayPal: si el peldaño 3 no corre, el walking skeleton no puede salir en verde."""
        rep = self._rep(VERDES_P1)
        codigo, salida, _ = self._run("--junit", str(rep), "--peldanos", "1")
        self.assertEqual(codigo, 1)
        self.assertTrue(any(h.startswith("AC-03 sin evidencia en el alcance") for h in json.loads(salida)["huecos"]))

    def test_alcance_vacio_es_error(self):
        rep = self._rep(VERDES_P1)
        self.assertEqual(self._run("--junit", str(rep), "--peldanos", "5")[0], 2)
        self.assertEqual(self._run("--junit")[0], 2, "--junit sin reportes es error")

    def test_junit_skipped_fallido_y_no_ejecutado_no_son_verdes(self):
        rep = self._rep([("ESC-01 alta", "skipped"), ("ESC-02 quinto #1", "passed"),
                         ("ESC-02 quinto #2", "failed"), ("TestSinID", "passed")])
        codigo, salida, _ = self._run("--junit", str(rep), "--peldanos", "1")
        r = json.loads(salida)
        self.assertEqual(codigo, 1)
        self.assertTrue(any("ESC-01 fue saltado" in h for h in r["huecos"]))
        self.assertTrue(any("ESC-02 falló" in h for h in r["huecos"]), "una sola fila roja del esquema basta")
        self.assertTrue(any("ESC-03 no aparece" in h for h in r["huecos"]))
        self.assertTrue(any("TestSinID" in a for a in r["avisos"]))

    def test_un_caso_no_puede_cubrir_varios_escenarios(self):
        rep = self._rep([("smoke ESC-01 ESC-02 ESC-03", "passed")])
        codigo, salida, _ = self._run("--junit", str(rep), "--ids", "ESC-01,ESC-02,ESC-03")
        r = json.loads(salida)
        self.assertEqual(codigo, 1)
        self.assertTrue(any("varios IDs" in h for h in r["huecos"]))
        self.assertTrue(any("ESC-01 no aparece" in h for h in r["huecos"]))

    def test_nombres_de_go_con_guion_bajo(self):
        rep = self._rep([("TestAceptacion/ESC-01_alta", "passed"), ("TestAceptacion/ESC-02_quinto", "passed"),
                         ("TestAceptacion/ESC-03_cuarto", "passed")])
        resultados, sin_id, _ = trazabilidad.leer_junit([rep])
        self.assertEqual(set(resultados), {"ESC-01", "ESC-02", "ESC-03"})
        self.assertEqual(sin_id, [])

    def test_esc_01_no_se_confunde_con_esc_010(self):
        rep = self._rep([("ESC-010 algo", "passed")])
        resultados, _, _ = trazabilidad.leer_junit([rep])
        self.assertNotIn("ESC-01", resultados)

    def test_reporte_anterior_a_la_ejecucion_se_rechaza(self):
        rep = self._rep(VERDES_P1)
        viejo = time.time() - 3600
        os.utime(rep, (viejo, viejo))
        self.assertEqual(self._run("--junit", str(rep), "--peldanos", "1", "--desde", str(time.time() - 60))[0], 2)

    def test_ritmo_por_rebanada_con_ids(self):
        rep = self._rep([("ESC-02 quinto", "passed"), ("ESC-03 cuarto", "passed")])
        codigo, salida, _ = self._run("--junit", str(rep), "--ids", "ESC-02,ESC-03")
        self.assertEqual(codigo, 0, salida)
        crit = [c["criterio"] for c in json.loads(salida)["cobertura"]]
        self.assertEqual(crit, ["AC-01", "AC-02"], "solo los criterios de esos escenarios")
        self.assertEqual(self._run("--junit", str(rep), "--ids", "ESC-42")[0], 2)

    def test_esperar_rojo_antes_de_implementar(self):
        rep = self._rep([("ESC-01 alta", "failed"), ("ESC-02 quinto", "failed"), ("ESC-03 cuarto", "passed")])
        codigo, salida, _ = self._run("--junit", str(rep), "--peldanos", "1", "--esperar-rojo")
        r = json.loads(salida)
        self.assertEqual(codigo, 0, salida)
        self.assertTrue(any("ESC-03 está en VERDE antes de implementar" in a for a in r["avisos"]))
        rep2 = self._rep([("ESC-01 alta", "failed")], "r2.xml")
        self.assertEqual(self._run("--junit", str(rep2), "--peldanos", "1", "--esperar-rojo")[0], 1,
                         "lo no ejecutado sigue siendo hueco aunque se espere rojo")

    def test_formatos_invalidos_son_error(self):
        malos = [
            ESCENARIOS.replace("| ESC-01 | AC-01 | particiones | 1 |", "| ESC-1 | AC-01 | particiones | 1 |"),
            ESCENARIOS.replace("| ESC-01 | AC-01 | particiones | 1 |", "| ESC-01 | AC-1 | particiones | 1 |"),
            ESCENARIOS.replace("| ESC-01 | AC-01 | particiones | 1 |", "| ESC-01 | AC-01 | particiones | 9 |"),
            ESCENARIOS.replace("| activo |\n| ESC-02", "| verde |\n| ESC-02"),
            ESCENARIOS.replace("| ESC-03 | AC-02, AC-01 |", "| ESC-03 | ninguno |"),
            ESCENARIOS.replace("| ESC-03 |", "| ESC-02 |"),
            ESCENARIOS.replace("| Peldaño |", "| Nivel |"),
        ]
        for texto in malos:
            (self.d / "escenarios.md").write_text(texto)
            self.assertEqual(self._run()[0], 2, texto[:300])
        (self.d / "escenarios.md").write_text(ESCENARIOS)
        for crit in ("# nada", "## AC-1: corto\n"):
            (self.d / "criterios.md").write_text(crit)
            self.assertEqual(self._run()[0], 2, crit)

    def test_encabezados_en_plural(self):
        texto = ESCENARIOS.replace("| ID | Criterio | Técnica | Peldaño |", "| ID | Criterios | Técnica | Peldaños |")
        self.assertEqual(len(trazabilidad.leer_escenarios(texto)), 7)


# ---------------------------------------------------------------- mutantes

CHECK = textwrap.dedent("""\
    import os, sys
    from app import limite
    ok = limite(4) and not limite(5)
    rep = os.environ.get("QA_REPORTES")
    if rep:
        fallo = "" if ok else "<failure message='limite'/>"
        open(os.path.join(rep, "r.xml"), "w").write(
            f'<testsuite><testcase name="ESC-01 limite">{fallo}</testcase></testsuite>')
    sys.exit(0 if ok else 1)
    """)


def _repo(dir_: Path) -> Path:
    _git_init(dir_)
    (dir_ / "app.py").write_text("def limite(n):\n    return n < 5\n")
    (dir_ / "check.py").write_text(CHECK)
    (dir_ / "acceptance").mkdir()
    (dir_ / "acceptance/ESC-01.txt").write_text("oráculo")
    (dir_ / ".gitignore").write_text("ignorado.txt\n")
    _commit(dir_, "init")
    return dir_


def _parche(repo: Path, nuevo: str, archivo: str = "app.py") -> str:
    """Construye el parche como lo indica la skill: diff -u del archivo actual contra una copia editada."""
    with tempfile.TemporaryDirectory() as t:
        copia = Path(t) / Path(archivo).name
        copia.write_text(nuevo)
        r = subprocess.run(["diff", "-u", "--label", f"a/{archivo}", "--label", f"b/{archivo}",
                            str(repo / archivo), str(copia)], capture_output=True, text=True)
    assert r.returncode == 1, r.stderr
    return r.stdout


class TestMutantes(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = _repo(Path(self.tmp.name) / "repo")
        self.parches = Path(self.tmp.name) / "parches"
        self.parches.mkdir()
        self.cmd = f"{sys.executable} check.py"

    def tearDown(self):
        self.tmp.cleanup()

    def _estado(self):
        return subprocess.run(["git", "-C", str(self.repo), "status", "--porcelain"],
                              capture_output=True, text=True).stdout

    def _p(self, nombre, contenido):
        p = self.parches / nombre
        p.write_text(contenido)
        return p

    def test_resultados_sin_tocar_el_repo(self):
        self._p("M-01-limite.patch", _parche(self.repo, "def limite(n):\n    return n <= 5\n"))
        self._p("M-02-equivalente.patch", _parche(self.repo, "def limite(n):\n    return not n >= 5\n"))
        self._p("M-03-roto.patch", "diff --git a/nada.py b/nada.py\n--- a/nada.py\n+++ b/nada.py\n@@ -1 +1 @@\n-x\n+y\n")
        self._p("M-04-no-compila.patch", _parche(self.repo, "def limite(n):\n    return n <\n"))
        self._p("M-05-oraculo.patch", _parche(self.repo, "otro oráculo\n", "acceptance/ESC-01.txt"))
        antes, contenido = self._estado(), (self.repo / "app.py").read_text()
        r = mutantes.ejecutar(self.repo, self.cmd, sorted(self.parches.iterdir()), timeout=60,
                              prohibidas=["acceptance"])
        res = {m["parche"]: m["resultado"] for m in r["mutantes"]}
        self.assertEqual(res, {"M-01-limite.patch": "detectado", "M-02-equivalente.patch": "sobrevive",
                               "M-03-roto.patch": "no-aplica", "M-04-no-compila.patch": "error-harness",
                               "M-05-oraculo.patch": "rechazado"})
        detectado = next(m for m in r["mutantes"] if m["parche"] == "M-01-limite.patch")
        self.assertEqual(detectado["escenarios_rojos"], ["ESC-01"])
        self.assertEqual(self._estado(), antes)
        self.assertEqual((self.repo / "app.py").read_text(), contenido)
        wts = subprocess.run(["git", "-C", str(self.repo), "worktree", "list"], capture_output=True, text=True).stdout
        self.assertEqual(len(wts.strip().splitlines()), 1, "no deben quedar worktrees temporales")
        self.assertEqual(r["huella"], mutantes.huella(self.repo))

    def test_usa_cambios_sin_commitear_y_no_rastreados(self):
        (self.repo / "app.py").write_text("def limite(n):\n    return n < 5  # editado sin commit\n")
        (self.repo / "extra.py").write_text("VALOR = 1\n")
        (self.repo / "check.py").write_text("import extra\n" + CHECK)
        p = self._p("M-01.patch", _parche(self.repo, "def limite(n):\n    return n <= 5  # editado sin commit\n"))
        r = mutantes.ejecutar(self.repo, self.cmd, [p], timeout=60)
        self.assertEqual(r["base"]["estado"], "pasa")
        self.assertEqual(r["mutantes"][0]["resultado"], "detectado")

    def test_repositorio_anidado_no_rompe(self):
        _git_init(self.repo / "anidado")
        p = self._p("M-01.patch", _parche(self.repo, "def limite(n):\n    return n <= 5\n"))
        r = mutantes.ejecutar(self.repo, self.cmd, [p], timeout=60)
        self.assertEqual(r["mutantes"][0]["resultado"], "detectado")

    def test_huella_cambia_con_el_codigo(self):
        h1 = mutantes.huella(self.repo)
        (self.repo / "app.py").write_text("def limite(n):\n    return n < 6\n")
        self.assertNotEqual(h1["cambios"], mutantes.huella(self.repo)["cambios"])
        self.assertEqual(h1["head"], mutantes.huella(self.repo)["head"])

    def test_base_roja_o_sin_reportes_aborta(self):
        p = self._p("M-01.patch", "x")
        (self.repo / "app.py").write_text("def limite(n):\n    return True\n")
        with self.assertRaises(mutantes.ErrorDeMutacion):
            mutantes.ejecutar(self.repo, self.cmd, [p], timeout=60)
        (self.repo / "app.py").write_text("def limite(n):\n    return n < 5\n")
        with self.assertRaises(mutantes.ErrorDeMutacion):
            mutantes.ejecutar(self.repo, f"{sys.executable} -c 'pass'", [p], timeout=60)

    def test_timeout_mata_el_grupo_y_no_cuenta_como_detectado(self):
        marca = Path(self.tmp.name) / "huerfano.txt"
        cmd = f"(sleep 6; touch {marca}) & sleep 30"
        r = mutantes.correr(cmd, self.repo, 2, {})
        self.assertEqual(r["estado"], "timeout")
        time.sleep(6)
        self.assertFalse(marca.exists(), "el proceso huérfano debió morir con el grupo")

    def test_nieto_en_segundo_plano_no_provoca_timeout_falso(self):
        r = mutantes.correr("(sleep 20 &) ; exit 1", self.repo, 10, {})
        self.assertEqual(r["estado"], "falla")
        self.assertLess(r["segundos"], 5)

    def test_cli_codigo_1_con_sobrevivientes(self):
        p = self._p("M-02.patch", _parche(self.repo, "def limite(n):\n    return not n >= 5\n"))
        codigo, salida, _ = _silencio(mutantes.main, ["ejecutar", "--cmd", self.cmd, "--repo", str(self.repo),
                                                      "--timeout", "60", str(p)])
        self.assertEqual(codigo, 1)
        self.assertIn("Detectados: 0/1", salida)


if __name__ == "__main__":
    unittest.main()
