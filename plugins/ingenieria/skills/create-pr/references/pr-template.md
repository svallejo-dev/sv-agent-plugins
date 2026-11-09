# Cuerpo de PR de respaldo

Úsalo solo cuando el repo no tenga plantilla de PR y sus PRs recientes no muestren una estructura que valga la pena copiar. Escríbelo en el idioma del repo: en un repo en inglés los encabezados son Summary, Why, What changed, Evidence, Merge danger, Issues.

## Plantilla

~~~markdown
## Resumen

<!-- Una o dos líneas: qué hace este PR. Debajo, el visual más pequeño que deje claro el cambio (ver visuales.md). -->

## Motivación

<!-- El problema que resuelve, el issue o ticket que lo pidió, decisiones de diseño tomadas. -->

## Qué cambió

-

## Evidencia

- **Antes:** <test fallando / salida / captura>
  **Después:** <test pasando / salida / captura>

```bash
# comandos que quien revisa puede pegar para verificarlo
```

## Riesgo de merge

- **Puerta:** <de un sentido o de dos sentidos>
- **Radio de impacto:** <una palabra> · <consecuencias posibles>
- **Migraciones / flags:**
- **Reversa:**

## Issues

Closes #
~~~

Quita las secciones que no apliquen (nada que enlazar → sin sección Issues) en vez de dejarlas vacías.

## Cómo rellenar cada sección

Con `BASE_REF` definido como en SKILL.md (la base traída con fetch, por ejemplo `origin/main`):

| Sección | Fuente | Comando |
|---|---|---|
| Resumen | Síntesis de los commits, no un volcado, más un visual | `git log "$BASE_REF"..HEAD --format=%s` |
| Motivación | Cuerpos de los commits más el issue, ticket o spec enlazado | `git log "$BASE_REF"..HEAD --format=%b` |
| Qué cambió | Un bullet por cambio relevante | `git log "$BASE_REF"..HEAD --format='- %s'` |
| Evidencia | Tests o comandos reales sobre lo que se tocó, con su salida antes y después | `git diff "$BASE_REF"...HEAD --stat` |
| Riesgo de merge | Archivos tocados, migraciones, flags, cambios de contrato | `git diff "$BASE_REF"...HEAD` |
| Issues | Footers `Closes`/`Refs` de los commits | `git log "$BASE_REF"..HEAD --format=%b \| grep -iE '(closes\|fixes\|refs) #'` |

Dos puntos para el log (commits de la rama), tres puntos para el diff (contra el merge-base, para que no aparezcan cambios ajenos que llegaron a la base).

## Guía

- **Evidencia**: las capturas son lo mejor cuando el cambio es visual y el entorno lo permite. Después, la evidencia por ejecución: el test exacto que antes fallaba y ahora pasa, salida de consola, una consulta de métricas antes y después. "Cómo probar" son comandos que se pueden pegar, no "prueba la app".
- **Puerta**: por una puerta de dos sentidos se puede volver; por una de un sentido, no. Un PR barato de revertir es de bajo riesgo. Las acciones destructivas o difíciles de revertir (migraciones que borran datos, contratos con partners, eventos ya publicados) son puertas de un sentido. Analogía: una puerta de dos sentidos es mover muebles; una de un sentido es tirar un muro.
- **Radio de impacto**: el alcance potencial del cambio. Considera consumidores rotos, contratos de API, eventos, rendimiento, configuración por país, feature flags.
- **Reversa**: si no hay migraciones ni flags, dilo; la reversa suele ser "revertir el merge commit", salvo que una migración de datos lo haga inseguro, y entonces explícalo.
- Nunca incluyas secretos, tokens ni contenido de `.env`.

## Ejemplo

Rama `feat/auth-refresh`, commits `feat(auth): add token refresh endpoint` y `test(auth): cover refresh happy path`.

**Título:** `feat(auth): add token refresh endpoint`

~~~markdown
## Resumen

Añade `POST /auth/refresh` para que los clientes renueven el access token sin volver a hacer login.

```text
Handler.Refresh
  sessions.FindByRefreshToken
  tokens.Issue
```

## Motivación

Las sesiones caducaban a la hora sin aviso y los usuarios volvían al login a mitad de flujo. Diseño acordado en #142.

## Qué cambió

- Endpoint de refresh nuevo sobre la tabla `sessions` existente
- Tests del camino feliz y de un refresh token caducado

## Evidencia

- **Antes:** `POST /auth/refresh` → 404
  **Después:** `POST /auth/refresh` → 200 con un access token nuevo

```bash
go test ./internal/auth/...
curl -sS -X POST localhost:8080/auth/refresh -H 'Authorization: Bearer <refresh-token>'
```

## Riesgo de merge

- **Puerta:** de dos sentidos.
- **Radio de impacto:** acotado · solo `internal/auth`; si el refresh falla, los clientes vuelven al login.
- **Migraciones / flags:** ninguno.
- **Reversa:** revertir el merge commit.

## Issues

Closes #142
~~~
