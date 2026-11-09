# Escalera de ambientes y ritmos de ejecución

Referencia compartida. Responde dos preguntas: **dónde** corre cada escenario y **cuándo** se ejecuta cada grupo.

**Analogía:** fabricar un auto.
- El **laboratorio de choque** (entorno hermético) repite el mismo impacto mil veces controlando cada variable.
- La **prueba en carretera** (staging) es real, pero no puedes pedir que un peatón cruce cuando lo necesitas.
- La **telemetría de la flota** (producción) ve lo que pasa de verdad.

Nadie valida los airbags en carretera pública, y nadie da el auto por bueno solo porque pasó el laboratorio.

## Caja negra no es lo mismo que ambiente desplegado

Son ejes independientes:
- **Caja negra** es una frontera de **información**: el QA no lee el código.
- **Ambiente** es un **lugar de ejecución**.

El QA prueba en caja negra contra la **imagen del PR** levantada en el peldaño 1 sin ver una línea de código. No necesita un staging compartido para no ver el código.

## Los peldaños

Una sola suite de aceptación, parametrizada por `base_url` y variables de entorno, sube por la escalera. El artefacto de test no sabe dónde corre.

| Peldaño | Dónde | Qué se prueba ahí | Quién lo opera | ¿Bloquea? |
|---|---|---|---|---|
| **0. Lazo interno** | Máquina del dev | Unit e integración del dev (`tdd`) | Dev | Su propio ciclo; no es del QA |
| **1. Hermético** | Local o CI: imagen del servicio + dependencias con Testcontainers + Toxiproxy + fakes de terceros | Escenarios de aceptación completos, **todos** los edge cases de estado, tiempo, fallo y concurrencia | QA | **Sí**: es la puerta principal |
| **2. Contrato** | Local, on-demand o CI | Pact entre servicios propios (verificación del proveedor) y learning tests contra el sandbox de terceros | Dev (tests de consumidor de Pact, con su código) y QA (learning tests, verificación) | Sí, en el ritmo completo |
| **3. Integrado aislado** | Ambiente efímero por PR, enrutamiento por cabecera sobre staging, o stack local apuntando a sandboxes reales | Walking skeleton con el consumidor real; recorridos con dependencias reales | QA | Sí, si la plataforma lo ofrece |
| **4. Staging compartido** | Después del deploy | Smoke y subconjunto de regresión de los caminos críticos; configuración, auth y red reales | QA | No: alerta |
| **5. Producción** | Canary, flags, monitoreo sintético | 3 a 5 recorridos críticos como checks sintéticos; métricas del canary | SRE o plataforma | Rollback |

## Regla de asignación de un escenario a un peldaño

**Asigna cada escenario al peldaño más bajo donde (a) el comportamiento es observable y (b) el oráculo es confiable.** Súbelo solo si el comportamiento depende de algo que el peldaño bajo no reproduce.

| Si el escenario depende de… | Peldaño | Por qué no más bajo |
|---|---|---|
| Lógica de negocio, validaciones, límites, estados | 1 | — |
| Tiempo (expiraciones, ventanas, TTL) | 1, con reloj controlable | Staging no deja adelantar el reloj |
| Fallos de dependencias (timeouts, 5xx, conexión cortada, respuesta parcial) | 1, con Toxiproxy o fakes | En staging compartido romperías a otros equipos |
| Concurrencia y condiciones de carrera | 1 | Requiere controlar la intercalación |
| Compatibilidad entre servicios propios | 2 (Pact) | — |
| Comportamiento real de un tercero (qué devuelve, con qué forma) | 2 (learning tests) | El fake solo sabe lo que tú creías |
| Que el consumidor real acepte lo que produces (SDK, front, partner) | 3 (walking skeleton) | Solo el consumidor real es oráculo de uso |
| Configuración, secretos, permisos, DNS, auth entre servicios | 3 o 4 | Solo existen desplegados |
| Volumen real, rendimiento | Pruebas de carga dedicadas (k6), fuera de la suite funcional | — |

Si un escenario necesita un seam de testabilidad que no existe (no hay forma de sembrar datos o de controlar el reloj), **no se sube de peldaño para esquivarlo**: se marca `bloqueado-testabilidad` y se registra como deuda. Subirlo a staging lo convierte en un test que no puede fallar por la razón correcta.

## Los ritmos

| Ritmo | Cuándo | Qué corre | Duración objetivo |
|---|---|---|---|
| **Continuo** | En cada ciclo del dev | Peldaño 0 | Segundos |
| **Por rebanada** | Al cerrar un ticket | Los escenarios del ticket en peldaño 1 + sello + trazabilidad | Minutos |
| **Completo** | Antes de PR, merge o release (o nocturno) | Peldaño 1 entero dos veces (estabilidad) + peldaño 2 + peldaño 3 si existe + Schemathesis + muestreo de mutantes | Decenas de minutos sin mutantes; con mutantes, (base + 5-10 mutantes) × (build + suite): puede pasar de una hora. Declara el presupuesto en `docs/agentes/qa.md` y, si no cabe antes del PR, ejecuta los mutantes en el nocturno y exige el informe para el diff antes del merge |
| **Post-deploy** | Tras desplegar en staging | Peldaño 4: los escenarios que incluyen el 4 en su columna Peldaño (smoke y regresión crítica, con el mismo ID que en el peldaño 1) | Minutos |
| **Producción** | Continuo | Peldaño 5: sintéticos | — |

**Por qué los tests de aceptación no corren en el ritmo continuo:** durante la implementación casi todos están en rojo por diseño. Correrlos en cada ciclo es lento y aumenta la presión del agente dev sobre el oráculo, que es justo lo que queremos evitar. El dev trabaja con su lazo interno y mira los de aceptación por rebanada (double-loop TDD: Freeman y Pryce).

## Los peldaños que da tu plataforma

Antes de configurar, mapea qué peldaños ofrece la plataforma interna (ambientes efímeros, scopes de prueba, canary, sintéticos) y cuáles hay que construir. Un peldaño que no existe se declara como "no disponible" en `docs/agentes/qa.md`; los escenarios asignados a él se reportan como no ejecutados, nunca como verdes. Y si un criterio solo tiene escenarios en peldaños no disponibles, `trazabilidad.py` lo marca "sin evidencia en el alcance": la puerta queda en rojo y el informe lo explica. Es intencional: el walking skeleton del caso PayPal no puede quedar en verde porque nadie lo ejecutó.
