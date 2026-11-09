#!/usr/bin/env python3
"""Casos golden de la calculadora: valores calculados a mano, independientes del código."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import capacidad as c  # noqa: E402


class TestCapacidad(unittest.TestCase):
    def test_little(self):
        r = c.little(rps=1000, latencia_ms=200, utilizacion=0.8)
        self.assertAlmostEqual(r["concurrencia_media"], 200)
        self.assertEqual(r["pool_recomendado"], 250)

    def test_utilizacion_mm1(self):
        r = c.utilizacion(servicio_ms=10, rho=0.8, rps=0)
        self.assertAlmostEqual(r["respuesta_ms_en_rho"], 50)
        self.assertAlmostEqual(r["respuesta_ms_por_rho"]["0.90"], 100)

    def test_servidores_por_rho(self):
        r = c.utilizacion(servicio_ms=20, rho=0.5, rps=1000)
        self.assertEqual(r["servidores_para_rho"], 40)

    def test_fanout_tail_at_scale(self):
        r = c.fanout(n=100, p=0.01)
        self.assertAlmostEqual(r["prob_respuesta_lenta"], 0.634, places=3)

    def test_disponibilidad(self):
        r = c.disponibilidad(serie=[0.999, 0.999], paralelo=[])
        self.assertAlmostEqual(r["disponibilidad"], 0.998001)
        r = c.disponibilidad(serie=[], paralelo=["0.99:2"])
        self.assertAlmostEqual(r["disponibilidad"], 0.9999)

    def test_shards(self):
        r = c.shards(qps_pico=120_000, qps_nodo=10_000, bytes_total=0, bytes_nodo=0, utilizacion=0.7)
        self.assertEqual(r["shards"], 18)
        r = c.shards(qps_pico=1_000, qps_nodo=10_000, bytes_total=10e12, bytes_nodo=1e12, utilizacion=0.5)
        self.assertEqual(r["shards"], 20)
        self.assertEqual(r["limitante"], "tamano")

    def test_backlog(self):
        r = c.backlog(mensajes=3_600_000, produccion_s=1_000, consumo_s=2_000)
        self.assertAlmostEqual(r["tiempo_drenaje_h"], 1.0)
        r = c.backlog(mensajes=10, produccion_s=5, consumo_s=5)
        self.assertIsNone(r["tiempo_drenaje_s"])

    def test_burn(self):
        r = c.burn(slo=0.999, ventana_dias=30, burn_rate=14.4)
        self.assertAlmostEqual(r["dias_hasta_agotar"], 2.0833, places=3)
        self.assertAlmostEqual(r["presupuesto_error_min"], 43.2, places=1)

    def test_medido(self):
        r = c.medido(rps_pico_actual=1_000, crecimiento_anual=4, horizonte_meses=6,
                     utilizacion_objetivo=0.5, rps_por_instancia=500)
        self.assertAlmostEqual(r["rps_pico_proyectado"], 2_000)
        self.assertEqual(r["instancias_necesarias"], 8)

    def test_demanda(self):
        r = c.demanda(dau=86_400_000, escrituras_usuario_dia=1, lecturas_por_escritura=10, pico=2,
                      bytes_objeto=1_000, retencion_dias=10, replicas=3, bytes_respuesta=1_000)
        self.assertAlmostEqual(r["escrituras_qps_promedio"], 1_000)
        self.assertAlmostEqual(r["lecturas_qps_pico"], 20_000)
        self.assertAlmostEqual(r["almacenamiento_total_bytes"], 86_400_000 * 1_000 * 10 * 3)


class TestExploratorio(unittest.TestCase):
    def test_escenarios(self):
        r = c.escenarios(dau=[86_400, 8_640_000], escrituras_usuario_dia=1, lecturas_por_escritura=10,
                         pico=2, bytes_objeto=1_000, retencion_dias=1, replicas=1, bytes_respuesta=1_000)
        filas = r["escenarios"]
        self.assertEqual(len(filas), 2)
        self.assertAlmostEqual(filas[0]["escrituras_qps_pico"], 2)
        self.assertAlmostEqual(filas[1]["lecturas_qps_pico"], 2_000)

    def test_umbral(self):
        # 1 000 escrituras/s al 50 % de utilización, 10 acciones por usuario al día, pico 2x
        r = c.umbral(qps_limite=1_000, acciones_usuario_dia=10, pico=2, utilizacion=0.5)
        self.assertAlmostEqual(r["dau_umbral"], 2_160_000)


if __name__ == "__main__":
    unittest.main()
