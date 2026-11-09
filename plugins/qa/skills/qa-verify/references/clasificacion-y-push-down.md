# Clasificar un fallo y bajarlo de peldaño

Un test que falla te da un **síntoma**, no un diagnóstico. "El escenario del límite devolvió 201" no dice qué cambiar. Este procedimiento convierte el síntoma en algo accionable: **quién** debe actuar (la clase) y **dónde** está el defecto (el peldaño más bajo donde se reproduce).

**Analogía:** un médico de urgencias. Primero clasifica (triage) para mandar al paciente al especialista correcto; luego pide estudios cada vez más específicos (radiografía, después tomografía) hasta localizar la lesión. No opera por el síntoma.

## Árbol de clasificación

Aplica las preguntas en orden; la primera que se responda con "sí" decide.

1. **¿El test refleja fielmente el escenario y el criterio aprobados?**
   Compara el test con su fila de `escenarios.md` y su criterio. Si el test verifica algo distinto (otro dato, otra aserción, otro oráculo) → **test**.
   En modo solo, si esta sesión escribió el código, esta respuesta la da un sub-agente QA limpio o el humano.

2. **¿Se reproduce de forma determinista?**
   Si el escenario alternó resultados entre las corridas de G5, es intermitente. Entonces:
   - Si es intermitente **en el peldaño 1** (entorno controlado), la causa casi nunca es "el entorno": suele ser una **carrera del código** o un **harness no determinista**. Candidato a **código** (con su patrón como evidencia, para `diagnosing-bugs`) o a **test** si el no determinismo está en el harness (datos compartidos, esperas, orden). Sigue con las preguntas 3 y 4.
   - Si es estable en el peldaño 1 e intermitente solo en ambientes compartidos (3 o 4) → **entorno**. Se registra con su patrón (cuántas veces falló, en qué paso) y queda como deuda.
   En cualquier caso, un intermitente cuenta como rojo, y en un escenario crítico es severidad major como mínimo.

3. **¿Se reproduce en el peldaño 1?**
   Ejecuta el escenario en el peldaño hermético.
   - Sí → candidato a **código**; sigue con la pregunta 4.
   - No (falla en 3 o 4, pasa en 1) → **configuración**: el defecto vive en lo que solo existe desplegado (variables, secretos, permisos, red, versión del vecino, migraciones). La evidencia es la **diferencia** entre peldaños: qué tiene el ambiente que el peldaño 1 no.

4. **¿El comportamiento que el test exige es el correcto según la realidad?**
   Busca evidencia externa: la documentación oficial del tercero, un learning test, el consumidor real, la respuesta del dueño de negocio.
   - Si la realidad contradice la spec (el tercero no se comporta así, el consumidor necesita otra cosa) o la spec es ambigua en este punto → **spec**.
   - Si no → **código**.

Si después de las cuatro preguntas no puedes decidir, la clase es **indeterminada** y el hallazgo lo resuelve el humano. No la fuerces.

## Bajar de peldaño (push the test down)

Cada bajada reduce el área donde puede estar el defecto. El objetivo es entregar el hallazgo con **el comando de reproducción más bajo y más rápido posible**.

```
peldaño 4 (staging)        "falla en staging"              → zona: todo el sistema desplegado
   ↓ reproducir en 1
peldaño 1 (hermético)      "falla con la imagen del PR"    → zona: el servicio y sus dependencias controladas
   ↓ el dev reproduce como test de integración
integración (lazo interno)  "falla el repositorio con Postgres" → zona: un módulo y su adapter
   ↓ el dev reproduce como unitario
unitario                     "falla la regla del límite"     → zona: una función
```

- **El QA baja hasta el peldaño 1.** Por debajo hace falta ver el código; eso es del dev, con `diagnosing-bugs`, que recibe el comando de reproducción del peldaño 1 como su feedback loop (su Fase 1).
- Si un fallo no baja del peldaño 3 o 4, eso ya es información: el defecto no es de lógica, es de integración o configuración.
- Al cerrarse el hallazgo, el test de bajo nivel que escribió el dev se queda como **regresión** en su suite; el escenario de aceptación sigue siendo el oráculo de negocio.

## Severidad

| Severidad | Criterio |
|---|---|
| **blocker** | Viola un criterio de prioridad crítica, un invariante (doble cobro, fuga de datos, token entregado al cliente equivocado) o rompe el walking skeleton |
| **major** | Viola un criterio de prioridad alta, o es un flaky en un escenario crítico |
| **minor** | Viola un criterio de prioridad media sin riesgo de datos ni de dinero |

## Lo que nunca se hace

- Cerrar un hallazgo porque "pasó al reintentar".
- Clasificar como `test` para desbloquear el ritmo sin la confirmación requerida.
- Bajar la severidad porque el arreglo es caro.
- Redactar una hipótesis sobre el **código**: el QA no lo vio. Las hipótesis son sobre el **comportamiento** ("parece que la caché no distingue entre clientes", no "el map de la línea 40 usa una clave global").
