# Docs de dominio

Cómo deben consumir las skills de ingeniería la documentación de dominio de este repo al explorar el código.

## Antes de explorar, lee esto

- **`GLOSARIO.md`** en la raíz, o
- **`MAPA-GLOSARIO.md`** en la raíz si existe: apunta a un `GLOSARIO.md` por contexto. Lee los relevantes para el tema.
- **`docs/adr/`**: lee los ADRs que tocan el área en la que vas a trabajar. En repos con varios contextos, revisa también `docs/adr/` dentro de cada contexto.

Si alguno de estos archivos no existe, **sigue en silencio**. No señales su ausencia ni sugieras crearlos de antemano. La skill `domain-modeling` (vía `grill-with-docs`) los crea cuando de verdad se resuelve un término o una decisión.

## Estructura

Un contexto (la mayoría):

```
/
├── GLOSARIO.md
├── docs/adr/
└── src/
```

Varios contextos (hay un `MAPA-GLOSARIO.md` en la raíz):

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

## Usa el vocabulario del glosario

Cuando tu salida nombre un concepto del dominio (el título de un ticket, una propuesta de refactor, una hipótesis, el nombre de un test), usa el término tal como lo define `GLOSARIO.md`. No derives a sinónimos que el glosario marca como `_Evitar_`.

Si el concepto que necesitas no está en el glosario, es una señal: o estás inventando lenguaje que el proyecto no usa (reconsidéralo) o hay un hueco real (anótalo para `domain-modeling`).

## Señala conflictos con ADRs

Si tu salida contradice un ADR existente, dilo explícitamente en vez de ignorarlo:

> _Contradice el ADR-0007 (eventos de dispositivo vía Kafka), pero vale la pena reabrirlo porque…_
