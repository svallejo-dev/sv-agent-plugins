# Formato de GLOSARIO.md (workspace de enseñanza)

`GLOSARIO.md` es el lenguaje canónico de este workspace de enseñanza. Todas las explicaciones, ejercicios y registros deben respetar su terminología. Construirlo es parte del aprendizaje: comprimir un concepto en una definición precisa es evidencia de que el usuario lo entiende.

## Estructura

```md
# Glosario: {Tema}

{Una o dos frases sobre el tema que cubre este glosario.}

## Términos

**Goroutine**:
Una función que se ejecuta de forma concurrente, gestionada por el runtime de Go y no por el sistema operativo.
_Analogía_: un mesero extra que el restaurante contrata al instante y despide al terminar el pedido.
_Evitar_: hilo, thread (son cosas distintas)

**Data race**:
Dos goroutines acceden a la misma variable sin sincronización y al menos una escribe.
_Analogía_: dos personas editando la misma celda de una hoja de cálculo sin verse.
_Evitar_: condición de carrera (más amplio: no toda race condition es un data race)

**Happens-before**:
La relación del modelo de memoria de Go que garantiza que los efectos de una operación son visibles para otra.
_Analogía_: el sello de "recibido" que prueba que la carta llegó antes de responderla.
_Evitar_: orden de ejecución
```

## Reglas

- **Añade un término solo cuando el usuario lo entienda.** El glosario registra conocimiento comprimido; no es un diccionario para aprender. Si el concepto acaba de presentarse, espera a que el usuario lo use correctamente.
- **Término canónico + analogía.** Cada entrada lleva su definición precisa y, en `_Analogía_`, el símil que ayudó a entenderla. La definición es lo que queda; la analogía es el andamio.
- **Sé opinativo.** Cuando varias palabras nombran el mismo concepto, elige la mejor y lista el resto en `_Evitar_`.
- **Definiciones cortas.** Una o dos frases. Define lo que el término ES, no lo que hace ni cómo se usa.
- **Usa los términos del glosario dentro de las definiciones.** Una vez que un término está en el glosario, úsalo en todas partes, incluso dentro de otras definiciones.
- **Agrupa en subtítulos** cuando aparezcan grupos naturales. Una lista plana basta si los términos son cohesivos.
- **Marca las ambigüedades.** Si el campo usa un término de forma laxa, anota la resolución: "En este workspace, 'concurrencia' nunca significa paralelismo."
- **Revisa a medida que se profundiza.** Una definición de la semana uno puede estar mal en la semana seis. Actualízala en su sitio; no dejes entradas obsoletas.
