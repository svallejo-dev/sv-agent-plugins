---
name: tdd
description: "Test-driven development en cualquier lenguaje. Úsala cuando el usuario quiera construir una feature o arreglar un bug test-first, mencione \"TDD\", \"red-green-refactor\" o \"test primero\", o pida tests de integración."
license: MIT
---

# Test-Driven Development

Responde en español y conserva en inglés los términos técnicos habituales.

TDD es el ciclo red → green, y es ante todo una **herramienta de diseño** del dev: el test escrito primero obliga a decidir la interfaz desde el punto de vista de quien la usa. No es un mecanismo de certificación: que el dev escriba sus propios tests no prueba que la feature cumpla la spec (ver "Double loop" abajo). Esta skill es la referencia que hace que ese ciclo produzca tests que valga la pena conservar: qué es un buen test, dónde van, los anti-patrones y las reglas del ciclo. Cada sección aplica en cada ciclo: consúltalas antes y durante, no después.

Analogía: el test en rojo es el plano del hueco que vas a rellenar; si escribes primero el código, estás rellenando sin saber la forma del hueco.

Al explorar el código, lee `GLOSARIO.md` (si existe) para que los nombres de los tests y de las interfaces coincidan con el lenguaje del dominio, y respeta los ADRs del área.

## Lenguaje

Esta skill es agnóstica al lenguaje. Identifica el lenguaje del código bajo test por las extensiones de sus archivos (`.go` → `go`, `.php` → `php`, `.ts`/`.tsx` → `typescript`, `.py` → `python`). Si entre tus skills disponibles existe `<lenguaje>-testing`, cárgala (en Claude Code, con la herramienta Skill; en otras herramientas, mencionándola por su nombre o leyendo su SKILL.md) antes del primer ciclo: aporta los idiomas de test, los ejemplos, los dobles de test preferidos y los comandos de ese lenguaje, y sus reglas prevalecen sobre los ejemplos genéricos de aquí. Si no existe, sigue solo con esta skill y dilo en una línea.

## Qué es un buen test

Los tests verifican comportamiento a través de interfaces públicas, no detalles de implementación. El código puede cambiar por completo; los tests no deberían. Un buen test se lee como una especificación: "el cliente puede pagar con un carrito válido" dice exactamente qué capacidad existe, y sobrevive a los refactors porque no le importa la estructura interna.

Ejemplos en [tests.md](tests.md) y guía de dobles de test en [mocking.md](mocking.md).

## Seams: dónde van los tests

Un **seam** es la frontera pública donde se testea: la interfaz en la que observas el comportamiento sin meterte dentro. Los tests viven en seams, nunca contra internos. Seams típicos: la API pública de un módulo o paquete, un endpoint HTTP, el consumidor de una cola, una CLI.

**Testea solo en seams acordados.** Antes de escribir ningún test, anota los seams y confírmalos con el usuario. No se escribe ningún test en un seam sin confirmar. No puedes testearlo todo; acordar los seams de antemano es cómo el esfuerzo de testing cae en los caminos críticos y la lógica compleja en vez de en cada caso límite.

Pregunta: "¿Cuál es la interfaz pública y qué seams testeamos?". Dale a cada seam propuesto una nota de una línea con qué atrapa y qué se le escapa.

Cuando lo que está en duda es la forma de esa interfaz (qué tan profundo es el módulo, dónde va el seam, qué debe exponer), invoca la skill `codebase-design` para el vocabulario. Es la fuente compartida de los términos módulo, interfaz, profundidad, seam, adapter, leverage y locality; es una referencia que consultas, no una sesión que ejecutas.

## Anti-patrones

- **Acoplado a la implementación**: mockea colaboradores internos, testea funciones privadas, o verifica por un canal lateral (consultar la base de datos en vez de usar la interfaz). La señal: el test se rompe al refactorizar aunque el comportamiento no cambió.
- **Tautológico**: la aserción recalcula el valor esperado igual que el código (el esperado de `sumar(a, b)` calculado como `a + b`, un snapshot generado por el propio código sin revisar, una constante comparada consigo misma), así que pasa por construcción y nunca puede discrepar. Los valores esperados vienen de una fuente de verdad independiente: un literal conocido, un ejemplo trabajado a mano, la spec.
- **Rebanado horizontal** (en el lazo interno): escribir todos tus tests primero y luego toda la implementación. No aplica a los tests de aceptación del QA, que se especifican por adelantado a propósito: son el lazo externo, no tus tests de diseño. Los tests en bloque verifican comportamiento _imaginado_: testean la _forma_ de las cosas en vez del comportamiento, se vuelven insensibles a cambios reales y fijan la estructura de tests antes de entender la implementación. Trabaja en **rebanadas verticales**: un test → una implementación → repetir; cada test es una **tracer bullet** que responde a lo que enseñó el ciclo anterior.

## Reglas del ciclo

- **Red antes que green.** Escribe primero el test que falla y míralo fallar ejecutando solo ese test; después escribe solo el código justo para que pase. No anticipes tests futuros ni añadas funcionalidad especulativa.
- **Una rebanada a la vez.** Un seam, un test, una implementación mínima por ciclo.
- **El refactor no es parte del ciclo.** Pertenece a la etapa de revisión (ver la skill `code-review`), no al ciclo red → green.

## Double loop: los tests de aceptación

TDD es el **lazo interno**. Si el repo usa el plugin `qa` (existe `docs/agentes/qa.md`), hay un **lazo externo**: los tests de aceptación que escribió el rol QA a partir de la spec (double-loop TDD, Freeman y Pryce).

Analogía: el lazo interno es el carpintero comprobando cada ensamble con su escuadra; el lazo externo es el cliente probando si el cajón abre y cierra. El carpintero no puede redefinir qué significa "el cajón funciona".

Reglas:

- **Los tests de aceptación son de solo lectura para ti.** No los editas, no los saltas, no les añades tags de exclusión ni cambias sus datos, aunque estés seguro de que están mal. Están sellados: cualquier cambio rompe el sello y la verificación lo detecta.
- **Si un test de aceptación parece incorrecto, escala**: registra una entrada en `.scratch/<feature>/qa/escalamientos.md` con el escenario, tu argumento y la evidencia, y sigue con otro escenario. Decide el QA o el humano.
- **Nada de special-casing**: el código de producción nunca reconoce datos, IDs (`ESC-NN`), rutas ni variables de los tests para responder lo que esperan. Es la otra forma de hacer trampa, y `qa-verify` la busca en el diff.
- **No los corras en cada ciclo**: durante la implementación casi todos están en rojo por diseño. Trabaja con tus tests del lazo interno y ejecuta los de aceptación del ticket **al cerrar la rebanada**, con `qa-verify` en ritmo por rebanada si está disponible.
- **Un ticket no está terminado** mientras sus escenarios de aceptación no estén en verde con el sello íntegro. Tus tests verdes no bastan.
- Si `qa-verify` te pasa un **hallazgo** (H-NN) de clase código, su comando de reproducción es el punto de partida: bájalo a un test de integración o unitario que lo reproduzca en rojo, y ese test se queda en tu suite como regresión.

