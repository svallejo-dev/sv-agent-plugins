---
name: writing-for-agents
description: "Referencia para escribir documentos que consume un agente. Úsala al crear o editar skills o system prompts de agentes, o al modificar AGENTS.md o CLAUDE.md."
license: MIT
---

Responde en español y conserva en inglés los términos técnicos habituales.

Referencia para escribir cualquier documento que consume un agente: una skill, un `AGENTS.md` / `CLAUDE.md`, un system prompt, un doc al que se llega por un puntero. El empaquetado cambia; la escritura no. Las mismas palancas hacen predecible a cada uno: el objetivo es que el agente siga el mismo _proceso_ en cada ejecución, no que produzca la misma salida.

Si el documento que escribes es una skill, lee [SKILL-MECHANICS.md](SKILL-MECHANICS.md) para el frontmatter, la elección de invocación y las skills router.

## Punteros de contexto

Un **puntero de contexto** (context pointer) es una referencia que vive en el contexto del agente, nombra material que está fuera del contexto y codifica la condición para ir a buscarlo. La descripción de una skill es uno; una línea de `AGENTS.md` que nombra un doc es el mismo objeto. La _redacción_ del puntero, no su destino, decide cuándo el agente alcanza el material y con qué fiabilidad. Un destino imprescindible detrás de un puntero mal redactado es un bug de varianza: afina primero la redacción, y mete el material en línea solo si afinar falla.

Analogía: el puntero es el letrero de una puerta. Lo que hay dentro de la sala da igual si el letrero no dice cuándo entrar.

Un puntero hace dos trabajos: decir qué es el material y listar las **ramas** que deben disparar la búsqueda (una rama es un caso distinto que el documento maneja, de modo que distintas ejecuciones toman caminos distintos). Cada palabra de un puntero siempre cargado cuesta en cada turno, así que merece una poda aún más dura que el cuerpo:

- **Pon delante la palabra guía**: en el puntero es donde hace su trabajo de disparo.
- **Un disparador por rama.** Los sinónimos que renombran una misma rama son una rama escrita dos veces; colápsalos y deja solo las ramas genuinamente distintas.
- **Corta la identidad que el cuerpo ya lleva.**

## Las dos cargas

Cada documento y cada puntero que añades gasta uno de dos presupuestos:

- **Carga de contexto** (context load): el coste del material siempre cargado sobre la ventana del agente. Una línea de `AGENTS.md`, la descripción de una skill, todo lo que está en contexto cada turno, gastando tokens y atención se dispare o no.
- **Carga cognitiva** (cognitive load): el coste sobre el humano: qué documentos existen y cuándo recurrir a cada uno. El humano es el índice. No es un coste a minimizar: es el precio de la agencia humana. Gástala donde importa el juicio humano y elimínala donde no.

El material al que solo se llega por un puntero se libra de la carga de contexto al precio de la línea del propio puntero; el material sin ningún puntero vive entero sobre la carga cognitiva.

## Jerarquía de información

Un documento se construye con dos tipos de contenido: **pasos** (las acciones ordenadas que hace el agente) y **referencia** (definiciones, reglas, hechos que se consultan a demanda). Se mezclan libremente: todo pasos (una receta), todo referencia (las reglas de una revisión, esta skill) o ambos. La decisión central es en qué peldaño de la **jerarquía de información** va cada pieza, una escalera ordenada por la urgencia con que el agente necesita el material:

1. **Paso en el archivo**: el peldaño principal, lo que el agente hace, en orden.
2. **Referencia en el archivo**: se consulta a demanda. A menudo es un conjunto plano legítimo (todas las reglas de una revisión en un peldaño), y eso está bien.
3. **Referencia revelada**: sacada a un archivo aparte, alcanzada por un puntero, cargada solo cuando el puntero se dispara. Va desde un archivo hermano en la misma carpeta hasta referencia totalmente externa que cualquier documento puede apuntar.

Si bajas muy poco, la cima se hincha; si bajas demasiado, escondes material que el agente sí necesita. Esa tensión es toda la decisión.

**Revelación progresiva** (progressive disclosure): bajar por la escalera (fuera del archivo principal y detrás de un puntero) para que la cima siga legible. No es sobre todo una optimización de tokens: es cómo se protege la jerarquía. La ramificación es la prueba más limpia: deja en línea lo que necesitan todas las ramas y pon detrás de un puntero lo que solo alcanzan algunas. Cuando un documento tiene pasos, la referencia en línea que debería estar revelada los entierra y convierte atenderlos en una moneda al aire: es una palanca de varianza, no solo de legibilidad.

**Co-ubicación** (co-location): el complemento dentro del archivo. La escalera decide _cuánto_ baja una pieza; la co-ubicación decide _qué va a su lado_. Mantén la definición, las reglas y las salvedades de un concepto bajo un mismo encabezado, para que leer una parte traiga a sus vecinas. La prueba: el documento debe leerse como documentación escrita para el agente. (Distinto de la duplicación: duplicar repite un significado en dos sitios; dispersar fragmenta un significado en muchos.)

**Expansión** (sprawl) es el modo de fallo: un documento simplemente demasiado largo, aunque cada línea esté viva y sea única. La atención se diluye en el exceso y cada línea extra es una más que mantener relevante. La cura es la escalera: revela referencia detrás de punteros y divide por rama o por secuencia para que cada camino lleve solo lo que necesita.

## Pasos y criterios de cierre

Cada paso termina en un **criterio de cierre** (completion criterion): la condición que le dice al agente que el trabajo está hecho. Dos propiedades lo convierten en palanca:

- **Claridad**: ¿el agente distingue hecho de no hecho? Un límite vago ("se alcanzó el entendimiento") invita al **cierre prematuro**: terminar el paso antes de tiempo, con la atención puesta en _haber terminado_. Los pasos visibles que quedan por delante tiran; la claridad del criterio resiste. Defiéndete en orden: **afina primero el límite** (local y barato); solo si es irreduciblemente difuso _y_ observas la prisa, esconde los pasos posteriores dividiendo la secuencia. Esconder solo funciona a través de una frontera de contexto real (un traspaso o un sub-agente; una llamada en línea deja los pasos posteriores en contexto y no limpia nada).
- **Exigencia**: cuánto pide. "Cada modelo modificado contabilizado" fuerza un trabajo exhaustivo donde "produce una lista de cambios" no. La exigencia impulsa el **trabajo de campo** (legwork: lo que el agente investiga dentro de la tarea, latente en la redacción en vez de escrito como paso), y no está atada a pasos: "cada regla aplicada" vincula un cuerpo de referencia plana igual que "cada paso hecho" vincula una secuencia.

Los criterios más fuertes son verificables y exhaustivos.

## Cuándo dividir

Dividir un documento en dos gasta una de las dos cargas, así que divide solo cuando el corte lo justifique:

- **Por secuencia**: divide una serie de pasos cuando los pasos posteriores tientan al agente a apurar el que tiene delante. Mantenerlos fuera de la vista genera más trabajo de campo en la tarea actual. Cuidado con lo inverso: fusionar secuencias expone a cada paso los que vienen después e invita al cierre prematuro.
- **Por invocación**, específico de skills: ver [SKILL-MECHANICS.md](SKILL-MECHANICS.md).

## Palabras guía

Una **palabra guía** (leading word) es un concepto compacto que ya vive en el preentrenamiento del modelo y con el que el agente piensa mientras ejecuta el documento (_lección_, _niebla de guerra_, _tracer bullets_). Repetida como token, nunca como frase, acumula una definición distribuida y ancla toda una región de comportamiento con el mínimo de tokens, porque recluta priors que el modelo ya tiene. Acuñar palabras propias funciona si las defines con claridad, pero una palabra inventada no recluta priors: pagas en tokens de definición lo que una palabra preentrenada da gratis. Busca primero una palabra existente.

Ancla dos veces. En el cuerpo, la _ejecución_: el agente recurre al mismo comportamiento cada vez que aparece la palabra, y dentro de referencia plana enfoca la atención en una clase de cosas a buscar. En un puntero, la _invocación_: cuando la misma palabra vive en tus prompts, tus docs y tu código, el agente conecta ese lenguaje compartido con el material y lo alcanza con más fiabilidad.

Busca oportunidades de refactorizar con palabras guía. Un trío escrito en tres sitios, un puntero que gasta una frase en señalar una idea: cada uno pide colapsar en un solo token:

- "rápido, determinista, de bajo coste" → _tight_ (un loop _tight_).
- "un loop en el que confías" → _rojo_, que convierte una compuerta difusa en un estado binario observable (el loop se pone _rojo_ con el bug, o no).

Ganas dos veces: menos tokens y un gancho más nítido para el pensamiento del agente. Asume que todo documento carga reformulaciones que las palabras guía pueden retirar. Ve a buscarlas.

Ojo con el idioma: las palabras guía más fuertes suelen ser los términos técnicos en inglés que el modelo ha visto millones de veces (_seam_, _tracer bullet_, _red-green_). En documentos en español, consérvalos en inglés en vez de traducirlos a una palabra que no recluta priors.

**Negación** es el modo de fallo junto a esta palanca: guiar por prohibición mete el comportamiento prohibido en el contexto y lo vuelve _más_ disponible. _No pienses en un elefante_, y solo hay elefante; la negación es un modificador débil que el concepto fuertemente activado arrolla, así que la prohibición se lee a medias como una instrucción de hacerlo. Escribe el **positivo**: enuncia el comportamiento objetivo ("escribe comentarios de una línea") para que el prohibido nunca se nombre. Una prohibición solo se gana su sitio como guardarraíl duro que no puedes expresar en positivo; aun así, acompáñala del objetivo positivo.

## Poda

- Mantén cada significado en una **única fuente de verdad**: un solo sitio autoritativo, para que cambiar el comportamiento sea editar un lugar. La **duplicación** (el mismo significado en más de un sitio) cuesta mantenimiento y tokens e infla la importancia de un significado por encima de su peldaño real. (Es el inverso accidental de una palabra guía, que repite un token a propósito, nunca el significado.)
- El **entorno** también es fuente de verdad (`go.mod`, el `Makefile`, archivos de configuración, la estructura de directorios, la salida de `--help`), y un documento que lo repite es una **caché**: una copia de una consulta, que solo se gana su carga cuando la consulta es cara. Cachea lo que el agente no encuentra mirando: la convención no escrita, la razón detrás de una elección, la trampa que ninguna configuración confiesa. Deja al entorno las consultas de un archivo o un comando, donde no pueden quedar obsoletas.
- Revisa la **relevancia** de cada línea: ¿sigue influyendo en lo que hace el documento? Una línea pierde relevancia si nunca influyó (mera exposición, o una rama que debería estar revelada) o si quedó obsoleta al cambiar el comportamiento o el mundo que describe. Los documentos cortos son más fáciles de mantener relevantes. Sin disciplina de poda, el destino por defecto es el **sedimento**: capas obsoletas que se asientan porque añadir parece seguro y quitar parece arriesgado.
- Caza **no-ops** frase a frase: una instrucción que el modelo ya cumple por defecto paga carga para no decir nada. La prueba (¿cambia el comportamiento frente al defecto?) es relativa al modelo, no al lector: dos personas que discuten si algo es un no-op discuten sobre el defecto, y se resuelve ejecutando el documento, no debatiendo. Cuando una frase falla, bórrala entera en vez de recortarle palabras. La prueba también evalúa las palabras guía: una demasiado débil para vencer al defecto (_sé minucioso_ cuando el agente ya lo es más o menos) es un no-op, y el arreglo es una palabra más fuerte (_implacable_), no otra técnica.
