#!/usr/bin/env python3
"""Calculadora de capacidad para diseño de sistemas (solo stdlib).

Cada subcomando es una fórmula explícita; la salida es JSON con las entradas,
los resultados y la fórmula usada, para que el razonamiento sea auditable.

Subcomandos:
  demanda        Demanda proyectada desde usuarios (sistema nuevo).
  medido         Proyección desde tráfico medido (sistema existente).
  escenarios     Demanda para varios órdenes de magnitud (sin métricas).
  umbral         Escala a partir de la cual una decisión deja de servir.
  little         Ley de Little: concurrencia y tamaño de pool.
  utilizacion    Tiempo de respuesta vs utilización (aproximación M/M/1).
  fanout         Probabilidad de pegar en la cola de latencia con fan-out.
  disponibilidad Composición de disponibilidad en serie y en paralelo.
  shards         Número de shards/nodos por throughput y por tamaño.
  backlog        Tiempo de drenaje de una cola atrasada.
  burn           Consumo del presupuesto de error según el burn rate.

Ejemplo:
  python3 capacidad.py little --rps 1200 --latencia-ms 180 --utilizacion 0.7
"""
import argparse
import json
import math
import sys

SEG_DIA = 86_400
MIN_MES = 30 * 24 * 60


def humano(n, unidad=""):
    for div, suf in ((1e15, "P"), (1e12, "T"), (1e9, "G"), (1e6, "M"), (1e3, "K")):
        if abs(n) >= div:
            return f"{n / div:.2f}{suf}{unidad}"
    return f"{n:.2f}{unidad}"


def demanda(dau, escrituras_usuario_dia, lecturas_por_escritura, pico, bytes_objeto,
            retencion_dias, replicas, bytes_respuesta):
    w_avg = dau * escrituras_usuario_dia / SEG_DIA
    r_avg = w_avg * lecturas_por_escritura
    bytes_dia = dau * escrituras_usuario_dia * bytes_objeto
    total = bytes_dia * retencion_dias * replicas
    return {
        "formula": "qps = dau * acciones / 86400; pico = qps * factor; almacenamiento = escrituras/dia * bytes * retencion * replicas",
        "escrituras_qps_promedio": w_avg,
        "escrituras_qps_pico": w_avg * pico,
        "lecturas_qps_promedio": r_avg,
        "lecturas_qps_pico": r_avg * pico,
        "almacenamiento_por_dia_bytes": bytes_dia,
        "almacenamiento_total_bytes": total,
        "almacenamiento_total": humano(total, "B"),
        "ingreso_pico_bytes_s": w_avg * pico * bytes_objeto,
        "egreso_pico_bytes_s": r_avg * pico * bytes_respuesta,
    }


def escenarios(dau, escrituras_usuario_dia, lecturas_por_escritura, pico, bytes_objeto,
               retencion_dias, replicas, bytes_respuesta):
    filas = []
    for d in dau:
        r = demanda(d, escrituras_usuario_dia, lecturas_por_escritura, pico, bytes_objeto,
                    retencion_dias, replicas, bytes_respuesta)
        filas.append({
            "dau": d,
            "escrituras_qps_pico": r["escrituras_qps_pico"],
            "lecturas_qps_pico": r["lecturas_qps_pico"],
            "almacenamiento_total": r["almacenamiento_total"],
            "egreso_pico": humano(r["egreso_pico_bytes_s"], "B/s"),
        })
    return {
        "formula": "demanda() evaluada en cada escenario; los factores por usuario son supuestos de arquetipo",
        "escenarios": filas,
        "nota": "Diseña para el escenario probable a 12-18 meses y verifica qué se rompe en el siguiente.",
    }


def umbral(qps_limite, acciones_usuario_dia, pico, utilizacion):
    dau = qps_limite * utilizacion * SEG_DIA / (acciones_usuario_dia * pico)
    return {
        "formula": "dau_umbral = qps_limite * utilizacion * 86400 / (acciones_usuario_dia * pico)",
        "dau_umbral": dau,
        "dau_umbral_legible": humano(dau),
        "nota": "A partir de esta escala la decisión (un solo nodo, una sola partición, etc.) deja de servir; úsalo en la columna 'cámbiala cuando…'.",
    }


def medido(rps_pico_actual, crecimiento_anual, horizonte_meses, utilizacion_objetivo,
           rps_por_instancia):
    factor = crecimiento_anual ** (horizonte_meses / 12)
    proyectado = rps_pico_actual * factor
    out = {
        "formula": "proyectado = rps_pico_actual * crecimiento_anual^(meses/12)",
        "factor_crecimiento": factor,
        "rps_pico_proyectado": proyectado,
    }
    if rps_por_instancia:
        out["instancias_necesarias"] = math.ceil(proyectado / (rps_por_instancia * utilizacion_objetivo))
        out["formula_instancias"] = "ceil(proyectado / (rps_por_instancia * utilizacion_objetivo))"
    return out


def little(rps, latencia_ms, utilizacion):
    concurrencia = rps * latencia_ms / 1000
    return {
        "formula": "L = lambda * W; pool = ceil(L / utilizacion)",
        "concurrencia_media": concurrencia,
        "pool_recomendado": math.ceil(concurrencia / utilizacion),
        "nota": "Usa la latencia del percentil que quieras soportar sin encolar (p99 para pools de conexiones a dependencias).",
    }


def utilizacion(servicio_ms, rho, rps):
    if not 0 <= rho < 1:
        raise ValueError("rho debe estar en [0, 1)")
    tabla = {f"{u:.2f}": servicio_ms / (1 - u) for u in (0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99)}
    out = {
        "formula": "R = S / (1 - rho)  (M/M/1: llegadas Poisson, un servidor; orientativo)",
        "respuesta_ms_en_rho": servicio_ms / (1 - rho),
        "respuesta_ms_por_rho": tabla,
    }
    if rps:
        out["servidores_para_rho"] = math.ceil(rps * servicio_ms / 1000 / rho)
        out["formula_servidores"] = "ceil(lambda * S / rho)"
    return out


def fanout(n, p):
    return {
        "formula": "P(al menos una lenta) = 1 - (1 - p)^n",
        "prob_respuesta_lenta": 1 - (1 - p) ** n,
        "nota": "p = probabilidad de que un backend responda por encima de su percentil (0.01 para p99).",
    }


def disponibilidad(serie, paralelo):
    total = 1.0
    detalle = []
    for a in serie:
        total *= a
        detalle.append({"serie": a})
    for item in paralelo:
        a, k = item.split(":")
        a, k = float(a), int(k)
        comp = 1 - (1 - a) ** k
        total *= comp
        detalle.append({"paralelo": a, "replicas": k, "compuesta": comp})
    return {
        "formula": "serie: producto; paralelo independiente: 1 - (1 - a)^k",
        "disponibilidad": total,
        "caida_min_mes": (1 - total) * MIN_MES,
        "detalle": detalle,
        "nota": "El paralelo asume fallos independientes; los fallos correlacionados (misma zona, mismo deploy, misma config) rompen esa suposición.",
    }


def shards(qps_pico, qps_nodo, bytes_total, bytes_nodo, utilizacion):
    por_qps = math.ceil(qps_pico / (qps_nodo * utilizacion)) if qps_nodo else 0
    por_bytes = math.ceil(bytes_total / (bytes_nodo * utilizacion)) if bytes_nodo else 0
    return {
        "formula": "max(ceil(qps / (qps_nodo * u)), ceil(bytes / (bytes_nodo * u)))",
        "por_throughput": por_qps,
        "por_tamano": por_bytes,
        "shards": max(por_qps, por_bytes),
        "limitante": "throughput" if por_qps >= por_bytes else "tamano",
        "nota": "Calcula sobre la key/partición más caliente, no sobre el promedio, si la distribución está sesgada.",
    }


def backlog(mensajes, produccion_s, consumo_s):
    neto = consumo_s - produccion_s
    out = {"formula": "t = backlog / (consumo - produccion)", "drenaje_neto_s": neto}
    if neto <= 0:
        out["tiempo_drenaje_s"] = None
        out["nota"] = "El backlog nunca drena: el consumo no supera a la producción."
    else:
        t = mensajes / neto
        out["tiempo_drenaje_s"] = t
        out["tiempo_drenaje_h"] = t / 3600
    return out


def burn(slo, ventana_dias, burn_rate):
    presupuesto_min = (1 - slo) * ventana_dias * 24 * 60
    return {
        "formula": "tiempo hasta agotar = ventana / burn_rate",
        "presupuesto_error_min": presupuesto_min,
        "dias_hasta_agotar": ventana_dias / burn_rate,
        "horas_hasta_agotar": ventana_dias * 24 / burn_rate,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)

    d = sp.add_parser("demanda")
    d.add_argument("--dau", type=float, required=True)
    d.add_argument("--escrituras-usuario-dia", type=float, required=True)
    d.add_argument("--lecturas-por-escritura", type=float, default=10.0)
    d.add_argument("--pico", type=float, default=2.0)
    d.add_argument("--bytes-objeto", type=float, default=1e3)
    d.add_argument("--retencion-dias", type=float, default=365)
    d.add_argument("--replicas", type=float, default=3)
    d.add_argument("--bytes-respuesta", type=float, default=1e3)

    e = sp.add_parser("escenarios")
    e.add_argument("--dau", type=float, nargs="+", required=True, help="p. ej. 1e4 1e6 1e8")
    e.add_argument("--escrituras-usuario-dia", type=float, required=True)
    e.add_argument("--lecturas-por-escritura", type=float, default=10.0)
    e.add_argument("--pico", type=float, default=2.0)
    e.add_argument("--bytes-objeto", type=float, default=1e3)
    e.add_argument("--retencion-dias", type=float, default=365)
    e.add_argument("--replicas", type=float, default=3)
    e.add_argument("--bytes-respuesta", type=float, default=1e3)

    um = sp.add_parser("umbral")
    um.add_argument("--qps-limite", type=float, required=True, help="capacidad de la opción evaluada")
    um.add_argument("--acciones-usuario-dia", type=float, required=True)
    um.add_argument("--pico", type=float, default=2.0)
    um.add_argument("--utilizacion", type=float, default=0.7)

    m = sp.add_parser("medido")
    m.add_argument("--rps-pico-actual", type=float, required=True)
    m.add_argument("--crecimiento-anual", type=float, default=1.0, help="factor, p. ej. 2 = se duplica al año")
    m.add_argument("--horizonte-meses", type=float, default=12)
    m.add_argument("--utilizacion-objetivo", type=float, default=0.6)
    m.add_argument("--rps-por-instancia", type=float, default=0)

    l = sp.add_parser("little")
    l.add_argument("--rps", type=float, required=True)
    l.add_argument("--latencia-ms", type=float, required=True)
    l.add_argument("--utilizacion", type=float, default=0.7)

    u = sp.add_parser("utilizacion")
    u.add_argument("--servicio-ms", type=float, required=True)
    u.add_argument("--rho", type=float, default=0.7)
    u.add_argument("--rps", type=float, default=0)

    f = sp.add_parser("fanout")
    f.add_argument("--n", type=int, required=True)
    f.add_argument("--p", type=float, default=0.01)

    a = sp.add_parser("disponibilidad")
    a.add_argument("--serie", type=float, nargs="*", default=[])
    a.add_argument("--paralelo", nargs="*", default=[], help="disponibilidad:replicas, p. ej. 0.99:3")

    s = sp.add_parser("shards")
    s.add_argument("--qps-pico", type=float, required=True)
    s.add_argument("--qps-nodo", type=float, required=True)
    s.add_argument("--bytes-total", type=float, default=0)
    s.add_argument("--bytes-nodo", type=float, default=0)
    s.add_argument("--utilizacion", type=float, default=0.7)

    b = sp.add_parser("backlog")
    b.add_argument("--mensajes", type=float, required=True)
    b.add_argument("--produccion-s", type=float, required=True)
    b.add_argument("--consumo-s", type=float, required=True)

    br = sp.add_parser("burn")
    br.add_argument("--slo", type=float, required=True)
    br.add_argument("--ventana-dias", type=float, default=30)
    br.add_argument("--burn-rate", type=float, required=True)

    x = p.parse_args(argv)
    args = {k: v for k, v in vars(x).items() if k != "cmd"}
    fn = {
        "demanda": demanda, "escenarios": escenarios, "umbral": umbral, "medido": medido, "little": little, "utilizacion": utilizacion,
        "fanout": fanout, "disponibilidad": disponibilidad, "shards": shards,
        "backlog": backlog, "burn": burn,
    }[x.cmd]
    out = {"calculo": x.cmd, "entradas": args, "resultado": fn(**args)}
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
