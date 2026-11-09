# Formato de ADR

Los ADRs (Architecture Decision Records) viven en `docs/adr/` con numeración secuencial: `0001-slug.md`, `0002-slug.md`, etc.

Crea `docs/adr/` de forma perezosa: solo cuando haga falta el primer ADR.

## Plantilla

```md
# {Título corto de la decisión}

{1-3 frases: el contexto, qué decidimos y por qué.}
```

Eso es todo. Un ADR puede ser un solo párrafo. El valor está en dejar constancia de _que_ se tomó una decisión y _por qué_, no en rellenar secciones.

## Secciones opcionales

Inclúyelas solo cuando aporten valor real. La mayoría de ADRs no las necesita.

- **Estado** en frontmatter (`propuesto | aceptado | obsoleto | reemplazado por ADR-NNNN`): útil cuando las decisiones se revisan.
- **Opciones consideradas**: solo cuando merece la pena recordar las alternativas rechazadas.
- **Consecuencias**: solo cuando hay efectos posteriores no obvios.

## Numeración

Busca el número más alto en `docs/adr/` y súmale uno.

## Cuándo ofrecer un ADR

Las tres condiciones deben cumplirse:

1. **Difícil de revertir**: cambiar de opinión después tiene un coste real.
2. **Sorprendente sin contexto**: un lector futuro mirará el código y pensará "¿por qué demonios lo hicieron así?".
3. **Fruto de un trade-off real**: había alternativas genuinas y se eligió una por razones concretas.

Si una decisión es fácil de revertir, sáltala: simplemente se revierte. Si no sorprende, nadie preguntará. Si no había alternativa real, no hay nada que registrar más allá de "hicimos lo obvio".

### Qué califica

- **Forma de la arquitectura.** "Usamos un monorepo." "El modelo de escritura es event-sourced y el de lectura se proyecta en Postgres."
- **Patrones de integración entre contextos.** "Suscripciones y Cobros se comunican con eventos de dominio, no con HTTP síncrono."
- **Tecnologías con lock-in.** Base de datos, bus de mensajes, proveedor de auth, plataforma de despliegue. No cada librería: solo las que costaría un trimestre cambiar.
- **Decisiones de frontera y alcance.** "Los datos del Cliente pertenecen al contexto Clientes; los demás solo los referencian por ID." Los "no" explícitos valen tanto como los "sí".
- **Desviaciones deliberadas del camino obvio.** "Usamos SQL a mano en vez de un ORM porque X." Todo lo que un lector razonable supondría al revés. Evita que el siguiente ingeniero "arregle" algo que era intencional.
- **Restricciones que el código no muestra.** "No podemos usar el proveedor X por requisitos de PCI." "La respuesta debe tardar menos de 200 ms por el contrato con el partner."
- **Alternativas rechazadas cuando el rechazo no es obvio.** Si se consideró gRPC y se eligió REST por razones sutiles, regístralo; si no, alguien propondrá gRPC otra vez en seis meses.
