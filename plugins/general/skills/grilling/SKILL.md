---
name: grilling
description: "Interroga al usuario sin tregua sobre un plan, decisión, diseño o idea hasta llegar a un entendimiento compartido. Úsala cuando el usuario quiera poner a prueba su razonamiento, pida \"grill me\", \"interrógame\", \"cuestióname\" o \"stress-test\" de un plan."
license: MIT
---

Responde en español y conserva en inglés los términos técnicos habituales.

Interroga al usuario sin tregua hasta llegar a un entendimiento compartido. Modela la conversación como un **árbol de decisiones**: cada decisión se ramifica en las decisiones que dependen de ella.

Trabaja el árbol por **rondas**. La **frontera** es toda decisión cuyos prerrequisitos ya están resueltos: las preguntas que puedes hacer _ahora_ sin adivinar respuestas que aún no has oído. Haz la frontera completa en una ronda: numera cada pregunta y da tu respuesta recomendada con una línea de por qué. Después espera las respuestas antes de la siguiente ronda.

Formato de una ronda:

```
❓ **P1** - **<título de la pregunta>**: <cuerpo, puede ocupar varios párrafos e incluir opciones>

➡️ <tu respuesta recomendada> (porque <razón en una línea>)

---

❓ **P2** - **<título de la pregunta>**: <cuerpo>

➡️ <tu respuesta recomendada> (porque <razón>)
```

Redacta cada pregunta para que "sí" acepte tu recomendación.

Cada ronda de respuestas cambia el árbol: las decisiones resueltas empujan la frontera hacia fuera y desbloquean las preguntas que dependían de ellas. Recalcula la frontera y haz la siguiente ronda. Una pregunta cuya respuesta depende de otra todavía abierta en esta ronda pertenece a una ronda _posterior_.

Encontrar _hechos_ es tu trabajo, nunca del usuario. Cuando una pregunta de la frontera necesite un dato del entorno (código, archivos, herramientas, git), lanza un sub-agente con contexto limpio para averiguarlo; no le pidas al usuario nada que puedas consultar tú. No te bloquees: una exploración en curso es un prerrequisito sin resolver, así que solo esperan las preguntas que dependen de ella; haz el resto de la frontera ahora. Las _decisiones_ son del usuario: plantéaselas y espera.

Cuando una pregunta use un concepto que el usuario quizá no domine, nómbralo con su término canónico y añade una analogía corta entre paréntesis.

La sesión termina cuando la frontera está vacía: cada rama del árbol visitada y nada asumido en silencio. No actúes sobre el resultado hasta que el usuario confirme que hay entendimiento compartido.
