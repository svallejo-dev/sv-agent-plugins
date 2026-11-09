---
name: qa-setup
description: "Configura el plugin qa en un repo: modo (solo o dúo), barrera de información, dónde viven los tests de aceptación, qué peldaños de la escalera existen y con qué script se ejecuta cada uno, la comprobación de caja negra y el presupuesto de mutantes. Escribe docs/agentes/qa.md. Úsala solo cuando el usuario la pida explícitamente."
license: MIT
---

# Setup de QA

Responde en español y conserva en inglés los términos técnicos habituales.

Escribe `docs/agentes/qa.md`, la configuración que leen todas las skills de `qa`. Sin ese archivo, las demás se detienen y piden ejecutar la skill `qa-setup`.

**Por qué la configuración fija comandos, y por qué se sella:** `qa-verify` ejecuta exactamente los scripts declarados aquí, no los improvisa. Un agente que decide en el momento cómo correr la suite puede, sin mala intención, elegir el comando que da verde (un subconjunto, un tag excluido). Por eso los comandos viven en scripts dentro de la carpeta de aceptación, y tanto esos scripts como este archivo quedan bajo el sello de cada feature: cambiarlos es cambiar el oráculo, y queda a la vista.

## Proceso

1. Lee `docs/agentes/tracker.md` (de `ingenieria-setup`) para saber dónde viven las specs. Si no existe, el tracker por defecto es `.scratch/`; dilo en una línea.
2. Explora el repo: carpetas de tests de aceptación, `Dockerfile`, `docker-compose`, Makefile, contratos OpenAPI o AsyncAPI, archivos `.feature`, `.hurl`, configuración de Playwright. Propón valores a partir de lo que encuentres.
3. Pregunta, en una sola ronda, lo que no puedas deducir. Usa el mecanismo de preguntas con opciones de tu herramienta si existe (AskUserQuestion en Claude Code); si no, pregunta en texto numerando las opciones:
   - **Modo**: `solo` o `duo`. Ver [../qa-core/referencias/modelo-de-roles.md](../qa-core/referencias/modelo-de-roles.md).
   - **Barrera de información**: N1, N2 o N3. Recomienda N2 si el modo es solo y el trabajo es crítico.
   - **Peldaños disponibles**. Ver [../qa-core/referencias/escalera-de-ambientes.md](../qa-core/referencias/escalera-de-ambientes.md). Un peldaño que la plataforma no ofrece se marca `no disponible`, nunca se omite.
   - **Rama base** contra la que se compara el sello (normalmente `origin/main`).
   - **Presupuesto de tiempo** para los mutantes.
4. Escribe el archivo con la plantilla. Ningún secreto en él: las credenciales se referencian por nombre de variable de entorno.
5. Añade la carpeta de reportes al `.gitignore`. Crea la carpeta de aceptación con un `README.md` de una línea: su contenido está sellado y el dev escala en vez de editar.
6. Dile al usuario el siguiente paso: `qa-acceptance-criteria` sobre la spec de la feature.

## Contrato de los scripts de peldaño

Cada peldaño se ejecuta con un script en `<Aceptación>/bin/` (por ejemplo `peldano-1.sh <feature>`). Si aún no existen, `qa-test-automation` los crea en su paso 1. Todo script de peldaño:

- termina con exit 0 solo si todo está en verde;
- escribe sus reportes JUnit **solo** en el directorio que recibe en `$QA_REPORTES` (vacío y propio de esa ejecución; lo crea `qa-verify`);
- no escribe nada dentro de `<Aceptación>/` (romperías el sello);
- si construye la imagen del servicio, lo hace desde el directorio actual y con el tag `$QA_IMAGEN_TAG` si está definido (lo usa `qa-test-the-tests` para no mezclar imágenes de mutantes con la real);
- no acepta argumentos que filtren escenarios.

## Plantilla de `docs/agentes/qa.md`

```markdown
# Configuración de QA

Modo: solo | duo
Barrera: N1 | N2 | N3
Rama base: origin/main
Tracker: .scratch/
Aceptación: acceptance/            # una subcarpeta por feature + bin/ con los scripts de peldaño
Sello: acceptance/<feature>/.qa-sello.json
Reportes: acceptance-reportes/     # fuera de acceptance/; ignorado por git; una subcarpeta por feature y ejecución

## Peldaños

| Peldaño | Disponible | Script | Variables |
|---|---|---|---|
| 1 hermético | sí | `acceptance/bin/peldano-1.sh <feature>` | el harness fija BASE_URL |
| 2 contrato | sí | `acceptance/bin/peldano-2.sh <feature>` | URLs de sandbox, credenciales por nombre de variable |
| 3 integrado aislado | no disponible | — | — |
| 4 staging | sí | `acceptance/bin/peldano-4.sh <feature>` | STAGING_URL |
| 5 producción | no disponible | — | — |

## Caja negra

Los tests de aceptación en Go viven en un **módulo propio** (`acceptance/go.mod`): el compilador impide importar paquetes `internal/` de otro módulo.
Comprobación (debe salir vacía y con exit 0 de `go list`):
`cd acceptance && go list -deps -test ./... > /tmp/deps.txt && ! grep -E '^<modulo-de-produccion>(/|$)' /tmp/deps.txt`

## Construcción del artefacto

Imagen del servicio: `docker build -t ${QA_IMAGEN_TAG:-<servicio>:qa} .`

## Contratos

| Dependencia | Tipo | Cómo se verifica |
|---|---|---|
| <servicio propio> | Pact modo A, B o D | … |
| <tercero> | learning tests + WireMock | … |

## Mutantes

Comando de suite: `acceptance/bin/peldano-1.sh <feature>`
Limpieza tras cada mutante: `docker rmi -f $QA_IMAGEN_TAG`
Timeout por mutante (s): 900
Presupuesto total: <minutos>; si no cabe antes del PR, se ejecuta en el nocturno
Rutas prohibidas para mutantes: acceptance/ .scratch/ docs/agentes/
```

Para repos que no son Go, la comprobación de caja negra usa el analizador de dependencias del lenguaje, o un `grep` de las rutas de import de producción con verificación del código de salida. Una comprobación que falla al ejecutarse **no** cuenta como superada.
