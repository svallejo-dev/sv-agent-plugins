---
name: codebase-design
description: "Vocabulario compartido, agnóstico al lenguaje, para diseñar módulos profundos. Úsala cuando el usuario quiera diseñar o mejorar la interfaz de un módulo, paquete o tipo, encontrar oportunidades de profundizar, decidir dónde va un seam, hacer el código más testeable o navegable por agentes, o cuando otra skill necesite este vocabulario."
license: MIT
---

# Diseño de código

Responde en español y conserva en inglés los términos técnicos habituales. La primera vez que uses un término del glosario en una conversación, acompáñalo de su analogía.

## Lenguaje

Esta skill es agnóstica al lenguaje. Identifica el lenguaje del código por las extensiones de sus archivos (`.go` → `go`, `.php` → `php`, `.ts`/`.tsx` → `typescript`, `.py` → `python`). Si entre tus skills disponibles existe `<lenguaje>-design`, cárgala (en Claude Code, con la herramienta Skill; en otras herramientas, mencionándola por su nombre o leyendo su SKILL.md): traduce este vocabulario a las herramientas del lenguaje (cómo se esconde la implementación, dónde se declaran las interfaces, cómo se inyectan dependencias) y sus reglas prevalecen sobre los ejemplos genéricos de aquí. Si no existe, sigue solo con esta skill.

Diseña **módulos profundos**: mucho comportamiento detrás de una interfaz pequeña, ubicada en un seam limpio y testeable a través de esa interfaz. Usa este lenguaje y estos principios dondequiera que se diseñe o reestructure código. El objetivo es leverage para los llamadores, locality para quien mantiene y testeabilidad para todos.

## Glosario

Usa estos términos exactamente: no los sustituyas por "componente", "servicio", "API" o "frontera". El lenguaje consistente es el objetivo.

**Módulo** (module): cualquier cosa con una interfaz y una implementación. Agnóstico de escala a propósito: una función, una clase o tipo con sus métodos, un paquete, un servicio. _Evitar_: unidad, componente, servicio.
Analogía: una caja con un enchufe por fuera y circuitos por dentro.

**Interfaz** (interface): todo lo que un llamador debe saber para usar el módulo correctamente: la firma de tipos, pero también invariantes, restricciones de orden, modos de error, configuración requerida y características de rendimiento. _Evitar_: API, firma (demasiado estrechos: solo cubren la superficie de tipos). Ojo: no es solo la palabra clave `interface` de algunos lenguajes.
Analogía: el manual de uso completo del electrodoméstico, no solo la forma del enchufe.

**Implementación** (implementation): lo que hay dentro del módulo, su código. Distinta de **adapter**: algo puede ser un adapter pequeño con una implementación grande (un repositorio Postgres) o un adapter grande con una implementación pequeña (un fake en memoria). Di "adapter" cuando el tema sea el seam; "implementación" en los demás casos.

**Profundidad** (depth): leverage en la interfaz. Cuánto comportamiento puede ejercitar un llamador (o un test) por unidad de interfaz que tiene que aprender. Un módulo es **profundo** cuando hay mucho comportamiento detrás de una interfaz pequeña, y **superficial** cuando la interfaz es casi tan compleja como la implementación.
Analogía: un interruptor de luz es profundo (un botón, toda la instalación eléctrica detrás); un panel con un interruptor por cable es superficial.

**Seam** _(Michael Feathers)_: un lugar donde puedes alterar el comportamiento sin editar ese lugar; la _ubicación_ donde vive la interfaz de un módulo. Dónde poner el seam es una decisión de diseño propia, distinta de qué va detrás. _Evitar_: frontera (sobrecargado con el bounded context de DDD).
Analogía: la costura de una prenda, donde puedes descoser y cambiar una pieza sin tocar el resto.

**Adapter**: algo concreto que satisface una interfaz en un seam. Describe un _rol_ (qué hueco llena), no una sustancia (qué tiene dentro).
Analogía: un adaptador de enchufe de viaje: el rol es encajar, lo de dentro da igual.

**Leverage**: lo que obtienen los llamadores de la profundidad. Más capacidad por unidad de interfaz aprendida. Una implementación paga en N llamadas y M tests.

**Locality**: lo que obtiene quien mantiene de la profundidad. Los cambios, bugs, conocimiento y verificación se concentran en un sitio en vez de repartirse entre llamadores. Se arregla una vez y queda arreglado en todas partes.

## Profundo vs superficial

**Módulo profundo** = interfaz pequeña + mucha implementación:

```
┌──────────────────────┐
│  Interfaz pequeña    │  ← Pocas operaciones públicas, parámetros simples
├──────────────────────┤
│                      │
│ Implementación honda │  ← Lógica compleja oculta
│                      │
└──────────────────────┘
```

**Módulo superficial** = interfaz grande + poca implementación (evítalo):

```
┌──────────────────────────────────┐
│       Interfaz grande            │  ← Muchas funciones, parámetros complejos
├──────────────────────────────────┤
│  Implementación fina             │  ← Solo reenvía
└──────────────────────────────────┘
```

Al diseñar una interfaz, pregúntate:

- ¿Puedo reducir el número de operaciones públicas?
- ¿Puedo simplificar los parámetros?
- ¿Puedo esconder más complejidad dentro?

## Principios

- **La profundidad es una propiedad de la interfaz, no de la implementación.** Un módulo profundo puede estar compuesto por dentro de piezas pequeñas y sustituibles; simplemente no forman parte de la interfaz. Un módulo puede tener **seams internos** (privados, usados por sus propios tests) además del **seam externo** de su interfaz.
- **La prueba del borrado.** Imagina que borras el módulo. Si la complejidad desaparece, era un pasamanos. Si la complejidad reaparece en N llamadores, se ganaba el sitio.
- **La interfaz es la superficie de test.** Llamadores y tests cruzan el mismo seam. Si quieres testear _más allá_ de la interfaz, probablemente el módulo tiene la forma equivocada.
- **Un adapter significa un seam hipotético. Dos adapters significan uno real.** No introduzcas un seam (ni una interfaz abstracta) si nada varía a través de él.

## Diseñar para testeabilidad

Las buenas interfaces hacen que testear sea natural:

1. **Acepta dependencias, no las crees.**

   ```text
   // Testeable
   procesarOrden(orden, cobrador)

   // Difícil de testear
   procesarOrden(orden):
       cobrador = nuevoClienteGestorPagos(env("KEY"))
       ...
   ```

2. **Devuelve resultados, no produzcas efectos laterales.**

   ```text
   // Testeable
   calcularDescuento(carrito) -> Descuento

   // Difícil de testear
   aplicarDescuento(carrito):
       carrito.total -= descuento     // muta el argumento
   ```

3. **Superficie pequeña.** Menos operaciones públicas = menos tests necesarios. Menos parámetros = setup de test más simple.

4. **Interfaces del lado del consumidor.** Declara la interfaz donde se usa, con las operaciones mínimas que ese consumidor necesita.

## Relaciones

- Un **módulo** tiene exactamente una **interfaz** (la superficie que presenta a llamadores y tests).
- La **profundidad** es una propiedad de un **módulo**, medida contra su **interfaz**.
- Un **seam** es donde vive la **interfaz** de un **módulo**.
- Un **adapter** se sitúa en un **seam** y satisface la **interfaz**.
- La **profundidad** produce **leverage** para los llamadores y **locality** para quien mantiene.

## Enfoques descartados

- **Profundidad como cociente entre líneas de implementación y de interfaz** (Ousterhout): premia inflar la implementación. Aquí usamos profundidad como leverage.
- **"Interfaz" como la palabra clave `interface` de un lenguaje o los métodos públicos de una clase**: demasiado estrecho; aquí la interfaz incluye todo lo que el llamador debe saber.
- **"Frontera"**: sobrecargado con el bounded context de DDD. Di **seam** o **interfaz**.

## Para profundizar

- **Profundizar un grupo de módulos según sus dependencias**: ver [DEEPENING.md](DEEPENING.md) (categorías de dependencias, disciplina de seams y testing que reemplaza en vez de apilar).
- **Explorar interfaces alternativas**: ver [DESIGN-IT-TWICE.md](DESIGN-IT-TWICE.md) (sub-agentes en paralelo que diseñan la interfaz de formas radicalmente distintas para compararlas).
