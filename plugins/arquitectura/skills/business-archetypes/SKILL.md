---
name: business-archetypes
description: "Arquetipos de negocio para diseñar sin métricas previas (diseño exploratorio, PoC, producto nuevo). Cada arquetipo (streaming y media, fintech y pagos, ticketing y eventos en vivo, e-commerce y marketplace, social y mensajería, SaaS B2B, IoT y telemetría, movilidad y logística, healthtech, plataforma de IA, plataforma de eventos interna) da fuerzas dominantes, forma de la carga, invariantes, subdominios típicos, arquitectura de referencia, modos de fallo e hipótesis de PoC. Lo cargan system-design, capacity-estimation, design-stress-test y strategic-design; úsalo también cuando el usuario diga \"es tipo Netflix/Stripe/Uber\" o describa un producto sin números."
license: MIT
---

# Arquetipos de negocio

Responde en español y conserva en inglés los términos técnicos habituales.

Cuando no hay métricas, **el tipo de negocio ya dice mucho**: un sistema de pagos no tolera duplicados aunque mueva poco tráfico; una venta de entradas recibe en un minuto lo que no recibe en un mes; un servicio de streaming es, ante todo, un problema de ancho de banda. El arquetipo reemplaza a la medición como punto de partida: no da números exactos, da **qué fuerzas mandan** y **qué preguntas cambian el diseño**.

**Analogía:** un médico sin análisis de laboratorio no se niega a atender. Parte del cuadro clínico típico (edad, síntomas, contexto), trata con lo razonable y pide el análisis que más incertidumbre quita. El arquetipo es el cuadro clínico.

## Cómo usarlo

1. **Identifica el arquetipo** a partir de la descripción del producto. Si el usuario dice "es tipo X", úsalo como pista, pero confirma la fuerza que importa ("¿te refieres a la escala o a la naturaleza en tiempo real?").
2. **Combina cuando aplique.** Muchos productos son mezcla: una plataforma de streaming con suscripciones es streaming + fintech (en la parte de cobro); una app de salud con telemedicina es healthtech + mensajería en tiempo real. Toma de cada arquetipo la parte que corresponde a cada subdominio, y no apliques los invariantes del más estricto a todo el sistema.
3. **Lee solo los archivos que aplican** en `references/`.
4. **Convierte el arquetipo en entradas para las demás skills**:
   - Fuerzas, invariantes y preguntas → requisitos de `system-design`.
   - Forma de la carga y escenarios de escala → modo exploratorio de `capacity-estimation`.
   - Modos de fallo típicos → semilla de `design-stress-test` cuando no hay incidentes propios.
   - Subdominios típicos → primer borrador de `strategic-design`.
   - Hipótesis de PoC → plan del experimento.
5. **Declara que es un supuesto de arquetipo**, no una medición, y qué medición lo sustituirá.

| Arquetipo | Archivo | Fuerza que suele mandar |
|---|---|---|
| Streaming y media (VOD y en vivo) | [streaming-media.md](references/streaming-media.md) | Ancho de banda y picos de audiencia simultánea |
| Fintech y pagos | [fintech-pagos.md](references/fintech-pagos.md) | Corrección: cero duplicados, auditoría, compliance |
| Ticketing, reservas y ventas flash | [ticketing-eventos.md](references/ticketing-eventos.md) | Contención por inventario escaso en picos extremos |
| E-commerce y marketplace | [ecommerce-marketplace.md](references/ecommerce-marketplace.md) | Lectura masiva de catálogo + checkout correcto |
| Social, feeds y mensajería | [social-mensajeria.md](references/social-mensajeria.md) | Fan-out, tiempo real y grafos sesgados (celebrities) |
| SaaS B2B multi-tenant | [saas-b2b.md](references/saas-b2b.md) | Aislamiento entre tenants y tenants gigantes |
| IoT y telemetría | [iot-telemetria.md](references/iot-telemetria.md) | Ingesta de escrituras continua y series temporales |
| Movilidad, logística y geolocalización | [movilidad-logistica.md](references/movilidad-logistica.md) | Estado geoespacial en tiempo real y matching |
| Healthtech | [healthtech.md](references/healthtech.md) | Privacidad, auditoría e integración con terceros clínicos |
| Plataforma de IA (inferencia) | [plataforma-ia.md](references/plataforma-ia.md) | Cómputo caro y escaso (GPU), latencia por token |
| Plataforma de eventos interna (bus, integración) | [plataforma-eventos.md](references/plataforma-eventos.md) | Contratos entre equipos, orden, entrega y replay |

## Si el negocio no encaja en ningún arquetipo

Deriva las fuerzas con estas preguntas, que son las que distinguen a los arquetipos entre sí:

1. ¿Qué es peor para el negocio: un dato incorrecto o un dato que llega tarde?
2. ¿La carga es estable, con picos diarios, o con picos de evento (×10-×100 en minutos)?
3. ¿Domina la lectura o la escritura? ¿Los objetos son pequeños (registros) o grandes (media, archivos)?
4. ¿Hay un recurso escaso que muchos se disputan (inventario, conductores, GPUs)?
5. ¿Hay entidades desproporcionadas (un tenant, un usuario, un producto que concentra la carga)?
6. ¿Qué regulación aplica (datos personales, pagos, salud, sector financiero)?
7. ¿Qué tiene que pasar en tiempo real (menos de un segundo) y qué puede ser diferido?
8. ¿De qué terceros depende el flujo crítico?

Con las respuestas, elige el arquetipo más cercano para las partes que encajan y trata el resto como hipótesis explícitas.

## Límites

Los casos públicos citados en cada arquetipo son el "camino recorrido" de otros: úsalos como punto de partida y verifica los detalles con `research` antes de citarlos en un documento. Su escala casi nunca es la tuya.
