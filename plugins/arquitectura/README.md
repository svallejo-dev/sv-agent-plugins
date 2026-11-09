# arquitectura

Diseño de sistemas a gran escala del marketplace `sv-agent-plugins`, pensado para partir de un camino ya recorrido: el sistema que existe, uno similar documentado o, sin métricas, el arquetipo del negocio. No tener números nunca bloquea: se trabaja con escenarios por orden de magnitud y umbrales de decisión. Diseña como delta (estado actual → objetivo → camino de migración), con números calculados en código y un red team en paralelo.

| Skill | Qué hace |
|---|---|
| `system-design` | Orquestador en rondas: punto de partida, requisitos como delta, números, 2-3 alternativas, trade-offs con disparador medible, red team, migración, rúbrica. |
| `design-stress-test` | Sub-agentes en paralelo por familia de ataques (carga, dependencias, datos, cambios, infraestructura, operación, abuso), sembrados con incidentes reales y verificados contra la config. |
| `capacity-estimation` | Calculadora probada (`scripts/capacidad.py`): demanda, proyección desde métricas, Little, utilización, fan-out, disponibilidad, shards, backlog, burn rate. |
| `strategic-design` | Subdominios, mapa de contextos AS-IS y TO-BE con patrones nombrados, acoplamiento de cambio desde git. |
| `business-archetypes` | 11 arquetipos de negocio (streaming, fintech, ticketing, e-commerce, social, SaaS B2B, IoT, movilidad, healthtech, plataforma de IA, plataforma de eventos) para diseñar sin métricas: fuerzas, invariantes, subdominios, fallos típicos e hipótesis de PoC. |
| `building-blocks` | Catálogo curado de 19 bloques (en inglés) de proyecto26/system-design-skills, sin archivos de proveedor y con errores corregidos (marcados `[sv-skills]`). |

Rinde más con `general` (research, grilling) e `ingenieria` (domain-modeling para ADRs y glosario) instalados.

## Instalación

Ver el [README del repositorio](../../README.md#instalación) para Claude Code, Codex, GitHub Copilot, Cursor y Windsurf. En resumen, con Claude Code:

```bash
claude plugin marketplace add svallejo-dev/sv-agent-plugins
claude plugin install arquitectura@sv-agent-plugins
```


Origen: el catálogo de bloques viene de [proyecto26/system-design-skills](https://github.com/proyecto26/system-design-skills) (MIT). Licencia MIT.
