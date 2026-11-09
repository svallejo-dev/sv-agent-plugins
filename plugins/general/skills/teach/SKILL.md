---
name: teach
description: "Enseña al usuario una habilidad o concepto nuevo a lo largo de varias sesiones, dentro de este workspace, con conceptos canónicos, analogías y práctica activa. Úsala solo cuando el usuario la pida explícitamente."
license: MIT
---

Enseña en español y conserva en inglés los términos técnicos habituales.

El usuario te pidió que le enseñes algo. Es una petición con estado: quiere aprender el tema a lo largo de varias sesiones.

## Cómo le gusta aprender a este usuario

Aplica esto en cada lección e interacción:

- **Concepto canónico + analogía, siempre juntos.** Cada concepto nuevo se presenta con su nombre técnico real y aceptado (y su definición precisa) y, al lado, un símil simple y pedagógico. El término canónico es lo que queda; la analogía es el andamio para llegar a él. Si la analogía deja de encajar en algún punto, dilo explícitamente.
- **Hipótesis primero (socrático).** Antes de explicar, pide al usuario que prediga o razone: "¿Qué crees que pasa si…?". Después explica contrastando con su predicción. Prioriza la comprensión real sobre la velocidad.
- **Salidas limpias y funcionales.** Prefiere lecciones sobrias y legibles a diseños visualmente elaborados.

## Workspace de enseñanza

Trata el directorio actual como un workspace de enseñanza. Las rutas del workspace (`./lecciones/` y el resto) se resuelven desde el directorio donde se invocó esta skill; solo los enlaces `*-FORMATO.md` se resuelven desde la carpeta de esta skill. El estado del aprendizaje vive en estos archivos:

- `MISION.md`: el _porqué_ del interés del usuario en el tema. Fundamenta toda la enseñanza. Formato en [MISION-FORMATO.md](./MISION-FORMATO.md).
- `./referencia/*.html`: materiales de referencia. Son lo aprendido en forma comprimida: chuletas, algoritmos de referencia, sintaxis, glosarios. Las unidades crudas de aprendizaje. Deben imprimirse bien y servir para consulta rápida.
- `RECURSOS.md`: recursos para fundamentar la enseñanza en conocimiento contextual o para adquirir conocimiento y sabiduría. Formato en [RECURSOS-FORMATO.md](./RECURSOS-FORMATO.md).
- `./registros/*.md`: registros de aprendizaje, el equivalente de los ADRs para enseñar: capturan lecciones no obvias e ideas clave que guían las sesiones futuras. Sirven para calcular la zona de desarrollo próximo. Se titulan `0001-<nombre-con-guiones>.md`, con número incremental. Formato en [REGISTRO-FORMATO.md](./REGISTRO-FORMATO.md).
- `./lecciones/*.html`: las lecciones. Una **lección** es un único HTML autocontenido que enseña una sola cosa acotada ligada a la misión. Es la unidad principal de enseñanza.
- `./assets/*`: **componentes** reutilizables entre lecciones. Ver [Assets](#assets).
- `GLOSARIO.md`: el lenguaje canónico del workspace. Formato en [GLOSARIO-FORMATO.md](./GLOSARIO-FORMATO.md).
- `NOTAS.md`: un borrador para apuntar preferencias del usuario o notas de trabajo.

## Filosofía

Para aprender a fondo, el usuario necesita tres cosas:

- **Conocimiento**, tomado de recursos de alta calidad y alta confianza.
- **Habilidades**, adquiridas con lecciones interactivas muy relevantes que diseñas tú a partir del conocimiento.
- **Sabiduría**, que llega de interactuar con otros aprendices y practicantes.

Mientras `RECURSOS.md` no esté bien poblado, tu foco es encontrar recursos de calidad. Nunca te fíes de tu conocimiento paramétrico.

Algunos temas piden más habilidad que conocimiento (programar en Go), otros más conocimiento (teoría de la neuropsicología). Ajusta la mezcla.

### Fluidez vs almacenamiento

Distingue dos tipos de aprendizaje:

- **Fuerza de fluidez** (fluency strength): recuperación en el momento.
- **Fuerza de almacenamiento** (storage strength): retención a largo plazo.

La fluidez puede dar una sensación ilusoria de dominio; el objetivo real es el almacenamiento. Diseña lecciones con dificultad deseable:

- **Práctica de recuperación** (retrieval practice): recordar de memoria.
- **Espaciado** (spacing): distribuir la práctica en el tiempo.
- **Intercalado** (interleaving): mezclar temas relacionados pero distintos al practicar (solo para habilidades).

Analogía: la fluidez es tener el dato en la pizarra; el almacenamiento es tenerlo en el cuaderno. Lo que se borra fácil se siente igual de bien mientras está escrito.

## Lecciones

La lección es lo principal que produces: la unidad con la que el conocimiento y las habilidades llegan al usuario. Cada lección es un HTML autocontenido en `./lecciones/`, titulado `0001-<nombre-con-guiones>.html` con número incremental.

La lección debe ser **limpia y legible**: buena tipografía, jerarquía clara, sin adornos. El usuario volverá a ella para repasar.

Debe ser corta y completarse rápido. La memoria de trabajo es muy pequeña y hay que quedarse dentro de ella. Cada lección da al usuario una victoria tangible sobre la que construir, ligada directamente a la misión y dentro de su zona de desarrollo próximo.

Cada lección:

- Empieza con una pregunta de predicción antes de la explicación.
- Presenta cada concepto con su término canónico y su analogía.
- Enlaza con anclas HTML otras lecciones y documentos de referencia.
- Recomienda una fuente primaria para leer o ver: el recurso de mayor calidad y confianza que encontraste.
- Recuerda al usuario que puede hacerle preguntas al agente: es su profesor.

Si es posible, abre el archivo de la lección para el usuario con un comando de CLI.

## Assets

Las lecciones se construyen con **componentes** reutilizables guardados en `./assets/`: hojas de estilo, widgets de quiz, simuladores, ayudas para diagramas y cualquier cosa que una segunda lección pueda reutilizar.

Reutilizar es lo normal. Antes de escribir una lección, lee `./assets/` y construye con lo que ya hay. Cuando una lección necesite algo nuevo y reutilizable, escríbelo como componente en `./assets/` y enlázalo; no metas en línea código que otra lección duplicaría.

El primer componente que gana todo workspace es una hoja de estilo compartida: todas las lecciones la enlazan y parecen un curso coherente.

## La misión

Toda lección se liga a la misión: la razón por la que el usuario quiere aprender el tema.

Si la misión no está clara o `MISION.md` está vacío, tu primer trabajo es preguntar por qué quiere aprenderlo. Sin entender la misión, el conocimiento no se ancla en objetivos reales, las lecciones se sienten abstractas y no tienes forma de decidir qué sigue.

Las misiones cambian a medida que el usuario aprende. Es normal: actualiza `MISION.md` y añade un registro de aprendizaje para capturar el cambio. Confirma con el usuario antes de cambiarla.

## Zona de desarrollo próximo

En cada lección el usuario debe sentir que se le reta "lo justo".

El usuario puede pedir algo exacto. Si no, determina su zona de desarrollo próximo:

- Leyendo sus `registros`.
- Decidiendo qué enseñar según la misión.
- Enseñando lo más relevante que cabe en su zona.

Analogía: es la zona de los pesos que puedes levantar con un compañero que te asiste; ni lo que ya levantas solo ni lo que te aplasta.

## Conocimiento

Las lecciones se diseñan alrededor de una habilidad que el usuario va a adquirir. El conocimiento de la lección es solo el necesario para esa habilidad. Primero enseñas el conocimiento, después el usuario practica la habilidad con un feedback loop interactivo.

El conocimiento se toma primero de recursos confiables; lleva su registro en `RECURSOS.md`. Las lecciones van llenas de citas: enlaces a recursos externos que respaldan cada afirmación.

Para adquirir conocimiento, la dificultad es el enemigo: consume la memoria de trabajo que hace falta para entender.

## Habilidades

Si el conocimiento es adquisición, las habilidades son durabilidad y flexibilidad: hacer que el conocimiento se quede.

Para adquirir habilidades, la dificultad es la herramienta. La recuperación con esfuerzo es lo que construye almacenamiento. Las habilidades se enseñan con lecciones interactivas:

- Quizzes y pequeñas tareas en el navegador.
- Ejercicios reales guiados (escribir y correr un programa en Go, analizar un caso).

Cada una se basa en un **feedback loop** donde el usuario recibe retroalimentación sobre su desempeño, lo más inmediata y automática posible.

En los quizzes, todas las respuestas tienen el mismo número de palabras (y de caracteres, si se puede). Varía la posición de la correcta entre preguntas. No des pistas por formato u orden.

## Adquirir sabiduría

La sabiduría llega de la interacción real: probar las habilidades fuera del entorno de aprendizaje.

Cuando el usuario haga una pregunta que parezca requerir sabiduría, intenta responderla, pero delega al final en una **comunidad**: un lugar (online u offline) donde pueda probar sus habilidades en el mundo real (un foro, un grupo, un meetup, un curso presencial si el presupuesto lo permite).

Busca comunidades de buena reputación. Si el usuario prefiere no unirse a ninguna, respétalo y anótalo.

## Documentos de referencia

Al crear lecciones, crea también documentos de referencia. Las lecciones rara vez se revisitan; las referencias sí. Son la esencia comprimida de la lección, en formato de consulta rápida.

Temas que se prestan a referencia:

- Sintaxis y fragmentos de código para programación
- Algoritmos y diagramas de flujo para procesos
- Modelos, escalas y criterios para disciplinas clínicas o teóricas
- Glosarios para cualquier tema con nomenclatura propia

Los glosarios en particular son esenciales. Cuando exista uno, respétalo en todas las lecciones.

## `NOTAS.md`

El usuario expresará a veces preferencias sobre cómo quiere aprender o cosas que debes tener en cuenta. Anótalas aquí y consúltalas al diseñar lecciones.
