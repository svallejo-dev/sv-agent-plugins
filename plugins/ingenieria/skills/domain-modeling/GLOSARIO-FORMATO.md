# Formato de GLOSARIO.md

## Estructura

```md
# {Nombre del contexto}

{Una o dos frases: qué es este contexto y por qué existe.}

## Lenguaje

**Dispositivo**:
Un equipo físico (Smart TV, móvil, set-top box) registrado a nombre de un Cliente.
_Evitar_: device, terminal, aparato

**Suscripción**:
El derecho de un Cliente a consumir contenido durante un periodo pagado.
_Evitar_: plan, membresía

**Cliente**:
Una persona que contrata Suscripciones y registra Dispositivos.
_Evitar_: usuario, cuenta, abonado
```

## Reglas

- **Sé opinativo.** Cuando varias palabras nombran el mismo concepto, elige la mejor y lista las demás en `_Evitar_`.
- **Definiciones cortas.** Una o dos frases como máximo. Define lo que el término ES, no lo que hace.
- **Solo términos propios de este contexto.** Los conceptos generales de programación (timeouts, tipos de error, utilidades) no entran aunque el proyecto los use mucho. Antes de añadir un término pregunta: ¿es un concepto único de este dominio o un concepto general? Solo entra el primero.
- **Agrupa en subtítulos** cuando aparezcan grupos naturales. Si todos los términos pertenecen a un área cohesiva, una lista plana basta.
- **Idioma.** Escribe los términos en el idioma que usa el negocio. Si el código usa el término en inglés (`Device`), indícalo en la definición para que el mapeo sea explícito.

## Un contexto o varios

**Un contexto (la mayoría):** un `GLOSARIO.md` en la raíz del repo.

**Varios contextos:** un `MAPA-GLOSARIO.md` en la raíz lista los contextos, dónde viven y cómo se relacionan:

```md
# Mapa de glosarios

## Contextos

- [Suscripciones](./src/suscripciones/GLOSARIO.md): altas, renovaciones y bajas
- [Cobros](./src/cobros/GLOSARIO.md): cargos a medios de pago y reintentos
- [Dispositivos](./src/dispositivos/GLOSARIO.md): registro y límites de equipos por Cliente

## Relaciones

- **Suscripciones → Cobros**: Suscripciones emite `RenovacionSolicitada`; Cobros la consume para generar el cargo
- **Cobros → Suscripciones**: Cobros emite `CobroRechazado`; Suscripciones suspende tras N reintentos
- **Dispositivos ↔ Suscripciones**: comparten `ClienteID`
```

Infiere qué estructura aplica:

- Si existe `MAPA-GLOSARIO.md`, léelo para encontrar los contextos.
- Si solo existe un `GLOSARIO.md` en la raíz, hay un contexto.
- Si no existe ninguno, crea un `GLOSARIO.md` en la raíz cuando se resuelva el primer término.

Con varios contextos, infiere a cuál se refiere el tema actual. Si no está claro, pregunta.
