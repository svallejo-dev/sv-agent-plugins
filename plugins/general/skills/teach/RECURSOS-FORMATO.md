# Formato de RECURSOS.md

`RECURSOS.md` es el conjunto curado de fuentes confiables del tema. El conocimiento de las explicaciones sale de aquí, no de conjeturas paramétricas. La sabiduría sale de las comunidades listadas aquí.

## Estructura

```md
# Recursos: {Tema}

## Conocimiento

- [Libro: _Concurrency in Go_, de Katherine Cox-Buday](https://example.com)
  Texto de referencia sobre goroutines, canales y patrones. Úsalo para: pipelines, cancelación, fan-out/fan-in.
- [Doc oficial: "The Go Memory Model"](https://go.dev/ref/mem)
  Definición canónica de happens-before en Go. Úsalo para: data races, sincronización.

## Sabiduría (comunidades)

- [Gophers Slack, canal #performance](https://example.com)
  Comunidad activa y moderada. Úsalo para: revisar diseños de concurrencia y perfiles de pprof.
- Local: meetup de Go de la ciudad
  Úsalo para: feedback en persona sobre charlas o diseños.
```

## Reglas

- **Solo alta confianza.** Prefiere fuentes primarias, expertos reconocidos, trabajo revisado por pares y comunidades bien moderadas. Si un recurso es marketing disfrazado de educación, déjalo fuera.
- **Anota cada entrada.** Un enlace suelto es inútil en tres meses. Añade una línea: qué cubre y cuándo usarlo.
- **Agrupa en Conocimiento / Sabiduría.** Refleja la filosofía de [SKILL.md](./SKILL.md). Un recurso puede estar en un solo grupo.
- **Haz visibles los huecos.** Si no existe un buen recurso para un área que la misión necesita, añade una sección `## Huecos` con lo que falta. Eso guía búsquedas futuras.
- **Poda sin piedad.** Un recurso que resultó erróneo, superficial o fuera de la misión se elimina, no se entierra. Mejor cinco fuentes buenas que treinta mediocres.
- **Registra las preferencias sobre comunidades.** Si el usuario decidió no unirse a comunidades, anótalo para que las sesiones futuras no insistan.
