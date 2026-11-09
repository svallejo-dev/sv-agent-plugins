---
name: domain-modeling
description: "Construye y afina el modelo de dominio de un proyecto. Úsala cuando se discuta la terminología del código o del negocio, al escribir o editar un GLOSARIO.md, o al registrar o editar un ADR."
license: MIT
---

# Modelado de dominio

Responde en español y conserva en inglés los términos técnicos habituales.

Construye y afina activamente el modelo de dominio mientras se diseña: cuestiona términos, inventa escenarios límite y deja por escrito el glosario y las decisiones en cuanto cristalizan. (Solo _leer_ `GLOSARIO.md` para usar su vocabulario no es esta skill; eso es un hábito de una línea que cualquier skill hace. Esta skill es para cuando el modelo cambia.)

Analogía: el glosario es el diccionario de la casa y los ADRs son las actas de las reuniones donde se decidió algo difícil de deshacer.

## Estructura de archivos

Si existe `docs/agentes/dominio.md` (lo escribe `setup`), sigue sus rutas. Si no, usa este layout por defecto. La mayoría de repos tiene un solo contexto:

```
/
├── GLOSARIO.md
├── docs/
│   └── adr/
│       ├── 0001-eventos-de-dispositivo-via-kafka.md
│       └── 0002-postgres-para-el-modelo-de-escritura.md
└── src/
```

Si existe un `MAPA-GLOSARIO.md` en la raíz, el repo tiene varios contextos y el mapa indica dónde vive cada uno:

```
/
├── MAPA-GLOSARIO.md
├── docs/adr/                          ← decisiones de todo el sistema
└── src/
    ├── suscripciones/
    │   ├── GLOSARIO.md
    │   └── docs/adr/                  ← decisiones del contexto
    └── cobros/
        ├── GLOSARIO.md
        └── docs/adr/
```

Crea los archivos de forma perezosa: solo cuando tengas algo que escribir. Si no hay `GLOSARIO.md`, créalo cuando se resuelva el primer término. Si no hay `docs/adr/`, créalo cuando haga falta el primer ADR.

## Durante la sesión

### Contrasta con el glosario

Cuando el usuario use un término que choca con el lenguaje de `GLOSARIO.md`, señálalo de inmediato: "Tu glosario define 'cancelación' como X, pero parece que quieres decir Y. ¿Cuál es?"

### Afina el lenguaje difuso

Cuando el usuario use términos vagos o sobrecargados, propón un término canónico preciso: "Dices 'cuenta': ¿te refieres al Cliente o al Usuario? Son cosas distintas."

### Discute escenarios concretos

Cuando se hable de relaciones del dominio, ponlas a prueba con escenarios específicos. Inventa escenarios que exploren casos límite y obliguen a precisar las fronteras entre conceptos.

### Cruza con el código

Cuando el usuario afirme cómo funciona algo, comprueba si el código está de acuerdo. Si encuentras una contradicción, muéstrala: "Tu código cancela Suscripciones completas, pero acabas de decir que la cancelación parcial es posible. ¿Qué es lo correcto?"

### Actualiza GLOSARIO.md en el momento

Cuando un término se resuelva, actualiza `GLOSARIO.md` ahí mismo, sin acumular cambios. Usa el formato de [GLOSARIO-FORMATO.md](./GLOSARIO-FORMATO.md).

`GLOSARIO.md` no contiene ningún detalle de implementación. No es una spec, ni un borrador, ni un registro de decisiones técnicas: es un glosario y nada más.

### Ofrece ADRs con moderación

Ofrece crear un ADR solo cuando se cumplan las tres condiciones:

1. **Difícil de revertir**: cambiar de opinión después tiene un coste real.
2. **Sorprendente sin contexto**: un lector futuro se preguntará "¿por qué lo hicieron así?".
3. **Fruto de un trade-off real**: había alternativas genuinas y se eligió una por razones concretas.

Si falta cualquiera de las tres, no hay ADR. Usa el formato de [ADR-FORMATO.md](./ADR-FORMATO.md).
