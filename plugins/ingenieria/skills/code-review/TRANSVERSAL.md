# Rúbrica transversal

Lo que aplica a cualquier cambio en cualquier lenguaje. Recorre cada archivo cambiado con estas dimensiones y registra cada hallazgo con una sola severidad. Los idiomas de un lenguaje concreto no van aquí: los revisa el plugin de ese lenguaje.

## Dimensiones

### 1. Corrección y casos límite
- ¿El código hace lo que dice la intención del cambio?
- Límites: entrada vacía, nulo, cero, negativos, listas de un elemento, overflow, off-by-one, orden, zonas horarias, unicode.
- Caminos de fallo: si una llamada de red o de base de datos falla a mitad, ¿el estado sigue siendo consistente?
- Idempotencia y reintentos donde el flujo los necesita.

### 2. Seguridad
- Inyección (SQL, NoSQL, shell, LDAP): entrada concatenada en vez de parámetros.
- Autenticación y autorización: ¿el permiso se comprueba en el lugar correcto? ¿IDOR? ¿Se decide el acceso con datos que manda el cliente?
- Secretos en el código o en logs: **blocker**, y nunca cites el valor.
- Entrada externa (HTTP, colas, archivos) validada y acotada; límites de tamaño al leer; deserialización segura.
- Criptografía: aleatoriedad segura para tokens, comparación en tiempo constante, sin algoritmos rotos.
- Datos personales: no aparecen en logs, métricas ni mensajes de error.

### 3. Tests
- El comportamiento nuevo o cambiado tiene tests, incluido el camino de fallo y los límites.
- Los tests son deterministas (sin sleeps, reloj ni red sin controlar).
- Un test que pasa de verdad ejercita el código nuevo; no es tautológico (el esperado no se recalcula como lo hace el código).

### 4. Manejo de errores
- Los errores se propagan con contexto en vez de tragarse o loguearse e ignorarse.
- Los errores esperados (no encontrado) se distinguen de los inesperados.
- Sin cierres abruptos del proceso en flujos normales; los recursos se liberan en los caminos de error.

### 5. API y compatibilidad hacia atrás
- Cambios en firmas públicas, endpoints, esquemas, formatos serializados, eventos, variables de entorno.
- Cambios incompatibles (campos renombrados o eliminados, tipos cambiados, defaults, status codes): ¿versionados, deprecados o migrados? ¿Quién depende hoy del comportamiento actual?

### 6. Rendimiento y concurrencia
- Consultas N+1, O(n²) evitable, asignaciones en caminos calientes, falta de paginación.
- Estado compartido sin sincronizar, deadlocks, tareas concurrentes sin forma de terminar, locks mantenidos durante I/O.
- Timeouts en toda llamada a red.

### 7. Tamaño y legibilidad
- ¿Es lo bastante pequeño y enfocado para revisarlo con rigor? ¿Mezcla asuntos?
- Nombres claros y fieles al vocabulario de `GLOSARIO.md`, funciones cohesivas, sin código muerto ni comentado.
- Archivos nombrados por lo que hacen. Los archivos cajón de sastre (`utils`, `helpers`, `common`, `manager`) dificultan navegar en cualquier lenguaje; su severidad depende de las reglas del repo.
- Comentarios que narran lo obvio o banners añaden ruido (minor o nit).

### 8. Documentación y migraciones
- Cambios de comportamiento reflejados en README, docs, CHANGELOG, documentación de API.
- Migraciones de base de datos: ¿reversibles? ¿Bloquean tablas grandes? ¿Compatibles con la versión que sigue desplegada durante el rollout (expand–contract)?
- Flags y configuración nuevos documentados.

### 9. Observabilidad
- Logs en el nivel correcto, con contexto, sin secretos, sin spam en caminos calientes.
- Métricas o trazas en los caminos nuevos que importan operativamente.
- Mensajes de error accionables para quien opera el sistema.

## Smells de diseño (Fowler, _Refactoring_ cap. 3)

Siempre son juicio, nunca violación dura: etiquétalos como "posible <smell>" y dales minor salvo que causen un bug. Un estándar documentado del repo que respalde el patrón los suprime. Cada uno se lee *qué es* → *cómo arreglarlo*.

- **Nombre misterioso**: el nombre no revela qué hace o qué contiene. → renómbralo; si no sale un nombre honesto, el diseño está turbio.
- **Código duplicado**: la misma forma de lógica en más de un hunk o archivo del cambio. → extrae la forma común.
- **Feature Envy**: una función usa más los datos de otro módulo que los suyos. → muévela junto a los datos que envidia.
- **Data Clumps**: los mismos campos o parámetros viajan siempre juntos. → agrúpalos en un tipo.
- **Obsesión por primitivos**: un string o número haciendo de concepto de dominio. → dale su propio tipo.
- **Switches repetidos**: el mismo `switch` o cascada de `if` sobre el mismo tipo en varios sitios. → polimorfismo o una tabla compartida.
- **Cirugía de escopeta**: un cambio lógico obliga a editar muchos archivos dispersos. → reúne lo que cambia junto.
- **Cambio divergente**: un módulo se edita por varias razones sin relación. → divídelo.
- **Generalidad especulativa**: abstracciones, parámetros o hooks para necesidades que nadie pidió. → bórralo hasta que la necesidad aparezca.
- **Cadenas de mensajes**: navegación larga `a.b().c().d()`. → escóndela tras una operación del primer objeto.
- **Intermediario**: un módulo que casi solo delega. → llama directo al destino.
- **Herencia rechazada** (solo en lenguajes con herencia): una subclase ignora o sobrescribe casi todo lo heredado. → composición.

## Severidad

Exactamente una por hallazgo:

- **blocker**: no se puede mergear así; rompe la corrección, la seguridad o un contrato público, pierde datos o introduce una race.
- **major**: debe arreglarse antes del merge; un bug real en un caso plausible, falta de tests para lógica nueva, mal manejo de errores, o la violación de una regla que el propio repo adoptó.
- **minor**: vale la pena arreglarlo, sin riesgo inmediato; claridad, un caso límite improbable, nombres confusos, sugerencias de estilo que el repo no adoptó.
- **nit**: preferencia opcional. Etiquétala para que el autor sepa que puede ignorarla.

## Formato de salida

```markdown
## Revisión: <título del cambio o del PR>

**Veredicto:** pedir cambios | comentar | parece listo · **Intención:** <una línea>
**Resumen:** <2-3 líneas: qué hace bien, qué falta, radio de impacto>
**Conteo:** Transversal 0B/1M/2m/0n · Go 0B/0M/1m/1n · Spec 0B/1M/0m/0n

### Transversal
- **major** `ruta/archivo.ext:LÍNEA`: <qué está mal y por qué>. **Arreglo:** <cambio concreto>

### <Lenguaje>
- **minor** `ruta/archivo.ext:LÍNEA`: … **Arreglo:** …

### Spec
- **major** <requisito citado de la spec>: … **Arreglo:** …

### Lo bueno
- <una o dos cosas que el cambio hace bien>

### Sin cobertura
- <lenguajes sin revisor idiomático, o "no hay spec">
```

Omite las secciones vacías.
