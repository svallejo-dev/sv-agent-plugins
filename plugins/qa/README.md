# qa

Dominio de QA del marketplace `sv-agent-plugins`: separa al que construye del que prueba, para que ningún agente se autocertifique. El dev implementa con `ingenieria`; el QA diseña y automatiza el oráculo con este plugin; los scripts deterministas cuentan; el humano decide.

## Principios

1. **El agente que implementa nunca escribe ni edita el oráculo** (criterios, escenarios, tests de aceptación). Si cree que un test está mal, escala.
2. **El QA no certifica.** `verify` entrega puertas y evidencia; la decisión es humana.
3. **Oráculo de uso**: si otro consume lo que produces, el consumidor decide si sirve, no la forma del artefacto.
4. **Caja negra es información, no lugar**: el QA prueba la imagen del PR en un entorno hermético sin ver el código.
5. **Si nadie lee el código, se prueban las pruebas**: sello de integridad, trazabilidad, determinismo e inyección de bugs.

## Flujo

```
to-spec ─► handoff ─► acceptance-criteria ─► test-design ─► test-automation ─► (dev: tdd)
                                      │ premortem           │ 5 técnicas      │ learning tests        │ tests de aceptación
                                      ▼                     ▼ en paralelo     ▼ rojo correcto         ▼ en solo lectura
                                  aprobación humana     sello del diseño   sello de los tests     verify ─► hallazgos
                                                                                                    │   (código → diagnosing-bugs)
                                                                                    test-the-tests ◄┘   (spec → acceptance-criteria)
```

## Skills

| Skill | Invocación | Qué hace |
|---|---|---|
| `qa-setup` | usuario | Modo (solo o dúo), barrera de información, peldaños disponibles con su comando, modo de Pact. Escribe `docs/agentes/qa.md`. |
| `qa-acceptance-criteria` | modelo | Criterios verificables desde fuera con su oráculo; oráculo de uso; criterios implícitos; premortem de criterios con 3 sub-agentes. |
| `qa-test-design` | modelo | Exige el contrato de handoff; 5 sub-agentes en paralelo por familia de técnicas ISTQB y de fallo; asigna peldaño; traza y sella. |
| `qa-test-automation` | modelo | Harness por peldaño, learning tests primero, escenarios con herramientas existentes; rojo por la razón correcta, determinismo y trazabilidad antes de sellar. |
| `qa-verify` | modelo | Puertas deterministas por ritmo; clasificación de fallos (código, configuración, spec, test, entorno); push-down; informe sin "aprobado". |
| `qa-test-the-tests` | modelo | Mutantes semánticos sobre el diff en worktrees temporales; los sobrevivientes son huecos concretos en los escenarios. |
| `qa-toolbox` | modelo | Radar de herramientas y guía de elección por necesidad y peldaño. |
| `qa-core` | modelo | Base compartida: referencias y scripts. **Instálala siempre** junto a las demás: todas la enlazan como carpeta hermana. |

## Scripts (en `skills/qa-core/scripts/`, biblioteca estándar de Python, con tests)

| Script | Qué hace |
|---|---|
| `scripts/sello.py` | Hash de todo el oráculo (criterios, escenarios, tests, scripts de peldaño, configuración); detecta cambios y enlaces simbólicos; contra la rama base lista cada re-sellado y rompe si se borró, se recreó o se re-selló sin citar `E-NN`/`H-NN`. |
| `scripts/trazabilidad.py` | Cadena criterio → escenario → test → resultado desde Markdown, fuentes y JUnit de una sola ejecución; saltado, no ejecutado, reporte viejo, caso con varios IDs o criterio sin evidencia en el alcance no son verdes. |
| `scripts/mutantes.py` | Parches de mutantes en worktrees temporales, con ejecución base obligatoria, huella del código, rutas prohibidas y grupo de procesos; solo cuenta como detectado si falla un escenario. |

Tests: `python3 -m unittest discover -s skills/qa-core/scripts/tests`.

## Referencias compartidas (en `skills/qa-core/referencias/`)

- `referencias/modelo-de-roles.md`: roles, modos solo y dúo, barrera de información N1-N3, escalamiento, permisos por artefacto.
- `referencias/escalera-de-ambientes.md`: peldaños 0 a 5, regla de asignación, ritmos.
- `referencias/formatos.md`: handoff, criterios, escenarios, convención de IDs en JUnit, hallazgos, escalamientos, informe.
- `referencias/portabilidad.md`: cómo se cumplen sub-agentes, preguntas y carga de skills en cada herramienta, y qué declarar si una capacidad falta.

## Lo que este plugin no garantiza (todavía)

- **La barrera de información es por convención en N1**, y la regla de contaminación también: ninguna puerta comprueba qué leyó una sesión. Para garantía real, N2 o N3.
- **El sello detecta, no impide, y no atribuye.** Un agente puede editar un test y volver a sellar. Lo que no puede es hacerlo sin que quede a la vista: `verify` compara contra la rama base y lista cada re-sellado para la revisión humana del PR. Quién lo hizo lo dice git, no el sello. Impedirlo según el rol (hooks) es la fase 2.
- **El special-casing** (código que reconoce los datos del test) no lo detecta ningún script con certeza. Lo mitigan los datos aleatorios sin marcas, el aviso G9 de `verify` y la revisión de código.
- **La cobertura depende del diseño de escenarios.** Las herramientas ejecutan; las técnicas y el humano deciden qué se prueba.

## Dependencias

Funciona solo. Rinde más con `ingenieria` (spec, tickets con walking skeleton, `tdd` como lazo interno, `diagnosing-bugs` para los hallazgos), `arquitectura` (modos de fallo por arquetipo) y un plugin de lenguaje (`go-testing` para la plomería en Go).

## Instalación

Ver el [README del repositorio](../../README.md#instalación) para Claude Code, Codex, GitHub Copilot, Cursor y Windsurf. En resumen, con Claude Code:

```bash
claude plugin marketplace add svallejo-dev/sv-agent-plugins
claude plugin install qa@sv-agent-plugins
```

Después, en cada repo, ejecuta la skill `qa-setup`.

Licencia MIT.
