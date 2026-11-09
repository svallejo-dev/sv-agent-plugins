---
name: qa-test-the-tests
description: "Prueba la suite de aceptación inyectando bugs plausibles (mutantes) en el código del diff, en worktrees temporales que nunca tocan el repo, y reporta qué bugs sobreviven; cada sobreviviente es un hueco concreto en los escenarios. Úsala cuando el usuario pregunte \"¿los tests sirven?\", \"¿la suite tiene dientes?\", pida \"mutation testing\", \"inyección de bugs\" o \"probar las pruebas\", y como puerta del ritmo completo (obligatoria en modo solo)."
license: MIT
---

# Probar las pruebas

Responde en español y conserva en inglés los términos técnicos habituales.

Si nadie lee el código y nadie lee los tests línea por línea, ¿cómo sabes que una suite en verde significa algo? Inyectando bugs conocidos y comprobando que la suite los detecta. Cada bug que sobrevive es un hueco **concreto** en los escenarios, con nombre y apellido, no una métrica abstracta de cobertura.

**Analogía:** calibrar una balanza con pesas patrón. Si pones una pesa de 1 kg y marca 0, la balanza no sirve, aunque siempre haya marcado "bien".

**Fundamento:** la detección de mutantes se asocia con la detección de fallos reales más que la cobertura de código (Just et al., 2014); la correlación existe pero es más débil cuando se controla el tamaño de la suite (Papadakis et al., 2018). Por eso aquí el valor no está en un porcentaje, sino en cada sobreviviente concreto. Google lo aplica sobre el diff, con pocos mutantes por cambio y mostrados en la revisión de código; Meta (ACH) usa LLMs para generar mutantes plausibles y los tests que los matan. Esta skill aplica la misma idea al nivel de **aceptación**: mutantes semánticos, plausibles y escogidos por riesgo, no miles de mutaciones sintácticas.

## 0. Precondiciones

- Ejecuta los scripts desde la raíz del repositorio. `<qa-core>` es la carpeta de la skill `qa-core`, hermana de esta; `<Aceptación>` y `<Reportes>` salen de `docs/agentes/qa.md`.
- `docs/agentes/qa.md` declara el **comando de suite para mutantes**, la limpieza, el timeout, el presupuesto y las rutas prohibidas. Si no, pide completarlo (`qa-setup`). El comando cumple el contrato de los scripts de peldaño: construye la imagen **desde el directorio actual** con `$QA_IMAGEN_TAG` y escribe el JUnit en `$QA_REPORTES`. Si no reconstruye la imagen desde el worktree, todos los mutantes "sobreviven" sin haberse probado.
- **Coste**: (base + N mutantes) × (build + suite). Con 5-10 mutantes puede pasar de una hora. Si no cabe en el presupuesto antes del PR, ejecútalo en el nocturno; el informe vale para la huella del código evaluado.
- La feature está implementada y la suite está en verde en el peldaño 1. El script lo comprueba (ejecución base) y aborta si no: con una base roja los resultados no significan nada.
- El sello está íntegro (`sello.py verificar`).

## 1. Separación de roles

El **agente de mutación** es un rol adversarial distinto:
- **Ve el código** (lo necesita para inyectar bugs), pero **no edita** ni tests ni código del repo: sus cambios solo existen como parches que el script aplica en worktrees temporales.
- **Reporta los sobrevivientes en términos de comportamiento**, no de código: "el sistema acepta un sexto dispositivo y ningún escenario lo detecta", no "cambié `<` por `<=` en la línea 40". Así el QA puede añadir escenarios sin ver el código, y la barrera de información se mantiene.

Lánzalo como sub-agente con contexto limpio si la sesión actual es la del QA (para no exponerla al código) o la del dev (para que no elija mutantes que sabe que su suite detecta).

> **Portabilidad:** si tu herramienta no tiene sub-agentes, sigue [../qa-core/referencias/portabilidad.md](../qa-core/referencias/portabilidad.md) y decláralo en el artefacto.

## 2. Elige los mutantes

1. Alcance: los archivos de producción del diff de la feature (`git diff <base>...HEAD --stat`).
2. Elige **entre 5 y 10 mutantes**, priorizando por riesgo: las reglas de los criterios críticos, las integraciones con terceros, la caché, la idempotencia, los límites. Usa el catálogo de [references/catalogo-mutantes.md](references/catalogo-mutantes.md).
3. Cada mutante cumple cuatro condiciones:
   - **Plausible**: un error que una persona o un agente podría cometer de verdad.
   - **Único**: un solo cambio de comportamiento por mutante.
   - **Observable**: cambia algo que algún criterio exige. Si crees que no cambia ningún comportamiento observable, es un candidato a **equivalente**: no lo ejecutes, pero **lístalo en el manifiesto** como "descartado por equivalente" con tu justificación. Lo confirma el humano, no tú.
   - **Solo código de producción**: nunca toca tests, la carpeta de aceptación, el tracker, la configuración de QA ni los scripts de peldaño. El script rechaza los parches que tocan las rutas prohibidas.

## 3. Escribe los parches

Un archivo por mutante en `.scratch/<feature>/qa/mutantes/<fecha>/M-NN-<slug>.patch`, construido contra el estado actual del árbol de trabajo:

```bash
cp <archivo> /tmp/mutante/<archivo>            # copia
# edita la copia con el cambio del mutante
diff -u --label a/<archivo> --label b/<archivo> <archivo> /tmp/mutante/<archivo> > M-NN-<slug>.patch
```

**Nunca edites el archivo del repo** para fabricar el parche. Junto a los parches, un `manifiesto.md`:

| ID | Archivo | Categoría | Comportamiento que cambia | Criterio que debería detectarlo | Estado |
|---|---|---|---|---|---|

Estado: `a ejecutar` o `descartado por equivalente: <justificación>`.

## 4. Ejecuta

```bash
python3 <qa-core>/scripts/mutantes.py ejecutar --cmd "<comando de suite de qa.md>" \
  --timeout <timeout> --limpieza "<limpieza de qa.md>" --prohibidas <rutas prohibidas de qa.md> \
  --salida .scratch/<feature>/qa/mutantes/<fecha>/resultados.json \
  .scratch/<feature>/qa/mutantes/<fecha>/M-*.patch
```

El script registra la **huella** del código (HEAD y hash de los cambios sin commitear), ejecuta primero la base sin mutantes (si no pasa, o no deja ningún JUnit con escenarios, aborta), y para cada parche crea un worktree temporal con el estado actual, aplica el parche, corre la suite en su propio grupo de procesos (en un timeout mata también los procesos hijos) y elimina el worktree pase lo que pase. El repositorio no se toca. No hay opción para saltarse la base.

## 5. Analiza

| Resultado | Qué significa | Acción |
|---|---|---|
| **detectado** | La suite terminó en rojo y al menos un escenario `ESC-NN` falló | Comprueba que entre los escenarios en rojo hay uno del criterio que el manifiesto esperaba; si solo cayó otro, anótalo: el criterio esperado puede tener un hueco |
| **sobrevive** | La suite pasó con el bug dentro | Triage (abajo) |
| **error-harness** | Rojo sin ningún escenario fallido: no compiló, el harness no arrancó | No cuenta como detectado. Rehaz el mutante (uno que no compila no es plausible) o arregla el harness |
| **timeout** | La suite no terminó | Investiga: un mutante que cuelga el sistema puede ser un bug real de robustez no cubierto; nunca cuenta como detectado |
| **no-aplica** | Parche mal construido | Rehazlo |
| **rechazado** | El parche toca rutas prohibidas | Rehazlo sobre código de producción |

Triage de cada sobreviviente:
1. **Equivalente**: el cambio no altera ningún comportamiento observable. Justifícalo por escrito; **lo decide el humano**, no el agente de mutación.
2. **Hueco de escenario**: el criterio existe pero ningún escenario observa ese comportamiento. Pasa al QA la descripción **en términos de comportamiento**; `qa-test-design` añade el escenario y el ciclo de aprobación y sello se repite.
3. **Hueco de criterio**: ningún criterio exige ese comportamiento. Vuelve a `qa-acceptance-criteria`: o falta un criterio, o el comportamiento no importa (y entonces el mutante es equivalente para el negocio).

## 6. Informe

Escribe `.scratch/<feature>/qa/mutantes/<fecha>.md` con:
- la **huella** de `resultados.json` (un informe vale solo para esa huella; si el código cambia, `qa-verify` pide uno nuevo en el ritmo completo);
- los descartados por equivalente, para que el humano los confirme;
- la tabla de resultados;
- cada sobreviviente con su triage y su decisión.

`qa-verify` lo usa como puerta G8.

## Complemento en el lazo interno

Para los tests unitarios del dev existen herramientas de mutación mecánica (en Go, Gremlins). Son útiles en el ritmo completo del dev, pero responden otra pregunta: si los tests **unitarios** detectan mutaciones sintácticas. No reemplazan a esta skill, que mide el oráculo de **negocio**.
